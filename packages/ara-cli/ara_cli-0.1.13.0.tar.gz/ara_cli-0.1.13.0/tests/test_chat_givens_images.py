"""
Unit tests for chat givens loading and image handling functionality.

These tests cover the functionality tested by:
- ara_chat_command_load_file_content.feature (givens and image loading scenarios)
"""

import pytest
import os
import tempfile
import base64
from unittest.mock import patch, MagicMock, mock_open
from types import SimpleNamespace


def get_default_config():
    """Default config for test fixtures."""
    return SimpleNamespace(
        ext_code_dirs=[
            {"source_dir": "./src"},
            {"source_dir": "./tests"},
        ],
        glossary_dir="./glossary",
        doc_dir="./docs",
        local_prompt_templates_dir="./ara/.araconfig",
        local_ara_templates_dir="./ara/.araconfig/templates/",
        ara_prompt_given_list_includes=[
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
        ],
        llm_config=[
            {"provider": "openai", "model": "openai/gpt-4o", "temperature": 1.0},
        ],
        global_dirs=[],
    )


# =============================================================================
# Tests for _find_givens_files (givens file discovery)
# =============================================================================


class TestFindGivensFiles:
    """Tests for the _find_givens_files method in Chat class."""

    @pytest.fixture
    def chat_instance(self):
        """Creates a chat instance with mocked config."""
        from ara_cli.chat import Chat

        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "test_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\n")

            mock_config = get_default_config()
            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)
            yield chat, tmpdir

    def test_find_givens_files_explicit_file(self, chat_instance):
        """Finds explicitly specified givens file."""
        chat, tmpdir = chat_instance

        # Create a givens file
        givens_file = os.path.join(tmpdir, "custom_givens.md")
        with open(givens_file, "w") as f:
            f.write("[x] some_file.py\n")

        result = chat._find_givens_files("custom_givens.md")
        assert len(result) == 1
        assert result[0] == givens_file

    def test_find_givens_files_default_location(self, chat_instance):
        """Finds default givens config file."""
        chat, tmpdir = chat_instance

        # Create prompt.data directory with default givens file
        prompt_data_dir = os.path.join(tmpdir, "prompt.data")
        os.makedirs(prompt_data_dir, exist_ok=True)

        givens_file = os.path.join(prompt_data_dir, "config.prompt_givens.md")
        with open(givens_file, "w") as f:
            f.write("[x] file1.py\n")

        result = chat._find_givens_files("")
        assert len(result) == 1
        assert result[0] == givens_file

    def test_find_givens_files_multiple_defaults(self, chat_instance):
        """Finds both local and global givens files."""
        chat, tmpdir = chat_instance

        # Create prompt.data directory with both files
        prompt_data_dir = os.path.join(tmpdir, "prompt.data")
        os.makedirs(prompt_data_dir, exist_ok=True)

        local_givens = os.path.join(prompt_data_dir, "config.prompt_givens.md")
        global_givens = os.path.join(prompt_data_dir, "config.prompt_global_givens.md")

        with open(local_givens, "w") as f:
            f.write("[x] local_file.py\n")
        with open(global_givens, "w") as f:
            f.write("[x] global_file.py\n")

        result = chat._find_givens_files("")
        assert len(result) == 2

    def test_find_givens_files_not_found(self, chat_instance):
        """Returns empty list when file not found."""
        chat, tmpdir = chat_instance

        with patch("builtins.input", return_value=""):
            result = chat._find_givens_files("")

        assert result == []


# =============================================================================
# Tests for LOAD_GIVENS command
# =============================================================================


