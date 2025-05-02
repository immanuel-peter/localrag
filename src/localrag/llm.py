import sys
import threading
import time
from openai import OpenAI
from .models import get_model_metadata

def get_chat_title(messages, config, config_path):
    """
    Generate a concise title for a chat using an LLM.
    Falls back to first user message if needed.
    """
    if len(messages) < 2:
        return "New Chat"

    try:
        # Prefer OpenAI if OpenAI key available
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
            else:
                print("Warning: Generated title did not meet criteria, falling back.")
        
        # Otherwise fallback to Anthropic if OpenAI key not present
        elif config.get("ANTHROPIC_API_KEY"):
            client = OpenAI(api_key=config["ANTHROPIC_API_KEY"], base_url="https://api.anthropic.com/v1/")
            response = client.chat.completions.create(
                model="claude-3-5-haiku-latest",
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
            else:
                print("Warning: Generated title did not meet criteria, falling back.")

    except Exception as e:
        print(f"Error generating title: {e}")

    # Fallback to first message
    first_message_content = messages[0]["content"]
    return (first_message_content[:30] + "...") if len(first_message_content) > 30 else first_message_content


def send_message_to_llm(model, messages, config, context="", console=None):
    """
    Send a message to the correct LLM (OpenAI or Anthropic) based on model.
    """
    # formatted_messages = [{"role": msg["role"], "content": msg["content"]} for msg in messages]
    formatted_messages = []
    for msg in messages:
        if msg["role"] == "user":
            content = f"(Relevant context: {msg['context']})\n\n{msg['content']}"
        else:
            content = msg["content"]
        formatted_messages.append({"role": msg["role"], "content": content})


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
        provider = model_meta["provider"]

        # OpenAI models
        if provider == "OpenAI":
            if not config.get("OPENAI_API_KEY"):
                return "Error: OpenAI API key not set. Run 'localrag config'."

            client = OpenAI(api_key=config["OPENAI_API_KEY"])

        # Anthropic models
        elif provider == "Anthropic":
            if not config.get("ANTHROPIC_API_KEY"):
                return "Error: Anthropic API key not set. Run 'localrag config'."

            client = OpenAI(api_key=config["ANTHROPIC_API_KEY"], base_url="https://api.anthropic.com/v1/")

        else:
            return f"Error: Unsupported provider '{provider}' for model '{model}'."

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
