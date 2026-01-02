"""
AitoCoder i18n (Internationalization) Module

This module provides a simple translation system for the AitoCoder REPL.
It supports English (en) and Chinese (zh) with fallback to English.

Usage:
    from aitocoder.i18n import _, init_language

    # Initialize language at startup (prompts user if needed)
    init_language()

    # Get translated message
    print(_("repl.welcome"))

    # Get translated message with format args
    print(_("repl.hello", name="Alice"))
"""

import os
from pathlib import Path
from typing import Optional

from .messages import MESSAGES

# Language preference storage location
_LANGUAGE_FILE = Path.home() / ".ac_config" / "language.txt"

# Current language (set by init_language())
_current_language: str = "en"


def _load_language_preference() -> Optional[str]:
    """
    Load saved language preference from config file.

    Returns:
        Language code if found and valid, None otherwise.
        Returns None if file doesn't exist or is empty.
    """
    try:
        if _LANGUAGE_FILE.exists():
            lang = _LANGUAGE_FILE.read_text().strip().lower()
            if lang in ("en", "zh"):
                return lang
    except Exception:
        pass
    return None


def _save_language_preference(lang: str) -> None:
    """
    Save language preference to config file.

    Args:
        lang: Language code to save ('en' or 'zh')
    """
    try:
        _LANGUAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _LANGUAGE_FILE.write_text(lang)
    except Exception:
        pass


def prompt_language_selection() -> str:
    """
    Prompt user to select a language using Rich.

    Returns:
        Selected language code ('en' or 'zh')
    """
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from global_utils import THEME

    console = Console()

    # Display language selection panel (styled like welcome panel)
    panel_content = (
        f"\n[{THEME.COL2}]>[/{THEME.COL2}] [{THEME.COL1}]1. English[/{THEME.COL1}]\n"
        f"[{THEME.COL2}]>[/{THEME.COL2}] [{THEME.COL1}]2. 简体中文[/{THEME.COL1}]\n"
    )
    console.print()
    console.print(Panel(
        panel_content,
        title=f"[bold {THEME.COL2}]Language / 语言[/bold {THEME.COL2}]",
        title_align="center",
        width=36,
        border_style=THEME.COL1,
        padding=(0, 1),
    ))

    while True:
        try:
            choice = Prompt.ask(
                f"[{THEME.COL1}]Enter number[/{THEME.COL1}]",
                choices=["1", "2"],
                default="1",
                show_default=False
            )

            if choice == "1":
                return "en"
            elif choice == "2":
                return "zh"
        except (KeyboardInterrupt, EOFError):
            console.print(f"\n[{THEME.COL1}]Defaulting to English.[/{THEME.COL1}]")
            return "en"


def init_language() -> str:
    """
    Initialize language for the session.

    Logic:
    1. Check if language preference is saved in ~/.ac_config/language.txt
    2. If saved and valid, use that
    3. If file doesn't exist or is empty, prompt user to choose
    4. Save the choice for future sessions

    Returns:
        The selected language code ('en' or 'zh')
    """
    global _current_language

    # Check saved preference
    saved_lang = _load_language_preference()
    if saved_lang:
        _current_language = saved_lang
        return _current_language

    # No saved preference or empty file - prompt user to choose
    _current_language = prompt_language_selection()

    # Save preference for future sessions
    _save_language_preference(_current_language)

    return _current_language


def get_language() -> str:
    """
    Get the current language.

    Returns:
        Current language code ('en' or 'zh')
    """
    return _current_language


def set_language(lang: str) -> None:
    """
    Set the current language.

    Args:
        lang: Language code ('en' or 'zh')
    """
    global _current_language
    if lang in ("en", "zh"):
        _current_language = lang
        _save_language_preference(lang)


def change_language() -> str:
    """
    Change the language by prompting the user to select.

    Returns:
        The newly selected language code ('en' or 'zh')
    """
    global _current_language

    new_lang = prompt_language_selection()
    _current_language = new_lang
    _save_language_preference(new_lang)

    return new_lang


def _(key: str, **kwargs) -> str:
    """
    Get translated message by key.

    This is the main translation function, following the common convention
    of using '_' as the translation function name.

    Args:
        key: Message key (e.g., 'repl.welcome')
        **kwargs: Optional format arguments for the message

    Returns:
        Translated message string. Falls back to English if key not found
        in current language. Returns the key itself if not found at all.
    """
    if key not in MESSAGES:
        return key

    msg_dict = MESSAGES[key]

    # Try current language first, then fall back to English
    message = msg_dict.get(_current_language) or msg_dict.get("en", key)

    # Apply format args if provided
    if kwargs:
        try:
            message = message.format(**kwargs)
        except (KeyError, ValueError):
            pass  # Return unformatted message if formatting fails

    return message


# Convenience exports
__all__ = [
    "_",
    "init_language",
    "get_language",
    "set_language",
    "change_language",
    "prompt_language_selection",
    "MESSAGES",
]
