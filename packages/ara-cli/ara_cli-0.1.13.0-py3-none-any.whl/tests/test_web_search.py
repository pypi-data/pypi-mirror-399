"""
Unit tests for chat_web_search/web_search.py

Provides full test coverage for web search functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from ara_cli.chat_web_search.web_search import (
    is_web_search_supported,
    get_supported_models_message,
    _get_raw_model_name,
    _deduplicate_citations,
    _format_citations,
    _create_chunk,
    _extract_openai_citations,
    _extract_anthropic_text_citations,
    _extract_anthropic_search_results,
    perform_openai_web_search,
    perform_anthropic_web_search,
    perform_web_search_completion,
    OPENAI_WEB_SEARCH_MODELS,
    ANTHROPIC_WEB_SEARCH_MODELS,
)
from ara_cli.error_handler import AraError


# =============================================================================
# Tests for is_web_search_supported
# =============================================================================


class TestIsWebSearchSupported:
    """Tests for is_web_search_supported function."""

    @pytest.mark.parametrize(
        "model",
        [
            "gpt-5",
            "gpt-5.1",
            "o3",
            "o4-mini",
            "openai/gpt-5",
            "openai/o4-mini",
            "gpt-5-search-api",
            "gpt-4o-search-preview",
        ],
    )
    def test_openai_models_supported(self, model):
        """OpenAI web search models are supported."""
        supported, provider = is_web_search_supported(model)
        assert supported is True
        assert provider == "openai"

    @pytest.mark.parametrize(
        "model",
        [
            "claude-sonnet-4-5-20250929",
            "claude-sonnet-4-20250514",
            "anthropic/claude-sonnet-4-5-20250929",
            "claude-haiku-4-5-20251001",
            "claude-opus-4-20250514",
        ],
    )
    def test_anthropic_models_supported(self, model):
        """Anthropic web search models are supported."""
        supported, provider = is_web_search_supported(model)
        assert supported is True
        assert provider == "anthropic"

    def test_unsupported_model_returns_false(self):
        """Unsupported models return False."""
        supported, provider = is_web_search_supported("gpt-4o")
        assert supported is False
        assert provider is None


# =============================================================================
# Tests for get_supported_models_message
# =============================================================================


class TestGetSupportedModelsMessage:
    """Tests for get_supported_models_message function."""

    def test_includes_model_name(self):
        """Message includes the unsupported model name."""
        result = get_supported_models_message("unsupported-model")
        assert "unsupported-model" in result

    def test_lists_openai_models(self):
        """Message lists OpenAI models."""
        result = get_supported_models_message("test")
        assert "gpt-5" in result
        assert "OpenAI" in result

    def test_lists_anthropic_models(self):
        """Message lists Anthropic models."""
        result = get_supported_models_message("test")
        assert "claude" in result
        assert "Anthropic" in result


# =============================================================================
# Tests for _get_raw_model_name
# =============================================================================


class TestGetRawModelName:
    """Tests for _get_raw_model_name function."""

    def test_strips_openai_prefix(self):
        """Strips openai/ prefix."""
        result = _get_raw_model_name("openai/gpt-5")
        assert result == "gpt-5"

    def test_strips_anthropic_prefix(self):
        """Strips anthropic/ prefix."""
        result = _get_raw_model_name("anthropic/claude-sonnet-4-20250514")
        assert result == "claude-sonnet-4-20250514"

    def test_returns_unchanged_without_prefix(self):
        """Returns model unchanged when no prefix."""
        result = _get_raw_model_name("gpt-5")
        assert result == "gpt-5"


# =============================================================================
# Tests for _deduplicate_citations
# =============================================================================


class TestDeduplicateCitations:
    """Tests for _deduplicate_citations function."""

    def test_removes_duplicate_urls(self):
        """Removes citations with duplicate URLs."""
        citations = [
            {"title": "First", "url": "https://example.com"},
            {"title": "Second", "url": "https://example.com"},
            {"title": "Third", "url": "https://other.com"},
        ]
        result = _deduplicate_citations(citations)
        assert len(result) == 2
        assert result[0]["title"] == "First"
        assert result[1]["title"] == "Third"

    def test_preserves_order(self):
        """Preserves order of first occurrences."""
        citations = [
            {"title": "A", "url": "https://a.com"},
            {"title": "B", "url": "https://b.com"},
            {"title": "C", "url": "https://c.com"},
        ]
        result = _deduplicate_citations(citations)
        assert [c["title"] for c in result] == ["A", "B", "C"]

    def test_handles_empty_list(self):
        """Handles empty citation list."""
        result = _deduplicate_citations([])
        assert result == []

    def test_skips_empty_urls(self):
        """Skips citations with empty URLs."""
        citations = [
            {"title": "First", "url": ""},
            {"title": "Second", "url": "https://example.com"},
        ]
        result = _deduplicate_citations(citations)
        assert len(result) == 1
        assert result[0]["title"] == "Second"


# =============================================================================
# Tests for _format_citations
# =============================================================================


class TestFormatCitations:
    """Tests for _format_citations function."""

    def test_formats_markdown_links(self):
        """Formats citations as markdown links."""
        citations = [
            {"title": "Example Site", "url": "https://example.com"},
        ]
        result = _format_citations(citations)
        assert "[Example Site](https://example.com)" in result

    def test_includes_sources_header(self):
        """Includes Sources header."""
        citations = [{"title": "Test", "url": "https://test.com"}]
        result = _format_citations(citations)
        assert "**Sources:**" in result

    def test_numbers_citations(self):
        """Numbers each citation."""
        citations = [
            {"title": "First", "url": "https://first.com"},
            {"title": "Second", "url": "https://second.com"},
        ]
        result = _format_citations(citations)
        assert "1. [First]" in result
        assert "2. [Second]" in result

    def test_returns_empty_for_no_citations(self):
        """Returns empty string when no citations."""
        result = _format_citations([])
        assert result == ""

    def test_handles_missing_url(self):
        """Handles citations without URL."""
        citations = [{"title": "No URL", "url": ""}]
        result = _format_citations(citations)
        assert result == ""  # Empty URL is filtered by deduplicate


# =============================================================================
# Tests for _create_chunk
# =============================================================================


class TestCreateChunk:
    """Tests for _create_chunk function."""

    def test_creates_mock_chunk_with_content(self):
        """Creates mock chunk with content accessible via choices."""
        chunk = _create_chunk("test content")
        assert chunk.choices[0].delta.content == "test content"


# =============================================================================
# Tests for _extract_openai_citations
# =============================================================================


class TestExtractOpenaiCitations:
    """Tests for _extract_openai_citations function."""

    def test_extracts_url_citations(self):
        """Extracts URL citations from response."""
        mock_annotation = MagicMock()
        mock_annotation.type = "url_citation"
        mock_annotation.title = "Test Title"
        mock_annotation.url = "https://test.com"

        mock_content_item = MagicMock()
        mock_content_item.annotations = [mock_annotation]

        mock_output_item = MagicMock()
        mock_output_item.type = "message"
        mock_output_item.content = [mock_content_item]

        mock_response = MagicMock()
        mock_response.output = [mock_output_item]

        result = _extract_openai_citations(mock_response)

        assert len(result) == 1
        assert result[0]["title"] == "Test Title"
        assert result[0]["url"] == "https://test.com"

    def test_returns_empty_for_no_output(self):
        """Returns empty list when no output."""
        mock_response = MagicMock()
        mock_response.output = None

        result = _extract_openai_citations(mock_response)

        assert result == []


# =============================================================================
# Tests for _extract_anthropic_text_citations
# =============================================================================


class TestExtractAnthropicTextCitations:
    """Tests for _extract_anthropic_text_citations function."""

    def test_extracts_citations_with_url(self):
        """Extracts citations that have URL attribute."""
        mock_citation = MagicMock()
        mock_citation.url = "https://example.com"
        mock_citation.title = "Example"

        mock_content_block = MagicMock()
        mock_content_block.citations = [mock_citation]

        result = _extract_anthropic_text_citations(mock_content_block)

        assert len(result) == 1
        assert result[0]["url"] == "https://example.com"

    def test_returns_empty_for_no_citations(self):
        """Returns empty list when no citations."""
        mock_content_block = MagicMock()
        mock_content_block.citations = None

        result = _extract_anthropic_text_citations(mock_content_block)

        assert result == []


# =============================================================================
# Tests for _extract_anthropic_search_results
# =============================================================================


class TestExtractAnthropicSearchResults:
    """Tests for _extract_anthropic_search_results function."""

    def test_extracts_web_search_results(self):
        """Extracts web search result citations."""
        mock_result = MagicMock()
        mock_result.type = "web_search_result"
        mock_result.title = "Search Result"
        mock_result.url = "https://search.com"

        mock_content_block = MagicMock()
        mock_content_block.content = [mock_result]

        result = _extract_anthropic_search_results(mock_content_block)

        assert len(result) == 1
        assert result[0]["title"] == "Search Result"
        assert result[0]["url"] == "https://search.com"

    def test_skips_non_search_results(self):
        """Skips items that aren't web_search_result type."""
        mock_result = MagicMock()
        mock_result.type = "other_type"

        mock_content_block = MagicMock()
        mock_content_block.content = [mock_result]

        result = _extract_anthropic_search_results(mock_content_block)

        assert result == []


