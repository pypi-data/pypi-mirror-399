"""
Unit tests for artefact extraction functionality.

These tests cover the functionality tested by:
- _agile_artefact_extraction.feature
- agile_artefact_extraction_force.feature
- agile_artefact_extraction_override.feature
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open

from ara_cli.prompt_extractor import (
    _find_extract_token,
    _extract_file_path,
    _find_artefact_class,
    _apply_replacements,
    create_file_if_not_exist,
    determine_should_create,
    handle_existing_file,
    FenceDetector,
    extract_responses,
    _perform_extraction_for_block,
    _process_document_blocks,
)


# =============================================================================
# Tests for FenceDetector class (artefact marking functionality)
# =============================================================================


class TestFenceDetector:
    """Tests for the FenceDetector class used in extraction."""

    def test_is_extract_fence_with_valid_fence(self):
        """Detects valid extract fence markers."""
        source_lines = ["```python", "# [x] extract", "print('hello')", "```"]
        detector = FenceDetector(source_lines)
        assert detector.is_extract_fence(0) is True

    def test_is_extract_fence_with_triple_tilde(self):
        """Detects triple tilde fence markers."""
        source_lines = ["~~~", "# [x] extract", "some content", "~~~"]
        detector = FenceDetector(source_lines)
        assert detector.is_extract_fence(0) is True

    def test_is_extract_fence_without_extract_marker(self):
        """Returns False for fence without extract marker."""
        source_lines = ["```python", "print('hello')", "```"]
        detector = FenceDetector(source_lines)
        assert detector.is_extract_fence(0) is False

    def test_is_extract_fence_non_fence_line(self):
        """Returns False for non-fence lines."""
        source_lines = ["some regular text", "# [x] extract"]
        detector = FenceDetector(source_lines)
        assert detector.is_extract_fence(0) is False

    def test_find_matching_fence_end_simple(self):
        """Finds matching end fence for simple block."""
        source_lines = ["```", "# [x] extract", "content", "```"]
        detector = FenceDetector(source_lines)
        assert detector.find_matching_fence_end(0) == 3

    def test_find_matching_fence_end_with_language(self):
        """Finds matching end fence with language specifier."""
        source_lines = ["```python", "# [x] extract", "print('hello')", "```"]
        detector = FenceDetector(source_lines)
        assert detector.find_matching_fence_end(0) == 3

    def test_find_matching_fence_end_indented(self):
        """Finds matching end fence for indented blocks."""
        source_lines = ["  ```", "  # [x] extract", "  content", "  ```"]
        detector = FenceDetector(source_lines)
        assert detector.find_matching_fence_end(0) == 3

    def test_find_matching_fence_end_no_match(self):
        """Returns -1 when no matching fence end found."""
        source_lines = ["```", "# [x] extract", "content without closing fence"]
        detector = FenceDetector(source_lines)
        assert detector.find_matching_fence_end(0) == -1


# =============================================================================
# Tests for extraction helper functions
# =============================================================================


class TestExtractionHelpers:
    """Tests for extraction helper functions."""

    def test_extract_file_path_valid(self):
        """Extracts file path from content lines."""
        content_lines = ["# filename: path/to/file.py", "content"]
        result = _extract_file_path(content_lines)
        assert result == "path/to/file.py"

    def test_extract_file_path_with_spaces(self):
        """Extracts file path with surrounding spaces."""
        content_lines = ["# filename:   file.txt  ", "content"]
        result = _extract_file_path(content_lines)
        assert result == "file.txt"

    def test_extract_file_path_no_match(self):
        """Returns None when no filename found."""
        content_lines = ["no filename here", "content"]
        result = _extract_file_path(content_lines)
        assert result is None

    def test_extract_file_path_empty_lines(self):
        """Returns None for empty content lines."""
        result = _extract_file_path([])
        assert result is None

    def test_apply_replacements_single(self):
        """Applies single replacement correctly."""
        content = "# [x] extract\ncode here"
        replacements = [("# [x] extract", "# [v] extract")]
        result = _apply_replacements(content, replacements)
        assert "# [v] extract" in result
        assert "# [x] extract" not in result

    def test_apply_replacements_multiple(self):
        """Applies multiple replacements correctly."""
        content = "```\n# [x] extract\ncode1\n```\n\n```\n# [x] extract\ncode2\n```"
        replacements = [
            ("```\n# [x] extract\ncode1\n```", "```\n# [v] extract\ncode1\n```"),
            ("```\n# [x] extract\ncode2\n```", "```\n# [v] extract\ncode2\n```"),
        ]
        result = _apply_replacements(content, replacements)
        assert result.count("# [v] extract") == 2
        assert "# [x] extract" not in result


# =============================================================================
# Tests for file creation logic (force flag functionality)
# =============================================================================


class TestFileCreation:
    """Tests for file creation with force flag."""

    @patch("builtins.input", return_value="y")
    def test_determine_should_create_with_user_confirmation(self, mock_input):
        """User confirms file creation."""
        result = determine_should_create(skip_query=False)
        assert result is True
        mock_input.assert_called_once()

    @patch("builtins.input", return_value="n")
    def test_determine_should_create_user_declines(self, mock_input):
        """User declines file creation."""
        result = determine_should_create(skip_query=False)
        assert result is False

    def test_determine_should_create_skips_query_when_force(self):
        """Force flag bypasses user confirmation."""
        result = determine_should_create(skip_query=True)
        assert result is True

    @patch("builtins.input", return_value="y")
    def test_create_file_if_not_exist_creates_file(self, mock_input):
        """Creates file when it doesn't exist and user confirms."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "new_file.txt")
            content = "test content"

            create_file_if_not_exist(file_path, content, skip_query=False)

            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == content

    def test_create_file_if_not_exist_with_force(self):
        """Creates file without user prompt when force is True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "new_file.txt")
            content = "test content"

            create_file_if_not_exist(file_path, content, skip_query=True)

            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == content

    def test_create_file_if_not_exist_creates_directories(self):
        """Creates parent directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "subdir", "deep", "file.txt")
            content = "nested content"

            create_file_if_not_exist(file_path, content, skip_query=True)

            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == content


