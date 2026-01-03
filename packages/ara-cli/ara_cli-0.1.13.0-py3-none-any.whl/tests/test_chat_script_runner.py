"""
Unit tests for chat_script_runner modules.

Provides full test coverage for:
- script_completer.py
- script_finder.py
- script_lister.py
- script_runner.py
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from ara_cli.chat_script_runner.script_completer import ScriptCompleter
from ara_cli.chat_script_runner.script_finder import ScriptFinder
from ara_cli.chat_script_runner.script_lister import ScriptLister
from ara_cli.chat_script_runner.script_runner import ScriptRunner


# =============================================================================
# Tests for ScriptFinder
# =============================================================================


class TestScriptFinder:
    """Tests for ScriptFinder class."""

    @patch("ara_cli.chat_script_runner.script_finder.ConfigManager.get_config")
    def test_get_custom_scripts_dir(self, mock_get_config):
        """Returns custom scripts directory path."""
        mock_config = MagicMock()
        mock_config.local_prompt_templates_dir = "/path/to/templates"
        mock_get_config.return_value = mock_config

        finder = ScriptFinder()
        result = finder.get_custom_scripts_dir()

        assert result == os.path.join("/path/to/templates", "custom-scripts")

    @patch("ara_cli.chat_script_runner.script_finder.ConfigManager.get_config")
    def test_get_global_scripts_dir(self, mock_get_config):
        """Returns global scripts directory path."""
        mock_config = MagicMock()
        mock_config.local_prompt_templates_dir = "/path/to/templates"
        mock_get_config.return_value = mock_config

        finder = ScriptFinder()
        result = finder.get_global_scripts_dir()

        assert result == os.path.join("/path/to/templates", "global-scripts")

    @patch("ara_cli.chat_script_runner.script_finder.ConfigManager.get_config")
    @patch("os.path.exists")
    def test_find_script_with_global_prefix(self, mock_exists, mock_get_config):
        """Finds script with global/ prefix."""
        mock_config = MagicMock()
        mock_config.local_prompt_templates_dir = "/templates"
        mock_get_config.return_value = mock_config
        mock_exists.return_value = True

        finder = ScriptFinder()
        result = finder.find_script("global/test.py")

        expected_path = os.path.join("/templates", "global-scripts", "test.py")
        assert result == expected_path

    @patch("ara_cli.chat_script_runner.script_finder.ConfigManager.get_config")
    @patch("os.path.exists")
    def test_find_script_in_custom_first(self, mock_exists, mock_get_config):
        """Finds script in custom-scripts first."""
        mock_config = MagicMock()
        mock_config.local_prompt_templates_dir = "/templates"
        mock_get_config.return_value = mock_config

        # Custom script exists
        def exists_side_effect(path):
            return "custom-scripts" in path

        mock_exists.side_effect = exists_side_effect

        finder = ScriptFinder()
        result = finder.find_script("test.py")

        assert "custom-scripts" in result

    @patch("ara_cli.chat_script_runner.script_finder.ConfigManager.get_config")
    @patch("os.path.exists")
    def test_find_script_falls_back_to_global(self, mock_exists, mock_get_config):
        """Falls back to global-scripts when not in custom."""
        mock_config = MagicMock()
        mock_config.local_prompt_templates_dir = "/templates"
        mock_get_config.return_value = mock_config

        # Only global script exists
        def exists_side_effect(path):
            return "global-scripts" in path

        mock_exists.side_effect = exists_side_effect

        finder = ScriptFinder()
        result = finder.find_script("test.py")

        assert "global-scripts" in result

    @patch("ara_cli.chat_script_runner.script_finder.ConfigManager.get_config")
    @patch("os.path.exists", return_value=False)
    def test_find_script_returns_none_when_not_found(
        self, mock_exists, mock_get_config
    ):
        """Returns None when script not found."""
        mock_config = MagicMock()
        mock_config.local_prompt_templates_dir = "/templates"
        mock_get_config.return_value = mock_config

        finder = ScriptFinder()
        result = finder.find_script("nonexistent.py")

        assert result is None


# =============================================================================
# Tests for ScriptLister
# =============================================================================


class TestScriptLister:
    """Tests for ScriptLister class."""

    @patch("ara_cli.chat_script_runner.script_lister.ScriptFinder")
    @patch("os.path.isdir", return_value=True)
    @patch("glob.glob")
    def test_get_custom_scripts(self, mock_glob, mock_isdir, mock_finder_class):
        """Returns list of custom script basenames."""
        mock_finder = MagicMock()
        mock_finder.get_custom_scripts_dir.return_value = "/templates/custom-scripts"
        mock_finder_class.return_value = mock_finder
        mock_glob.return_value = [
            "/templates/custom-scripts/script1.py",
            "/templates/custom-scripts/script2.py",
        ]

        lister = ScriptLister()
        result = lister.get_custom_scripts()

        assert result == ["script1.py", "script2.py"]

    @patch("ara_cli.chat_script_runner.script_lister.ScriptFinder")
    @patch("os.path.isdir", return_value=True)
    @patch("glob.glob")
    def test_get_global_scripts(self, mock_glob, mock_isdir, mock_finder_class):
        """Returns list of global script basenames."""
        mock_finder = MagicMock()
        mock_finder.get_global_scripts_dir.return_value = "/templates/global-scripts"
        mock_finder_class.return_value = mock_finder
        mock_glob.return_value = ["/templates/global-scripts/global1.py"]

        lister = ScriptLister()
        result = lister.get_global_scripts()

        assert result == ["global1.py"]

    @patch("ara_cli.chat_script_runner.script_lister.ScriptFinder")
    @patch("os.path.isdir", return_value=False)
    def test_get_custom_scripts_returns_empty_when_dir_not_exists(
        self, mock_isdir, mock_finder_class
    ):
        """Returns empty list when custom scripts dir doesn't exist."""
        mock_finder = MagicMock()
        mock_finder.get_custom_scripts_dir.return_value = "/nonexistent"
        mock_finder_class.return_value = mock_finder

        lister = ScriptLister()
        result = lister.get_custom_scripts()

        assert result == []

    @patch("ara_cli.chat_script_runner.script_lister.ScriptFinder")
    @patch("os.path.isdir", return_value=True)
    @patch("glob.glob")
    def test_get_all_scripts_combines_and_prefixes(
        self, mock_glob, mock_isdir, mock_finder_class
    ):
        """Combines custom and global scripts with global/ prefix."""
        mock_finder = MagicMock()
        mock_finder.get_custom_scripts_dir.return_value = "/templates/custom-scripts"
        mock_finder.get_global_scripts_dir.return_value = "/templates/global-scripts"
        mock_finder_class.return_value = mock_finder

        def glob_side_effect(pattern):
            if "custom" in pattern:
                return ["/templates/custom-scripts/custom.py"]
            return ["/templates/global-scripts/global.py"]

        mock_glob.side_effect = glob_side_effect

        lister = ScriptLister()
        result = lister.get_all_scripts()

        assert "custom.py" in result
        assert "global.py" in result
        assert "global/global.py" in result