# =============================================================================
# Tests for perform_openai_web_search
# =============================================================================


class TestPerformOpenaiWebSearch:
    """Tests for perform_openai_web_search function."""

    @patch("openai.OpenAI")
    @patch("os.getenv", return_value="test-api-key")
    def test_uses_chat_completions_for_search_models(
        self, mock_getenv, mock_openai_class
    ):
        """Uses Chat Completions API for search models."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock(delta=MagicMock(content="response"))]
        mock_client.chat.completions.create.return_value = [mock_chunk]

        results = list(perform_openai_web_search("test query", "gpt-5-search-api"))

        mock_client.chat.completions.create.assert_called_once()

    @patch("openai.OpenAI")
    @patch("os.getenv", return_value="test-api-key")
    def test_uses_responses_api_for_other_models(self, mock_getenv, mock_openai_class):
        """Uses Responses API for non-search models."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.output_text = "response text"
        mock_response.output = []
        mock_client.responses.create.return_value = mock_response

        results = list(perform_openai_web_search("test query", "gpt-5"))

        mock_client.responses.create.assert_called_once()


# =============================================================================
# Tests for perform_anthropic_web_search
# =============================================================================


class TestPerformAnthropicWebSearch:
    """Tests for perform_anthropic_web_search function."""

    @patch("anthropic.Anthropic")
    @patch("os.getenv", return_value="test-api-key")
    def test_creates_message_with_web_search_tool(
        self, mock_getenv, mock_anthropic_class
    ):
        """Creates message with web_search tool."""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "response text"
        mock_text_block.citations = None

        mock_response = MagicMock()
        mock_response.content = [mock_text_block]
        mock_client.messages.create.return_value = mock_response

        results = list(
            perform_anthropic_web_search("test query", "claude-sonnet-4-20250514")
        )

        mock_client.messages.create.assert_called_once()
        call_args = mock_client.messages.create.call_args
        assert any("web_search" in str(arg) for arg in call_args)


