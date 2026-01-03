"""
Unit tests for llm_utils.py

Provides full test coverage for LLM utility functions.
"""

import pytest
from unittest.mock import patch, MagicMock
from ara_cli.llm_utils import (
    get_configured_conversion_llm_model,
    create_pydantic_ai_agent,
    FALLBACK_MODEL,
)


# =============================================================================
# Tests for get_configured_conversion_llm_model
# =============================================================================


class TestGetConfiguredConversionLlmModel:
    """Tests for get_configured_conversion_llm_model function."""

    @patch("ara_cli.llm_utils.ConfigManager.get_config")
    def test_returns_fallback_when_no_config(self, mock_get_config):
        """Returns fallback model when config is missing."""
        mock_get_config.side_effect = Exception("Config not found")

        result = get_configured_conversion_llm_model()

        assert result == FALLBACK_MODEL

    @patch("ara_cli.llm_utils.ConfigManager.get_config")
    def test_returns_fallback_when_conversion_llm_not_set(self, mock_get_config):
        """Returns fallback when conversion_llm is not set."""
        mock_config = MagicMock()
        mock_config.conversion_llm = None
        mock_get_config.return_value = mock_config

        result = get_configured_conversion_llm_model()

        assert result == FALLBACK_MODEL

    @patch("ara_cli.llm_utils.ConfigManager.get_config")
    def test_returns_fallback_when_key_not_in_llm_config(self, mock_get_config):
        """Returns fallback when conversion_llm key not in llm_config."""
        mock_config = MagicMock()
        mock_config.conversion_llm = "nonexistent_key"
        mock_config.llm_config = {}
        mock_get_config.return_value = mock_config

        result = get_configured_conversion_llm_model()

        assert result == FALLBACK_MODEL

    @patch("ara_cli.llm_utils.ConfigManager.get_config")
    def test_converts_litellm_format_to_pydantic_format(self, mock_get_config):
        """Converts LiteLLM model format (/) to PydanticAI format (:)."""
        mock_config = MagicMock()
        mock_config.conversion_llm = "default"
        mock_llm_item = MagicMock()
        mock_llm_item.model = "openai/gpt-4o"
        mock_config.llm_config = {"default": mock_llm_item}
        mock_get_config.return_value = mock_config

        result = get_configured_conversion_llm_model()

        assert result == "openai:gpt-4o"

    @patch("ara_cli.llm_utils.ConfigManager.get_config")
    def test_keeps_pydantic_format_unchanged(self, mock_get_config):
        """Keeps PydanticAI format unchanged."""
        mock_config = MagicMock()
        mock_config.conversion_llm = "default"
        mock_llm_item = MagicMock()
        mock_llm_item.model = "openai:gpt-4o"
        mock_config.llm_config = {"default": mock_llm_item}
        mock_get_config.return_value = mock_config

        result = get_configured_conversion_llm_model()

        assert result == "openai:gpt-4o"

    @patch("ara_cli.llm_utils.ConfigManager.get_config")
    def test_handles_model_without_prefix(self, mock_get_config):
        """Handles model name without provider prefix."""
        mock_config = MagicMock()
        mock_config.conversion_llm = "default"
        mock_llm_item = MagicMock()
        mock_llm_item.model = "gpt-4o"
        mock_config.llm_config = {"default": mock_llm_item}
        mock_get_config.return_value = mock_config

        result = get_configured_conversion_llm_model()

        assert result == "gpt-4o"


# =============================================================================
# Tests for create_pydantic_ai_agent
# =============================================================================


class TestCreatePydanticAiAgent:
    """Tests for create_pydantic_ai_agent function."""

    @patch("ara_cli.llm_utils.Agent")
    @patch("ara_cli.llm_utils.get_configured_conversion_llm_model")
    def test_uses_configured_model_when_not_provided(self, mock_get_model, mock_agent):
        """Uses configured model when model_name not provided."""
        mock_get_model.return_value = "configured:model"
        mock_output_type = MagicMock()

        create_pydantic_ai_agent(output_type=mock_output_type)

        mock_agent.assert_called_once_with(
            model="configured:model",
            output_type=mock_output_type,
            instrument=True,
        )

    @patch("ara_cli.llm_utils.Agent")
    @patch("ara_cli.llm_utils.get_configured_conversion_llm_model")
    def test_uses_provided_model_name(self, mock_get_model, mock_agent):
        """Uses provided model_name instead of configured model."""
        mock_output_type = MagicMock()

        create_pydantic_ai_agent(
            output_type=mock_output_type, model_name="custom:model"
        )

        mock_agent.assert_called_once_with(
            model="custom:model",
            output_type=mock_output_type,
            instrument=True,
        )
        mock_get_model.assert_not_called()

    @patch("ara_cli.llm_utils.Agent")
    @patch("ara_cli.llm_utils.get_configured_conversion_llm_model")
    def test_sets_instrument_flag(self, mock_get_model, mock_agent):
        """Sets instrument flag correctly."""
        mock_get_model.return_value = "test:model"
        mock_output_type = MagicMock()

        create_pydantic_ai_agent(output_type=mock_output_type, instrument=False)

        mock_agent.assert_called_once_with(
            model="test:model",
            output_type=mock_output_type,
            instrument=False,
        )

    @patch("ara_cli.llm_utils.Agent")
    @patch("ara_cli.llm_utils.get_configured_conversion_llm_model")
    def test_returns_agent_instance(self, mock_get_model, mock_agent):
        """Returns the created agent instance."""
        mock_get_model.return_value = "test:model"
        mock_agent_instance = MagicMock()
        mock_agent.return_value = mock_agent_instance

        result = create_pydantic_ai_agent(output_type=MagicMock())

        assert result == mock_agent_instance
