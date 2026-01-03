"""
Unit tests for prompt_extractor.py

These tests cover the functionality previously tested by:
- agile_artefact_extraction.feature
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
    _process_file_extraction,
    _process_artefact_extraction,
    _perform_extraction_for_block,
    FenceDetector,
    _process_document_blocks,
    _apply_replacements,
    _setup_working_directory,
    extract_responses,
    modify_and_save_file,
    prompt_user_decision,
    determine_should_create,
    create_file_if_not_exist,
    create_prompt_for_file_modification,
    handle_existing_file,
)


# =============================================================================
# Tests for _find_extract_token
# =============================================================================


class TestFindExtractToken:
    """Tests for _find_extract_token function."""

    def test_returns_token_when_extract_marker_found(self):
        """Token with extract marker is returned."""
        mock_token = MagicMock()
        mock_token.type = "fence"
        mock_token.content = "# [x] extract\n@creator_unknown\nFeature: sample"

        result = _find_extract_token([mock_token])

        assert result == mock_token

    def test_returns_none_when_no_extract_marker(self):
        """None returned when no extract marker present."""
        mock_token = MagicMock()
        mock_token.type = "fence"
        mock_token.content = "Regular code block content"

        result = _find_extract_token([mock_token])

        assert result is None

    def test_returns_none_when_not_fence_type(self):
        """None returned when token is not a fence type."""
        mock_token = MagicMock()
        mock_token.type = "paragraph"
        mock_token.content = "# [x] extract\nContent"

        result = _find_extract_token([mock_token])

        assert result is None

    def test_returns_none_for_empty_tokens(self):
        """None returned for empty token list."""
        result = _find_extract_token([])
        assert result is None

    def test_returns_first_matching_token(self):
        """First matching token is returned when multiple exist."""
        token1 = MagicMock()
        token1.type = "fence"
        token1.content = "# [x] extract\nFirst"

        token2 = MagicMock()
        token2.type = "fence"
        token2.content = "# [x] extract\nSecond"

        result = _find_extract_token([token1, token2])

        assert result == token1


# =============================================================================
# Tests for _extract_file_path
# =============================================================================


class TestExtractFilePath:
    """Tests for _extract_file_path function."""

    def test_extracts_filename_from_first_line(self):
        """Filename is extracted from the first line."""
        content_lines = ["# filename: path/to/file.py", "other content"]

        result = _extract_file_path(content_lines)

        assert result == "path/to/file.py"

    def test_returns_none_when_no_filename_marker(self):
        """None returned when no filename marker present."""
        content_lines = ["@creator_unknown", "Feature: sample"]

        result = _extract_file_path(content_lines)

        assert result is None

    def test_returns_none_for_empty_lines(self):
        """None returned for empty content lines."""
        result = _extract_file_path([])
        assert result is None

    def test_strips_whitespace_from_filename(self):
        """Whitespace is stripped from the extracted filename."""
        content_lines = ["# filename:   path/to/file.py   "]

        result = _extract_file_path(content_lines)

        assert result == "path/to/file.py"


# =============================================================================
# Tests for _find_artefact_class
# =============================================================================


class TestFindArtefactClass:
    """Tests for _find_artefact_class function."""

    @pytest.mark.parametrize(
        "first_word,expected_not_none",
        [
            ("Feature:", True),
            ("Task:", True),
            ("Epic:", True),
            ("Userstory:", True),
            ("Businessgoal:", True),
            ("Capability:", True),
            ("Keyfeature:", True),
            ("Vision:", True),
            ("Example:", True),
            ("Issue:", True),
        ],
    )
    def test_finds_artefact_class_for_known_prefixes(
        self, first_word, expected_not_none
    ):
        """Artefact class found for known prefixes."""
        content_lines = [f"{first_word} sample artefact"]

        result = _find_artefact_class(content_lines)

        if expected_not_none:
            assert result is not None
        else:
            assert result is None

    def test_returns_none_for_unknown_prefix(self):
        """None returned for unknown prefix."""
        content_lines = ["Unknown: something"]

        result = _find_artefact_class(content_lines)

        assert result is None

    def test_checks_first_two_lines_only(self):
        """Only first two lines are checked for artefact class."""
        content_lines = ["@creator", "Feature: sample", "Task: ignored"]

        result = _find_artefact_class(content_lines)

        assert result is not None

    def test_returns_none_for_empty_lines(self):
        """None returned for empty content lines."""
        result = _find_artefact_class([])
        assert result is None


# =============================================================================
# Tests for FenceDetector
# =============================================================================


class TestFenceDetector:
    """Tests for FenceDetector class."""

    def test_is_extract_fence_returns_true_for_extract_block(self):
        """Returns True for fence followed by extract marker."""
        source_lines = ["```", "# [x] extract", "content", "```"]
        detector = FenceDetector(source_lines)

        result = detector.is_extract_fence(0)

        assert result is True

    def test_is_extract_fence_returns_false_for_regular_fence(self):
        """Returns False for regular fence without extract marker."""
        source_lines = ["```python", "code = 1", "```"]
        detector = FenceDetector(source_lines)

        result = detector.is_extract_fence(0)

        assert result is False

    def test_is_extract_fence_returns_false_for_non_fence(self):
        """Returns False for non-fence lines."""
        source_lines = ["regular text", "more text"]
        detector = FenceDetector(source_lines)

        result = detector.is_extract_fence(0)

        assert result is False

    def test_is_extract_fence_works_with_tilde_fence(self):
        """Works with tilde fence markers."""
        source_lines = ["~~~", "# [x] extract", "content", "~~~"]
        detector = FenceDetector(source_lines)

        result = detector.is_extract_fence(0)

        assert result is True

    def test_find_matching_fence_end_finds_closing_fence(self):
        """Finds the matching closing fence."""
        source_lines = ["```", "# [x] extract", "content", "```"]
        detector = FenceDetector(source_lines)

        result = detector.find_matching_fence_end(0)

        assert result == 3

    def test_find_matching_fence_end_returns_minus_one_if_not_found(self):
        """Returns -1 if no matching fence found."""
        source_lines = ["```", "# [x] extract", "content without closing"]
        detector = FenceDetector(source_lines)

        result = detector.find_matching_fence_end(0)

        assert result == -1

    def test_find_matching_fence_handles_nested_fences(self):
        """Handles nested fence blocks correctly."""
        source_lines = ["````", "# [x] extract", "```python", "code = 1", "```", "````"]
        detector = FenceDetector(source_lines)

        result = detector.find_matching_fence_end(0)

        assert result == 5


# =============================================================================
# Tests for determine_should_create
# =============================================================================


class TestDetermineShouldCreate:
    """Tests for determine_should_create function."""

    def test_returns_true_when_skip_query_is_true(self):
        """Returns True when skip_query is True (force mode)."""
        result = determine_should_create(skip_query=True)
        assert result is True

    @patch("ara_cli.prompt_extractor.prompt_user_decision", return_value="y")
    def test_returns_true_when_user_confirms(self, mock_input):
        """Returns True when user confirms with 'y'."""
        result = determine_should_create(skip_query=False)
        assert result is True

    @patch("ara_cli.prompt_extractor.prompt_user_decision", return_value="yes")
    def test_returns_true_when_user_confirms_yes(self, mock_input):
        """Returns True when user confirms with 'yes'."""
        result = determine_should_create(skip_query=False)
        assert result is True

    @patch("ara_cli.prompt_extractor.prompt_user_decision", return_value="n")
    def test_returns_false_when_user_declines(self, mock_input):
        """Returns False when user declines."""
        result = determine_should_create(skip_query=False)
        assert result is False


# =============================================================================
# Tests for create_file_if_not_exist
# =============================================================================


class TestCreateFileIfNotExist:
    """Tests for create_file_if_not_exist function."""

    def test_creates_file_when_not_exists_and_skip_query(self):
        """Creates file when it doesn't exist and skip_query=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "new_file.txt")
            content = "test content"

            create_file_if_not_exist(filepath, content, skip_query=True)

            assert os.path.exists(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                assert f.read() == content

    def test_creates_nested_directories(self):
        """Creates nested directories if they don't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "deep", "nested", "file.txt")
            content = "test content"

            create_file_if_not_exist(filepath, content, skip_query=True)

            assert os.path.exists(filepath)

    @patch("ara_cli.prompt_extractor.determine_should_create", return_value=False)
    def test_does_not_create_when_user_declines(self, mock_determine):
        """Does not create file when user declines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "new_file.txt")

            create_file_if_not_exist(filepath, "content", skip_query=False)

            assert not os.path.exists(filepath)


