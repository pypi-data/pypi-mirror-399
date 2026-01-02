"""A simple Dash app example using slangweb for translations."""

from pathlib import Path

import dash
from dash import html, page_container

from slangweb_dash_example.components.navbar import navbar_layout

# Translator instances are created inside page layouts to avoid shared state


app = dash.Dash(
    __name__,
    use_pages=True,
    pages_folder=Path(__file__).parent / "pages",
    suppress_callback_exceptions=True,
)

app.layout = html.Div([navbar_layout(), page_container])