# =============================================================================
# Tests for ScriptRunner
# =============================================================================


class TestScriptRunner:
    """Tests for ScriptRunner class."""

    @patch("ara_cli.chat_script_runner.script_runner.ScriptFinder")
    @patch("ara_cli.chat_script_runner.script_runner.ScriptLister")
    def test_run_script_returns_error_when_not_found(
        self, mock_lister, mock_finder_class
    ):
        """Returns error message when script not found."""
        mock_finder = MagicMock()
        mock_finder.find_script.return_value = None
        mock_finder_class.return_value = mock_finder

        runner = ScriptRunner(chat_instance=MagicMock())
        result = runner.run_script("nonexistent.py")

        assert "not found" in result

    @patch("ara_cli.chat_script_runner.script_runner.ScriptFinder")
    @patch("ara_cli.chat_script_runner.script_runner.ScriptLister")
    @patch("subprocess.run")
    def test_run_script_returns_stdout_on_success(
        self, mock_run, mock_lister, mock_finder_class
    ):
        """Returns stdout when script runs successfully."""
        mock_finder = MagicMock()
        mock_finder.find_script.return_value = "/path/to/script.py"
        mock_finder_class.return_value = mock_finder

        mock_result = MagicMock()
        mock_result.stdout = "Script output"
        mock_run.return_value = mock_result

        runner = ScriptRunner(chat_instance=MagicMock())
        result = runner.run_script("script.py")

        assert result == "Script output"

    @patch("ara_cli.chat_script_runner.script_runner.ScriptFinder")
    @patch("ara_cli.chat_script_runner.script_runner.ScriptLister")
    @patch("subprocess.run")
    def test_run_script_returns_error_on_failure(
        self, mock_run, mock_lister, mock_finder_class
    ):
        """Returns error message when script fails."""
        import subprocess

        mock_finder = MagicMock()
        mock_finder.find_script.return_value = "/path/to/script.py"
        mock_finder_class.return_value = mock_finder

        mock_run.side_effect = subprocess.CalledProcessError(
            1, "python", stderr="Error details"
        )

        runner = ScriptRunner(chat_instance=MagicMock())
        result = runner.run_script("script.py")

        assert "Error running script" in result

    @patch("ara_cli.chat_script_runner.script_runner.ScriptFinder")
    @patch("ara_cli.chat_script_runner.script_runner.ScriptLister")
    def test_get_available_scripts(self, mock_lister_class, mock_finder):
        """Returns all available scripts."""
        mock_lister = MagicMock()
        mock_lister.get_all_scripts.return_value = ["script1.py", "script2.py"]
        mock_lister_class.return_value = mock_lister

        runner = ScriptRunner(chat_instance=MagicMock())
        result = runner.get_available_scripts()

        assert result == ["script1.py", "script2.py"]

    @patch("ara_cli.chat_script_runner.script_runner.ScriptFinder")
    @patch("ara_cli.chat_script_runner.script_runner.ScriptLister")
    def test_get_global_scripts(self, mock_lister_class, mock_finder):
        """Returns global scripts."""
        mock_lister = MagicMock()
        mock_lister.get_global_scripts.return_value = ["global.py"]
        mock_lister_class.return_value = mock_lister

        runner = ScriptRunner(chat_instance=MagicMock())
        result = runner.get_global_scripts()

        assert result == ["global.py"]