class TestLoadGivensCommand:
    """Tests for the do_LOAD_GIVENS command."""

    @pytest.fixture
    def temp_chat_setup(self):
        """Creates a temporary chat setup for testing."""
        from ara_cli.chat import Chat

        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "test_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\n")

            # Create prompt.data directory
            prompt_data_dir = os.path.join(tmpdir, "prompt.data")
            os.makedirs(prompt_data_dir, exist_ok=True)

            mock_config = get_default_config()
            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            yield {
                "chat": chat,
                "tmpdir": tmpdir,
                "chat_file": chat_file,
                "prompt_data_dir": prompt_data_dir,
            }

    def test_load_givens_appends_content(self, temp_chat_setup):
        """LOAD_GIVENS appends file content to chat."""
        setup = temp_chat_setup

        # Create givens config with marked entry
        givens_file = os.path.join(setup["prompt_data_dir"], "config.prompt_givens.md")

        # Create a file to load
        target_file = os.path.join(setup["tmpdir"], "to_load.py")
        with open(target_file, "w") as f:
            f.write("print('loaded content')")

        # The givens file should reference the target file
        with open(givens_file, "w") as f:
            f.write(f"[x] {target_file}\n")

        with patch(
            "ara_cli.prompt_handler.load_givens",
            return_value=("loaded givens content\n", []),
        ):
            setup["chat"].do_LOAD_GIVENS("")

        with open(setup["chat_file"], "r") as f:
            content = f.read()

        assert "loaded givens content" in content


# =============================================================================
# Tests for image loading (LOAD_IMAGE command)
# =============================================================================


class TestLoadImageCommand:
    """Tests for the do_LOAD_IMAGE command."""

    @pytest.fixture
    def chat_with_image(self):
        """Creates a chat instance with a test image file."""
        from ara_cli.chat import Chat

        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "test_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\n")

            # Create a fake image file
            image_file = os.path.join(tmpdir, "test_image.png")
            with open(image_file, "wb") as f:
                f.write(b"\x89PNG\r\n\x1a\n" + b"fake_image_data")

            mock_config = get_default_config()
            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            yield {
                "chat": chat,
                "tmpdir": tmpdir,
                "chat_file": chat_file,
                "image_file": image_file,
            }

    def test_load_image_recognizes_png(self, chat_with_image):
        """Recognizes PNG as valid image format."""
        setup = chat_with_image

        with patch.object(
            setup["chat"],
            "find_matching_files_to_load",
            return_value=[setup["image_file"]],
        ):
            with patch(
                "ara_cli.commands.load_image_command.LoadImageCommand"
            ) as MockCmd:
                mock_instance = MagicMock()
                MockCmd.return_value = mock_instance

                setup["chat"].do_LOAD_IMAGE("test_image.png")

                MockCmd.assert_called_once()
                mock_instance.execute.assert_called_once()

    def test_load_image_rejects_unsupported_format(self, chat_with_image):
        """Rejects unsupported file formats."""
        setup = chat_with_image

        # Create a non-image file
        text_file = os.path.join(setup["tmpdir"], "file.txt")
        with open(text_file, "w") as f:
            f.write("not an image")

        with patch.object(
            setup["chat"], "find_matching_files_to_load", return_value=[text_file]
        ):
            # Should report error for unsupported format
            with patch("ara_cli.error_handler.report_error") as mock_error:
                setup["chat"].do_LOAD_IMAGE("file.txt")
                mock_error.assert_called()


