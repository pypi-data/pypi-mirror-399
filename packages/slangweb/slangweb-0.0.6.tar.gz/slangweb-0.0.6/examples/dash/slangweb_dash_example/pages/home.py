"""Homepage."""

from dash import html, register_page

from slangweb_dash_example import SW


def layout(lang: str = "en"):
    """Layout for the home page."""
    SW.set_language(lang)
    return html.Div(
        [
            html.H1(SW("Welcome to the Home Page")),
            html.P(SW("This is the homepage of our multilingual Dash application.")),
        ]
    )


register_page(__name__, path_template="/<lang>/home")
