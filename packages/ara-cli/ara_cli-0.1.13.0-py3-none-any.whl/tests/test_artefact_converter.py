"""
Unit tests for artefact_converter.py

Provides full test coverage for the AraArtefactConverter class.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from ara_cli.artefact_converter import AraArtefactConverter
from ara_cli.error_handler import AraError


# =============================================================================
# Test fixtures
# =============================================================================


@pytest.fixture
def mock_file_system():
    """Mock file system for testing."""
    mock_fs = MagicMock()
    mock_fs.path = MagicMock()
    mock_fs.path.join = os.path.join
    mock_fs.path.exists = MagicMock(return_value=False)
    return mock_fs


@pytest.fixture
def converter(mock_file_system):
    """Create converter instance with mocked dependencies."""
    with patch("ara_cli.artefact_converter.ArtefactReader") as mock_reader, patch(
        "ara_cli.artefact_converter.ArtefactCreator"
    ):
        converter = AraArtefactConverter(file_system=mock_file_system)
        converter.reader = mock_reader.return_value
        return converter


# =============================================================================
# Tests for __init__
# =============================================================================


class TestAraArtefactConverterInit:
    """Tests for AraArtefactConverter initialization."""

    def test_uses_provided_file_system(self, mock_file_system):
        """Uses provided file system when given."""
        with patch("ara_cli.artefact_converter.ArtefactReader"), patch(
            "ara_cli.artefact_converter.ArtefactCreator"
        ):
            converter = AraArtefactConverter(file_system=mock_file_system)
            assert converter.file_system == mock_file_system

    def test_uses_os_as_default_file_system(self):
        """Uses os module as default file system."""
        with patch("ara_cli.artefact_converter.ArtefactReader"), patch(
            "ara_cli.artefact_converter.ArtefactCreator"
        ):
            converter = AraArtefactConverter()
            assert converter.file_system == os


# =============================================================================
# Tests for _validate_classifiers
# =============================================================================


class TestValidateClassifiers:
    """Tests for classifier validation."""

    @patch("ara_cli.artefact_converter.Classifier.is_valid_classifier")
    def test_raises_for_invalid_old_classifier(self, mock_is_valid, converter):
        """Raises ValueError for invalid old classifier."""
        mock_is_valid.side_effect = lambda x: x != "invalid"

        with pytest.raises(ValueError) as exc_info:
            converter._validate_classifiers("invalid", "feature")

        assert "Invalid classifier: invalid" in str(exc_info.value)

    @patch("ara_cli.artefact_converter.Classifier.is_valid_classifier")
    def test_raises_for_invalid_new_classifier(self, mock_is_valid, converter):
        """Raises ValueError for invalid new classifier."""
        mock_is_valid.side_effect = lambda x: x != "invalid"

        with pytest.raises(ValueError) as exc_info:
            converter._validate_classifiers("feature", "invalid")

        assert "Invalid classifier: invalid" in str(exc_info.value)

    @patch(
        "ara_cli.artefact_converter.Classifier.is_valid_classifier", return_value=True
    )
    def test_passes_for_valid_classifiers(self, mock_is_valid, converter):
        """Passes validation for valid classifiers."""
        converter._validate_classifiers("feature", "userstory")
        assert mock_is_valid.call_count == 2


# =============================================================================
# Tests for _resolve_target_content
# =============================================================================


class TestResolveTargetContent:
    """Tests for target content resolution."""

    def test_raises_when_target_exists_without_flags(self, converter):
        """Raises ValueError when target exists and no override/merge flags."""
        converter.reader.read_artefact_data.return_value = (None, {"exists": True})

        with pytest.raises(ValueError) as exc_info:
            converter._resolve_target_content(
                "test", "feature", merge=False, override=False
            )

        assert "already exiting" in str(exc_info.value)

    def test_returns_content_when_merge_flag_set(self, converter):
        """Returns existing content when merge flag is set."""
        converter.reader.read_artefact_data.return_value = (
            "existing content",
            {"exists": True},
        )

        result = converter._resolve_target_content(
            "test", "feature", merge=True, override=False
        )

        assert result == "existing content"

    def test_returns_none_when_override_flag_set(self, converter):
        """Returns None when override flag is set (different path)."""
        converter.reader.read_artefact_data.return_value = (None, {"exists": True})

        # Override skips the existence check entirely
        result = converter._resolve_target_content(
            "test", "feature", merge=False, override=True
        )

        # This won't raise because override=True skips the check
        assert result is None

    def test_returns_none_when_no_existing_target(self, converter):
        """Returns None when no existing target artefact."""
        converter.reader.read_artefact_data.return_value = (None, None)

        result = converter._resolve_target_content(
            "test", "feature", merge=False, override=False
        )

        assert result is None


# =============================================================================
# Tests for _get_target_class
# =============================================================================


class TestGetTargetClass:
    """Tests for getting target artefact class."""

    def test_returns_class_for_valid_classifier(self, converter):
        """Returns artefact class for valid classifier."""
        # Using a known classifier
        result = converter._get_target_class("feature")
        assert result is not None

    def test_raises_for_invalid_classifier(self, converter):
        """Raises ValueError for invalid classifier string."""
        with pytest.raises(ValueError):
            converter._get_target_class("definitely_not_a_type")


# =============================================================================
# Tests for _get_prompt
# =============================================================================


class TestGetPrompt:
    """Tests for prompt generation."""

    @patch("ara_cli.artefact_converter.LLMSingleton")
    def test_uses_fallback_when_langfuse_unavailable(self, mock_singleton, converter):
        """Uses fallback prompt when Langfuse is unavailable."""
        mock_singleton.get_instance.return_value.langfuse = None

        result = converter._get_prompt(
            old_classifier="feature",
            new_classifier="userstory",
            artefact_name="test",
            content="content",
            target_content_existing=None,
            merge=False,
        )

        assert "Convert the following feature artefact" in result
        assert "content" in result

    @patch("ara_cli.artefact_converter.LLMSingleton")
    def test_merge_prompt_includes_both_contents(self, mock_singleton, converter):
        """Merge prompt includes source and target content."""
        mock_singleton.get_instance.return_value.langfuse = None

        result = converter._get_prompt(
            old_classifier="feature",
            new_classifier="userstory",
            artefact_name="test",
            content="source content",
            target_content_existing="target content",
            merge=True,
        )

        assert "Merge" in result
        assert "source content" in result
        assert "target content" in result

    @patch("ara_cli.artefact_converter.LLMSingleton")
    def test_uses_langfuse_prompt_when_available(self, mock_singleton, converter):
        """Uses Langfuse prompt when available."""
        mock_langfuse = MagicMock()
        mock_prompt = MagicMock()
        mock_prompt.compile.return_value = "langfuse prompt"
        mock_langfuse.get_prompt.return_value = mock_prompt
        mock_singleton.get_instance.return_value.langfuse = mock_langfuse

        result = converter._get_prompt(
            old_classifier="feature",
            new_classifier="userstory",
            artefact_name="test",
            content="content",
            target_content_existing=None,
            merge=False,
        )

        assert result == "langfuse prompt"


# =============================================================================
# Tests for _run_conversion_agent
# =============================================================================


class TestRunConversionAgent:
    """Tests for running the conversion agent."""

    @patch("ara_cli.llm_utils.create_pydantic_ai_agent")
    def test_returns_converted_artefact(self, mock_create_agent, converter):
        """Returns converted artefact from agent."""
        mock_result = MagicMock()
        mock_result.output = "converted artefact"
        mock_agent = MagicMock()
        mock_agent.run_sync.return_value = mock_result
        mock_create_agent.return_value = mock_agent

        result = converter._run_conversion_agent("prompt", MagicMock)

        assert result == "converted artefact"

    @patch("ara_cli.llm_utils.create_pydantic_ai_agent")
    def test_raises_ara_error_on_failure(self, mock_create_agent, converter):
        """Raises AraError when agent fails."""
        mock_agent = MagicMock()
        mock_agent.run_sync.side_effect = Exception("LLM error")
        mock_create_agent.return_value = mock_agent

        with pytest.raises(AraError) as exc_info:
            converter._run_conversion_agent("prompt", MagicMock)

        assert "LLM conversion failed" in str(exc_info.value)


# =============================================================================
# Tests for _write_artefact
# =============================================================================


class TestWriteArtefact:
    """Tests for writing converted artefacts."""

    @patch("ara_cli.artefact_converter.DirectoryNavigator")
    @patch(
        "ara_cli.artefact_converter.Classifier.get_sub_directory",
        return_value="features",
    )
    @patch("builtins.open", new_callable=mock_open)
    @patch("os.makedirs")
    @patch("shutil.rmtree")
    def test_writes_artefact_file(
        self,
        mock_rmtree,
        mock_makedirs,
        mock_file,
        mock_subdir,
        mock_navigator,
        converter,
        mock_file_system,
    ):
        """Writes artefact content to file."""
        mock_file_system.path.exists.return_value = False

        converter._write_artefact(
            "feature", "test", "content", merge=False, override=False
        )

        mock_file.assert_called()
        mock_file().write.assert_called_with("content")

    @patch("ara_cli.artefact_converter.DirectoryNavigator")
    @patch(
        "ara_cli.artefact_converter.Classifier.get_sub_directory",
        return_value="features",
    )
    def test_raises_when_file_exists_without_flags(
        self, mock_subdir, mock_navigator, converter, mock_file_system
    ):
        """Raises ValueError when target file exists without override/merge."""
        mock_file_system.path.exists.return_value = True

        with pytest.raises(ValueError) as exc_info:
            converter._write_artefact(
                "feature", "test", "content", merge=False, override=False
            )

        assert "already exists" in str(exc_info.value)


# =============================================================================
# Tests for convert (integration)
# =============================================================================


class TestConvert:
    """Integration tests for the convert method."""

    @patch(
        "ara_cli.artefact_converter.Classifier.is_valid_classifier", return_value=True
    )
    def test_raises_when_source_not_found(self, mock_is_valid, converter):
        """Raises AraError when source artefact not found."""
        converter.reader.read_artefact_data.return_value = (None, None)

        with pytest.raises(AraError) as exc_info:
            converter.convert("feature", "test", "userstory")

        assert "not found" in str(exc_info.value)

    @patch("ara_cli.artefact_converter.Classifier.is_valid_classifier")
    def test_raises_for_invalid_classifier(self, mock_is_valid, converter):
        """Raises ValueError for invalid classifier."""
        mock_is_valid.return_value = False

        with pytest.raises(ValueError):
            converter.convert("invalid", "test", "userstory")
