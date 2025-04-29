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
        return json.load(f)

def save_config(config_path, config):
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)  

def configure_api_keys(config_path, console):
    config = load_config(config_path)
    console.print(Panel.fit("LocalRAG Configuration", style="bold green"))
    console.print("Set your API keys for different LLM providers.")
    console.print("Leave blank to keep existing keys.\n")
    openai_key = Prompt.ask("[bold]OpenAI API Key[/bold]", password=True, default="")
    if openai_key:
        config["OPENAI_API_KEY"] = openai_key
    anthropic_key = Prompt.ask("[bold]Anthropic API Key[/bold]", password=True, default="")
    if anthropic_key:
        config["ANTHROPIC_API_KEY"] = anthropic_key
    save_config(config_path, config)
    console.print("\n[green]Configuration saved![/green]")