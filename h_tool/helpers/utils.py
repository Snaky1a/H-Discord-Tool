from typing import Any, Literal

from rich.box import ROUNDED
from rich.markdown import Markdown
from rich.panel import Panel


def build_panel(
        box: Any = ROUNDED,
        title: str = None, text: str = None,
        style: str = "", border_style: str = "",
        expand: bool = True
) -> Panel:
    return Panel(
        text, box=box, title=title,
        style=style, border_style=border_style,
        highlight=True, expand=expand
    )


def build_markdown(
        text: str, *,
        code_theme: str = "monokai",
        justify: Literal["default", "left", "center", "right", "full"] = "center",
        style: str = "",
) -> Markdown:
    return Markdown(
        markup=text, code_theme=code_theme,
        justify=justify, style=style
    )
