"""
Unit tests for artefact_autofix.py - Integration scenarios

These tests extend the existing test_artefact_autofix.py to cover scenarios from:
- ara_autofix_command.feature
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from ara_cli.artefact_autofix import (
    read_report_file,
    parse_report,
    apply_autofix,
    read_artefact,
    determine_artefact_type_and_class,
    fix_title_mismatch,
    fix_contribution,
    fix_rule,
    fix_scenario_placeholder_mismatch,
    populate_classified_artefact_info,
    should_skip_issue,
    determine_attempt_count,
    apply_deterministic_fix,
    apply_non_deterministic_fix,
    attempt_autofix_loop,
    set_closest_contribution,
    ask_for_contribution_choice,
    ask_for_correct_contribution,
    _extract_scenario_block,
    _convert_to_scenario_outline,
    _create_examples_table,
    _extract_placeholders_from_scenario,
)
from ara_cli.artefact_models.artefact_model import Artefact, Contribution


# =============================================================================
# Tests for single-pass mode (from ara_autofix_command.feature)
# =============================================================================


class TestSinglePassMode:
    """Tests for single-pass autofix mode."""

    @patch("ara_cli.artefact_autofix.check_file")
    @patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
    def test_single_pass_runs_only_once(self, mock_determine, mock_check_file, capsys):
        """Single-pass mode runs the loop only once."""
        mock_artefact_type = MagicMock()
        mock_artefact_type.value = "feature"
        mock_artefact_class = MagicMock()
        mock_determine.return_value = (mock_artefact_type, mock_artefact_class)
        mock_check_file.return_value = (False, "Some unfixable error")

        apply_autofix(
            file_path="file.feature",
            classifier="feature",
            reason="any",
            single_pass=True,
            deterministic=False,
            non_deterministic=False,
            classified_artefact_info={},
        )

        output = capsys.readouterr().out
        assert "Single-pass mode enabled" in output
        assert "1/1" in output
        mock_check_file.assert_called_once()


# =============================================================================
# Tests for deterministic vs non-deterministic flags
# =============================================================================


class TestDeterministicFlags:
    """Tests for deterministic and non-deterministic flag behavior."""

    @patch("ara_cli.artefact_autofix.run_agent")
    @patch("ara_cli.artefact_autofix.fix_title_mismatch", return_value="fixed")
    @patch("ara_cli.artefact_autofix.check_file")
    @patch("ara_cli.artefact_autofix.write_corrected_artefact")
    @patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
    @patch("ara_cli.artefact_autofix.read_artefact", return_value="original")
    @patch("ara_cli.artefact_autofix.FileClassifier")
    def test_deterministic_only_skips_llm(
        self,
        mock_fc,
        mock_read,
        mock_determine,
        mock_write,
        mock_check,
        mock_fix,
        mock_agent,
    ):
        """Deterministic-only mode skips LLM fixes."""
        mock_type = MagicMock()
        mock_type.value = "feature"
        mock_class = MagicMock()
        mock_class._title_prefix.return_value = "Feature:"
        mock_determine.return_value = (mock_type, mock_class)
        mock_check.side_effect = [(False, "Filename-Title Mismatch"), (True, "")]

        apply_autofix(
            file_path="file.feature",
            classifier="feature",
            reason="Filename-Title Mismatch",
            deterministic=True,
            non_deterministic=False,
            classified_artefact_info={},
        )

        mock_fix.assert_called_once()
        mock_agent.assert_not_called()

    @patch("ara_cli.artefact_autofix.run_agent")
    @patch("ara_cli.artefact_autofix.fix_title_mismatch")
    @patch("ara_cli.artefact_autofix.check_file")
    @patch("ara_cli.artefact_autofix.determine_artefact_type_and_class")
    @patch("ara_cli.artefact_autofix.read_artefact", return_value="original")
    def test_non_deterministic_only_skips_deterministic_fixes(
        self, mock_read, mock_determine, mock_check, mock_fix_title, mock_agent, capsys
    ):
        """Non-deterministic-only mode skips deterministic fixes."""
        mock_type = MagicMock()
        mock_type.value = "feature"
        mock_class = MagicMock()
        mock_determine.return_value = (mock_type, mock_class)
        mock_check.return_value = (False, "Filename-Title Mismatch")

        apply_autofix(
            file_path="file.feature",
            classifier="feature",
            reason="Filename-Title Mismatch",
            deterministic=False,
            non_deterministic=True,
            classified_artefact_info={},
        )

        output = capsys.readouterr().out
        assert "Skipping" in output or mock_fix_title.call_count == 0


# =============================================================================
# Tests for contribution fixes (from ara_autofix_command.feature)
# =============================================================================


class TestContributionFixes:
    """Tests for contribution mismatch fixes."""

    @patch("ara_cli.artefact_autofix.FileClassifier")
    @patch("ara_cli.artefact_autofix.extract_artefact_names_of_classifier")
    @patch("ara_cli.artefact_autofix.find_closest_name_matches")
    def test_set_closest_contribution_single_match(
        self, mock_find, mock_extract, mock_fc
    ):
        """Sets contribution when single close match is found."""
        mock_artefact = MagicMock()
        mock_contribution = MagicMock()
        mock_contribution.artefact_name = "test_epic"
        mock_contribution.classifier = "epic"
        mock_contribution.rule = None
        mock_artefact.contribution = mock_contribution
        mock_artefact.title = "test_userstory"
        mock_artefact._artefact_type.return_value.value = "userstory"

        mock_find.return_value = ["test_epic"]

        artefact, changed = set_closest_contribution(mock_artefact)

        assert changed is False  # Already correct

    @patch("ara_cli.artefact_autofix.FileClassifier")
    @patch("ara_cli.artefact_autofix.extract_artefact_names_of_classifier")
    @patch("ara_cli.artefact_autofix.find_closest_name_matches")
    @patch(
        "ara_cli.artefact_autofix.ask_for_contribution_choice",
        return_value="first_match",
    )
    def test_set_closest_contribution_multiple_matches(
        self, mock_ask, mock_find, mock_extract, mock_fc, capsys
    ):
        """Prompts user when multiple close matches found."""
        mock_artefact = MagicMock()
        mock_contribution = MagicMock()
        mock_contribution.artefact_name = "test_Epic"  # Slightly different
        mock_contribution.classifier = "epic"
        mock_contribution.rule = None
        mock_artefact.contribution = mock_contribution
        mock_artefact.title = "test_userstory"
        mock_artefact._artefact_type.return_value.value = "userstory"

        mock_find.return_value = ["test_epic", "Test_Epic"]

        artefact, changed = set_closest_contribution(mock_artefact)

        mock_ask.assert_called_once()

    @patch("ara_cli.artefact_autofix.FileClassifier")
    @patch("ara_cli.artefact_autofix.extract_artefact_names_of_classifier")
    @patch("ara_cli.artefact_autofix.find_closest_name_matches", return_value=[])
    @patch(
        "ara_cli.artefact_autofix.ask_for_correct_contribution",
        return_value=("new_epic", "epic"),
    )
    def test_set_closest_contribution_no_match_user_provides(
        self, mock_ask, mock_find, mock_extract, mock_fc
    ):
        """Prompts user to provide contribution when no match found."""
        mock_artefact = MagicMock()
        mock_contribution = MagicMock()
        mock_contribution.artefact_name = "nonexistent"
        mock_contribution.classifier = "epic"
        mock_contribution.rule = None
        mock_artefact.contribution = mock_contribution
        mock_artefact.title = "test_userstory"
        mock_artefact._artefact_type.return_value.value = "userstory"

        artefact, changed = set_closest_contribution(mock_artefact)

        assert changed is True
        mock_ask.assert_called_once()


# =============================================================================
# Tests for user input handling
# =============================================================================


class TestUserInputHandling:
    """Tests for user input during autofix."""

    @patch("builtins.input", side_effect=["1"])
    def test_ask_for_contribution_choice_selects_first(self, mock_input):
        """User selects first option."""
        choices = ["option1", "option2", "option3"]
        result = ask_for_contribution_choice(choices)
        assert result == "option1"

    @patch("builtins.input", side_effect=["2"])
    def test_ask_for_contribution_choice_selects_second(self, mock_input):
        """User selects second option."""
        choices = ["option1", "option2", "option3"]
        result = ask_for_contribution_choice(choices)
        assert result == "option2"

    @patch("builtins.input", side_effect=["0"])
    def test_ask_for_contribution_choice_invalid_zero(self, mock_input, capsys):
        """Zero is invalid choice."""
        choices = ["option1", "option2"]
        result = ask_for_contribution_choice(choices)
        assert result is None

    @patch("builtins.input", side_effect=["epic my_epic_name"])
    def test_ask_for_correct_contribution_parses_input(self, mock_input):
        """Parses classifier and name from user input."""
        name, classifier = ask_for_correct_contribution()
        assert name == "my_epic_name"
        assert classifier == "epic"

    @patch("builtins.input", side_effect=[""])
    def test_ask_for_correct_contribution_empty_clears(self, mock_input):
        """Empty input results in None values."""
        name, classifier = ask_for_correct_contribution()
        assert name is None
        assert classifier is None


# =============================================================================
# Tests for rule mismatch fixes
# =============================================================================


class TestRuleFixes:
    """Tests for rule mismatch fixes."""

    @patch("ara_cli.artefact_autofix._update_rule")
    @patch("ara_cli.artefact_autofix.populate_classified_artefact_info")
    def test_fix_rule_updates_rule(self, mock_populate, mock_update):
        """Updates rule when mismatch detected."""
        mock_artefact = MagicMock()
        mock_contribution = MagicMock()
        mock_contribution.artefact_name = "parent"
        mock_contribution.classifier = "epic"
        mock_contribution.rule = "wrong rule"
        mock_artefact.contribution = mock_contribution
        mock_artefact.title = "my_artefact"
        mock_artefact.serialize.return_value = "serialized"
        mock_artefact._artefact_type.return_value.value = "userstory"

        mock_artefact_class = MagicMock()
        mock_artefact_class.deserialize.return_value = mock_artefact
        mock_populate.return_value = {"info": "data"}

        result = fix_rule(
            file_path="file.userstory",
            artefact_text="text",
            artefact_class=mock_artefact_class,
            classified_artefact_info={},
        )

        mock_update.assert_called_once()
        assert result == "serialized"


# =============================================================================
# Tests for scenario placeholder to outline conversion
# =============================================================================


class TestScenarioPlaceholderConversion:
    """Tests for converting Scenario with placeholders to Scenario Outline."""

    def test_extract_placeholders_from_scenario(self):
        """Extracts placeholder variables from scenario."""
        scenario_lines = [
            "Given the system is running with <frequency> Hz",
            "When the <role> performs an action",
            "Then the result should be <expected_result>",
        ]

        result = _extract_placeholders_from_scenario(scenario_lines)

        assert "frequency" in result
        assert "role" in result
        assert "expected_result" in result

    def test_create_examples_table(self):
        """Creates Examples table from placeholders."""
        placeholders = {"role", "frequency", "result"}
        indentation = "  "

        result = _create_examples_table(placeholders, indentation)

        assert any("Examples:" in line for line in result)
        # Check header contains placeholders
        header_line = result[1] if len(result) > 1 else ""
        assert (
            "role" in header_line
            or "frequency" in header_line
            or "result" in header_line
        )

    def test_convert_to_scenario_outline(self):
        """Converts Scenario to Scenario Outline."""
        scenario_lines = ["Scenario: Test scenario", "  Given a step"]
        placeholders = {"value"}
        indentation = ""

        result = _convert_to_scenario_outline(scenario_lines, placeholders, indentation)

        assert any("Scenario Outline:" in line for line in result)


# =============================================================================
# Tests for should_skip_issue
# =============================================================================


class TestShouldSkipIssue:
    """Tests for should_skip_issue function."""

    def test_skips_deterministic_issue_when_flag_false(self):
        """Skips deterministic issues when deterministic=False."""
        # deterministic_issue is not None means it's a deterministic issue
        result = should_skip_issue(
            deterministic_issue="Filename-Title Mismatch",
            deterministic=False,
            non_deterministic=True,
            file_path="test.feature",
        )
        assert result is True

    def test_skips_non_deterministic_when_flag_false(self):
        """Skips non-deterministic issues when non_deterministic=False."""
        # deterministic_issue=None means it's a non-deterministic issue
        result = should_skip_issue(
            deterministic_issue=None,
            deterministic=True,
            non_deterministic=False,
            file_path="test.feature",
        )
        assert result is True

    def test_does_not_skip_when_both_flags_true(self):
        """Does not skip when both flags are True."""
        result = should_skip_issue(
            deterministic_issue="Filename-Title Mismatch",
            deterministic=True,
            non_deterministic=True,
            file_path="test.feature",
        )
        assert result is False


# =============================================================================
# Tests for determine_attempt_count
# =============================================================================


class TestDetermineAttemptCount:
    """Tests for determine_attempt_count function."""

    def test_single_pass_returns_one(self):
        """Single-pass mode returns 1 attempt."""
        result = determine_attempt_count(single_pass=True, file_path="test.feature")
        assert result == 1

    def test_default_returns_three(self):
        """Default returns 3 attempts."""
        result = determine_attempt_count(single_pass=False, file_path="test.feature")
        assert result == 3


# =============================================================================
# Tests for parse_report edge cases
# =============================================================================


class TestParseReportEdgeCases:
    """Tests for parse_report edge cases."""

    def test_handles_special_characters_in_reason(self):
        """Handles special characters in reason field."""
        content = "# Artefact Check Report\n\n## feature\n- `file.feature`: Contains <placeholders> and 'quotes'\n"
        result = parse_report(content)

        assert "feature" in result
        assert len(result["feature"]) == 1
        assert "<placeholders>" in result["feature"][0][1]

    def test_handles_multiple_issues_per_classifier(self):
        """Handles multiple issues for same classifier."""
        content = """# Artefact Check Report