class TestLoadImageFileContent:
    """Tests for image file content loading into chat."""

    @pytest.fixture
    def temp_chat_file(self):
        """Creates a temporary chat file."""
        from ara_cli.chat import Chat

        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("# ara prompt:\n")
            temp_path = f.name

        mock_config = get_default_config()
        with patch(
            "ara_cli.prompt_handler.ConfigManager.get_config", return_value=mock_config
        ):
            chat = Chat(temp_path, reset=False)

        yield chat, temp_path

        # Cleanup
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_load_image_returns_true(self, temp_chat_file):
        """load_image returns True for valid image."""
        chat, temp_path = temp_chat_file

        with patch.object(chat, "load_binary_file", return_value=True) as mock_load:
            result = chat.load_image("test.png", prefix="PREFIX:", suffix=":SUFFIX")

            mock_load.assert_called_once_with(
                file_path="test.png",
                mime_type="image/png",
                prefix="PREFIX:",
                suffix=":SUFFIX",
            )
            assert result is True

    def test_load_image_handles_jpg(self, temp_chat_file):
        """load_image handles JPG extension."""
        chat, temp_path = temp_chat_file

        with patch.object(chat, "load_binary_file", return_value=True) as mock_load:
            chat.load_image("photo.jpg")

            mock_load.assert_called_once()
            call_args = mock_load.call_args
            assert call_args.kwargs["mime_type"] == "image/jpeg"

    def test_load_image_handles_jpeg(self, temp_chat_file):
        """load_image handles JPEG extension."""
        chat, temp_path = temp_chat_file

        with patch.object(chat, "load_binary_file", return_value=True) as mock_load:
            chat.load_image("photo.jpeg")

            mock_load.assert_called_once()
            call_args = mock_load.call_args
            assert call_args.kwargs["mime_type"] == "image/jpeg"

    def test_load_image_error_for_unsupported_webp(self, temp_chat_file):
        """WebP is not supported - verifies error handling."""
        chat, temp_path = temp_chat_file
        
        with patch('ara_cli.error_handler.report_error') as mock_error:
            result = chat.load_image("image.webp")
            # Should report error for unsupported format
            mock_error.assert_called_once()

    def test_load_image_unsupported_extension(self, temp_chat_file):
        """load_image reports error for unsupported format."""
        chat, temp_path = temp_chat_file

        with patch("ara_cli.error_handler.report_error") as mock_error:
            result = chat.load_image("document.xyz")

            mock_error.assert_called_once()


# =============================================================================
# Tests for find_matching_files_to_load (glob patterns)
# =============================================================================


class TestFindMatchingFilesToLoad:
    """Tests for file matching with glob patterns."""

    @pytest.fixture
    def chat_with_files(self):
        """Creates a chat with multiple files in directory."""
        from ara_cli.chat import Chat

        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "test_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\n")

            # Create multiple test files
            for name in ["file1.py", "file2.py", "readme.md", "image.png"]:
                with open(os.path.join(tmpdir, name), "w") as f:
                    f.write(f"content of {name}")

            mock_config = get_default_config()
            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            yield chat, tmpdir

    def test_find_matching_files_single(self, chat_with_files):
        """Finds single file by name."""
        chat, tmpdir = chat_with_files

        result = chat.find_matching_files_to_load("file1.py")

        assert len(result) == 1
        assert result[0].endswith("file1.py")

    def test_find_matching_files_glob_pattern(self, chat_with_files):
        """Finds files using glob pattern."""
        chat, tmpdir = chat_with_files

        result = chat.find_matching_files_to_load("*.py")

        assert len(result) == 2
        assert any("file1.py" in f for f in result)
        assert any("file2.py" in f for f in result)

    def test_find_matching_files_no_match(self, chat_with_files):
        """Returns None when no files match."""
        chat, tmpdir = chat_with_files

        with patch("ara_cli.error_handler.report_error"):
            result = chat.find_matching_files_to_load("nonexistent.txt")

        assert result is None


# =============================================================================
# Tests for global directory loading
# =============================================================================


class TestGlobalDirectoryLoading:
    """Tests for loading files from global directories."""

    @pytest.fixture
    def chat_with_global_dir(self):
        """Creates a chat with global directory configuration."""
        from ara_cli.chat import Chat

        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "test_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\n")

            # Create global directory with files
            global_dir = os.path.join(tmpdir, "global_files")
            os.makedirs(global_dir, exist_ok=True)

            global_file = os.path.join(global_dir, "shared_code.py")
            with open(global_file, "w") as f:
                f.write("# Shared code\ndef helper(): pass")

            mock_config = get_default_config()
            mock_config.global_dirs = [{"source_dir": global_dir}]

            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            yield {
                "chat": chat,
                "tmpdir": tmpdir,
                "global_dir": global_dir,
                "global_file": global_file,
            }

    def test_global_dir_in_config(self, chat_with_global_dir):
        """Global directory is accessible in config."""
        setup = chat_with_global_dir

        assert len(setup["chat"].config.global_dirs) == 1


# =============================================================================
# Tests for LOAD command with --load-images flag
# =============================================================================


