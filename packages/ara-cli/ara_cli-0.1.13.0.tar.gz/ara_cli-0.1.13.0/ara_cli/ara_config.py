from typing import List, Dict, Optional
from pydantic import BaseModel, ValidationError, Field, model_validator
import json
import os
from os import makedirs
from os.path import exists, dirname
from functools import lru_cache
import sys
import warnings

DEFAULT_CONFIG_LOCATION = "./ara/.araconfig/ara_config.json"


class LLMConfigItem(BaseModel):
    provider: str
    model: str
    temperature: Optional[float] = Field(ge=0.0, le=2.0)
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None


def get_default_llm_config() -> Dict[str, "LLMConfigItem"]:
    """Returns the default LLM configuration."""
    return {
        "gpt-5.2": LLMConfigItem(
            provider="openai",
            model="openai/gpt-5.2",
            temperature=1,
            max_completion_tokens=16000,
        ),
        "gpt-5-mini": LLMConfigItem(
            provider="openai", model="openai/gpt-5-mini", temperature=1
        ),
        "gpt-5-web": LLMConfigItem(
            provider="openai",
            model="openai/gpt-5-search-api",
            temperature=1,
            max_completion_tokens=16000,
        ),
        "gpt-4o": LLMConfigItem(
            provider="openai",
            model="openai/gpt-4o",
            temperature=0.8,
            max_tokens=16000,
        ),
        "gpt-4o-search-preview": LLMConfigItem(
            provider="openai",
            model="openai/gpt-4o-search-preview",
            temperature=None,
            max_tokens=None,
            max_completion_tokens=None,
        ),
        "opus-4.5-advanced": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-opus-4-5-20251101",
            temperature=0.5,
            max_tokens=32000,
        ),
        "opus-4.1-exceptional": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-opus-4-1-20250805",
            temperature=0.5,
            max_tokens=32000,
        ),
        "sonnet-4.5-coding": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-sonnet-4-5-20250929",
            temperature=0.5,
            max_tokens=32000,
        ),
        "haiku-4-5": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-haiku-4-5-20251001",
            temperature=0.8,
            max_tokens=32000,
        ),
        "together-ai-llama-2": LLMConfigItem(
            provider="together_ai",
            model="together_ai/togethercomputer/llama-2-70b",
            temperature=0.8,
            max_tokens=4000,
        ),
        "groq-llama-3": LLMConfigItem(
            provider="groq",
            model="groq/llama3-70b-8192",
            temperature=0.8,
            max_tokens=4000,
        ),
    }


class ARAconfig(BaseModel):
    ext_code_dirs: List[Dict[str, str]] = Field(
        default_factory=lambda: [{"source_dir": "./src"}, {"source_dir": "./tests"}]
    )
    global_dirs: Optional[List[Dict[str, str]]] = Field(default=[])
    glossary_dir: str = "./glossary"
    doc_dir: str = "./docs"
    local_prompt_templates_dir: str = "./ara/.araconfig"
    custom_prompt_templates_subdir: Optional[str] = "custom-prompt-modules"
    local_scripts_dir: str = "./ara/.araconfig"
    custom_scripts_subdir: Optional[str] = "custom-scripts"
    local_ara_templates_dir: str = "./ara/.araconfig/templates/"
    ara_prompt_given_list_includes: List[str] = Field(
        default_factory=lambda: [
            "*.businessgoal",
            "*.vision",
            "*.capability",
            "*.keyfeature",
            "*.epic",
            "*.userstory",
            "*.example",
            "*.feature",
            "*.task",
            "*.py",
            "*.md",
            "*.png",
            "*.jpg",
            "*.jpeg",
        ]
    )
    # llm_config defaults to the standard set of models
    llm_config: Dict[str, LLMConfigItem] = Field(default_factory=get_default_llm_config)
    default_llm: Optional[str] = None
    extraction_llm: Optional[str] = None
    conversion_llm: Optional[str] = None

    def _validate_llm_field(
        self, field: str, fallback: str, missing_msg: str, invalid_msg: str
    ):
        """Helper to validate and set fallback for LLM fields."""
        value = getattr(self, field)
        if not value:
            print(f"Warning: '{field}' is not set. {missing_msg}: '{fallback}'.")
            setattr(self, field, fallback)
        elif value not in self.llm_config:
            print(
                f"Warning: The configured '{field}' ('{value}') does not exist in 'llm_config'."
            )
            print(f"-> Reverting to {invalid_msg}: '{fallback}'.")
            setattr(self, field, fallback)

    @model_validator(mode="after")
    def check_critical_fields(self) -> "ARAconfig":
        """Check for empty critical fields and validate default_llm and extraction_llm."""
        critical_fields = {
            "ext_code_dirs": [{"source_dir": "./src"}, {"source_dir": "./tests"}],
            "local_ara_templates_dir": "./ara/.araconfig/templates/",
            "local_prompt_templates_dir": "./ara/.araconfig",
            "local_scripts_dir": "./ara/.araconfig",
            "glossary_dir": "./glossary",
        }

        for field, default_value in critical_fields.items():
            if not getattr(self, field):
                print(
                    f"Warning: Value for '{field}' is missing or empty. Using default."
                )
                setattr(self, field, default_value)

        if not self.llm_config:
            print(
                "Warning: 'llm_config' is empty. 'default_llm' and 'extraction_llm' cannot be set."
            )
            self.default_llm = None
            self.extraction_llm = None
            return self

        first_available = next(iter(self.llm_config))
        self._validate_llm_field(
            "default_llm",
            first_available,
            "Defaulting to the first available model",
            "the first available model",
        )

        # Now used as fallback for others
        fallback_val = self.default_llm
        fallback_missing_msg = "Setting it to the same as 'default_llm'"
        fallback_invalid_msg = "the 'default_llm' value"

        self._validate_llm_field(
            "extraction_llm", fallback_val, fallback_missing_msg, fallback_invalid_msg
        )
        self._validate_llm_field(
            "conversion_llm", fallback_val, fallback_missing_msg, fallback_invalid_msg
        )

        return self


