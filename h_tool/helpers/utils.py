from typing import Any

from rich.box import ROUNDED
from rich.markdown import Markdown
from rich.panel import Panel


def build_panel(
        box: Any = ROUNDED,
        title: str = None, text: str = None, style: str = "", border_style: str = "", expand: bool = True) -> Panel:
    return Panel(text, box=box, title=title, style=style, border_style=border_style, highlight=True, expand=expand)


def build_markdown(
        text: str, *,
        code_theme: str = "monokai",
        justify: str = "center",
        style: str = "",
) -> Markdown:
    return Markdown(markup=text, code_theme=code_theme, justify=justify, style=style)  # type: ignore