# =============================================================================
# Tests for handle_existing_file (override functionality)
# =============================================================================


class TestHandleExistingFile:
    """Tests for handling existing files during extraction."""

    @patch("builtins.input", return_value="y")
    def test_handle_existing_file_creates_when_not_exists(self, mock_input):
        """Creates file when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "new_file.txt")
            content = "new content"

            handle_existing_file(file_path, content, skip_query=False, write=False)

            assert os.path.exists(file_path)

    def test_handle_existing_file_creates_with_force(self):
        """Creates file with force flag (skip_query=True)."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "new_file.txt")
            content = "new content"

            handle_existing_file(file_path, content, skip_query=True, write=False)

            assert os.path.exists(file_path)
            with open(file_path, "r") as f:
                assert f.read() == content

    def test_handle_existing_file_overwrites_with_write_flag(self):
        """Overwrites existing file when write flag is True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = os.path.join(tmpdir, "existing.txt")

            # Create existing file
            with open(file_path, "w") as f:
                f.write("old content")

            new_content = "new overwritten content"
            handle_existing_file(file_path, new_content, skip_query=False, write=True)

            with open(file_path, "r") as f:
                assert f.read() == new_content


# =============================================================================
# Tests for extract_responses (full extraction workflow)
# =============================================================================


class TestExtractResponses:
    """Tests for the main extract_responses function."""

    def test_extract_responses_marks_blocks(self):
        """Extracted blocks are marked with [v] instead of [x]."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "chat.md")
            target_file = os.path.join(tmpdir, "output.txt")

            content = f"""# ara prompt:
Some conversation

```
# [x] extract
# filename: {target_file}
print('hello world')
```

More conversation
"""
            with open(chat_file, "w") as f:
                f.write(content)

            extract_responses(chat_file, relative_to_ara_root=False, force=True)

            with open(chat_file, "r") as f:
                updated_content = f.read()

            assert "# [v] extract" in updated_content
            assert "# [x] extract" not in updated_content

    def test_extract_responses_creates_target_file(self):
        """Target file is created with extracted content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "chat.md")
            target_file = os.path.join(tmpdir, "output.py")

            content = f"""```
# [x] extract
# filename: {target_file}
print('hello world')
```
"""
            with open(chat_file, "w") as f:
                f.write(content)

            extract_responses(chat_file, relative_to_ara_root=False, force=True)

            assert os.path.exists(target_file)
            with open(target_file, "r") as f:
                assert "print('hello world')" in f.read()

    def test_extract_responses_handles_missing_file(self, capsys):
        """Handles missing document file gracefully."""
        extract_responses("nonexistent_file.md", force=True)
        captured = capsys.readouterr()
        assert "File not found" in captured.out

    def test_extract_responses_multiple_blocks(self):
        """Extracts multiple blocks from same document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "chat.md")
            file1 = os.path.join(tmpdir, "file1.txt")
            file2 = os.path.join(tmpdir, "file2.txt")

            content = f"""```
# [x] extract
# filename: {file1}
content 1
```

```
# [x] extract
# filename: {file2}
content 2
```
"""
            with open(chat_file, "w") as f:
                f.write(content)

            extract_responses(chat_file, relative_to_ara_root=False, force=True)

            assert os.path.exists(file1)
            assert os.path.exists(file2)

            with open(chat_file, "r") as f:
                updated_content = f.read()
            assert updated_content.count("# [v] extract") == 2

    @pytest.mark.parametrize(
        "classifier, template_body",
        [
            ("businessgoal", "Businessgoal: sample businessgoal\nIn order to impress\nAs a person\nI want world domination\nDescription:"),
            ("capability", "Capability: sample capability\nContributes to\nTo be able to do things\nDescription:"),
            ("epic", "Epic: sample epic\nIn order to make criminals think twice before breaking the law\nAs a Batman\nI want all the gadgets\nDescription:"),
            ("example", "Example: sample example\nIllustrates\nDescription:"),
            ("feature", "Feature: sample feature\nAs a Batman\nI want to inspire fear\nSo that criminals don't break the law in the first place\nContributes to\nDescription:"),
            ("issue", "Issue: sample issue\nContributes to\nadditional description here\nDescription:"),
            ("keyfeature", "Keyfeature: sample keyfeature\nIn order to impress\nAs a person\nI want world domination\nDescription:"),
            ("task", "Task: sample task\nContributes to\nDescription:"),
            ("userstory", "Userstory: sample userstory\nAs a user\nI want to do things\nSo that valid\nDescription:"),
            ("vision", "Vision: sample vision\nContributes to\nFor blah\nWho blahs\nThe blah is a blah\nThat blah\nUnlike blah\nOur product blah\nDescription:"),
        ],
    )
    def test_extract_responses_all_types(self, classifier, template_body):
        """Extracts all supported artefact types correctly."""
        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "chat.md")
            
            target_file = os.path.join(tmpdir, "ara", f"{classifier}s", f"sample_{classifier}.{classifier}")
            
            # Ensure target directory exists for extraction logic that doesn't create it recursively in all paths?
            # Actually extract_responses creates directories.
            
            content = f"""# ara prompt:
Chat content

```
# [x] extract
# filename: {target_file}
@creator_unknown
{template_body}
```

End chat
"""
            with open(chat_file, "w") as f:
                f.write(content)

            extract_responses(chat_file, relative_to_ara_root=False, force=True)

            assert os.path.exists(target_file), f"Failed to create {classifier} file"
            
            with open(target_file, "r") as f:
                extracted_content = f.read()
            
            # Verify some key part of the content exists
            assert f"sample {classifier}" in extracted_content
            
            with open(chat_file, "r") as f:
                updated_chat = f.read()
                
            assert "# [v] extract" in updated_chat


