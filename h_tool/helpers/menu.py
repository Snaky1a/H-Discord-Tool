from h_tool.core.get_info import check_token
from ..helpers.logs import console
from ..helpers.utils import build_markdown, build_panel

options = [
    "1. Check token",
    "2. Placeholder",
    "3. Placeholder",
    "4. Placeholder",
    "5. Placeholder",
    "6. Placeholder",
    "7. Placeholder",
    "8. Placeholder",
    "9. Placeholder",
    "10. Exit",
]


async def main_menu() -> None:
    console.print(markdown=build_markdown("Welcome to H-Discord-Tool!", justify="left"))
    option = int(console.choice(
        "Option", choices=[str(index + 1) for index, _ in enumerate(options)],
        panel=build_panel(title="Please, select an option", text='\n'.join(options), expand=False), default=10
    ))

    if option == 1:
        token = console.input("Token: ", password=True)
        mask_token = console.choice("Mask Token in result? ", choices=["y", "n"], show_choices=True, default="n")
        await check_token(token=token, mask_token=True if mask_token == "y" else False)

    if option == 10:
        console.print("Bye!")
