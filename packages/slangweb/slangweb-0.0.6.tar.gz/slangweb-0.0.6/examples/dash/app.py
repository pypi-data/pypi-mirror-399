"""Run the Dash app example for SlangWeb."""

import logging

from slangweb_dash_example.main import app

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)


def run_app(debug=True):
    """Run the Dash app."""
    app.run(debug=debug)


if __name__ == "__main__":
    run_app(debug=True)