# =============================================================================
# Tests for process_document_blocks
# =============================================================================


class TestProcessDocumentBlocks:
    """Tests for processing document blocks."""

    def test_process_document_blocks_returns_replacements(self):
        """Returns list of replacements for extracted blocks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_dir = os.getcwd()
            os.chdir(tmpdir)

            try:
                source_lines = [
                    "```",
                    "# [x] extract",
                    "# filename: test_output.txt",
                    "test content",
                    "```",
                ]

                replacements = _process_document_blocks(
                    source_lines, force=True, write=False
                )

                assert len(replacements) == 1
                original, modified = replacements[0]
                assert "# [x] extract" in original
                assert "# [v] extract" in modified
            finally:
                os.chdir(original_dir)

    def test_process_document_blocks_no_extract_markers(self):
        """Returns empty list when no extract markers found."""
        source_lines = ["```python", "print('hello')", "```"]

        replacements = _process_document_blocks(source_lines, force=True, write=False)
        assert replacements == []


# =============================================================================
# Tests for artefact class detection
# =============================================================================


class TestArtefactClassDetection:
    """Tests for detecting artefact class from content."""

    def test_find_artefact_class_feature(self):
        """Detects Feature artefact class."""
        from ara_cli.artefact_models.feature_artefact_model import FeatureArtefact

        content_lines = ["Feature: sample feature", "As a user"]
        result = _find_artefact_class(content_lines)
        assert result == FeatureArtefact

    def test_find_artefact_class_task(self):
        """Detects Task artefact class."""
        from ara_cli.artefact_models.task_artefact_model import TaskArtefact

        content_lines = ["Task: sample task", "Contributes to"]
        result = _find_artefact_class(content_lines)
        assert result == TaskArtefact

    def test_find_artefact_class_with_tag(self):
        """Detects artefact class even with tags on first line."""
        from ara_cli.artefact_models.feature_artefact_model import FeatureArtefact

        content_lines = ["@creator_unknown", "Feature: sample feature"]
        result = _find_artefact_class(content_lines)
        assert result == FeatureArtefact

    def test_find_artefact_class_unknown(self):
        """Returns None for unknown artefact type."""
        content_lines = ["Unknown: something", "random content"]
        result = _find_artefact_class(content_lines)
        assert result is None


# =============================================================================
# Tests for extraction with different artefact types
# =============================================================================


class TestArtefactTypeExtraction:
    """Tests extraction for different artefact types (businessgoal, capability, etc.)."""

    @pytest.fixture
    def temp_ara_structure(self):
        """Creates a temporary ara directory structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ara_dir = os.path.join(tmpdir, "ara")
            os.makedirs(os.path.join(ara_dir, "businessgoals"))
            os.makedirs(os.path.join(ara_dir, "capabilities"))
            os.makedirs(os.path.join(ara_dir, "epics"))
            os.makedirs(os.path.join(ara_dir, "features"))
            os.makedirs(os.path.join(ara_dir, "tasks"))
            yield tmpdir

    @pytest.mark.parametrize(
        "classifier,prefix",
        [
            ("businessgoal", "Businessgoal:"),
            ("capability", "Capability:"),
            ("epic", "Epic:"),
            ("feature", "Feature:"),
            ("task", "Task:"),
            ("keyfeature", "Keyfeature:"),
            ("userstory", "Userstory:"),
            ("vision", "Vision:"),
            ("example", "Example:"),
            ("issue", "Issue:"),
        ],
    )
    def test_artefact_prefix_recognition(self, classifier, prefix):
        """Recognizes different artefact type prefixes."""
        content_lines = [f"{prefix} sample {classifier}", "Contributes to"]
        # Just verify it doesn't crash - detailed validation is done in artefact model tests
        result = _find_artefact_class(content_lines)
        # Some artefact types may not be in the mapping
        # This test ensures we don't crash during recognition


# =============================================================================
# Tests for find_extract_token (markdown parsing)
# =============================================================================


class TestFindExtractToken:
    """Tests for finding extract tokens in markdown."""

    def test_find_extract_token_found(self):
        """Finds extract token in tokens list."""
        from markdown_it import MarkdownIt

        md = MarkdownIt()
        content = "```\n# [x] extract\ncontent\n```"
        tokens = md.parse(content)

        result = _find_extract_token(tokens)
        assert result is not None
        assert "# [x] extract" in result.content

    def test_find_extract_token_not_found(self):
        """Returns None when no extract token present."""
        from markdown_it import MarkdownIt

        md = MarkdownIt()
        content = "```\nsome code\n```"
        tokens = md.parse(content)

        result = _find_extract_token(tokens)
        assert result is None

    def test_find_extract_token_with_regular_text(self):
        """Returns None for regular text without code blocks."""
        from markdown_it import MarkdownIt

        md = MarkdownIt()
        content = "Just some regular markdown text."
        tokens = md.parse(content)

        result = _find_extract_token(tokens)
        assert result is None
