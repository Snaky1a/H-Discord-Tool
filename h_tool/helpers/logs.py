"""
H-Discord-Tool

helpers/logs module (Console and logging)

2023-2023
"""

from datetime import datetime
from typing import Union, IO, Literal

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt


class SimpleConsole:

    def __init__(self, file: Union[IO, str] = None) -> None:
        """
        initializing custom console
        :param file: file to log (default: None)
        """

        self.log_file = Console(
            file=file
            if isinstance(file, IO)
            else open(file, "a+", encoding="utf-8")
            if file else open(
                f"../h_tool-{datetime.now().strftime('%Y-%m-%d %H.%M.%S')}.log",
                "a+",
                encoding="utf-8"
            )
        )
        self.console = Console()
        self.prompt = Prompt()

    def _log(self, message: str, *args, **kwargs) -> None:
        self.console.log(message, *args, **kwargs)
        self.log_file.log(message, *args, **kwargs)

    def print(
            self, message: str = "", *,
            justify: Literal["default", "left", "center", "right", "full"] = "default",
            emoji: bool = True,
            markdown: Union[Markdown, Panel, str] = None,
            panel: Panel = None,
    ) -> None:
        """
        Reads a message from the console.
        :param panel: Panel to render
        :param message: Text to render in the prompt
        :param justify: Justify method
        :param emoji: Enable emoji support
        :param markdown: Render markdown
        """
        if markdown:
            if isinstance(markdown, str):
                markdown = Markdown(markdown)

            self.console.print(markdown)
            self.log_file.print(markdown)

        if panel:
            self.console.print(panel)
            self.log_file.print(panel)

        if message:
            self.log_file.log(message)
            self.console.print(message, justify=justify, emoji=emoji)

    def log(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message in Console.
        :param message: Message text to log
        """
        self._log(message, *args, **kwargs)

    def input(
            self, message: str, *,
            password: bool = False,
            emoji: bool = True,
            markdown: Union[Markdown, Panel, str] = None,
            panel: Panel = None,
    ) -> str:
        """
        Reads a message from the console.
        :param panel: Panel to render
        :param message: Text to render in the prompt
        :param password: Hide typed text
        :param emoji: Enable emoji support
        :param markdown: Render markdown
        """
        if markdown:
            if isinstance(markdown, str):
                markdown = Markdown(markdown)

            self.console.print(markdown)

        if panel:
            self.console.print(panel)

        return self.console.input(prompt=message, password=password, emoji=emoji)  # type: ignore

    def choice(
            self, message: str,
            choices: list, *,
            default: str = None,
            panel: Panel = None,
            password: bool = False,
            show_choices: bool = True
    ) -> str:
        """
        Reads a message from the console.
        :param panel: Panel to render
        :param message: Text to render in the prompt
        :param choices: List of choices
        :param default: Default choice
        :param password: Hide typed text
        :param show_choices: Show choices
        """
        if panel:
            self.console.print(panel)

        return self.prompt.ask(
            prompt=message, choices=choices,
            default=default, password=password,
            show_choices=show_choices
        )


console = SimpleConsole()
