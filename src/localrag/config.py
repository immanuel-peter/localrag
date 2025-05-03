import os
import json
from rich.panel import Panel
from rich.prompt import Prompt

def ensure_config_exists(config_path, default_model):
    if not os.path.exists(config_path):
        default_config = {
            "OPENAI_API_KEY": "",
            "ANTHROPIC_API_KEY": "",
            "default_model": default_model,
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    config["OPENAI_API_KEY"] = config.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    config["ANTHROPIC_API_KEY"] = config.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    
    return config


def save_config(config_path, config):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)  

def configure_api_keys(config_path, console):
    config = load_config(config_path)
    console.print(Panel.fit("LocalRAG Configuration", style="bold green"))
    console.print("Set your API keys for different LLM providers.")
    console.print("Leave blank to keep existing keys.\n")
    openai_env = os.environ.get("OPENAI_API_KEY")
    anthropic_env = os.environ.get("ANTHROPIC_API_KEY")

    # Show a masked indicator if env var is set
    openai_prompt_default = "env key set" if openai_env else ""
    anthropic_prompt_default = "env key set" if anthropic_env else ""

    openai_key = Prompt.ask(
        "[bold]OpenAI API Key[/bold]",
        password=True,
        default=openai_prompt_default
    )
    if openai_key and openai_key != "env key set":
        config["OPENAI_API_KEY"] = openai_key

    anthropic_key = Prompt.ask(
        "[bold]Anthropic API Key[/bold]",
        password=True,
        default=anthropic_prompt_default
    )
    if anthropic_key and anthropic_key != "env key set":
        config["ANTHROPIC_API_KEY"] = anthropic_key


    save_config(config_path, config)
    console.print("\n[green]Configuration saved![/green]")