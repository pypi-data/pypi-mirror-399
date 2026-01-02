"""Navigation bar component for the web application."""

import json

import dash
from dash import callback, dcc, html
from dash.dependencies import ALL, Input, Output, State


def navbar_layout():
    """Create the navigation bar layout."""
    return html.Nav(
        [
            dcc.Location(id="nav-location"),
            dcc.Store(id="nav-lang-store", data="en"),
            html.Div(
                children=[
                    dcc.Link(
                        "Home",
                        href="#",
                        id={"type": "nav-link", "path": "home"},
                        className="nav-link",
                    ),
                    dcc.Link(
                        "Test Page 1",
                        href="#",
                        id={"type": "nav-link", "path": "test1"},
                        className="nav-link",
                    ),
                    dcc.Link(
                        "Test Page 2",
                        href="#",
                        id={"type": "nav-link", "path": "test2"},
                        className="nav-link",
                    ),
                ],
                className="nav-left",
            ),
            html.Div(
                children=[
                    html.Button(
                        "en",
                        id={"type": "lang-link", "index": "en"},
                        className="lang-link",
                        type="button",
                    ),
                    html.Button(
                        "es",
                        id={"type": "lang-link", "index": "es"},
                        className="lang-link",
                        type="button",
                    ),
                    html.Button(
                        "fr",
                        id={"type": "lang-link", "index": "fr"},
                        className="lang-link",
                        type="button",
                    ),
                ],
                className="nav-right lang-links",
            ),
        ],
        className="navbar",
    )


@callback(
    Output({"type": "nav-link", "path": ALL}, "href"),
    Input("nav-location", "pathname"),
    State({"type": "nav-link", "path": ALL}, "id"),
)
def update_links(pathname, ids):
    """Update navigation links based on current language in the URL."""
    path_parts = pathname.split("/")
    if len(path_parts) > 2:
        lang = path_parts[1]
    else:
        lang = "en"
    hrefs = [f"/{lang}/{id_obj['path']}" for id_obj in ids]
    return hrefs


@callback(
    Output("nav-lang-store", "data"),
    Output("nav-location", "pathname"),
    Input({"type": "lang-link", "index": ALL}, "n_clicks"),
    State("nav-location", "pathname"),
    prevent_initial_call=True,
)
def handle_language_click(n_clicks, pathname):
    """Handle language button clicks to update URL and language store."""
    ctx = dash.callback_context
    if not ctx.triggered:
        raise dash.exceptions.PreventUpdate
    triggered = ctx.triggered[0]["prop_id"].split(".")[0]
    try:
        triggered_obj = json.loads(triggered)
    except Exception:
        triggered_obj = eval(triggered)
    lang = triggered_obj.get("index")
    path_parts = pathname.split("/")
    path_rest = "/".join(path_parts[2:])
    if path_rest:
        new_location = f"/{lang}/{path_rest}"
    else:
        new_location = f"/{lang}/home"

    return lang, new_location
