import typer

from ara_cli import error_handler
from ara_cli.completers import DynamicCompleters


def register(app: typer.Typer):
    @app.command()
    def convert(
        old_classifier: str = typer.Argument(
            ...,
            help=" The classifier of the source artefact",
            autocompletion=DynamicCompleters.create_classifier_completer(),
        ),
        artefact_name: str = typer.Argument(
            ...,
            help="The name of the artefact to convert",
            autocompletion=DynamicCompleters.create_convert_source_artefact_name_completer(),
        ),
        new_classifier: str = typer.Argument(
            ...,
            help="The target classifier",
            autocompletion=DynamicCompleters.create_classifier_completer(),
        ),
        merge: bool = typer.Option(
            False, "--merge", help="Merge with existing artefact if it exists"
        ),
        override: bool = typer.Option(
            False, "--override", help="Override existing artefact if it exists"
        ),
    ):
        """
        Convert an existing artefact from one classifier to another.
        """
        try:
            from ara_cli.artefact_converter import AraArtefactConverter

            converter = AraArtefactConverter()
            converter.convert(
                old_classifier, artefact_name, new_classifier, merge, override
            )
        except Exception as e:
            error_handler.handle_error(e)