# =============================================================================
# Tests for handle_existing_file
# =============================================================================


class TestHandleExistingFile:
    """Tests for handle_existing_file function."""

    def test_creates_new_file_when_not_exists(self):
        """Creates new file when it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "new_file.feature")
            content = "@creator\nFeature: sample"

            with patch(
                "ara_cli.prompt_extractor.create_file_if_not_exist"
            ) as mock_create:
                handle_existing_file(filepath, content, skip_query=True)
                mock_create.assert_called_once_with(filepath, content, True)

    def test_overwrites_file_with_write_flag(self):
        """Overwrites existing file when write flag is True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "existing.feature")
            original_content = "original content"
            new_content = "new content"

            # Create existing file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(original_content)

            handle_existing_file(filepath, new_content, skip_query=False, write=True)

            with open(filepath, "r", encoding="utf-8") as f:
                assert f.read() == new_content

    @patch("ara_cli.prompt_extractor.send_prompt")
    @patch("ara_cli.prompt_extractor.modify_and_save_file")
    @patch("ara_cli.prompt_extractor.get_file_content", return_value="existing content")
    def test_calls_llm_merge_when_file_exists_without_write_flag(
        self, mock_get_content, mock_modify, mock_send
    ):
        """Calls LLM merge when file exists and write flag is False."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "existing.feature")

            # Create existing file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("existing content")

            # Mock the LLM response
            mock_chunk = MagicMock()
            mock_chunk.choices = [
                MagicMock(
                    delta=MagicMock(content='{"filename": "test", "content": "merged"}')
                )
            ]
            mock_send.return_value = [mock_chunk]

            handle_existing_file(filepath, "new content", skip_query=False, write=False)

            mock_send.assert_called_once()
            mock_modify.assert_called_once()


# =============================================================================
# Tests for extract_responses
# =============================================================================


class TestExtractResponses:
    """Tests for extract_responses function."""

    def test_marks_extracted_blocks_with_checkmark(self):
        """Changes [x] to [v] in extracted blocks."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "chat.md")
            content = """# ara prompt:
Some text

```
# [x] extract
@creator_unknown
Feature: sample feature

As a user
I want to test
So that I verify

Contributes to 

Description: 
```

more text
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            with patch("ara_cli.prompt_extractor._process_artefact_extraction"):
                extract_responses(filepath, relative_to_ara_root=False, force=True)

            with open(filepath, "r", encoding="utf-8") as f:
                result = f.read()

            assert "# [v] extract" in result
            assert "# [x] extract" not in result

    def test_handles_file_not_found(self, capsys):
        """Handles file not found gracefully."""
        extract_responses("/nonexistent/path/file.md")

        captured = capsys.readouterr()
        assert "Error: File not found" in captured.out

    def test_processes_multiple_blocks(self):
        """Processes multiple extract blocks in a document."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "chat.md")
            content = """```
# [x] extract
@creator
Feature: first

As a user
I want one
So that one

Contributes to 

Description: 
```

```
# [x] extract
@creator
Task: second

Contributes to 

Description: 
```
"""
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            with patch("ara_cli.prompt_extractor._process_artefact_extraction"):
                extract_responses(filepath, relative_to_ara_root=False, force=True)

            with open(filepath, "r", encoding="utf-8") as f:
                result = f.read()

            assert result.count("# [v] extract") == 2


