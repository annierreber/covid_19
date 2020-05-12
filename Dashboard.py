# -*- coding: utf-8 -*-
"""
Created on Sun May  3 18:16:12 2020

@author: Annie
"""
import os
from random import randint
import flask
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

githublink='https://github.com/anniereber/MSDS-498'

#configure app - might need more research on external stylesheets
#app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
#server = app.server
#app.config.suppress_callback_exceptions = True

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, external_stylesheets = [dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

us_data = pd.read_json(path_or_buf='https://covidtracking.com/api/us/daily')
state_data = pd.read_json(path_or_buf='https://covidtracking.com/api/states/daily')
state_data['date'] = state_data['date'].astype(str)
us_data['date'] = us_data['date'].astype(str)
state_data['date'] = state_data.apply(lambda x: datetime.datetime.strptime(x['date'], '%Y%m%d'), axis = 1)
us_data['date'] = us_data.apply(lambda x: datetime.datetime.strptime(x['date'], '%Y%m%d'), axis = 1)

states = sorted(set(state_data['state']))
geo_values = ['positive', 'hospitalized','recovered', 'death', 'totalTestResults', 'positiveIncrease', 'deathIncrease', 'hospitalizedIncrease']
recent_date = max(state_data['date'])
recent_state_data = state_data.loc[state_data['date'] == recent_date]
recent_us_data = us_data.loc[us_data['date'] == recent_date]

#navigation bar items
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Overview", href="/Overview")),
        dbc.NavItem(dbc.NavLink("US Dashboard", href="/US_Dashboard")),
        dbc.NavItem(dbc.NavLink("State Dashboard", href="/State_Dashboard")),
        dbc.NavItem(dbc.NavLink("Forecast Dashboard", href="/Forecast_Dashboard")),
    ],
    fill=True,
    horizontal = 'center',
    pills=True
 #   navbar = True
   # vertical= "xs"
)

#create navigation bar
navbar = dbc.NavbarSimple(
    children=[nav],
    brand = "JJSAM Consulting",
    sticky="top",
    className="mb-5"
)

#set the app.layout - current setup for two pages
app.layout = html.Div([
    navbar,
    dcc.Location(id='url'),
    html.Div(id='page-content')

])

#create cards for totals
def create_card(title, content):
    card = dbc.Card(
        dbc.CardBody(
            [
                html.H4(title, className="card-title"),
                html.Br(),
                html.Br(),
                html.H2(content, className="card-subtitle"),
                html.Br(),
                html.Br(),
                ]
        ),
        color="info", inverse=True
    )
    return(card)

total_us_cases = recent_us_data['positive']
total_us_deaths = recent_us_data['death']
total_us_hospitalized = recent_us_data['hospitalized']
total_us_recovered = recent_us_data['recovered']

total_cases_card = create_card("Total US Cases", total_us_cases)
total_deaths_card = create_card("Total US Deaths", total_us_deaths)
total_hospitalized_card = create_card("Total US Hospitalized", total_us_hospitalized)
total_recovered_card = create_card("Total US Recovered", total_us_recovered)

#will add tabs - example for now
Overview_layout = html.Div([
    html.H1('Overview'),
    html.Br(),
    dbc.Row([dbc.Col(id='card1', children=[total_cases_card], md=2), 
             dbc.Col(id='card2', children=[total_deaths_card], md=2), 
             dbc.Col(id='card3', children=[total_hospitalized_card], md=2), 
             dbc.Col(id='card4', children=[total_recovered_card], md=2)]),
    html.Label('Select Value'),
    dcc.Dropdown(id='value-select', options=[{'label': i, 'value': i} for i in geo_values],
                           value='positive', style={'width': '140px'}),
    dcc.Graph('geospatial-graph', config={'displayModeBar': False}) 
    ])
 
@app.callback(
    Output('geospatial-graph', 'figure'),
    [Input('value-select', 'value')]
)    
def update_geo_graph(valname):
    fig = go.Figure(data=go.Choropleth(
    locations=recent_state_data['state'], # Spatial coordinates
    z = recent_state_data[valname].astype(float), # Data to be color-coded
    locationmode = 'USA-states' # set of locations match entries in `locations
    ))
    fig.update_layout(
            title_text = 'US COVID-19 ' + valname + ' by State',
            geo_scope='usa',# limite map scope to USA
            height=700, width=1400
            )
    return fig
    
def create_time_graph(data, state):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['positive'],mode='lines', name='Positive Cases'))
    fig.add_trace(go.Scatter(x=data['date'], y=data['hospitalized'], mode='lines', name='Hospitalized Cases'))
    fig.add_trace(go.Scatter(x=data['date'], y=data['recovered'],mode='lines', name='Recovered Cases'))
    fig.add_trace(go.Scatter(x=data['date'], y=data['death'],mode='lines', name='Deaths'))
    fig.update_layout(title='Daily ' + state + ' COVID-19 Reported Numbers',xaxis_title='Date')
    return fig

us_time_graph = create_time_graph(us_data, 'US')

US_layout = html.Div([
        html.H1('US COVID-19 Dashboard'), 
        dcc.Graph(figure=us_time_graph)
        ])

State_layout = html.Div([
        html.H1('State COVID-19 Dashboard'), 
        dcc.Dropdown(id='group-select', options=[{'label': i, 'value': i} for i in states],
                           value='IL', style={'width': '140px'}),
        dcc.Graph('states-graph', config={'displayModeBar': False}) 
        ])

@app.callback(
    Output('states-graph', 'figure'),
    [Input('group-select', 'value')]
)
def update_state_graph(state):
    select_state = state_data.loc[state_data['state'] == state]
    fig = create_time_graph(select_state, state)
    return fig

Forecast_layout = html.Div([
        html.H1('COVID-19 Predictions'), 
        ])

    
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/Overview':
        return Overview_layout
    elif pathname == '/US_Dashboard':
        return US_layout
    elif pathname == '/State_Dashboard':
        return State_layout
    elif pathname == '/Forecast_Dashboard':
        return Forecast_layout
    else:
        return Overview_layout
    
#run the app
if __name__ == "__main__":
    app.run_server()