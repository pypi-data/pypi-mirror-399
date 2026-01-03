import os
from typing import List, Optional
from pathlib import Path
import typer

from ara_cli.classifier import Classifier
from ara_cli.constants import VALID_ASPECTS


def complete_classifier(incomplete: str) -> List[str]:
    """Complete classifier names."""
    return [c for c in Classifier.ordered_classifiers() if c.startswith(incomplete)]


def complete_aspect(incomplete: str) -> List[str]:
    """Complete aspect names."""
    aspects = VALID_ASPECTS
    return [a for a in aspects if a.startswith(incomplete)]


def complete_status(incomplete: str) -> List[str]:
    """Complete task status values."""
    statuses = ["to-do", "in-progress", "review", "done", "closed"]
    return [s for s in statuses if s.startswith(incomplete)]


def complete_template_type(incomplete: str) -> List[str]:
    """Complete template type values."""
    template_types = ["rules", "intention", "commands", "blueprint"]
    return [t for t in template_types if t.startswith(incomplete)]


def complete_artefact_name(classifier: str, incomplete: str = "") -> List[str]:
    """Complete artefact names for a given classifier."""
    try:
        # Get the directory for the classifier
        classifier_dir = f"ara/{Classifier.get_sub_directory(classifier)}"

        if not os.path.exists(classifier_dir):
            return []

        # Find all files with the classifier extension
        artefacts = []
        suffix = f".{classifier}"

        # We only care about files that match the incomplete prefix AND the suffix
        # Since os.listdir gives filenames, we can check startswith(incomplete)
        # but we must be careful because the file starts with the artefact name, not necessarily the incomplete part + suffix directly unless full match.
        # Actually, incomplete corresponds to the artefact name part.
        # So file must start with incomplete AND end with suffix.

        for file in os.listdir(classifier_dir):
            if file.startswith(incomplete) and file.endswith(suffix):
                # Remove the extension to get the artefact name
                name = file[: -len(suffix)]
                artefacts.append(name)

        return sorted(artefacts)
    except Exception:
        return []


def complete_artefact_name_for_classifier(classifier: str):
    """Create a completer function for artefact names of a specific classifier."""

    def completer(incomplete: str) -> List[str]:
        return complete_artefact_name(classifier, incomplete)

    return completer


def complete_chat_files(incomplete: str) -> List[str]:
    """Complete chat file names (without .md extension)."""
    try:
        chat_files = []
        current_dir = Path.cwd()

        # Optimize by using glob with the incomplete prefix
        # Note: glob pattern needs to be careful with special chars, but for autocompletion usually fine.
        pattern = f"{incomplete}*.md" if incomplete else "*.md"

        for file in current_dir.glob(pattern):
            chat_files.append(file.stem)

        return sorted(chat_files)
    except Exception:
        return []


# Dynamic completers that need context
class DynamicCompleters:
    @staticmethod
    def create_classifier_completer():
        """Create a completer for classifiers."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            return complete_classifier(incomplete)

        return completer

    @staticmethod
    def create_aspect_completer():
        """Create a completer for aspects."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            return complete_aspect(incomplete)

        return completer

    @staticmethod
    def create_status_completer():
        """Create a completer for status values."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            return complete_status(incomplete)

        return completer

    @staticmethod
    def create_template_type_completer():
        """Create a completer for template types."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            return complete_template_type(incomplete)

        return completer

    @staticmethod
    def create_artefact_name_completer():
        """Create a completer for artefact names based on classifier context."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            # Try to get classifier from context
            if hasattr(ctx, "params") and "classifier" in ctx.params:
                classifier = ctx.params["classifier"]
                if hasattr(classifier, "value"):
                    classifier = classifier.value
                return complete_artefact_name(classifier, incomplete)
            return []

        return completer

    @staticmethod
    def create_parent_name_completer():
        """Create a completer for parent artefact names based on parent classifier context."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            # Try to get parent_classifier from context
            if hasattr(ctx, "params") and "parent_classifier" in ctx.params:
                parent_classifier = ctx.params["parent_classifier"]
                if hasattr(parent_classifier, "value"):
                    parent_classifier = parent_classifier.value
                return complete_artefact_name(parent_classifier, incomplete)
            return []

        return completer

    @staticmethod
    def create_chat_file_completer():
        """Create a completer for chat files."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            return complete_chat_files(incomplete)

        return completer

    @staticmethod
    def create_convert_source_artefact_name_completer():
        """Create a completer for convert command source artefact names based on old_classifier context."""

        def completer(ctx: typer.Context, incomplete: str) -> List[str]:
            # Try to get old_classifier from context
            if hasattr(ctx, "params") and "old_classifier" in ctx.params:
                old_classifier = ctx.params["old_classifier"]
                if hasattr(old_classifier, "value"):
                    old_classifier = old_classifier.value
                return complete_artefact_name(old_classifier, incomplete)
            return []

        return completer
