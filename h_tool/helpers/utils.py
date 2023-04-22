"""
H-Discord-Tool

helpers/utils module

2023-2023
"""

from typing import Literal

from rich.markdown import Markdown
from rich.panel import Panel


def build_panel(
    title: str = None, text: str = None,
    style: str = "", border_style: str = "",
    expand: bool = True
) -> Panel:
    """
    Builds a :class:`Panel`
    :return: :class:`Panel`
    """
    return Panel(
        text, title=title,
        style=style, border_style=border_style,
        highlight=True, expand=expand
    )


def build_markdown(
        text: str, *,
        code_theme: str = "monokai",
        justify: Literal["default", "left", "center", "right", "full"] = "center",
        style: str = "",
) -> Markdown:
    """
    Builds a :class:`Markdown`
    :return: :class:`Markdown`
    """
    return Markdown(
        markup=text, code_theme=code_theme,
        justify=justify, style=style
    )