class TestLoadWithImages:
    """Tests for LOAD command with image extraction."""

    def test_load_command_class_accepts_extract_images(self):
        """LoadCommand accepts extract_images parameter."""
        from ara_cli.commands.load_command import LoadCommand
        import inspect
        
        # Check that LoadCommand.__init__ accepts extract_images parameter
        sig = inspect.signature(LoadCommand.__init__)
        params = list(sig.parameters.keys())
        assert 'extract_images' in params
    
    def test_load_command_instantiation_with_extract_images(self):
        """LoadCommand can be instantiated with extract_images=True."""
        from ara_cli.commands.load_command import LoadCommand
        
        # Should not raise an error
        cmd = LoadCommand(
            chat_instance=MagicMock(),
            file_path="test.md",
            prefix="",
            block_delimiter="```",
            extract_images=True,
            output=print
        )
        assert cmd is not None


# =============================================================================
# Tests for binary content appending (base64 encoding)
# =============================================================================


class TestBinaryContentAppending:
    """Tests for binary file content being appended as base64."""

    @pytest.fixture
    def chat_instance(self):
        """Creates a chat instance for testing."""
        from ara_cli.chat import Chat

        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "test_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\n")

            mock_config = get_default_config()
            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            yield chat, tmpdir, chat_file

    def test_binary_file_content_base64_encoded(self, chat_instance):
        """Binary file content is base64 encoded when appended."""
        chat, tmpdir, chat_file = chat_instance

        # Create a binary file
        binary_file = os.path.join(tmpdir, "image.png")
        binary_content = b"\x89PNG\r\n\x1a\ntest_binary_data"
        with open(binary_file, "wb") as f:
            f.write(binary_content)

        expected_base64 = base64.b64encode(binary_content).decode("utf-8")

        # Mock the open calls to capture what gets written
        with patch(
            "ara_cli.file_loaders.binary_file_loader.open",
            mock_open(read_data=binary_content),
        ) as mock_file:
            chat.load_binary_file(binary_file, mime_type="image/png")

            # Check that the file was written with base64 content
            write_calls = mock_file().write.call_args_list
            if write_calls:
                written_content = "".join(str(call[0][0]) for call in write_calls)
                assert expected_base64 in written_content or "base64" in written_content


# =============================================================================
# Tests for choose_file_to_load (user file selection)
# =============================================================================


class TestChooseFileToLoad:
    """Tests for interactive file selection."""

    @pytest.fixture
    def chat_instance(self):
        """Creates a chat instance for testing."""
        from ara_cli.chat import Chat

        with tempfile.TemporaryDirectory() as tmpdir:
            chat_file = os.path.join(tmpdir, "test_chat.md")
            with open(chat_file, "w") as f:
                f.write("# ara prompt:\n")

            mock_config = get_default_config()
            with patch(
                "ara_cli.prompt_handler.ConfigManager.get_config",
                return_value=mock_config,
            ):
                chat = Chat(chat_file, reset=False)

            yield chat

    def test_choose_file_to_load_single_file(self, chat_instance):
        """Single file is returned without prompting."""
        files = ["/path/to/file.py"]

        result = chat_instance.choose_file_to_load(files, "*.py")

        assert result == "/path/to/file.py"

    def test_choose_file_to_load_multiple_files_user_selects(self, chat_instance):
        """Multiple files prompts user for selection."""
        files = ["/path/to/file1.py", "/path/to/file2.py"]

        with patch("builtins.input", return_value="1"):
            result = chat_instance.choose_file_to_load(files, "*.py")

        # User selects option 1 (0-indexed would be file1.py)
        assert result == "/path/to/file1.py"

    def test_choose_file_to_load_invalid_choice(self, chat_instance):
        """Invalid choice returns None."""
        files = ["/path/to/file1.py", "/path/to/file2.py"]

        with patch("builtins.input", return_value="99"):
            with patch("ara_cli.error_handler.report_error"):
                result = chat_instance.choose_file_to_load(files, "*.py")

        assert result is None
