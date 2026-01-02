"""repl_entry.py

This module is the entry to the AitoCoder REPL.
It handles user authentication, model initialization,
and starts the REPL session.
"""
import sys
import os

# Parse flag before importing modules that suppress warnings
# (By default, warnings are suppressed for cleaner user experience.)
if "--show-warning" not in sys.argv:
    os.environ["AITOCODER_SUPPRESS_WARNINGS"] = "1"
else:
    sys.argv.remove("--show-warning")

from importlib.metadata import version
from login_modules import Auth, ModelManager

from rich.console import Console
from rich.panel import Panel

from prompt_toolkit import prompt
from prompt_toolkit.formatted_text import HTML

from global_utils import clear_screen, clear_lines, THEME
from aitocoder.i18n import _, init_language

console = Console()

# Get version from package metadata synced with pyproject.toml
try:
    __version__ = version("aitocoder")
except Exception:
    __version__ = "v.beta"


def ac_welcome():
    """Display welcome panel"""
    WelcomePanel = Panel(f"[bold {THEME.COL1}]{_('repl.welcome_to')}[/bold {THEME.COL1}]\n"
                         f"[bold][{THEME.COL2}]{_('repl.cli_title')}[/bold][/{THEME.COL2}]\n"
                         f"[{THEME.COL2}]v{__version__}[/{THEME.COL2}]\n"
                         f"[{THEME.COL1}]─────────────────────────────────────────────[/{THEME.COL1}]\n"
                         f"[{THEME.COL2}]>>[/{THEME.COL2}] [{THEME.COL1}]{_('repl.visit_download')}[/{THEME.COL1}]\n\n"
                         f"[{THEME.COL2}]>>[/{THEME.COL2}] [{THEME.COL1}]{_('repl.visit_website')}[/{THEME.COL1}]\n\n"
                         f"[{THEME.COL2}]>>[/{THEME.COL2}] [{THEME.COL1}]{_('repl.ctrl_c_hint')}[/{THEME.COL1}]\n"
                         f"[{THEME.COL2}]>>[/{THEME.COL2}] [{THEME.COL1}]{_('repl.ctrl_d_hint')}[/{THEME.COL1}]",
                         title="[italic]beta[/italic]", title_align="right",
                         width=50, border_style=f"{THEME.COL1}",
                         padding=(0,1),
                         highlight=False)
    console.print()
    console.print(WelcomePanel)
    console.print()


def chat_login():
    """Login flow with authentication and model initialization"""
    auth = Auth()

    # Check existing authentication
    if auth.is_authenticated():
        with console.status(f"[{THEME.COL1}]{_('login.fetching_user_info')}[/{THEME.COL1}]"):
            user = auth.get_user_info()
        if not user:
            console.print(f"[red]{_('login.failed_fetch_user')}[/red]")
            return False
        username = user.get('user', {}).get('userName', 'User')
        console.print(f"[{THEME.COL1}]\u00B7 {_('login.hello', username=username)}[/{THEME.COL1}]", highlight=False)
        console.print(f"[{THEME.COL1}]──────────────────────────────────────[/{THEME.COL1}]")
        console.print(f"[{THEME.COL1}]\u00B7 {_('login.type_help')}[/{THEME.COL1}]")
        return True

    # Login
    while True:
        # Prompt for credentials
        try:
            username = prompt(
                HTML(f'<style fg="{THEME.COL1}">{_("login.username_prompt")}</style> '),
            ).strip()

            password = prompt(
                HTML(f'<style fg="{THEME.COL1}">{_("login.password_prompt")}</style> '),
                is_password=True,
            )
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[red]{_('login.cancelled')}[/red]\n")
            return False

        # Clear the username and password lines
        clear_lines(console, 2)

        # Authenticate
        with console.status(f"[{THEME.COL1}]{_('login.logging_in')}[/{THEME.COL1}]"):
            login_success = auth.login(username, password)

        if not login_success:
            console.print(f"[red]{_('login.failed')}[/red]")
            console.print(f"[dim]{_('login.exit_hint')}[/dim]\n")
            continue  # Retry login

        break

    # Initialize models
    with console.status(f"[{THEME.COL1}]{_('login.initializing_models')}[/{THEME.COL1}]"):
        auth_data = auth.storage.load()
        token = auth_data.get("token")
        manager = ModelManager()
        init_success = manager.initialize_models(token)

    if init_success:
        console.print(f"\n[italic {THEME.COL2}]{_('login.all_set')}[/italic {THEME.COL2}]")
        console.print(f"\n[{THEME.COL1}]\u00B7 {_('login.hello', username=username)}[/{THEME.COL1}]", highlight=False)
        console.print(f"[{THEME.COL1}]──────────────────────────────────────[/{THEME.COL1}]")
        console.print(f"[{THEME.COL1}]\u00B7 {_('login.type_help')}[/{THEME.COL1}]")
        return True
    else:
        console.print(f"\n[yellow]{_('login.model_init_failed')}[/yellow]")
        return True


def check_environment():
    """Check environment and show warnings if needed"""
    import shutil
    from pathlib import Path

    # Check if git is available
    if not shutil.which("git"):
        console.print(f"[yellow]{_('repl.warn_no_git')}[/yellow]")

    # Check if running in home directory
    if Path.cwd() == Path.home():
        console.print(f"[yellow]{_('repl.warn_home_dir')}[/yellow]")


def main():
    """Entry point"""
    try:
        init_language()

        with console.status(f"[{THEME.COL1}]{_('repl.loading')}[/{THEME.COL1}]"):
            from autocoder.chat_auto_coder import main as repl_main

        ac_welcome()
        check_environment()

        if not chat_login():
            sys.exit(0)
        repl_main()
    except Exception as e:
        console.print(f"\n[red]{_('error.generic', message=str(e))}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
