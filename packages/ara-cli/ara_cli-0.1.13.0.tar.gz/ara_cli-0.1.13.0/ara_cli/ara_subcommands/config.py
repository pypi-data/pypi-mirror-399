"""
Config subcommand for ara-cli.
Provides commands for managing ara configuration.
"""
import typer
import os
from typing import Optional

config_app = typer.Typer(
    help="Manage ara configuration",
    no_args_is_help=True,
)


def _show_config_status(config_path: str, current_data: dict) -> None:
    """Display current configuration status."""
    import typer
    typer.echo("Current configuration status:")
    typer.echo(f"  Config file: {config_path}")
    typer.echo(
        f"  LLM configs: {len(current_data.get('llm_config', {}))} models defined")
    typer.echo(f"  Default LLM: {current_data.get('default_llm', 'not set')}")
    typer.echo(
        f"  Extraction LLM: {current_data.get('extraction_llm', 'not set')}")
    typer.echo("")
    typer.echo("Use flags to reset specific parts:")
    typer.echo("  --all          Reset everything")
    typer.echo("  --llm-config   Reset LLM configurations")
    typer.echo("  --default-llm  Reset default LLM selection")
    typer.echo("  --paths        Reset directory paths")


def _prepare_changes(
    all_config: bool, llm_config: bool, default_llm: bool,
    extraction_llm: bool, paths: bool, current_data: dict, defaults: dict
) -> tuple[list, dict]:
    """Prepare the list of changes and new data."""
    changes = []
    new_data = current_data.copy()

    if all_config:
        changes.append("All configuration values")
        return changes, defaults.copy()

    if llm_config:
        changes.append("llm_config (LLM configurations)")
        new_data["llm_config"] = defaults["llm_config"]

    if default_llm:
        first_llm = next(
            iter(new_data.get("llm_config", defaults["llm_config"])))
        changes.append(f"default_llm -> '{first_llm}'")
        new_data["default_llm"] = first_llm

    if extraction_llm:
        target_llm = new_data.get("default_llm") or next(
            iter(new_data.get("llm_config", defaults["llm_config"])))
        changes.append(f"extraction_llm -> '{target_llm}'")
        new_data["extraction_llm"] = target_llm

    if paths:
        path_fields = [
            "ext_code_dirs", "global_dirs", "glossary_dir", "doc_dir",
            "local_prompt_templates_dir", "local_scripts_dir", "local_ara_templates_dir",
        ]
        for field in path_fields:
            if field in defaults:
                new_data[field] = defaults[field]
        changes.append(
            "Directory paths (ext_code_dirs, glossary_dir, doc_dir, etc.)")

    return changes, new_data


def _apply_config_changes(config_path: str, new_data: dict) -> None:
    """Validate and save configuration changes."""
    import typer
    from ara_cli.ara_config import ARAconfig, save_data, ConfigManager

    validated_config = ARAconfig(**new_data)
    save_data(config_path, validated_config)
    ConfigManager.reset()

    typer.echo("")
    typer.echo("✓ Configuration reset successfully.")
    typer.echo(f"  Saved to: {config_path}")


@config_app.command("reset")
def reset_config(
    all_config: bool = typer.Option(
        False, "--all", "-a", help="Reset entire configuration to defaults"),
    llm_config: bool = typer.Option(
        False, "--llm-config", help="Reset only llm_config to defaults"),
    default_llm: bool = typer.Option(
        False, "--default-llm", help="Reset only default_llm to first available LLM"),
    extraction_llm: bool = typer.Option(
        False, "--extraction-llm", help="Reset only extraction_llm to match default_llm"),
    paths: bool = typer.Option(
        False, "--paths", help="Reset directory paths to defaults"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be reset without making changes"),
    yes: bool = typer.Option(False, "--yes", "-y",
                             help="Skip confirmation prompt"),
):
    """
    Reset ara configuration to default values.

    If no flags are specified, shows current configuration status.
    Use specific flags to reset only certain parts of the configuration.

    Examples:
        ara config reset --llm-config         # Reset only LLM configurations
        ara config reset --all                # Reset everything to defaults
        ara config reset --paths --dry-run    # Preview path reset without applying
    """
    from ara_cli.ara_config import DEFAULT_CONFIG_LOCATION, ARAconfig, get_default_llm_config
    import json

    config_path = DEFAULT_CONFIG_LOCATION

    if not os.path.exists(config_path):
        typer.echo(f"Configuration file not found at '{config_path}'.")
        typer.echo("Run any ara command to create a default configuration.")
        raise typer.Exit(1)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            current_data = json.load(f)
    except json.JSONDecodeError as e:
        typer.echo(f"Error reading configuration: {e}")
        raise typer.Exit(1)

    no_flags = not any(
        [all_config, llm_config, default_llm, extraction_llm, paths])
    if no_flags:
        _show_config_status(config_path, current_data)
        return

    default_config = ARAconfig(llm_config=get_default_llm_config())
    defaults = default_config.model_dump()

    changes, new_data = _prepare_changes(
        all_config, llm_config, default_llm, extraction_llm, paths, current_data, defaults
    )

    typer.echo("The following will be reset to defaults:")
    for change in changes:
        typer.echo(f"  • {change}")

    if dry_run:
        typer.echo("")
        typer.echo("[Dry run - no changes made]")
        return

    if not yes:
        typer.echo("")
        if not typer.confirm("Proceed with reset?"):
            typer.echo("Reset cancelled.")
            raise typer.Exit(0)

    try:
        _apply_config_changes(config_path, new_data)
    except Exception as e:
        typer.echo(f"Error saving configuration: {e}", err=True)
        raise typer.Exit(1)


@config_app.command("show")
def show_config(
    llm_only: bool = typer.Option(
        False,
        "--llm",
        help="Show only LLM configurations"
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON"
    ),
):
    """
    Show current ara configuration.

    Examples:
        ara config show              # Show full configuration
        ara config show --llm        # Show only LLM configurations
        ara config show --json       # Output as JSON
    """
    from ara_cli.ara_config import DEFAULT_CONFIG_LOCATION
    import json

    config_path = DEFAULT_CONFIG_LOCATION

    if not os.path.exists(config_path):
        typer.echo(f"Configuration file not found at '{config_path}'.")
        raise typer.Exit(1)

    with open(config_path, "r", encoding="utf-8") as f:
        config_data = json.load(f)

    if llm_only:
        output_data = {
            "llm_config": config_data.get("llm_config", {}),
            "default_llm": config_data.get("default_llm"),
            "extraction_llm": config_data.get("extraction_llm"),
        }
    else:
        output_data = config_data

    if json_output:
        typer.echo(json.dumps(output_data, indent=2))
    else:
        typer.echo(f"Configuration file: {config_path}")
        typer.echo("")
        typer.echo(json.dumps(output_data, indent=2))


def register(app: typer.Typer):
    """Register the config command group with the main app."""
    app.add_typer(config_app, name="config")
