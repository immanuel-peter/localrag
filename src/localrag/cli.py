import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import datetime
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

from .config import ensure_config_exists, load_config, configure_api_keys
from .vectorstore import VectorStore
from .chatstore import load_chat, save_chat, create_new_chat, get_all_chats
from .llm import send_message_to_llm, get_chat_title
from .models import get_model_metadata, list_supported_models
from .utils import ensure_ollama_model

DEFAULT_MODEL = "gpt-4.1"
LOCALRAG_DIR = os.path.expanduser("~/.localrag")
CHATS_DIR = os.path.join(LOCALRAG_DIR, "chats")
VECTOR_STORE_PATH = os.path.join(LOCALRAG_DIR, "vector_store")
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CONFIG_PATH = os.path.join(LOCALRAG_DIR, "config.json")

console = Console()

def init_localrag():
    """Initializes the necessary directories and config file for LocalRAG."""
    os.makedirs(CHATS_DIR, exist_ok=True)
    os.makedirs(VECTOR_STORE_PATH, exist_ok=True) # Ensure vector store directory exists
    ensure_config_exists(CONFIG_PATH)


@click.group()
def cli():
    """LocalRAG - A local LLM interface with conversation memory."""
    init_localrag()

@cli.command()
@click.argument("model", default="")
def run(model):
    """Start an interactive chat with the specified model."""
    config = load_config(CONFIG_PATH)
    if not model:
        model = config.get("default_model", "gpt-4.1")

    try:
        model_metadata = get_model_metadata(model)
        provider = model_metadata.get("provider")
        runtime = model_metadata.get("runtime", provider)
        model = model_metadata["full_name"]
    except ValueError as e:
        console.print(f"[red]{e}[/red]")
        console.print("Supported models are:\n" + list_supported_models())
        return

    if runtime == "OpenAI" and not config.get("OPENAI_API_KEY"):
        console.print("[red]Error: OpenAI API key not set. Run 'localrag config' to set your API keys.[/red]")
        return
    elif runtime == "Anthropic" and not config.get("ANTHROPIC_API_KEY"):
        console.print("[red]Error: Anthropic API key not set. Run 'localrag config' to set your API keys.[/red]")
        return
    elif runtime == "Google" and not config.get("GOOGLE_API_KEY"):
        console.print("[red]Error: Gemini API key not set. Run 'localrag config' to set your API keys.[/red]")
        return
    elif runtime == "xAI" and not config.get("XAI_API_KEY"):
        console.print("[red]Error: xAI API key not set. Run 'localrag config' to set your API keys.[/red]")
        return
    elif runtime == "Ollama":
        if not config.get("OLLAMA_BASE_URL"):
            console.print("[red]Error: Ollama is not installed. Please install Ollama from https://ollama.com/[/red]")
            return
        if not ensure_ollama_model(model, console):
            return

    vector_store = VectorStore(VECTOR_STORE_PATH, EMBEDDING_MODEL)
    chat = create_new_chat(model)
    title_generated = False

    image_buffer = None

    console.print(Panel.fit(f"Chat with {model}", style="bold blue"))
    console.print("Type your message below. Use [bold]\\commands[/bold] for special actions.")
    console.print("Available commands: [bold]\\save[/bold], [bold]\\clear[/bold], [bold]\\switch <model>[/bold], [bold]\\quit[/bold], [bold]\\help[/bold]\n")

    while True:
        user_input = Prompt.ask("\n[bold cyan]user[/bold cyan] >")

        if user_input.startswith("\\"):
            command_parts = user_input[1:].strip().lower().split(maxsplit=1)
            command = command_parts[0]
            arg = command_parts[1] if len(command_parts) > 1 else None

            if command == "image":
                image_path = arg
                if os.path.exists(image_path):
                    image_buffer = os.path.abspath(image_path)
                    console.print(f"[green]Image path '{image_path}' buffered. Now type your message to pair with it.[/green]")
                else:
                    console.print(f"[red]Image file not found at '{image_path}'[/red]")
                continue

            if command == "save":
                chat["favorite"] = True
                save_chat(CHATS_DIR, chat)
                console.print("[green]Chat saved as favorite![/green]")
            elif command == "clear":
                if chat["messages"]: # Only clear if there are messages
                     chat = create_new_chat(model) # Create a *new* chat to truly clear state
                     title_generated = False
                     console.print("[yellow]Chat cleared. Starting new conversation.[/yellow]")
                else:
                     console.print("[yellow]Chat is already empty.[/yellow]")

            elif command == "switch":
                if arg:
                    if chat["messages"]:
                        console.print("[red]Can't switch model in the middle of a conversation. Use \\clear first.[/red]")
                    else:
                        try:
                            model_metadata = get_model_metadata(arg)
                            resolved_model = model_metadata["full_name"]
                            chat["model"] = resolved_model
                            model = resolved_model
                            console.print(f"[green]Switched to model: {resolved_model}[/green]")
                        except ValueError as e:
                            console.print(f"[red]{e}[/red]")
                            console.print("Supported models are:\n" + list_supported_models())

                else:
                     console.print("[red]Usage: \\switch <model>[/red]")

            elif command == "quit":
                if chat["messages"]: # Save the chat if there was any interaction
                    chat["updated_at"] = datetime.datetime.now().isoformat()
                    save_chat(CHATS_DIR, chat)
                console.print("[yellow]Goodbye![/yellow]")
                return # Exit the run function, ending the chat session

            elif command == "help":
                console.print(Panel.fit(
                    "[bold]Available Commands:[/bold]\n"
                    "\\image <path> - Add an image to the message (use relative path)\n"
                    "\\save - Save chat as favorite\n"
                    "\\clear - Clear current chat and start fresh\n"
                    "\\switch <model> - Switch to a different LLM model (only on an empty chat)\n"
                    "\\quit - Exit the application\n"
                    "\\help - Show this help information",
                    title="Help",
                    border_style="blue"
                ))
            else:
                console.print("[red]Unknown command. Type \\help for available commands.[/red]")

        else:
            # Normal chat turn
            # chat["messages"].append({"role": "user", "content": user_input})
            chat["messages"].append({
                "role": "user",
                "content": user_input,
                "context": "",  # will be filled later
                "image": image_buffer  # None if no image buffered
            })
            image_buffer = None  # reset


            # Retrieve context
            context = get_relevant_context(vector_store, user_input)

            for i in range(len(chat["messages"]) - 1, -1, -1):
                if chat["messages"][i]["role"] == "user":
                    chat["messages"][i]["context"] = context
                    break

            console.print("\n[bold green]assistant[/bold green] >", end=" ") # Use end=" " to keep the cursor on the same line
            assistant_response = send_message_to_llm(model, chat["messages"], config, context, console)

            # Add assistant response to messages
            chat["messages"].append({"role": "assistant", "content": assistant_response})

            # Add user input and assistant response to vector store for context retrieval
            # Ensure unique IDs for each message entry in the vector store
            user_message_id = f"{chat['id']}:{len(chat['messages']) - 2}" # ID for the user message just added
            assistant_message_id = f"{chat['id']}:{len(chat['messages']) - 1}" # ID for the assistant message just added

            vector_store.add(user_message_id, user_input)
            vector_store.add(assistant_message_id, assistant_response)

            # Generate title after the first exchange (user + assistant message)
            if not title_generated and len(chat["messages"]) >= 2:
                # Pass only the first user/assistant exchange for title generation
                chat["title"] = get_chat_title(chat["messages"][:2], config, CONFIG_PATH)
                title_generated = True
                console.print(f"\n[dim]Chat title: {chat['title']}[/dim]") # Print the title once generated

            # Update timestamp and save chat after each turn
            chat["updated_at"] = datetime.datetime.now().isoformat()
            save_chat(CHATS_DIR, chat)