## feature
- `file1.feature`: Issue 1
- `file2.feature`: Issue 2
- `file3.feature`: Issue 3
"""
        result = parse_report(content)

        assert len(result["feature"]) == 3

    def test_handles_empty_reason(self):
        """Handles empty reason field."""
        content = "# Artefact Check Report\n\n## task\n- `file.task`\n"
        result = parse_report(content)

        assert "task" in result
        assert result["task"][0][1] == ""


# =============================================================================
# Tests for populate_classified_artefact_info
# =============================================================================


class TestPopulateClassifiedArtefactInfo:
    """Tests for populate_classified_artefact_info function."""

    @patch("ara_cli.artefact_autofix.FileClassifier")
    def test_returns_existing_info_when_not_force(self, mock_fc):
        """Returns existing info when force=False and info exists."""
        existing_info = {"existing": "data"}
        result = populate_classified_artefact_info(existing_info, force=False)

        assert result == existing_info
        mock_fc.assert_not_called()

    @patch("ara_cli.artefact_autofix.FileClassifier")
    def test_creates_new_info_when_none(self, mock_fc):
        """Creates new info when None provided."""
        mock_instance = mock_fc.return_value
        mock_instance.classify_files.return_value = {"new": "data"}

        result = populate_classified_artefact_info(None, force=False)

        assert result == {"new": "data"}
        mock_fc.assert_called_once()

    @patch("ara_cli.artefact_autofix.FileClassifier")
    def test_creates_new_info_when_force(self, mock_fc):
        """Creates new info when force=True even if info exists."""
        mock_instance = mock_fc.return_value
        mock_instance.classify_files.return_value = {"new": "data"}
        existing_info = {"old": "data"}

        result = populate_classified_artefact_info(existing_info, force=True)

        assert result == {"new": "data"}
        mock_fc.assert_called_once()
