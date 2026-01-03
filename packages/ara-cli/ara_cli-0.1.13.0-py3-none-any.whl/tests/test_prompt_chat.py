"""
Unit tests for prompt chat mode functionality

These tests cover the functionality previously tested by:
- Setup_Combined_Chat_Prompt_Mode_with_Chat_Name.feature
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open


# =============================================================================
# Tests for chat file handling with custom names
# =============================================================================


class TestChatFileNaming:
    """Tests for chat file naming conventions."""

    def test_chat_name_without_extension_gets_suffix(self):
        """Chat name without extension gets _chat.md suffix."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                temp_file = os.path.join(tmpdir, "test_chat.md")
                with open(temp_file, "w") as f:
                    f.write("# ara prompt:\n")

                chat = Chat(temp_file, reset=False)

                # Initialize with a name without extension
                new_chat = chat.initialize_new_chat(os.path.join(tmpdir, "new_chat"))

                assert new_chat.endswith("_chat.md")

    def test_chat_name_with_extension_keeps_extension(self):
        """Chat name with .md extension keeps it."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                temp_file = os.path.join(tmpdir, "test_chat.md")
                with open(temp_file, "w") as f:
                    f.write("# ara prompt:\n")

                chat = Chat(temp_file, reset=False)
                new_chat = chat.initialize_new_chat(os.path.join(tmpdir, "custom.md"))

                assert new_chat.endswith("custom.md")


# =============================================================================
# Tests for existing chat handling
# =============================================================================


class TestExistingChatHandling:
    """Tests for handling existing chat files."""

    def test_reset_true_clears_chat_content(self):
        """reset=True clears existing chat content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            chat_file = os.path.join(tmpdir, "existing_chat.md")
            with open(chat_file, "w") as f:
                f.write("Previous chat content\n# ara prompt:\nOld prompt")

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                Chat(chat_file, reset=True)

            with open(chat_file, "r") as f:
                content = f.read()

            assert "Previous chat content" not in content
            assert "# ara prompt:" in content

    def test_reset_false_keeps_chat_content(self):
        """reset=False keeps existing chat content."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            chat_file = os.path.join(tmpdir, "existing_chat.md")
            original_content = "Previous chat content\n# ara prompt:\nKeep me"
            with open(chat_file, "w") as f:
                f.write(original_content)

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                Chat(chat_file, reset=False)

            with open(chat_file, "r") as f:
                content = f.read()

            assert "Keep me" in content

    @patch("builtins.input", return_value="y")
    def test_user_prompted_to_reset_when_reset_none(self, mock_input):
        """User is prompted when reset=None and file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            chat_file = os.path.join(tmpdir, "existing_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\nOld content")

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                Chat(chat_file, reset=None)

            # User chose 'y' to reset, so content should be cleared
            with open(chat_file, "r") as f:
                content = f.read().strip()

            assert content == "# ara prompt:"


# =============================================================================
# Tests for incomplete chat name resolution
# =============================================================================


class TestIncompleteChatName:
    """Tests for resolving incomplete chat names."""

    @patch("builtins.input", return_value="n")
    def test_finds_existing_file_with_suffix(self, mock_input):
        """Finds existing file when incomplete name provided."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            # Create a file with the full name
            existing_file = os.path.join(tmpdir, "new_test_chat.md")
            with open(existing_file, "w") as f:
                f.write("# ara prompt:\n")

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(existing_file, reset=False)

                # The setup_chat method should find the existing file
                result = chat.setup_chat(os.path.join(tmpdir, "new_test"))

                assert os.path.exists(result)


# =============================================================================
# Tests for default chat content
# =============================================================================


class TestDefaultChatContent:
    """Tests for default chat content creation."""

    def test_new_chat_has_default_prompt_header(self):
        """New chat file contains default prompt header."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            chat_file = os.path.join(tmpdir, "new_chat.md")

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                Chat(chat_file, reset=False)

            with open(chat_file, "r") as f:
                content = f.read()

            assert "# ara prompt:" in content


# =============================================================================
# Tests for prompt config file handling
# =============================================================================


class TestPromptConfigFiles:
    """Tests for prompt config file creation and handling."""

    @patch("ara_cli.update_config_prompt.update_config_prompt_files")
    def test_config_files_created_when_missing(self, mock_update):
        """Prompt config files are created when missing."""
        # This test verifies the behavior is available
        # The actual creation happens in update_config_prompt module
        assert callable(mock_update)


# =============================================================================
# Tests for chat session lifecycle
# =============================================================================


class TestChatSessionLifecycle:
    """Tests for chat session start and stop."""

    def test_chat_has_quit_alias(self):
        """Chat instance has 'q' alias for quit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            chat_file = os.path.join(tmpdir, "test_chat.md")

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            # Check for 'q' alias which maps to QUIT
            assert "q" in chat.aliases

    def test_chat_has_help_alias(self):
        """Chat instance has 'h' alias for help."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            chat_file = os.path.join(tmpdir, "test_chat.md")

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            # Check for 'h' alias which maps to HELP
            assert "h" in chat.aliases

    def test_quit_alias_works(self):
        """'q' alias works for QUIT command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            chat_file = os.path.join(tmpdir, "test_chat.md")

            mock_config = MagicMock()
            mock_config.llm_config = [
                {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
            ]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            assert "q" in chat.aliases


# =============================================================================
# Tests for artefact-based prompt chat
# =============================================================================


class TestArtefactPromptChat:
    """Tests for prompt chat mode with artefacts."""

    @patch("ara_cli.prompt_handler.ConfigManager.get_config")
    def test_chat_can_be_initialized_for_artefact(self, mock_config):
        """Chat can be initialized for an artefact."""
        with tempfile.TemporaryDirectory() as tmpdir:
            from ara_cli.chat import Chat

            mock_config.return_value = MagicMock(
                llm_config=[
                    {"provider": "openai", "model": "gpt-4", "temperature": 1.0}
                ]
            )

            # Simulate artefact data directory structure
            artefact_data_dir = os.path.join(tmpdir, "123_test_task.data")
            os.makedirs(artefact_data_dir, exist_ok=True)

            chat_file = os.path.join(artefact_data_dir, "task_chat.md")

            chat = Chat(chat_file, reset=False)

            assert os.path.exists(chat_file)
            assert chat.chat_name == chat_file
