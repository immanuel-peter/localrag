# Structured metadata about supported models
SUPPORTED_MODELS = {
    "gpt-4o-mini": {
        "full_name": "gpt-4o-mini",
        "display_name": "GPT-4o Mini",
        "provider": "OpenAI",
        "runtime": "OpenAI",
        "context_window": 128_000,
        "max_output_tokens": 16_384,
        "knowledge_cutoff": "September 2023"
    },
    "gpt-4.1": {
        "full_name": "gpt-4.1",
        "display_name": "GPT-4.1",
        "provider": "OpenAI",
        "runtime": "OpenAI",
        "context_window": 1_047_576,
        "max_output_tokens": 32_768,
        "knowledge_cutoff": "May 2024"    
    },
    "o4-mini": {
        "full_name": "o4-mini",
        "display_name": "o4 Mini",
        "provider": "OpenAI",
        "runtime": "OpenAI",
        "context_window": 200_000,
        "max_output_tokens": 100_000,
        "knowledge_cutoff": "May 2024"
    },
    "o3": {
        "full_name": "o3",
        "display_name": "o3",
        "provider": "OpenAI",
        "runtime": "OpenAI",
        "context_window": 200_000,
        "max_output_tokens": 100_000,
        "knowledge_cutoff": "May 2024"
    },
    "claude-3.7": {
        "full_name": "claude-3-7-sonnet-latest",
        "display_name": "Claude 3.7 Sonnet",
        "provider": "Anthropic",
        "runtime": "Anthropic",
        "context_window": 200_000,
        "max_output_tokens": 64_000,
        "knowledge_cutoff": "November 2024"
    },
    "claude-3.5": {
        "full_name": "claude-3-5-haiku-latest",
        "display_name": "Claude 3.5 Haiku",
        "provider": "Anthropic",
        "runtime": "Anthropic",
        "context_window": 200_000,
        "max_output_tokens": 8_192,
        "knowledge_cutoff": "July 2024"
    },
    "gemini-2.5-pro": {
        "full_name": "gemini-2.5-pro-preview-05-06",
        "display_name": "Gemini 2.5 Pro",
        "provider": "Google",
        "runtime": "Google",
        "context_window": 1_048_576,
        "max_output_tokens": 65_536,
        "knowledge_cutoff": "May 2025"
    },
    "gemini-2.5-flash": {
        "full_name": "gemini-2.5-flash-preview-04-17",
        "display_name": "Gemini 2.5 Flash",
        "provider": "Google",
        "runtime": "Google",
        "context_window": 1_048_576,
        "max_output_tokens": 65_536,
        "knowledge_cutoff": "April 2025"
    },
    "gemini-2.0": {
        "full_name": "gemini-2.0-flash",
        "display_name": "Gemini 2.0 Flash",
        "provider": "Google",
        "runtime": "Google",
        "context_window": 1_048_576,
        "max_output_tokens": 8_192,
        "knowledge_cutoff": "February 2025"
    },
    "grok-3": {
        "full_name": "grok-3-mini-beta",
        "display_name": "Grok 3",
        "provider": "xAI",
        "runtime": "xAI",
        "context_window": 131_072,
        "max_output_tokens": 131_072,
        "knowledge_cutoff": "November 2024"
    },
    "llama-4-scout": {
        "full_name": "llama4:scout",
        "display_name": "Llama 4 Scout",
        "provider": "Meta",
        "runtime": "Ollama",
        "context_window": 10_000_000,
        "max_output_tokens": 8_192,
        "knowledge_cutoff": "August 2024"
    },
    "llama-4-maverick": {
        "full_name": "llama4:maverick",
        "display_name": "Llama 4 Maverick",
        "provider": "Meta",
        "runtime": "Ollama",
        "context_window": 10_000_000,
        "max_output_tokens": 8_192,
        "knowledge_cutoff": "August 2024"
    },
    "llama-3.3": {
        "full_name": "llama3.3",
        "display_name": "Llama 3.3",
        "provider": "Meta",
        "runtime": "Ollama",
        "context_window": 128_000,
        "max_output_tokens": 2_048,
        "knowledge_cutoff": "December 2023"
    },
    "gemma3": {
        "full_name": "gemma3",
        "display_name": "Gemma 3",
        "provider": "Google",
        "runtime": "Ollama",
        "context_window": 128_000,
        "max_output_tokens": 8_192,
        "knowledge_cutoff": "August 2024"
    },
    "deepseek-r1": {
        "full_name": "deepseek-r1",
        "display_name": "DeepSeek R1",
        "provider": "DeepSeek",
        "runtime": "Ollama",
        "context_window": 128_000,
        "max_output_tokens": 32_768,
        "knowledge_cutoff": "July 2024"
    },
    "phi-4-mini": {
        "full_name": "phi4-mini",
        "display_name": "Phi-4 Mini",
        "provider": "Microsoft",
        "runtime": "Ollama",
        "context_window": 128_000,
        "max_output_tokens": 8_192,
        "knowledge_cutoff": "June 2024"
    }
}

# Create reverse lookup
FULL_NAME_TO_ALIAS = {v["full_name"]: k for k, v in SUPPORTED_MODELS.items()}


def resolve_model_alias(alias_or_full: str) -> str:
    """Resolve an alias or full name into the full name."""
    alias_or_full = alias_or_full.lower()
    if alias_or_full in SUPPORTED_MODELS:
        return SUPPORTED_MODELS[alias_or_full]["full_name"]
    elif alias_or_full in FULL_NAME_TO_ALIAS:
        return alias_or_full
    else:
        raise ValueError(f"Model '{alias_or_full}' is not a supported model.")

def get_model_metadata(alias_or_full: str) -> dict:
    """Retrieve full metadata about a model."""
    alias_or_full = alias_or_full.lower()
    if alias_or_full in SUPPORTED_MODELS:
        return SUPPORTED_MODELS[alias_or_full]
    elif alias_or_full in FULL_NAME_TO_ALIAS:
        alias = FULL_NAME_TO_ALIAS[alias_or_full]
        return SUPPORTED_MODELS[alias]
    else:
        raise ValueError(f"Model '{alias_or_full}' is not a supported model.")

def list_supported_models() -> str:
    """Return a pretty list of supported models."""
    proprietary_models = []
    local_models = []
    
    for alias, meta in SUPPORTED_MODELS.items():
        model_info = f"- {alias} → {meta['display_name']} ({meta['provider']}, {meta['context_window']:,} ctx)"
        if meta['runtime'] == "Ollama":
            local_models.append(model_info)
        else:
            proprietary_models.append(model_info)
    
    sections = []
    if proprietary_models:
        sections.append("[bold blue]Proprietary Models[/bold blue]")
        sections.extend(proprietary_models)
    
    if local_models:
        if sections:
            sections.append("")
        sections.append("[bold yellow]Local Models (requires Ollama)[/bold yellow]")
        sections.extend(local_models)
    
    return "\n".join(sections)
