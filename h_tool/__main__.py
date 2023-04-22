"""
H-Discord-Tool

2023-2023
"""
import asyncio
import os

from . import main_menu

if __name__ == "__main__":
    if os.name == "nt":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_menu())
