import pandas as pd
import numpy as np
import os
import json

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
df_gv = pd.read_csv('data/gun_violence_clean.csv', index_col='incident_id')
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

def clr_check(val, default_color, mass_color='black', threshold=10):
    '''
    For use in the individual incident plot.

    Returns default_color if val is below threshold, else mass_color
    '''
    if int(val) < threshold:
        return default_color
    else:
        return mass_color

app.layout = html.Div([
    html.H1('U.S. Gun Violence 2014-2018', style={'textAlign': 'center'}),
    # State Choropleth
    html.Div([
        html.H2('Incidents by State', style={'textAlign': 'center'}),
        html.H5(id='choropleth-title', style={'textAlign': 'center'}),
        # Main Plot
        html.Div([
            dcc.Graph(
                id='choropleth-plot',
                config={'displayModeBar': False},
                hoverData={'points': [{'text': 'Colorado'}]}
            ),
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
            dcc.Graph(id='choropleth-trend', config={'displayModeBar': False}),
            html.Div(
                id='choropleth-totals',
                style={
                    'height': 200,
                    'overflowY': 'scroll',
                    'margin-left': 10,
                    # 'margin-right': 'auto'
                })
        ], style={
            'width': '24%',
            'height': 500,
            'display': 'inline-block',
            'borderStyle': 'solid',
            'borderColor': 'black',
        }
        )
    ]),
    html.Br(),
    # Individual Incidents
    html.Div([
        html.H2('Individual Incidents', style={'textAlign': 'center'}),
        # Main Plot & Selectors
        html.Div([
            html.Div([
                # Year Dropdown
                html.Div(
                    dcc.Checklist(
                        id='incident-checklist-year',
                        options=[{'label': i, 'value': i} for i in
                            range(2014, 2019)],
                        values=[2017],
                        labelStyle={'display': 'inline-block'}
                    ),
                style={'width': '35%', 'display': 'inline-block'}
                ),
                # State Dropdown
                html.Div(
                    dcc.Dropdown(
                        id='incident-dropdown-state',
                        options=[{'label':i,'value':i} for i in df_state.index],
                        value='Arizona',
                    ),
                style={
                    'width': '20%',
                    'display': 'inline-block',
                    'margin-left': '5%',
                    'margin-right': '5%',
                    'margin-top': 5
                }),
                # Feature Radio
                html.Div(
                    dcc.RadioItems(
                        id='incident-radio-feature',
                        options=[{'label': i, 'value': i} for i in
                            ['Show All', 'Killed Only', 'Injured Only']],
                        value='Show All',
                        labelStyle={'display': 'inline-block'}
                    ),
                style={'width': '35%', 'display': 'inline-block'},
                )
            ], style={
                'borderStyle': 'solid',
                'borderColor': 'black',
                'backgroundColor': 'rgba(110, 110, 110, 0.15)',
            }
            ),
            dcc.Graph(
                id='incident-plot',
                config={'displayModeBar': False},
                style={'width': '100%', 'display': 'inline-block'},
            )
        ], style={'width': '70%', 'display': 'inline-block'}),
        # # Info Boxes
        html.Div([
            html.H3('Info', style={'margin-left': '10%'}),
            dcc.Textarea(
                id='incident-info',
                readOnly=True,
                wrap=True,
                style={'width': '100%', 'height': 220}
            ),
            html.H3('Notes', style={'margin-left': '10%'}),
            dcc.Textarea(
                id='incident-notes',
                readOnly=True,
                wrap=True,
                style={'width': '100%', 'height': 140}
            )
        ], style={
            'width': '30%',
            'height': 500,
            'display': 'inline-block'
        }),
    ])
],
style={
    'width': '85vw',
    'margin-left': 'auto',
    'margin-right': 'auto',
}
)

app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})

@app.callback(
    Output('choropleth-title', 'children'),
    [Input('choropleth-slider-year', 'value'),
    Input('choropleth-radio-metric', 'value')])
def choropleth_plot(year, metric):
    '''
    This function returns the title for the choropleth

    Updates on year and metric changes
    '''
    return f'{metric}, ({year})'

