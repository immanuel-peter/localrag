import os
import json
import shutil
from rich.panel import Panel
from rich.prompt import Prompt
from .models import list_supported_models

def ensure_config_exists(config_path):
    if not os.path.exists(config_path):
        default_config = {
            "OPENAI_API_KEY": None,
            "ANTHROPIC_API_KEY": None,
            "GOOGLE_API_KEY": None,
            "XAI_API_KEY": None,
            "OLLAMA_BASE_URL": None,
            "default_model": "gpt-4.1",
        }
        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

def load_config(config_path):
    with open(config_path, 'r') as f:
        config = json.load(f)
    
    config["OPENAI_API_KEY"] = config.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    config["ANTHROPIC_API_KEY"] = config.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
    config["GOOGLE_API_KEY"] = config.get("GOOGLE_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    config["XAI_API_KEY"] = config.get("XAI_API_KEY") or os.environ.get("XAI_API_KEY")
    config["OLLAMA_BASE_URL"] = config.get("OLLAMA_BASE_URL") or os.environ.get("OLLAMA_BASE_URL")
    if config["OLLAMA_BASE_URL"] and not shutil.which("ollama"):
        config["OLLAMA_BASE_URL"] = None
    
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
    google_env = os.environ.get("GOOGLE_API_KEY")
    xai_env = os.environ.get("XAI_API_KEY")

    openai_prompt_default = "env key set" if openai_env else ""
    anthropic_prompt_default = "env key set" if anthropic_env else ""
    google_prompt_default = "env key set" if google_env else ""
    xai_prompt_default = "env key set" if xai_env else ""

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
    
    google_key = Prompt.ask(
        "[bold]Google API Key[/bold]",
        password=True,
        default=google_prompt_default
    )
    if google_key and google_key != "env key set":
        config["GOOGLE_API_KEY"] = google_key

    xai_key = Prompt.ask(
        "[bold]xAI API Key[/bold]",
        password=True,
        default=xai_prompt_default
    )
    if xai_key and xai_key != "env key set":
        config["XAI_API_KEY"] = xai_key

    if shutil.which("ollama"):
        console.print("[green]Ollama is installed! You can run local models.[/green]")
        config["OLLAMA_BASE_URL"] = "http://localhost:11434"
    else:
        console.print("[yellow]Ollama is not installed. You can still run remote models.[/yellow]")
        config["OLLAMA_BASE_URL"] = None

    console.print("\n[bold]Configure Default Model[/bold]")
    console.print("Available models:")
    console.print(list_supported_models())
    default_model = Prompt.ask(
        "[bold]Default Model[/bold]",
        default=config.get("default_model", "gpt-4.1")
    )
    if default_model:
        config["default_model"] = default_model

    save_config(config_path, config)
    console.print("\n[green]Configuration saved![/green]")