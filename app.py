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

df_state = pd.read_csv('data/state_clean.csv', index_col='state')
usa_row = df_state.iloc[0]
df_state.drop('United States', inplace=True)
df_gv = pd.read_csv('data/gun_violence_clean.csv')
df_gv['date'] = pd.to_datetime(df_gv['date'])

mapbox_access_token = os.environ['MAPBOX_ACCESS_TOKEN']

def lookup(state, feature, years=range(2014, 2018)):
    '''
    Returns a list of the feature/state requested from df_state
    '''
    return [df_state.loc[state, f'{feature}{year}'] for year in years]

def generate_table(dataframe, max_rows=10):
    '''
    Returns a html Table of a pandas df
    '''

    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in dataframe.columns])] +

        # Body
        [html.Tr([
            html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
        ]) for i in range(min(len(dataframe), max_rows))]
    )

app.layout = html.Div([
    html.H1('U.S. Gun Violence 2014-2018', style={'textAlign': 'center'}),
    # State Choropleth
    html.Div([
        html.H2('Incidents by State', style={'textAlign': 'center'}),
        # Main Plot
        html.Div([
            dcc.Graph(id='choropleth-plot', config={'displayModeBar': False}),
            html.Div(
                dcc.Slider(
                    id='choropleth-slider-year',
                    min=2014,
                    max=2017,
                    step=1,
                    value=2017,
                    marks={str(i) : str(i) for i in range(2014, 2018)}
                ),
            style={'margin-left': '15%', 'margin-right': '15%'}
            )
        ], style={'width': '75%', 'display': 'inline-block'}),
        # Side Plot, Selectors, Notes Box
        html.Div([
            dcc.Graph(id='choropleth-trend', config={'displayModeBar': False}),
            dcc.Dropdown(
                id='choropleth-dropdown-feature',
                options=[{'label': i, 'value': i} for i in
                    ['Killed', 'Injured', 'Total']],
                value='Killed',
            ),
            dcc.RadioItems(
                id='choropleth-radio-metric',
                options=[{'label':i,'value':i} for i in ['Raw', 'Per 100,000']],
                value='Per 100,000'
            ),
            html.Div(id='choropleth-totals', style={'height': 200, 'overflowY': 'scroll', 'display': 'inline-block'})
        ], style={'width': '25%', 'height': 500, 'display': 'inline-block'}
        )
    ]),
    # Individual Incidents
    html.Div([
        html.H2('Individual Incidents', style={'textAlign': 'center'}),
        # Main Plot
        html.Div([
            dcc.Graph(id='incident-plot'),
        ], style={'width': '70%', 'display': 'inline-block'}),
        # Info Boxes
        html.Div([
            html.H3('Info'),
            dcc.Textarea(
                id='incident-info',
                readOnly=True,
                wrap=True,
                style={'width': '100%', 'height': 180}
            ),
            html.H3('Notes'),
            dcc.Textarea(
                id='incident-notes',
                readOnly=True,
                wrap=True,
                style={'width': '100%', 'height': 180}
            )
        ], style={'width': '30%', 'height': 500, 'display': 'inline-block'}),
        # Selectors
        html.Div([
            # State Dropdown
            html.Div(
                dcc.Dropdown(
                    id='incident-dropdown-state',
                    options=[{'label': i, 'value': i} for i in df_state.index],
                    value='Arizona',
                ),
            style={'width': '50%', 'display': 'inline-block'}
            ),
            # Year Checklist
            html.Div(
                dcc.Checklist(
                    id='incident-checklist-year',
                    options=[{'label': i, 'value': i} for i in
                        range(2014, 2019)],
                    values=[2017]
                ),
            style={'width': '50%', 'float': 'right'}
            )
        ],
        style={'width': '50%', 'margin-left': 'auto', 'margin-right': 'auto'}
        ),
    ])
],
style={
    'width': '85vw',
    'margin-left': 'auto',
    'margin-right': 'auto'
}
)

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('choropleth-plot', 'figure'),
    [Input('choropleth-slider-year', 'value'),
    Input('choropleth-dropdown-feature', 'value'),
    Input('choropleth-radio-metric', 'value')])
