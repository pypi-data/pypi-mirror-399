"""A Dash page example demonstrating dynamic translation using SlangWeb."""

from dash import Input, Output, State, callback, dcc, html, register_page

from slangweb_dash_example import SW, t


def layout(lang: str = "en"):
    """Layout for the test1 page."""
    SW.set_language(lang)
    lang_name = SW.models_lookup.get(lang, {"name": "English"}).get("name", "English")
    return html.Div(
        [
            dcc.Location(id="test1-location"),
            html.H2(
                f"{SW('This is a test for the dynamic translation system. Translating to')} {t(lang_name)}",
                style={"textAlign": "center", "marginBottom": "30px"},
            ),
            html.Div(
                children=[
                    html.Label(
                        SW("Type something in English:"),
                        style={"display": "block", "marginBottom": "10px"},
                    ),
                    dcc.Input(
                        id="test1-input",
                        value="Type here",
                        type="text",
                        style={
                            "width": "100%",
                            "padding": "10px",
                            "border": "1px solid #ccc",
                            "borderRadius": "4px",
                        },
                    ),
                    html.Button(
                        SW("Translate"),
                        id="translate-button",
                        n_clicks=0,
                        style={
                            "marginTop": "10px",
                            "padding": "10px 20px",
                            "backgroundColor": "#007BFF",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "4px",
                            "cursor": "pointer",
                        },
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            html.Div(
                children=[
                    html.Label(SW("Outcome:"), style={"display": "block", "marginBottom": "10px"}),
                    html.Div(
                        id="test1-output",
                        style={
                            "border": "1px solid #ccc",
                            "padding": "10px",
                            "minHeight": "40px",
                            "borderRadius": "4px",
                            "backgroundColor": "#f9f9f9",
                        },
                    ),
                ],
                style={"marginBottom": "20px"},
            ),
            html.H2(SW("Thanks for using SlangWeb!"), style={"textAlign": "center"}),
        ],
        style={
            "padding": "20px",
            "maxWidth": "600px",
            "margin": "0 auto",
            "fontFamily": "Arial, sans-serif",
        },
    )


@callback(
    Output("test1-output", "children"),
    Input("translate-button", "n_clicks"),
    State("test1-input", "value"),
    State("test1-location", "pathname"),
)
def update_test1_output(n_clicks, value, pathname):
    """Update the output area with the translated text when the button is clicked."""
    lang = pathname.split("/")[1] if pathname else "en"
    SW.set_language(lang)
    print(lang)
    if n_clicks == 0:
        return ""
    return t(value)


register_page(__name__, path_template="/<lang>/test1")
