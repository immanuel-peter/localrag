# Structured metadata about supported models
SUPPORTED_MODELS = {
    "gpt-4o-mini": {
        "full_name": "gpt-4o-mini",
        "provider": "OpenAI",
        "context_window": 128_000,
        "max_output_tokens": 16_384,
        "knowledge_cutoff": "September 2023"
    },
    "gpt-4.1": {
        "full_name": "gpt-4.1",
        "provider": "OpenAI",
        "context_window": 1_047_576,
        "max_output_tokens": 32_768,
        "knowledge_cutoff": "May 2024"    
    },
    "claude-3.7": {
        "full_name": "claude-3-7-sonnet-latest",
        "provider": "Anthropic",
        "context_window": 200_000,
        "max_output_tokens": 64_000,
        "knowledge_cutoff": "November 2024"
    },
    "claude-3.5": {
        "full_name": "claude-3-5-haiku-latest",
        "provider": "Anthropic",
        "context_window": 200_000,
        "max_output_tokens": 8_192,
        "knowledge_cutoff": "July 2024"
    },
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
    lines = []
    for alias, meta in SUPPORTED_MODELS.items():
        lines.append(f"- {alias} → {meta['full_name']} ({meta['provider']}, {meta['context_window']:,} ctx)")
    return "\n".join(lines)