@cli.command()
@click.option("-c", "--continue-chat", type=int, help="Continue the chat with the given number from the saved list.")
def saved(continue_chat):
    """List saved chats or continue a specific chat."""
    chats = get_all_chats(CHATS_DIR)
    favorite_chats = [chat for chat in chats if chat.get("favorite", False)]

    if not chats:
        console.print("[yellow]No chats found at all.[/yellow]")
        return

    if continue_chat is not None:
        chat_index = continue_chat - 1
        if 0 <= chat_index < len(favorite_chats):
            chat = favorite_chats[chat_index]
            model = chat["model"]
            config = load_config(CONFIG_PATH)

            try:
                model_metadata = get_model_metadata(model)
                runtime = model_metadata.get("runtime", model_metadata.get("provider"))
                
                if runtime == "OpenAI" and not config.get("OPENAI_API_KEY"):
                    console.print("[red]Error: OpenAI API key not set. Run 'localrag config' to set your API keys.[/red]")
                    return
                elif runtime == "Anthropic" and not config.get("ANTHROPIC_API_KEY"):
                    console.print("[red]Error: Anthropic API key not set. Run 'localrag config' to set your API keys.[/red]")
                    return
                elif runtime == "Google" and not config.get("GOOGLE_API_KEY"):
                    console.print("[red]Error: Gemini API key not set. Run 'localrag config' to set your API keys.[/red]")
                    return
                elif runtime == "xAI" and not config.get("XAI_API_KEY"):
                    console.print("[red]Error: xAI API key not set. Run 'localrag config' to set your API keys.[/red]")
                    return
                elif runtime == "Ollama":
                    if not config.get("OLLAMA_BASE_URL"):
                        console.print("[red]Error: Ollama is not installed. Please install Ollama from https://ollama.com/[/red]")
                        return
                    if not ensure_ollama_model(model, console):
                        return
            except ValueError as e:
                console.print(f"[red]{e}[/red]")
                console.print("Supported models are:\n" + list_supported_models())
                return

            console.print(Panel.fit(f"Continuing chat: {chat.get('title', 'Untitled Chat')}", style="bold blue"))

            for msg in chat["messages"]:
                if msg["role"] == "user":
                    console.print(f"\n[bold cyan]user[/bold cyan] > {msg['content']}")
                else:
                    console.print(f"\n[bold green]assistant[/bold green] > {msg['content']}")

            console.print("\nContinue the conversation. Use [bold]\\commands[/bold] for special actions.")
            vector_store = VectorStore(VECTOR_STORE_PATH, EMBEDDING_MODEL)

            while True:
                user_input = Prompt.ask("\n[bold cyan]user[/bold cyan] >")

                if user_input.startswith("\\"):
                    command_parts = user_input[1:].strip().lower().split(maxsplit=1)
                    command = command_parts[0]
                    arg = command_parts[1] if len(command_parts) > 1 else None

                    if command == "image":
                        image_path = arg
                        if os.path.exists(image_path):
                            image_buffer = os.path.abspath(image_path)
                            console.print(f"[green]Image path '{image_path}' buffered. Now type your message to pair with it.[/green]")
                        else:
                            console.print(f"[red]Image file not found at '{image_path}'[/red]")
                        continue

                    if command == "save":
                        # It's already a favorite chat, but ensure the flag is True
                        chat["favorite"] = True
                        save_chat(CHATS_DIR, chat)
                        console.print("[green]Chat already saved as favorite![/green]")
                    elif command == "clear":
                        # Clearing means starting a new conversation within this chat ID
                        chat["messages"] = []
                        # Do NOT create a new chat object here, just clear messages
                        console.print("[yellow]Chat history cleared. Continuing with the same chat ID.[/yellow]")
                        # Note: Clearing history means previous context might not be directly available
                        # for the LLM unless retrieved from the vector store.

                    elif command == "switch":
                        if arg:
                            if chat["messages"]:
                                console.print("[red]Can't switch model in the middle of a conversation. Use \\clear first.[/red]")
                            else:
                                try:
                                    model_metadata = get_model_metadata(arg)
                                    runtime = model_metadata.get("runtime", model_metadata.get("provider"))
                                    
                                    # Runtime checks for the new model
                                    if runtime == "OpenAI" and not config.get("OPENAI_API_KEY"):
                                        console.print("[red]Error: OpenAI API key not set. Run 'localrag config' to set your API keys.[/red]")
                                        continue
                                    elif runtime == "Anthropic" and not config.get("ANTHROPIC_API_KEY"):
                                        console.print("[red]Error: Anthropic API key not set. Run 'localrag config' to set your API keys.[/red]")
                                        continue
                                    elif runtime == "Google" and not config.get("GOOGLE_API_KEY"):
                                        console.print("[red]Error: Gemini API key not set. Run 'localrag config' to set your API keys.[/red]")
                                        continue
                                    elif runtime == "xAI" and not config.get("XAI_API_KEY"):
                                        console.print("[red]Error: xAI API key not set. Run 'localrag config' to set your API keys.[/red]")
                                        continue
                                    elif runtime == "Ollama":
                                        if not config.get("OLLAMA_BASE_URL"):
                                            console.print("[red]Error: Ollama is not installed. Please install Ollama from https://ollama.com/[/red]")
                                            continue
                                        if not ensure_ollama_model(model_metadata["full_name"], console):
                                            continue
                                    
                                    chat["model"] = model_metadata["full_name"]
                                    model = model_metadata["full_name"]
                                    console.print(f"[green]Switched to model: {model}[/green]")
                                except ValueError as e:
                                    console.print(f"[red]{e}[/red]")
                                    console.print("Supported models are:\n" + list_supported_models())
                        else:
                            console.print("[red]Usage: \\switch <model>[/red]")

                    elif command == "quit":
                        # Save the chat before quitting
                        chat["updated_at"] = datetime.datetime.now().isoformat()
                        save_chat(CHATS_DIR, chat)
                        console.print("[yellow]Goodbye![/yellow]")
                        return # Exit the saved function

                    elif command == "help":
                         console.print(Panel.fit(
                            "[bold]Available Commands:[/bold]\n"
                            "\\save - Save chat as favorite\n"
                            "\\clear - Clear current chat history\n" # Clarified help text
                            "\\switch <model> - Switch to a different LLM model (only on an empty chat)\n"
                            "\\quit - Exit the application\n"
                            "\\help - Show this help information",
                            title="Help",
                            border_style="blue"
                        ))
                    else:
                        console.print("[red]Unknown command. Type \\help for available commands.[/red]")

                else:
                    # Normal chat turn in a continued conversation
                    # chat["messages"].append({"role": "user", "content": user_input})
                    chat["messages"].append({
                        "role": "user",
                        "content": user_input,
                        "context": "",  # will be filled later
                        "image": image_buffer  # None if no image buffered
                    })
                    image_buffer = None  # reset

                    # Retrieve context
                    context = get_relevant_context(vector_store, user_input)

                    for i in range(len(chat["messages"]) - 1, -1, -1):
                        if chat["messages"][i]["role"] == "user":
                            chat["messages"][i]["context"] = context
                            break

                    console.print("\n[bold green]assistant[/bold green] >", end=" ")
                    # Pass the loaded config to send_message_to_llm
                    assistant_response = send_message_to_llm(model, chat["messages"], config, context, console)

                    chat["messages"].append({"role": "assistant", "content": assistant_response})

                    # Add to vector store (even in continued chats)
                    user_message_id = f"{chat['id']}:{len(chat['messages']) - 2}"
                    assistant_message_id = f"{chat['id']}:{len(chat['messages']) - 1}"
                    vector_store.add(user_message_id, user_input)
                    vector_store.add(assistant_message_id, assistant_response)


                    # Update timestamp and save chat
                    chat["updated_at"] = datetime.datetime.now().isoformat()
                    save_chat(CHATS_DIR, chat)

    else:
        console.print(Panel.fit("Saved Chats", style="bold green"))
        if not favorite_chats:
            console.print("[yellow]No saved chats found.[/yellow]")
        else:
            for i, chat in enumerate(favorite_chats, 1):
                console.print(f"[bold]{i}.[/bold] {chat['title']} [dim]({chat['model']})[/dim]")


