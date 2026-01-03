from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
import subprocess
import sys

from rich import print as rprint
from rich.console import Console
from rich.panel import Panel

from decoder import __version__
from decoder.core.paths.config_paths import unlock_config_paths
from decoder.core.trusted_folders import trusted_folders_manager
from decoder.setup.trusted_folders.trust_folder_dialog import (
    TrustDialogQuitException,
    ask_trust_folder,
)

PYPI_PACKAGE_NAME = "decoder-cli"


async def _check_for_updates() -> tuple[bool, str | None]:
    """Check PyPI for updates.

    Returns: (has_update, latest_version)
    """
    from decoder.cli.update_notifier import (
        FileSystemUpdateCacheRepository,
        PyPIVersionUpdateGateway,
        get_update_if_available,
    )

    try:
        gateway = PyPIVersionUpdateGateway(project_name=PYPI_PACKAGE_NAME)
        cache = FileSystemUpdateCacheRepository()

        update = await get_update_if_available(
            version_update_notifier=gateway,
            current_version=__version__,
            update_cache_repository=cache,
        )

        if update is not None:
            return True, update.latest_version
        return False, None

    except Exception:
        return False, None


def _run_update() -> bool:
    """Run pip upgrade command.

    Returns True if update succeeded.
    """
    console = Console()

    with console.status("[cyan]Обновление...[/]", spinner="dots"):
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", PYPI_PACKAGE_NAME],
            capture_output=True,
            text=True,
        )

    if result.returncode == 0:
        console.print("[bold green]✓ Обновление завершено![/]")
        console.print()
        console.print("[yellow]Перезапустите decoder для применения изменений.[/]")
        return True
    else:
        console.print(f"[bold red]✗ Ошибка обновления:[/]")
        console.print(result.stderr or result.stdout)
        return False


def check_and_force_update() -> bool:
    """Check for updates and force user to update if available.

    Returns True if app can continue, False if should exit.
    """
    console = Console()

    try:
        has_update, latest_version = asyncio.run(_check_for_updates())
    except Exception:
        return True

    if not has_update or not latest_version:
        return True

    console.print()
    console.print(
        Panel(
            f"[bold yellow]Доступно обновление![/]\n\n"
            f"  Текущая версия: [red]{__version__}[/]\n"
            f"  Новая версия:   [green]{latest_version}[/]\n\n"
            f"[dim]Для продолжения работы необходимо обновление.[/]",
            title="[bold][*] Decoder Update[/]",
            border_style="yellow",
        )
    )
    console.print()

    try:
        _ = console.input(
            "[bold]Нажмите Enter для обновления (или Ctrl+C для выхода): [/]"
        )
    except (KeyboardInterrupt, EOFError):
        console.print("\n[dim]Выход...[/]")
        return False

    if _run_update():
        return False

    console.print("[red]Не удалось обновить. Попробуйте вручную:[/]")
    console.print(f"  pip install --upgrade {PYPI_PACKAGE_NAME}")
    return False


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Decoder interactive CLI")
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.add_argument(
        "initial_prompt",
        nargs="?",
        metavar="PROMPT",
        help="Initial prompt to start the interactive session with.",
    )
    parser.add_argument(
        "-p",
        "--prompt",
        nargs="?",
        const="",
        metavar="TEXT",
        help="Run in programmatic mode: send prompt, auto-approve all tools, "
        "output response, and exit.",
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        default=False,
        help="Start in auto-approve mode: never ask for approval before running tools.",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        default=False,
        help="Start in plan mode: read-only tools for exploration and planning.",
    )
    parser.add_argument(
        "--max-turns",
        type=int,
        metavar="N",
        help="Maximum number of assistant turns "
        "(only applies in programmatic mode with -p).",
    )
    parser.add_argument(
        "--max-price",
        type=float,
        metavar="DOLLARS",
        help="Maximum cost in dollars (only applies in programmatic mode with -p). "
        "Session will be interrupted if cost exceeds this limit.",
    )
    parser.add_argument(
        "--enabled-tools",
        action="append",
        metavar="TOOL",
        help="Enable specific tools. In programmatic mode (-p), this disables "
        "all other tools. "
        "Can use exact names, glob patterns (e.g., 'bash*'), or "
        "regex with 're:' prefix. Can be specified multiple times.",
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json", "streaming"],
        default="text",
        help="Output format for programmatic mode (-p): 'text' "
        "for human-readable (default), 'json' for all messages at end, "
        "'streaming' for newline-delimited JSON per message.",
    )
    parser.add_argument(
        "--agent",
        metavar="NAME",
        default=None,
        help="Load agent configuration from ~/.decoder/agents/NAME.toml",
    )
    parser.add_argument("--setup", action="store_true", help="Setup API key and exit")

    continuation_group = parser.add_mutually_exclusive_group()
    continuation_group.add_argument(
        "-c",
        "--continue",
        action="store_true",
        dest="continue_session",
        help="Continue from the most recent saved session",
    )
    continuation_group.add_argument(
        "--resume",
        metavar="SESSION_ID",
        help="Resume a specific session by its ID (supports partial matching)",
    )
    return parser.parse_args()


def check_and_resolve_trusted_folder() -> None:
    cwd = Path.cwd()
    if not (cwd / ".decoder").exists() or cwd.resolve() == Path.home().resolve():
        return

    is_folder_trusted = trusted_folders_manager.is_trusted(cwd)

    if is_folder_trusted is not None:
        return

    try:
        is_folder_trusted = ask_trust_folder(cwd)
    except (KeyboardInterrupt, EOFError, TrustDialogQuitException):
        sys.exit(0)
    except Exception as e:
        rprint(f"[yellow]Error showing trust dialog: {e}[/]")
        return

    if is_folder_trusted is True:
        trusted_folders_manager.add_trusted(cwd)
    elif is_folder_trusted is False:
        trusted_folders_manager.add_untrusted(cwd)


def main() -> None:
    args = parse_arguments()

    # Forced update check - block if update available
    is_interactive = args.prompt is None
    if is_interactive:
        if not check_and_force_update():
            sys.exit(0)
        check_and_resolve_trusted_folder()
    unlock_config_paths()

    from decoder.cli.cli import run_cli

    run_cli(args)


if __name__ == "__main__":
    main()
