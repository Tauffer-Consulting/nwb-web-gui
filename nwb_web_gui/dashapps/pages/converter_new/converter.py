import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import json
from pathlib import Path
from .converter_utils.utils import get_forms_from_schema
from nwb_web_gui.dashapps.utils.make_components import make_modal


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app
        modal = make_modal(parent_app)

        source_schema_path = Path('/home/vinicius/Área de Trabalho/Trabalhos/nwb-web-gui/nwb_web_gui/static/uploads/formData/source_schema.json')
        with open(source_schema_path, 'r') as inp:
            self.source_json_schema = json.load(inp)

        source_forms = get_forms_from_schema(self.source_json_schema, source=True)

        self.children = [
            dbc.Container([
                dbc.Row(html.H1('NWB Converter'), style={'justify-content': 'center'}),
                dbc.Row([
                    dbc.Col(source_forms, width={'size': 4})
                ]),
                dbc.Row(modal)
            ],fluid=True)
        ]

        @self.parent_app.callback(
            Output('modal_explorer', 'is_open'),
            [Input({'name': 'source_explorer', 'index': ALL}, 'n_clicks'), Input('close_explorer_modal', 'n_clicks')],
            [State("modal_explorer", "is_open")]
        )
        def open_explorer(click_open, click_close, is_open):

            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if 'index' in source:
                dict_source = json.loads(source)
                self.current_modal_source = dict_source['index']

            if source != '' and (any(click_open) or click_close):
                return not is_open
            else:
                return is_open