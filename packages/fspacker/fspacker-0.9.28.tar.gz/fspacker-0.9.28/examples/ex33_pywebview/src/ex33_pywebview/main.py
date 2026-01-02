from pathlib import Path

import webview

"""
An example of serverless app architecture
"""


CWD = Path(__file__).parent
PATH_INDEX = CWD / "assets" / "index.html"


class Api:
    """Api class."""

    def addItem(self, title: str) -> None:
        """Add an item to the list."""
        print(f"Added item {title}")

    def removeItem(self, item: str) -> None:
        """Remove an item from the list."""
        print(f"Removed item {item}")

    def editItem(self, item: str) -> None:
        """Edit an item."""
        print(f"Edited item {item}")

    def toggleItem(self, item: str) -> None:
        """Toggle an item."""
        print(f"Toggled item {item}")

    def toggleFullscreen(self) -> None:
        """Toggle fullscreen."""
        webview.windows[0].toggle_fullscreen()


def main() -> None:
    api = Api()
    webview.create_window(
        "Todos magnificos",
        url=str(PATH_INDEX),
        js_api=api,
        min_size=(600, 450),
    )
    try:
        import cryptography  # noqa: F401, PLC0415
    except ImportError:
        print(
            "Cryptography not installed, start without SSL encryption.",
        )
        webview.start()
    else:
        webview.start(ssl=True)


if __name__ == "__main__":
    main()