@app.callback(
    Output('choropleth-plot', 'figure'),
    [Input('choropleth-slider-year', 'value'),
    Input('choropleth-dropdown-feature', 'value'),
    Input('choropleth-radio-metric', 'value')])
def choropleth_plot(year, feature, metric):
    '''
    Returns a plotly figure for the main state choropleth
    '''
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

    # Color Scale
    scl = [[0.0, 'rgb(255, 255, 255)'], [0.3, 'rgb(215, 190, 190)'],
           [0.4, 'rgb(215, 160, 160)'], [0.6, 'rgb(215, 130, 130)'],
           [0.8, 'rgb(215, 100, 100)'], [1.0, 'rgb(140, 0, 0)']]

    # Yes, this is mega ugly right now. I'll do something different later
    # Get right zmax for feature
    if (feature == 'Killed') * (metric == 'Per 100,000'):
        zmax = 12
    elif (feature == 'Injured') & (metric == 'Per 100,000'):
        zmax = 30
    elif (feature == 'Total') & (metric == 'Per 100,000'):
        zmax = 40
    if (feature == 'Killed') * (metric == 'Raw'):
        zmax = 1500
    elif (feature == 'Injured') & (metric == 'Raw'):
        zmax = 3500
    elif (feature == 'Total') & (metric == 'Raw'):
        zmax = 4500

    data = [dict(
        type='choropleth',
        colorscale=scl,
        autocolorscale=False,
        locationmode='USA-states',
        locations=df_state['code'],
        z=z,
        zmin=0,
        zmax=zmax,
        text=df_state.index,
        colorbar={
            'title': feature,
            'x': 0
        }
    )]

    layout = go.Layout(
        margin={'l': 10, 'b': 20, 't': 0, 'r': 10},
        geo = dict(scope='usa', projection={'type': 'albers usa'})
    )

    return {'data': data, 'layout': layout}

@app.callback(
    Output('choropleth-trend', 'figure'),
    [Input('choropleth-dropdown-feature', 'value'),
    Input('choropleth-radio-metric', 'value'),
    Input('choropleth-plot', 'hoverData'),
    Input('choropleth-plot', 'clickData')])
def choropleth_trend(feature, metric, hoverData, clickData):
    '''
    This function returns the plotly figure for the state's trend plot
    '''
    hover_state = hoverData['points'][0]['text']

    # Checks if total
    if feature != 'Total':
        y = lookup(hover_state, feature.lower())
    else:
        killed = np.array(lookup(hover_state, 'killed'))
        injured = np.array(lookup(hover_state, 'injured'))
        y = killed + injured
    # Check for Population scaling
    if metric == 'Per 100,000':
        pop = np.array(lookup(hover_state, 'popestimate'))
        y = np.array(y) / (pop / 100000)
    max_y = max(y)

    # Main trace
    data = [go.Scatter(x=list(range(2014, 2018)), y=y, name=hover_state)]

    # Checks for clicked on state
    if type(clickData) == dict:
        click_state = clickData['points'][0]['text']
        # Checks if total
        if feature != 'Total':
            y = lookup(click_state, feature.lower())
        else:
            killed = np.array(lookup(click_state, 'killed'))
            injured = np.array(lookup(click_state, 'injured'))
            y = killed + injured
        # Check for Population scaling
        if metric == 'Per 100,000':
            pop = np.array(lookup(click_state, 'popestimate'))
            y = np.array(y) / (pop / 100000)
        # Check for a new larger y
        if max_y < max(y):
            max_y = max(y)
        # Data Trace
        trace = go.Scatter(
            x=list(range(2014, 2018)),
            y=y,
            name=click_state,
            line={'color': 'red'}
        )
        data.append(trace)

    # Rescales yaxis
    if max_y > 7:
        yaxis_range = [0, max_y + 1]
    else:
        yaxis_range = [0, 8]

    # Layout
    layout = go.Layout(
        height=200,
        margin={'l': 20, 'b': 20, 't': 5, 'r': 5},
        yaxis={'range': yaxis_range},
        legend={'x': 0, 'y': 1.2, 'orientation': 'h'},
        showlegend=True
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
    hover_state = hoverData['points'][0]['text']

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
    [Input('incident-checklist-year', 'values'),
    Input('incident-dropdown-state', 'value'),
    Input('incident-radio-feature', 'value')])
