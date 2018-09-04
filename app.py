import pandas as pd
import numpy as np
import os

import dash
import dash_auth
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.graph_objs as go

app = dash.Dash()
server = app.server

df_state = pd.read_csv('data/state_clean.csv')

app.layout = html.Div([
    # App Title
    html.H1('U.S. Gun Violence 2014-2018', style={'textAlign': 'center'}),
    # YoY
    html.Div([
        html.H2('U.S. Yearly Totals', style={'textAlign': 'center'}),
        # Selectors
        html.Div([
            # Metric Radio
            html.Div(
                dcc.RadioItems(
                    id='yoy-radio-metric',
                    options=[{'label': i, 'value': i} for i in
                        ['Raw', 'Per 100,000']],
                    value='Raw'
                ),
            style={'margin-left': 'auto', 'margin-right': 'auto'}
            ),
            # Feature Dropdwon
            html.Div(
                dcc.Dropdown(
                    id='yoy-dropdown-feature',
                    options=[{'label': i, 'value': i} for i in
                        ['Killed', 'Injured', 'Total']],
                    value='Killed'
                ),
            style={'margin-left': 'auto', 'margin-right': 'auto'}
            )
        ],
        style={'width': '25%', 'margin-left': 'auto', 'margin-right': 'auto'}
        ),
        # Main Plot
        dcc.Graph(id='yoy-plot')
    ],
    style={'width': '85%', 'margin-left': 'auto', 'margin-right': 'auto'}
    ),
    # All States
    html.Div([
        html.H2('Gun Violence by State', style={'textAlign': 'center'}),
        # Feature Dropdwon
        html.Div(
            dcc.Dropdown(
                id='state-dropdown-feature',
                options=[{'label': i, 'value': i} for i in
                    ['Killed', 'Injured', 'Total']],
                value='Killed'
            ),
        style={'width': '30%', 'margin-left': '70%'}
        ),
        # Main Plot
        dcc.Graph(id='state-plot')
    ],
    style={'width': '85%', 'margin-left': 'auto', 'margin-right': 'auto'}
    ),
    # Individual Incidents
    html.Div([
        html.H2('Individual Incidents', style={'textAlign': 'center'}),
        # Selectors
        html.Div([
            # State Dropdown
            html.Div(
                dcc.Dropdown(
                    id='individual-dropdown-state',
                    options=[{'label': i, 'value': i} for i in
                        np.unique(df_state['name'])],
                    value='Nevada',
                ),
            style={'width': '50%', 'display': 'inline-block'}
            ),
            # Year Checklist
            html.Div(
                dcc.Checklist(
                    id='individual-checklist-year',
                    options=[{'label': i, 'value': i} for i in
                        [2014, 2015, 2016, 2017, 2018]],
                    values=[2018]
                ),
            style={'width': '50%', 'float': 'right'}
            )
        ],
        style={'width': '50%', 'margin-left': 'auto', 'margin-right': 'auto'}
        ),
        # Main Plot
        dcc.Graph(id='individual-plot')
    ],
    style={'width': '85%', 'margin-left': 'auto', 'margin-right': 'auto'}
    )
])

if __name__ == '__main__':
    app.scripts.config.serve_locally = True
    app.css.config.serve_locally = True
    app.run_server(debug=True)
