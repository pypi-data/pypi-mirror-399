from __future__ import annotations

import typer

from . import config, github, notebook
from .cli_utils import show_help_callback

app = typer.Typer(
    name="sdt",
    help="SDT CLI Tool - Your awesome command-line utility",
)

app.add_typer(config.app, name="config")
app.add_typer(github.app, name="github")


# Add notebook command with context settings to capture all arguments
@app.command(
    name="nb",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def nb(ctx: typer.Context) -> None:
    """Notebook management - store and retrieve text notes organized by category."""
    notebook.nb_command(ctx, ctx.args)


@app.callback(invoke_without_command=True)
def _root(ctx: typer.Context) -> None:
    """
    Prints the Typer app help and exits successfully when no subcommand was invoked.

    If the provided context has no invoked subcommand, writes the full help text to stdout and exits with code 0.

    Parameters:
        ctx (typer.Context): Invocation context used to check for a subcommand and to retrieve the help text.
    """
    show_help_callback(ctx)


def main() -> None:
    """
    Run the Typer command-line application.

    Invoke the module's Typer `app` to execute the CLI; intended as the program entry point.
    """
    app()


if __name__ == "__main__":
    main()
