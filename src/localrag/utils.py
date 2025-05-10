import ollama
from rich.console import Console

def ensure_ollama_model(model_name: str, console: Console) -> bool:
    """Ensure the Ollama model is pulled and available."""
    try:
        models_info = ollama.ps()
        base_model = get_base_model_name(model_name)
        for m in models_info.get("models", []):
            if get_base_model_name(m.get("model", "")) == base_model:
                return True
        if model_name != "llama3.2:1b":
            console.print(
                f"[red]Ollama model '{model_name}' is not available locally. "
                f"Please run 'ollama pull {model_name}' and then return to LocalRAG for faster, local performance.[/red]"
            )
        return False
    except Exception as e:
        console.print(f"[red]Error checking Ollama models: {e}[/red]")
        return False

def get_base_model_name(model_name: str) -> str:
    """
    Extract the base model name by removing the tag after the colon.
    Example: llama3.2:1b -> llama3.2
    """
    return model_name.split(":")[0]

