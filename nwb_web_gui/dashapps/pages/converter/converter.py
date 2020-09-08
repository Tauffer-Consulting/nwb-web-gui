import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State, ALL, MATCH
import dash_bootstrap_components as dbc
import json
import yaml
import base64
from .converter_utils.utils import get_forms_from_schema
from .converter_utils.forms import SourceForm, MetadataForm
from nwb_web_gui.dashapps.utils.make_components import make_modal
from pathlib import Path


class ConverterForms(html.Div):
    def __init__(self, parent_app):
        super().__init__([])
        self.parent_app = parent_app
        self.current_modal_source = ''
        modal = make_modal(parent_app)

        examples_path = Path(__file__).parent.absolute() / 'example_schemas'

        source_schema_path = examples_path / 'source_schema.json'
        with open(source_schema_path, 'r') as inp:
            self.source_json_schema = json.load(inp)

        metadata_schema_path = examples_path / 'metadata_schema.json'
        with open(metadata_schema_path, 'r') as inp:
            self.metadata_json_schema = json.load(inp)

        # Source data Form
        source_forms = get_forms_from_schema(self.source_json_schema, source=True)

        # Metadata Form
        self.parent_app.data_to_field = dict()
        self.metadata_forms = MetadataForm(
            schema=self.metadata_json_schema,
            key="Metadata",
            parent_app=self.parent_app
        )

        # Fill form
        metadata_data_path = examples_path / 'metadata_example_0.json'
        with open(metadata_data_path, 'r') as inp:
            self.metadata_json_data = json.load(inp)
        self.metadata_forms.update_form_dict_values(data=self.metadata_json_data)

        self.children = [
            dbc.Container([
                dbc.Col(html.H4('Input Files'), width={'size': 12}, style={'text-align': 'left'}),
                dbc.Col(source_forms, width={'size': 12}),
                dbc.Col(
                    dbc.Button('Get Metadata Form', id='get_metadata_btn'),
                    style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    width={'size': 4}
                ),
                dbc.Row([
                    dbc.Col(
                        dbc.Button('Save Metadata', id='save_metadata_button'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    ),
                    dbc.Col(
                        dbc.Button('Save as JSON', id='save_as_json_button'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    ),
                    dbc.Col(
                        dcc.Upload(dbc.Button('Load data'), id='button_load_metadata'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    ),
                    dbc.Col(
                        dbc.Button('Refresh', id='button_refresh'),
                        width={'size': 2},
                        style={'justify-content': 'left', 'text-align': 'left', 'margin-top': '1%'},
                    )
                ]),
                dbc.Row([
                    dbc.Col(self.metadata_forms, width={'size': 12})
                ], style={'margin-top': '1%'}),
                dbc.Row(modal),
                html.Div(id='hidden', style={'display': 'none'}),
                dbc.Row(
                    dbc.Col(
                        dbc.Button('Run Conversion', id='run_conversion_button'), width={'size': 11}
                    ), style={'text-align': 'right', 'margin-top': '1%'}
                ),
            ], style={'min-height': '110vh'})
        ]

        self.update_forms_callback_outputs = [Output(v['compound_id'], 'value') for v in self.parent_app.data_to_field.values() if v['compound_id']['data_type'] != 'link']
        self.update_forms_callback_outputs.append(Output('button_refresh', 'n_clicks'))

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

        @self.parent_app.callback(
            Output({'name': 'source_string_input', 'index': MATCH}, 'value'),
            [Input('submit_file_browser_modal', 'n_clicks')],
            [
                State('chosen_file_modal', 'value'),
                State({'name': 'source_string_input', 'index': MATCH}, 'value'),
                State({'name': 'source_string_input', 'index': MATCH}, 'id'),
            ]
        )
        def change_path_values(click, input_value, values, ids):
            ctx = dash.callback_context
            source = ctx.triggered[0]['prop_id'].split('.')[0]

            if self.current_modal_source.replace('explorer', 'input') == ids['index'] and input_value != '':
                return input_value
            else:
                return values

        @self.parent_app.callback(
            self.update_forms_callback_outputs,
            [Input('button_load_metadata', 'contents')]
        )
        def update_forms_values(contents):
            """
            Updates forms values (except links) when:
            - Forms are created (receives metadata dict from Converter)
            - User upload metadata json / yaml file
            """
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_source == 'button_load_metadata':
                content_type, content_string = contents.split(',')
                if 'json' in content_type:
                    bs4decode = base64.b64decode(content_string)
                    json_string = bs4decode.decode('utf8').replace("'", '"')
                    self.metadata_json_data = json.loads(json_string)
                    self.metadata_forms.update_form_dict_values(data=self.metadata_json_data)
                elif 'yaml' in content_type:
                    bs4decode = base64.b64decode(content_string)
                    yaml_data = yaml.load(bs4decode, Loader=yaml.BaseLoader)
                    self.metadata_json_data = yaml_data
                    self.metadata_forms.update_form_dict_values(data=self.metadata_json_data)
                output = [v['value'] for v in self.parent_app.data_to_field.values() if v['compound_id']['data_type'] != 'link']
                output.append(1)
                return output
            else:
                output = [v['value'] for v in self.parent_app.data_to_field.values() if v['compound_id']['data_type'] != 'link']
                output.append(1)
                return output

        @self.parent_app.callback(
            [Output(v['compound_id'], 'options') for v in self.parent_app.data_to_field.values() if v['compound_id']['data_type'] == 'link'],
            [Input('button_refresh', 'n_clicks')],
            [State(v['compound_id'], 'value') for v in self.parent_app.data_to_field.values() if v['compound_id']['data_type'] == 'name']
        )
        def update_forms_links(click_update, *name_change):
            """
            Updates forms values for links (dropdown options) when names change.

            data_to_field = {
                'Ecephys-ElectrodeGroup1-device': {
                    'compound_id': {
                        'type': 'metadata-input',
                        'index': 'Ecephys-ElectrodeGroup1-device',
                        'owner_class': 'pynwb.ecephys.ElectrodeGroup',
                        'data_type': 'link'
                    }
                    'value': 'device 1',
                    'target': 'pynwb.device.Device'
                },
                'Ecephys-Device-name': {
                    'compound_id': {
                        'type': 'metadata-input',
                        'index': 'Ecephys-Device-name',
                        'owner_class': 'pynwb.device.Device',
                        'data_type': 'string'
                    }
                    'value': 'device 1',
                    'target': None
                }
            }
            """
            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_source == 'button_refresh':
                # Update changed names on backend mapping dictionary
                i = 0
                for k, v in self.parent_app.data_to_field.items():
                    if v['compound_id']['data_type'] == 'name':
                        self.parent_app.data_to_field[k]['value'] = name_change[i]
                        i += 1

                # Get specific options for each link dropdown
                list_options = []
                for k, v in self.parent_app.data_to_field.items():
                    if v['target'] is not None:
                        target_class = v['target']
                        options = [
                            {'label': v['value'], 'value': v['value']}
                            for v in self.parent_app.data_to_field.values() if
                            (v['owner_class'] == target_class and 'name' in v['compound_id']['index'])
                        ]
                        list_options.append(options)

                for sublist in list_options[:]:
                    for e in sublist[:]:
                        if e['value'] is None:
                            sublist.remove(e)

                return list_options

            return [[] for v in self.parent_app.data_to_field.values() if v['compound_id']['data_type'] == 'link']

        @self.parent_app.callback(
            Output('hidden', 'children'),
            [
                Input('save_metadata_button', 'n_clicks'),
                Input('save_as_json_button', 'n_clicks')
            ],
            [State(v['compound_id'], 'value') for v in self.parent_app.data_to_field.values()]
        )
        def update_data_to_field(click, *values):
            """
            Updates data_to_field dictionary with input values from forms
            This allows the user to save the fields already filled and even 
            if he uploads a new metadata file, the fields not present in the file will be kept
            """

            ctx = dash.callback_context
            trigger_source = ctx.triggered[0]['prop_id'].split('.')[0]

            if trigger_source == 'save_metadata_button':
                i = 0
                for k, v in self.parent_app.data_to_field.items():
                    field_value = values[i]
                    v['value'] = field_value
                    i += 1
            elif trigger_source == 'save_as_json_button':
                output_json = self.field_to_json(values)
                # self.parent_app.data_to_field.key


    def field_to_json(self, values):
        output = {}
        for k, v in self.parent_app.data_to_field.items():
            splited_keys = k.split('-')
            field_name = splited_keys[-1]
            if len(splited_keys) > 2:
                # here create compound nested dict
                pass
            else:
                # create simple nested dict
                if splited_keys[0] in output:
                    output[splited_keys[0]][field_name] = v['value']
                else:
                    output[splited_keys[0]] = {field_name: v['value']}
        
        print(output)

