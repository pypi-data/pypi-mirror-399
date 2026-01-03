import typer


def register(app: typer.Typer):
    @app.command(
        name="fetch-scripts",
        help="Fetch global scripts into your config directory.",
        deprecated=True,
    )
    def fetch_scripts():
        from ara_cli.commands.fetch_scripts_command import FetchScriptsCommand

        typer.secho(
            "WARNING: 'fetch-scripts' is deprecated. Please use 'ara fetch --scripts' or just 'ara fetch' instead.",
            fg=typer.colors.YELLOW,
            err=True,
        )
        command = FetchScriptsCommand()
        command.execute()
