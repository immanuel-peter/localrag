import sys
import base64
import threading
import time
from openai import OpenAI
from rich.console import Console
from ollama import chat as ollama_chat
from .models import get_model_metadata
from .utils import ensure_ollama_model

def get_chat_title(messages, config, config_path):
    """
    Generate a concise title for a chat using an LLM.
    Prioritizes Ollama for cost savings, then falls back to proprietary models.
    Falls back to first user message if all else fails.
    """
    console = Console()

    if len(messages) < 2:
        return "New Chat"

    try:
        # Try Ollama first if available
        if config.get("OLLAMA_BASE_URL"):
            if ensure_ollama_model("llama3.2:1b", console):
                response = ollama_chat(
                    model="llama3.2:1b",
                    messages=[
                        {"role": "system", "content": "Generate a concise, specific 2-5 word title for this conversation. Respond with ONLY the title, no quotes or explanations."},
                        {"role": "user", "content": messages[0]["content"]},
                        {"role": "assistant", "content": messages[1]["content"]}
                    ]
                )
                title = response.message.content.strip()
                if 2 <= len(title.split()) <= 5 and '"' not in title and "'" not in title:
                    return title
                console.print("[yellow]Warning: Ollama generated title did not meet criteria, trying proprietary models.[/yellow]")
        
        # Try proprietary models in order of preference
        if config.get("OPENAI_API_KEY"):
            client = OpenAI(api_key=config["OPENAI_API_KEY"])
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Force title generation to be done with small, cheap model
                messages=[
                    {
                        "role": "developer",
                        "content": "Generate a concise, specific 2-5 word title for this conversation. Respond with ONLY the title, no quotes or explanations."
                    },
                    {"role": "user", "content": messages[0]["content"]},
                    {"role": "assistant", "content": messages[1]["content"]}
                ],
                max_tokens=25
            )
            title = response.choices[0].message.content.strip()
            if 2 <= len(title.split()) <= 5 and '"' not in title and "'" not in title:
                return title
        
        elif config.get("ANTHROPIC_API_KEY"):
            client = OpenAI(api_key=config["ANTHROPIC_API_KEY"], base_url="https://api.anthropic.com/v1/")
            response = client.chat.completions.create(
                model="claude-3-5-haiku-latest",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a concise, specific 2-5 word title for this conversation. Respond with ONLY the title, no quotes or explanations."
                    },
                    {"role": "user", "content": messages[0]["content"]},
                    {"role": "assistant", "content": messages[1]["content"]}
                ],
                max_tokens=25
            )
            title = response.choices[0].message.content.strip()
            if 2 <= len(title.split()) <= 5 and '"' not in title and "'" not in title:
                return title

        elif config.get("GOOGLE_API_KEY"):
            client = OpenAI(api_key=config["GOOGLE_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
            response = client.chat.completions.create(
                model="gemini-1.5-flash",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a concise, specific 2-5 word title for this conversation. Respond with ONLY the title, no quotes or explanations."
                    },
                    {"role": "user", "content": messages[0]["content"]},
                    {"role": "assistant", "content": messages[1]["content"]}
                ],
                max_tokens=25
            )
            title = response.choices[0].message.content.strip()
            if 2 <= len(title.split()) <= 5 and '"' not in title and "'" not in title:
                return title
        
        elif config.get("XAI_API_KEY"):
            client = OpenAI(api_key=config["XAI_API_KEY"], base_url="https://api.x.ai/v1/")
            response = client.chat.completions.create(
                model="grok-3-mini-beta",
                messages=[
                    {
                        "role": "system",
                        "content": "Generate a concise, specific 2-5 word title for this conversation. Respond with ONLY the title, no quotes or explanations."
                    },
                    {"role": "user", "content": messages[0]["content"]},
                    {"role": "assistant", "content": messages[1]["content"]}
                ],
                max_tokens=25
            )
            title = response.choices[0].message.content.strip()
            if 2 <= len(title.split()) <= 5 and '"' not in title and "'" not in title:
                return title

    except Exception as e:
        console.print(f"[yellow]Error generating title: {e}[/yellow]")

    # Fallback to first message
    first_message_content = messages[0]["content"]
    # return (first_message_content[:30] + "...") if len(first_message_content) > 30 else first_message_content
    return first_message_content
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def send_message_to_llm(model, messages, config, context="", console=None):
    """
    Send a message to the correct LLM (OpenAI or Anthropic) based on model.
    """
    formatted_messages = []
    for msg in messages:
        if msg["role"] == "user":
            if msg.get("image"):
                base64_image = encode_image(msg['image'])
                formatted_messages.append({
                    "role": "user",
                    "content": [
                        {"type": "text", "text": msg["content"]},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                })
            else:
                content = f"(Relevant context: {msg.get('context', '')})\n\n{msg['content']}"
                formatted_messages.append({"role": "user", "content": content})
        else:
            formatted_messages.append({"role": "assistant", "content": msg["content"]})


    full_response = ""
    spinner_thread = None
    stop_spinner = threading.Event()

    def spinner_animation():
        spinner = "|/-\\"
        i = 0
        while not stop_spinner.is_set():
            sys.stdout.write("\r" + spinner[i % len(spinner)] + " Generating...")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write("\r")
        sys.stdout.flush()

    try:
        model_meta = get_model_metadata(model)
        # provider = company that trained the model
        provider = model_meta.get("provider")
        # runtime: how to execute the model (SDK or service)
        runtime = model_meta.get("runtime", provider)
        client = None

        # OpenAI runtime via OpenAI Python SDK
        if runtime == "OpenAI":
            if not config.get("OPENAI_API_KEY"):
                return "Error: OpenAI API key not set. Run 'localrag config'."
            client = OpenAI(api_key=config["OPENAI_API_KEY"])

        # Anthropic runtime via OpenAI Python SDK with Anthropic endpoint
        elif runtime == "Anthropic":
            if not config.get("ANTHROPIC_API_KEY"):
                return "Error: Anthropic API key not set. Run 'localrag config'."
            client = OpenAI(api_key=config["ANTHROPIC_API_KEY"], base_url="https://api.anthropic.com/v1/")
        
        elif runtime == "Google":
            if not config.get("GOOGLE_API_KEY"):
                return "Error: Gemini API key not set. Run 'localrag config'."
            client = OpenAI(api_key=config["GOOGLE_API_KEY"], base_url="https://generativelanguage.googleapis.com/v1beta/openai/")
        
        elif runtime == "xAI":
            if not config.get("XAI_API_KEY"):
                return "Error: xAI API key not set. Run 'localrag config'."
            client = OpenAI(api_key=config["XAI_API_KEY"], base_url="https://api.x.ai/v1/")

        # Ollama runtime via Ollama Python SDK
        elif runtime == "Ollama":
            # Start streaming via Ollama
            if console:
                spinner_thread = threading.Thread(target=spinner_animation)
                spinner_thread.start()
            response = ollama_chat(model=model, messages=formatted_messages, stream=True)
            for chunk in response:
                content = chunk["message"]["content"]
                if content:
                    if not full_response and console:
                        stop_spinner.set()
                        if spinner_thread:
                            spinner_thread.join()
                        console.print("\r", end="")
                    full_response += content
                    if console:
                        console.print(content, end="", highlight=False)
                    sys.stdout.flush()
            return full_response

        else:
            return f"Error: Unsupported runtime '{runtime}' for model '{model}'."

        # Send streaming request
        response = client.chat.completions.create(
            model=model,
            messages=formatted_messages,
            stream=True
        )

        if console:
            spinner_thread = threading.Thread(target=spinner_animation)
            spinner_thread.start()

        for chunk in response:
            if chunk.choices[0].delta.content:
                if not full_response and console:
                    stop_spinner.set()
                    if spinner_thread:
                        spinner_thread.join()
                    console.print("\r", end="")

                content = chunk.choices[0].delta.content
                full_response += content
                if console:
                    console.print(content, end="", highlight=False)
                sys.stdout.flush()

    except Exception as e:
        return f"Error during LLM call: {str(e)}"

    finally:
        stop_spinner.set()
        if spinner_thread and spinner_thread.is_alive():
            spinner_thread.join()
        if console:
            console.print()  # Final newline after response

    return full_response
