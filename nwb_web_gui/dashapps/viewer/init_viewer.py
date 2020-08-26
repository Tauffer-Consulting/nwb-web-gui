import dash
import dash_html_components as html
from nwb_web_gui.dashapps.viewer.viewer import Viewer
import dash_bootstrap_components as dbc


def init_viewer(server):
    FONT_AWESOME = "https://use.fontawesome.com/releases/v5.7.2/css/all.css"
    external_stylesheets = [dbc.themes.BOOTSTRAP, FONT_AWESOME]
    dash_app = dash.Dash(
        server=server,
        external_stylesheets=external_stylesheets,
        suppress_callback_exceptions=True,
        routes_pathname_prefix='/viewer/',
    )

    # Create Dash Layout
    dash_app.layout = Viewer(parent_app=dash_app)

    return dash_app.server