@cli.command()
def config():
    """Configure API keys and settings."""
    configure_api_keys(CONFIG_PATH, console)

@cli.command()
def models():
    """List supported models."""
    console.print(Panel.fit("Supported Models", style="bold green"))
    console.print(list_supported_models())

@cli.command()
def update():
    """Update localrag to the latest version from the git repository."""
    import requests
    import subprocess

    console.print("Checking for updates...")
    try:
        repo_url = "https://github.com/immanuel-peter/localrag"
        release_api_url = f"https://api.github.com/repos/immanuel-peter/localrag/releases/latest"

        response = requests.get(release_api_url)
        response.raise_for_status()
        latest_release_info = response.json()
        latest_version_tag = latest_release_info.get("tag_name", "")

        if not latest_version_tag:
            console.print("[yellow]Could not determine latest version from GitHub releases.[/yellow]")
            return

        # Assuming version tags are like v1.2.3
        latest_version = latest_version_tag.strip("v")

        try:
            from importlib.metadata import version, PackageNotFoundError
            try:
                current_version = version("localrag")
                console.print(f"Currently installed version: v{current_version}")
            except PackageNotFoundError:
                current_version = "0.0.0"
                console.print("[yellow]Could not detect current installed version. Assuming old version.[/yellow]")

        except ImportError:
            console.print("[yellow]Python 3.8 or higher is recommended for version detection.[/yellow]")
            current_version = "0.0.0"

        if latest_version and (current_version == "0.0.0" or tuple(map(int, latest_version.split('.'))) > tuple(map(int, current_version.split('.')))):
            console.print(f"[green]Update available: v{latest_version}[/green]")
            update_confirm = Prompt.ask("Would you like to update now?", choices=["y", "n"], default="y")

            if update_confirm.lower() == "y":
                console.print(f"Updating using: pip install --upgrade git+{repo_url}")
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", f"git+{repo_url}"], check=True)
                    console.print("[green]Update complete! Please restart localrag.[/green]")
                except subprocess.CalledProcessError as e:
                    console.print(f"[red]Error during update: {e}[/red]")
                except FileNotFoundError:
                    console.print("[red]Error: 'pip' command not found. Ensure Python and pip are in your PATH.[/red]")
            else:
                console.print("Update cancelled.")
        else:
            console.print("[green]You're already using the latest version![/green]")

    except requests.exceptions.RequestException as e:
        console.print(f"[red]Error checking for updates (network error or API issue): {e}[/red]")
        console.print("You can manually update with: [bold]pip install --upgrade git+https://github.com/yourusername/localrag.git[/bold]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred during update check: {e}[/red]")


def get_relevant_context(vector_store: VectorStore, query: str):
    """
    Searches the vector store for context relevant to the query.
    Returns a formatted string of relevant context.
    """
    SIMILARITY_THRESHOLD = 0.7

    results = vector_store.search(query)

    if not results:
        return ""

    context_parts = []

    for message_id, text, score in results:
        if score >= SIMILARITY_THRESHOLD:
            try:
                chat_id, msg_idx_str = message_id.split(":")
                msg_idx = int(msg_idx_str)

                chat = load_chat(CHATS_DIR, chat_id)

                if chat:
                    speaker = chat["messages"][msg_idx]["role"] if 0 <= msg_idx < len(chat["messages"]) else "unknown"
                    context_parts.append(f"From chat '{chat.get('title', 'Untitled')}' ({speaker}): {text}")

            except (ValueError, IndexError) as e:
                console.print(f"[yellow]Warning: Could not parse message_id '{message_id}' for context retrieval: {e}[/yellow]", file=sys.stderr)
                context_parts.append(f"From historical context: {text}")
            except Exception as e:
                 console.print(f"[red]Error retrieving context for message_id '{message_id}': {e}[/red]", file=sys.stderr)

    return "\n\n".join(context_parts)