# =============================================================================
# Tests for ScriptCompleter
# =============================================================================


class TestScriptCompleter:
    """Tests for ScriptCompleter class."""

    @patch("ara_cli.chat_script_runner.script_completer.ScriptLister")
    def test_completes_all_scripts_by_default(self, mock_lister_class):
        """Returns all scripts when not global prefix."""
        mock_lister = MagicMock()
        mock_lister.get_all_scripts.return_value = [
            "script1.py",
            "script2.py",
            "global/test.py",
        ]
        mock_lister_class.return_value = mock_lister

        completer = ScriptCompleter()
        result = completer("", "rpy ", 4, 4)

        assert "script1.py" in result
        assert "script2.py" in result

    @patch("ara_cli.chat_script_runner.script_completer.ScriptLister")
    def test_filters_scripts_by_prefix(self, mock_lister_class):
        """Filters scripts by text prefix."""
        mock_lister = MagicMock()
        mock_lister.get_all_scripts.return_value = [
            "script1.py",
            "script2.py",
            "other.py",
        ]
        mock_lister_class.return_value = mock_lister

        completer = ScriptCompleter()
        result = completer("script", "rpy script", 4, 10)

        assert "script1.py" in result
        assert "script2.py" in result
        assert "other.py" not in result

    @patch("ara_cli.chat_script_runner.script_completer.ScriptLister")
    def test_completes_global_scripts_with_prefix(self, mock_lister_class):
        """Returns only global scripts when using global/ prefix."""
        mock_lister = MagicMock()
        mock_lister.get_global_scripts.return_value = ["global1.py", "global2.py"]
        mock_lister_class.return_value = mock_lister

        completer = ScriptCompleter()
        result = completer("", "rpy global/", 11, 11)

        assert "global1.py" in result
        assert "global2.py" in result

    @patch("ara_cli.chat_script_runner.script_completer.ScriptLister")
    def test_returns_all_when_text_empty(self, mock_lister_class):
        """Returns all scripts when text is empty."""
        mock_lister = MagicMock()
        mock_lister.get_all_scripts.return_value = ["a.py", "b.py"]
        mock_lister_class.return_value = mock_lister

        completer = ScriptCompleter()
        result = completer("", "rpy ", 4, 4)

        assert result == ["a.py", "b.py"]