# =============================================================================
# Tests for perform_web_search_completion
# =============================================================================


class TestPerformWebSearchCompletion:
    """Tests for perform_web_search_completion function."""

    @patch("ara_cli.chat_web_search.web_search.LLMSingleton")
    def test_raises_for_unsupported_model(self, mock_singleton):
        """Raises AraError for unsupported model."""
        mock_instance = MagicMock()
        mock_instance.get_config_by_purpose.return_value = {"model": "gpt-4o"}
        mock_singleton.get_instance.return_value = mock_instance

        with pytest.raises(AraError) as exc_info:
            list(perform_web_search_completion("test query"))

        assert "not supported" in str(exc_info.value)

    @patch("ara_cli.chat_web_search.web_search.perform_openai_web_search")
    @patch("ara_cli.chat_web_search.web_search.LLMSingleton")
    def test_uses_openai_for_openai_models(self, mock_singleton, mock_openai_search):
        """Uses OpenAI search for OpenAI models."""
        mock_instance = MagicMock()
        mock_instance.get_config_by_purpose.return_value = {"model": "gpt-5"}
        mock_singleton.get_instance.return_value = mock_instance
        mock_openai_search.return_value = iter([])

        list(perform_web_search_completion("test query"))

        mock_openai_search.assert_called_once()

    @patch("ara_cli.chat_web_search.web_search.perform_anthropic_web_search")
    @patch("ara_cli.chat_web_search.web_search.LLMSingleton")
    def test_uses_anthropic_for_anthropic_models(
        self, mock_singleton, mock_anthropic_search
    ):
        """Uses Anthropic search for Anthropic models."""
        mock_instance = MagicMock()
        mock_instance.get_config_by_purpose.return_value = {
            "model": "claude-sonnet-4-20250514"
        }
        mock_singleton.get_instance.return_value = mock_instance
        mock_anthropic_search.return_value = iter([])

        list(perform_web_search_completion("test query"))

        mock_anthropic_search.assert_called_once()
