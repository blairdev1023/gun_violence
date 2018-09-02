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

app.layout = html.Div([
    html.H1('U.S. Gun Violence 2014-2018', style={'textAlign': 'center'}),
    ])

if __name__ == '__main__':
    app.scripts.config.serve_locally = True
    app.css.config.serve_locally = True
    app.run_server(debug=True)