# Function to ensure the necessary directories exist
@lru_cache(maxsize=None)
def ensure_directory_exists(directory: str):
    """Creates a directory if it doesn't exist."""
    if not exists(directory):
        os.makedirs(directory)
        print(f"New directory created at {directory}")
    return directory


def handle_unrecognized_keys(data: dict) -> dict:
    """Removes unrecognized keys from the data and warns the user."""
    known_fields = set(ARAconfig.model_fields.keys())
    cleaned_data = {}
    for key, value in data.items():
        if key not in known_fields:
            print(f"Warning: Unrecognized configuration key '{key}' will be ignored.")
        else:
            cleaned_data[key] = value
    return cleaned_data


# Function to read the JSON file and return an ARAconfig model


def _create_default_config(filepath: str) -> ARAconfig:
    """Create and save a default configuration."""
    print(f"Configuration file not found. Creating a default one at '{filepath}'.")
    default_config = ARAconfig(llm_config=get_default_llm_config())
    save_data(filepath, default_config)
    print("Please review the default configuration and re-run your command.")
    sys.exit(0)


def _load_json_config(filepath: str) -> dict:
    """Load and parse JSON configuration file."""

    def warn_on_duplicate_llm_dict_key(ordered_pairs):
        """Reject duplicate keys."""
        d = {}
        for k, v in ordered_pairs:
            if k in d:
                warnings.warn(
                    f"Duplicate LLM configuration identifier '{k}'. The previous entry will be removed.",
                    UserWarning,
                )
            d[k] = v
        return d

    with open(filepath, "r", encoding="utf-8") as file:
        content = file.read()
        return json.loads(content, object_pairs_hook=warn_on_duplicate_llm_dict_key)


def _correct_validation_errors(data: dict, errors: list) -> ARAconfig:
    """Correct validation errors and return a valid config."""
    print("--- Configuration Error Detected ---")
    print(
        "Some settings in your configuration file are invalid. Attempting to fix them."
    )

    corrected_data = data.copy()
    defaults = ARAconfig(llm_config=get_default_llm_config()).model_dump()
    error_fields = {err["loc"][0] for err in errors if err["loc"]}

    for field_name in error_fields:
        print(
            f"-> Field '{field_name}' is invalid and will be reverted to its default value."
        )
        if field_name in corrected_data:
            corrected_data[field_name] = defaults.get(field_name)

    print("--- End of Error Report ---")
    return ARAconfig(**corrected_data)


@lru_cache(maxsize=1)
def read_data(filepath: str) -> ARAconfig:
    """
    Reads, validates, and repairs the configuration file.
    If the file doesn't exist, it creates a default one.
    If the file is invalid, it corrects only the broken parts.
    """
    ensure_directory_exists(dirname(filepath))

    if not exists(filepath):
        return _create_default_config(filepath)

    try:
        data = _load_json_config(filepath)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        print("Creating a new configuration with defaults...")
        default_config = ARAconfig(llm_config=get_default_llm_config())
        save_data(filepath, default_config)
        return default_config

    data = handle_unrecognized_keys(data)

    needs_save = False
    if "llm_config" not in data or not data.get("llm_config"):
        print(
            "Info: 'llm_config' is missing or empty. Populating with default LLM configurations."
        )
        data["llm_config"] = {
            k: v.model_dump() for k, v in get_default_llm_config().items()
        }
        needs_save = True

    try:
        config = ARAconfig(**data)
        if needs_save:
            save_data(filepath, config)
        return config
    except ValidationError as e:
        final_config = _correct_validation_errors(data, e.errors())
        save_data(filepath, final_config)
        print(f"Configuration has been corrected and saved to '{filepath}'.")
        return final_config


# Function to save the modified configuration back to the JSON file
def save_data(filepath: str, config: ARAconfig):
    """Saves the Pydantic config model to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(config.model_dump(), file, indent=4)


# Singleton for configuration management
class ConfigManager:
    _config_instance = None

    @classmethod
    def get_config(cls, filepath=None) -> ARAconfig:
        if filepath:
            return read_data(filepath)

        if cls._config_instance is None:
            cls._config_instance = read_data(DEFAULT_CONFIG_LOCATION)
        return cls._config_instance

    @classmethod
    def reset(cls):
        """Reset the configuration instance (useful for testing)."""
        cls._config_instance = None
        read_data.cache_clear()