def choropleth_plot(year, feature, metric):
    '''
    Returns a plotly figure for the main state choropleth
    '''
    scl = [[0.0, 'rgb(242,240,247)'], [0.2, 'rgb(218,218,235)'],
           [0.4, 'rgb(188,189,220)'], [0.6, 'rgb(158,154,200)'],
           [0.8, 'rgb(117,107,177)'], [1.0, 'rgb(84,39,143)']]

    # Checks type of feature
    if feature != 'Total':
        z = df_state[feature.lower() + str(year)]
    else:
        z = df_state['killed' + str(year)] + df_state['injured' + str(year)]

    # Checks metric
    if metric == 'Per 100,000':
        pop = df_state['popestimate' + str(year)]
        z = z / (pop / 100000)
        z = z.round(2)

    data = [dict(
        type='choropleth',
        colorscl=scl,
        autocolorscale=False,
        locationmode='USA-states',
        locations=df_state['code'],
        z=z,
        text=df_state.index,
        colorbar={
            'title': feature,
            'x': 0
        }
    )]

    layout = go.Layout(
        margin={'l': 10, 'b': 20, 't': 0, 'r': 10},
        geo = dict(
            scope='usa',
            projection=dict(type='albers usa'),
        ),
    )

    return {'data': data, 'layout': layout}

@app.callback(
    Output('choropleth-trend', 'figure'),
    [Input('choropleth-dropdown-feature', 'value'),
    Input('choropleth-radio-metric', 'value'),
    Input('choropleth-plot', 'hoverData')])
def choropleth_trend(feature, metric, hoverData):
    '''
    This function will return a plotly figure

    This figure will have a trace for each requested feature aggregated by state
    '''
    # Checks if user has hovered yet
    if type(hoverData) == dict:
        hover_state = hoverData['points'][0]['text']
    else:
        hover_state = 'Arizona'

    y = lookup(hover_state, feature.lower())
    if metric == 'Per 100,000':
        pop = np.array(lookup(hover_state, 'popestimate'))
        y = np.array(y) / (pop / 100000)

    data = [go.Scatter(
        x=list(range(2014, 2018)),
        y=y,
    )]

    layout = go.Layout(
        height=200,
        margin={'l': 20, 'b': 20, 't': 5, 'r': 5},
    )
    return {'data': data, 'layout': layout}

@app.callback(
    Output('choropleth-totals', 'children'),
    [Input('choropleth-plot', 'hoverData'),
    Input('choropleth-slider-year', 'value')])
def choropleth_totals(hoverData, year):
    '''
    This function will return the totals info for the hover-on state
    '''
    # Checks if user has hovered yet
    if type(hoverData) == dict:
        hover_state = hoverData['points'][0]['text']
    else:
        hover_state = 'Arizona'

    row = df_state.loc[hover_state]
    killed = row[f'killed{year}']
    injured = row[f'injured{year}']
    total = killed + injured
    pop = row[f'popestimate{year}']

    raw = [killed, injured, total]
    per = np.round(np.array(raw) / (pop / 100000), 2)
    idxs = ['Killed' , 'Injured', 'Total']

    df = pd.DataFrame(data={' ': idxs, 'Raw': raw, 'Per 100,000': per})

    table = generate_table(df)
    table.style = {'height': 50, 'width': '50%', 'overflowY': 'scroll'}
    return table

@app.callback(
    Output('incident-plot', 'figure'),
    [Input('incident-dropdown-state', 'value'),
    Input('incident-checklist-year', 'values')])
def incident_plot(state, years):
    '''
    Returns figure for the main Mapbox
    '''
    years.sort()

    df = df_gv.copy()
    df = df[df['state']==state]

    colors = ['red', 'orange', 'green', 'blue', 'purple']
    center = df_state.loc[state, 'center']
    lat, lon = [float(i) for i in center.split(',')]
    center = {'lat': lat, 'lon': lon}

    data = []
    for year in years:
        df_year = df[df['date'].apply(lambda x: x.year==year)]
        data.append(go.Scattermapbox(
            lat=df_year['latitude'],
            lon=df_year['longitude'],
            text=df_year['notes'],
            mode='markers',
            name=year,
            marker={
                'size': 7,
                'color': colors.pop(0),
                'opacity': 0.6
            },
        ))

    layout = go.Layout(
        margin={'l': 10, 'b': 20, 't': 0, 'r': 10},
        autosize=True,
        mapbox={
            'accesstoken': mapbox_access_token,
            'center':center,
            'zoom': 8,
            'style': 'light'
        }
    )

    return {'data': data, 'layout': layout}

@app.callback(
    Output('incident-info', 'value'),
    [Input('incident-plot', 'hoverData')])
def incident_info(hoverData):
    '''
    This will be a function that returns the basic info for each marker

    Right now it doesn't work until the user hovers over a marker
    '''
    killed = 'Killed: 5'
    injured = 'Injured: 13'
    guntype = 'Guntype: Pistol'
    text = '\n'.join([killed, injured, guntype])
    return text

@app.callback(
    Output('incident-notes', 'value'),
    [Input('incident-plot', 'hoverData')])
def incident_notes(hoverData):
    '''
    This will be a function for returning the notes of the incident
    '''
    return 'Someone shot some people'


if __name__ == '__main__':
    app.run_server(debug=True)