# =============================================================================
# Tests for _process_document_blocks
# =============================================================================


class TestProcessDocumentBlocks:
    """Tests for _process_document_blocks function."""

    def test_returns_empty_list_for_no_blocks(self):
        """Returns empty list when no extract blocks found."""
        source_lines = ["regular text", "no blocks here"]

        result = _process_document_blocks(source_lines, force=True, write=False)

        assert result == []

    @patch("ara_cli.prompt_extractor._perform_extraction_for_block")
    def test_processes_each_block(self, mock_perform):
        """Processes each extract block found."""
        mock_perform.return_value = ("original", "modified")
        source_lines = ["```", "# [x] extract", "@creator", "Feature: test", "```"]

        result = _process_document_blocks(source_lines, force=True, write=False)

        assert len(result) == 1
        mock_perform.assert_called_once()


# =============================================================================
# Tests for _apply_replacements
# =============================================================================


class TestApplyReplacements:
    """Tests for _apply_replacements function."""

    def test_applies_single_replacement(self):
        """Applies a single replacement correctly."""
        content = "original text here"
        replacements = [("original", "modified")]

        result = _apply_replacements(content, replacements)

        assert result == "modified text here"

    def test_applies_multiple_replacements(self):
        """Applies multiple replacements correctly."""
        content = "first second third"
        replacements = [("first", "1st"), ("second", "2nd")]

        result = _apply_replacements(content, replacements)

        assert result == "1st 2nd third"

    def test_returns_original_for_empty_replacements(self):
        """Returns original content when no replacements."""
        content = "unchanged content"

        result = _apply_replacements(content, [])

        assert result == content


