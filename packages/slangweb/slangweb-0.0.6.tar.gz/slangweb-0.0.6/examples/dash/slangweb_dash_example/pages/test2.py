"""A Dash page example demonstrating dynamic translation using SlangWeb."""

from dash import html, register_page

from slangweb import Translator


def layout(lang: str = "en"):
    """Layout for the test2 page."""
    SW = Translator()
    SW.set_language(lang)
    return html.Div(
        [
            html.H2(SW("This is Test Page 2")),
        ]
    )


register_page(__name__, path_template="/<lang>/test2")