def incident_plot(years, state, feature):
    '''
    Returns figure for the main Individual Incidents Mapbox
    '''
    years.sort()

    df = df_gv.copy()
    df = df[df['state']==state]

    colors = ['red', 'orange', 'green', 'blue', 'purple']
    center = df_state.loc[state, 'center']
    lat, lon = [float(i) for i in center.split(',')]
    center = {'lat': lat, 'lon': lon}


    data = []
    # Make a trace for each year user is interested in
    for year in years:
        df_year = df[df['date'].apply(lambda x: x.year==year)]
        # Check incident filter
        if feature != 'Show All':
            feature = feature.split()[0].lower()
            if feature == 'killed':
                df_year = df_year[df_year['n_killed'] > 0]
            elif feature == 'injured':
                df_year = df_year[df_year['n_killed'] == 0]

        # Partition out mass shootings
        print(len(df_year))
        df_year['total'] = df_year['n_killed'] + df_year['n_injured']
        df_mass = df_year[df_year['total'] >= 5]
        df_year = df_year[df_year['total'] < 5]
        print(len(df_year))
        print(len(df_mass))

        # Main Traces
        text = 'ID: ' + df_year.index.astype(str) + '<br>' + \
            df_year['address'].fillna('') +  '<br>' + \
            df_year['location_description'].fillna('')
        data.append(go.Scattermapbox(
            lat=df_year['latitude'],
            lon=df_year['longitude'],
            hoverinfo='text',
            text=text,
            mode='markers',
            name=year,
            marker={
                'size': 7,
                'color': colors.pop(0),
                'opacity': 0.6,
            }
        ))

        # Mass Traces
        text = 'ID: ' + df_mass.index.astype(str) + '<br>' + \
            df_mass['address'].fillna('') +  '<br>' + \
            df_mass['location_description'].fillna('')
        data.append(go.Scattermapbox(
            lat=df_mass['latitude'],
            lon=df_mass['longitude'],
            hoverinfo='text',
            text=text,
            mode='markers',
            marker={
                'size': 9,
                'color': 'black',
                'opacity': 0.9,
            },
            showlegend=False
        ))


    layout = go.Layout(
        margin={'l': 0, 'b': 0, 't': 0, 'r': 0},
        height=450,
        autosize=True,
        mapbox={
            'accesstoken': mapbox_access_token,
            'center':center,
            'zoom': 8.5,
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
    # check for initial hover
    if type(hoverData) != dict:
        return "Hover over a marker to get incident info"
    else:
        hovertext = hoverData['points'][0]['text']
        id =int(hovertext.split('<br>')[0].split()[1])
        row = df_gv.loc[id]

    # date, killed, injured, participants, victims
    text = 'Date:\t' + str(row['date'])[:-9] + '\n' + \
           'Killed:\t' + str(row['n_killed']) + '\n' + \
           'Injured:\t' + str(row['n_injured']) + '\n\n'
    # gun type
    if type(row['gun_type']) == str:
        text += 'Gun Type:\t\t' + row['gun_type'] + '\n'
    else:
        text += 'Gun Type:\t\tUnknown\n'

    # participants
    if type(row['participant_age']) == str:
        text += 'Participants:\t\t' + \
                str(len(row['participant_age'].split(','))) + '\n'
        text += 'Participant Age:\t' + \
                row['participant_age'].replace(',', ', ') + '\n'
    else:
        text += 'Participants:\t\tUnknown\n'
        text += 'Participant Age:\tUnknown\n'

    # url
    text += '\n' + 'URL: ' + row['incident_url']

    return text

@app.callback(
    Output('incident-notes', 'value'),
    [Input('incident-plot', 'hoverData')])
def incident_notes(hoverData):
    '''
    This will be a function for returning the notes of the incident
    '''
    if type(hoverData) != dict:
        return "Hover over a marker to read notes on that incident"
    else:
        hovertext = hoverData['points'][0]['text']
        id =int(hovertext.split('<br>')[0].split()[1])
        row = df_gv.loc[id]

    notes = row['notes']
    if type(notes) != str:
        return 'No notes for this incident'
    return notes


if __name__ == '__main__':
    app.run_server(debug=True)