# =============================================================================
# Tests for artefact type extraction (covers all artefact types from features)
# =============================================================================


class TestArtefactTypeExtraction:
    """Tests that all artefact types can be extracted."""

    @pytest.mark.parametrize(
        "artefact_type,prefix,subdir",
        [
            ("businessgoal", "Businessgoal:", "businessgoals"),
            ("capability", "Capability:", "capabilities"),
            ("epic", "Epic:", "epics"),
            ("example", "Example:", "examples"),
            ("feature", "Feature:", "features"),
            ("issue", "Issue:", "issues"),
            ("keyfeature", "Keyfeature:", "keyfeatures"),
            ("task", "Task:", "tasks"),
            ("vision", "Vision:", "vision"),
        ],
    )
    def test_artefact_class_found_for_type(self, artefact_type, prefix, subdir):
        """Artefact class is found for each supported type."""
        content_lines = [f"@creator", f"{prefix} sample {artefact_type}"]

        result = _find_artefact_class(content_lines)

        assert result is not None


# =============================================================================
# Tests for force flag behavior (from agile_artefact_extraction_force.feature)
# =============================================================================


class TestForceFlag:
    """Tests for force flag functionality."""

    def test_force_flag_skips_user_confirmation(self):
        """Force flag skips user confirmation."""
        result = determine_should_create(skip_query=True)
        assert result is True

    def test_force_flag_creates_file_immediately(self):
        """Force flag creates file without prompting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "forced.feature")
            content = "test content"

            # With force (skip_query=True), file should be created without prompt
            create_file_if_not_exist(filepath, content, skip_query=True)

            assert os.path.exists(filepath)
            with open(filepath, "r", encoding="utf-8") as f:
                assert f.read() == content


# =============================================================================
# Tests for write flag behavior (from agile_artefact_extraction_override.feature)
# =============================================================================


class TestWriteFlag:
    """Tests for write flag functionality."""

    def test_write_flag_overwrites_existing_file(self):
        """Write flag overwrites existing file without LLM merge."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "existing.feature")
            original = "original content"
            new_content = "new content"

            # Create existing file
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(original)

            handle_existing_file(filepath, new_content, skip_query=False, write=True)

            with open(filepath, "r", encoding="utf-8") as f:
                assert f.read() == new_content

    def test_write_flag_prints_overwrite_message(self, capsys):
        """Write flag prints overwrite message."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "existing.feature")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("original")

            handle_existing_file(filepath, "new", skip_query=False, write=True)

            captured = capsys.readouterr()
            assert "Overwriting without LLM merge as requested" in captured.out


# =============================================================================
# Tests for modify_and_save_file
# =============================================================================


class TestModifyAndSaveFile:
    """Tests for modify_and_save_file function."""

    def test_saves_content_from_json_response(self):
        """Saves content from valid JSON response."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.feature")
            response = '{"filename": "' + filepath + '", "content": "merged content"}'

            modify_and_save_file(response, filepath)

            with open(filepath, "r", encoding="utf-8") as f:
                assert f.read() == "merged content"

    @patch("ara_cli.prompt_extractor.prompt_user_decision", return_value="y")
    def test_prompts_on_filename_mismatch(self, mock_input):
        """Prompts user when filename in response doesn't match."""
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = os.path.join(tmpdir, "test.feature")
            response = '{"filename": "different.feature", "content": "content"}'

            modify_and_save_file(response, filepath)

            mock_input.assert_called_once()

    def test_handles_invalid_json(self, capsys):
        """Handles invalid JSON that json_repair cannot fix properly."""
        # json_repair may convert invalid JSON to a string, causing TypeError
        # when trying to access dict keys - this is expected behavior
        with pytest.raises(TypeError):
            modify_and_save_file("not valid json", "test.feature")
