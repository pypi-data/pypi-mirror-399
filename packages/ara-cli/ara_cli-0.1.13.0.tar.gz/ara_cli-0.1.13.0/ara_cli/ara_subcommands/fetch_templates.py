import typer


def register(app: typer.Typer):
    @app.command(
        name="fetch-templates",
        help="Fetch global prompt templates into your config directory.",
        deprecated=True,
    )
    def fetch_templates():
        from ara_cli.commands.fetch_templates_command import FetchTemplatesCommand

        typer.secho(
            "WARNING: 'fetch-templates' is deprecated. Please use 'ara fetch --templates' or just 'ara fetch' instead.",
            fg=typer.colors.YELLOW,
            err=True,
        )
        command = FetchTemplatesCommand()
        command.execute()
