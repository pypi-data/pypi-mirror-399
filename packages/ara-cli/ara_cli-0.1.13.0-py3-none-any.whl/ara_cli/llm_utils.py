from ara_cli.ara_config import ConfigManager
from pydantic_ai import Agent

FALLBACK_MODEL = "anthropic:claude-4-sonnet-20250514"


def get_configured_conversion_llm_model() -> str:
    """
    Retrieves the configured conversion LLM model string, adapted for pydantic_ai.
    Falls back to a default model if configuration is missing or invalid.
    """
    model_name = FALLBACK_MODEL
    try:
        config = ConfigManager.get_config()
        conversion_llm_key = config.conversion_llm

        if conversion_llm_key and conversion_llm_key in config.llm_config:
            llm_config_item = config.llm_config[conversion_llm_key]
            raw_model_name = llm_config_item.model

            # Adapt LiteLLM model string to PydanticAI format
            # LiteLLM: provider/model-name (e.g. openai/gpt-4o)
            # PydanticAI: provider:model-name (e.g. openai:gpt-4o)
            if "/" in raw_model_name and ":" not in raw_model_name:
                parts = raw_model_name.split("/", 1)
                if len(parts) == 2:
                    model_name = f"{parts[0]}:{parts[1]}"
                else:
                    model_name = raw_model_name
            else:
                model_name = raw_model_name
        else:
            print(
                f"Warning: Conversion LLM configuration issue. Using fallback model: {FALLBACK_MODEL}"
            )
    except Exception as e:
        print(
            f"Warning: Error resolving LLM config ({e}). Using fallback model: {FALLBACK_MODEL}"
        )
        model_name = FALLBACK_MODEL

    return model_name


def create_pydantic_ai_agent(
    output_type, model_name: str = None, instrument: bool = True
) -> Agent:
    """
    Creates a pydantic_ai Agent with the specified or configured model.
    """
    if not model_name:
        model_name = get_configured_conversion_llm_model()

    return Agent(
        model=model_name,
        output_type=output_type,
        instrument=instrument,
    )
