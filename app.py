# -*- coding: utf-8 -*-
"""
Created on Sun May  3 18:16:12 2020

@author: Annie
"""
#import os
#from random import randint
#import flask
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
#import numpy as np
import plotly.graph_objects as go
#import plotly.express as px
import datetime

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']#, dbc.themes.BOOTSTRAP]

#configure app - might need more research on external stylesheets
app = dash.Dash(__name__, external_stylesheets = [dbc.themes.BOOTSTRAP])
server = app.server
#app.config.suppress_callback_exceptions = True

#server = flask.Flask(__name__)
#server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
#app = dash.Dash(__name__, server=server, external_stylesheets = [dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True


#data setup
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

#MA WOW
SevenDaysBack = recent_date + datetime.timedelta(days=-7)
FourteenDaysBack = recent_date + datetime.timedelta(days=-14)
df_State_PastWeek = state_data[state_data['date']>=SevenDaysBack ]
df_State_PriorPastWeek = state_data[(state_data['date']>=FourteenDaysBack) & (state_data['date']<SevenDaysBack )]
df_State_PastWeek_Summary= df_State_PastWeek.groupby('state')['totalTestResults', 'positive', 'negative','death','recovered','hospitalizedCumulative'].apply(lambda x: x.max() - x.min()).reset_index()
df_State_PriorPastWeek_Summary= df_State_PriorPastWeek.groupby('state')['totalTestResults', 'positive', 'negative','death','recovered','hospitalizedCumulative'].apply(lambda x: x.max() - x.min()).reset_index()
df_Week_over_Week = pd.merge(df_State_PastWeek_Summary, df_State_PriorPastWeek_Summary,how='inner', on=['state'])

df_Week_over_Week['totalTestResults_growth'] = (df_Week_over_Week['totalTestResults_x']-df_Week_over_Week['totalTestResults_y'])/df_Week_over_Week['totalTestResults_y']
df_Week_over_Week['positive_growth'] = ((df_Week_over_Week['positive_x']-df_Week_over_Week['positive_y'])/df_Week_over_Week['positive_y'])
df_Week_over_Week['negative_growth'] = (df_Week_over_Week['negative_x']-df_Week_over_Week['negative_y'])/df_Week_over_Week['negative_y']
df_Week_over_Week['death_growth'] = (df_Week_over_Week['death_x']-df_Week_over_Week['death_y'])/df_Week_over_Week['death_y']
df_Week_over_Week['recovered_growth'] = (df_Week_over_Week['recovered_x']-df_Week_over_Week['recovered_y'])/df_Week_over_Week['recovered_y']
df_Week_over_Week['hospitalized_growth'] = (df_Week_over_Week['hospitalizedCumulative_x']-df_Week_over_Week['hospitalizedCumulative_y'])/df_Week_over_Week['hospitalizedCumulative_y']

df_Week_over_Week['Tests_last_week'] = (df_Week_over_Week['totalTestResults_x'])
df_Week_over_Week['New_Cases_last_week'] = (df_Week_over_Week['positive_x'])
df_Week_over_Week['Recovered_last_week'] = (df_Week_over_Week['recovered_x'])
df_Week_over_Week['Deaths_last_week'] = (df_Week_over_Week['death_x'])
df_Week_over_Week['hospitalized_last_week'] = (df_Week_over_Week['hospitalizedCumulative_x'])

df_Week_over_Week['Tests_last_week'] = df_Week_over_Week['Tests_last_week'].fillna(0)
df_Week_over_Week['New_Cases_last_week'] = df_Week_over_Week['New_Cases_last_week'].fillna(0)
df_Week_over_Week['Recovered_last_week'] = df_Week_over_Week['Recovered_last_week'].fillna(0)
df_Week_over_Week['Deaths_last_week'] = df_Week_over_Week['Deaths_last_week'].fillna(0)
df_Week_over_Week['hospitalized_last_week'] = df_Week_over_Week['hospitalized_last_week'].fillna(0)

df_Week_over_Week= df_Week_over_Week[['state', 'totalTestResults_growth','positive_growth', 'negative_growth', 'death_growth', 'recovered_growth', 'hospitalized_growth', 'Tests_last_week', 'New_Cases_last_week', 'Recovered_last_week', 'Deaths_last_week', 'hospitalized_last_week']]
#df_Week_over_Week= df_Week_over_Week.sort_values('positive_growth',ascending=False)
df_Week_over_Week['Weekly_Tests'] =  'Number of Tests last week ='+df_Week_over_Week['Tests_last_week'].astype(int).astype(str)+' ('  + df_Week_over_Week['totalTestResults_growth'].apply(lambda x: x*100).round(1).astype(str) +'% change vs the week prior)'
df_Week_over_Week['Weekly_New_Cases'] =  'Number of New Cases last week ='+df_Week_over_Week['New_Cases_last_week'].astype(int).astype(str)+' ('  + df_Week_over_Week['positive_growth'].apply(lambda x: x*100).round(1).astype(str) +'% change vs the week prior)'
df_Week_over_Week['Weekly_Deaths'] =  'Number of Deaths last week ='+df_Week_over_Week['Deaths_last_week'].astype(int).astype(str)+' ('  + df_Week_over_Week['death_growth'].apply(lambda x: x*100).round(1).astype(str) +'% change vs the week prior)'
df_Week_over_Week['Weekly_Recovered'] =  'Number of Recovered Cases last week ='+df_Week_over_Week['Recovered_last_week'].astype(int).astype(str)+' ('  + df_Week_over_Week['recovered_growth'].apply(lambda x: x*100).round(1).astype(str) +'% change vs the week prior)'
df_Week_over_Week['Weekly_Hospitalization'] =  'Number of Hospitalizations last week ='+df_Week_over_Week['hospitalized_last_week'].astype(int).astype(str)+' ('  + df_Week_over_Week['hospitalized_growth'].apply(lambda x: x*100).round(1).astype(str) +'% change vs the week prior)'

Weekly_Selection = ['Weekly_Tests', 'Weekly_New_Cases' ,'Weekly_Recovered' ,'Weekly_Deaths', 'Weekly_Hospitalization']
#navigation bar items
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("US Dashboard", href="/US_Dashboard")),
        dbc.NavItem(dbc.NavLink("State Dashboard", href="/State_Dashboard")),
        dbc.NavItem(dbc.NavLink("Forecast Dashboard", href="/Forecast_Dashboard")),
    ],
  #  fill=True,
  #  horizontal = 'center',
   # pills=True
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
            height=600, width=850
            )
    return fig
    
def create_time_graph(data, state):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['date'], y=data['positive'],mode='lines', name='Positive Cases'))
    fig.add_trace(go.Scatter(x=data['date'], y=data['hospitalized'], mode='lines', name='Hospitalized Cases'))
    fig.add_trace(go.Scatter(x=data['date'], y=data['recovered'],mode='lines', name='Recovered Cases'))
    fig.add_trace(go.Scatter(x=data['date'], y=data['death'],mode='lines', name='Deaths'))
    fig.update_layout(title='Daily ' + state + ' COVID-19 Reported Numbers',xaxis_title='Date', height=500, width=850)
    return fig

def marker_selector(metric):
    if metric == 'totalTestResults' :
        return 'rgba(138, 187, 249, 0.9)'#'rgba(74,160,181,0.9)'
    elif metric == 'positive' :
        return 'rgba(247, 195, 68, 0.9)'
    elif metric == 'recovered' :
        return 'rgba(103, 205, 206, 0.9)'# 'rgba(83, 164, 81, 0.9)'
    elif metric == 'death' :
        return 'rgba(204, 68, 75, 0.9)'
    else: 
        return 'rgba(232, 133, 183, 0.9)'


@app.callback(
    Output('top-ten-graph', 'figure'),
    [Input('top-value-select', 'value')]
) 
def top_ten_states(valname):
    marker = marker_selector(valname)
    df_Barchart = recent_state_data.sort_values(valname, ascending=False).head(10)
    trace1 = go.Bar(
            y= df_Barchart['state'],
            x= df_Barchart[valname],orientation="h",
            marker={'color':marker}
            )
    data = [trace1]
    layout = go.Layout(barmode= 'group', plot_bgcolor='rgba(0,0,0,0)',yaxis=dict(autorange="reversed"))
    fig = go.Figure(data = data, layout = layout)
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=marker)
    return fig

def marker_geo_selector(metric):    
    if metric == 'Weekly_Tests' :
        return ['totalTestResults_growth','blues']
    elif metric == 'Weekly_New_Cases' :
        return ['positive_growth','ylorrd']
    elif metric == 'Weekly_Recovered' :
        return ['recovered_growth','emrld']
    elif metric == 'Weekly_Deaths' :
        return ['death_growth','burg']
    elif metric == 'Weekly_Hospitalization' :
        return ['death_growth','sunsetdark']
    else:
        return ['Weekly_New_Cases', 'blues']


us_time_graph = create_time_graph(us_data, 'US')

@app.callback(
    Output('WoW-graph', 'figure'),
    [Input('weekly-select', 'value')]
) 
def WoW_geo(valname):
    value = marker_geo_selector(valname)[0]
    color = marker_geo_selector(valname)[1]
    fig = go.Figure(data=go.Choropleth(
            locations=df_Week_over_Week['state'], # Spatial coordinates
            z = df_Week_over_Week[value], # Data to be color-coded
            hovertext =  df_Week_over_Week[valname],
            #'{:.2f}%'
            #z= df_Week_over_Week['positive_growth'].mul(100).astype(float).astype(str).add('%'),
            locationmode = 'USA-states', # set of locations match entries in `locations`
            colorscale = color ,# colorscale,#'Viridis'
            text=df_Week_over_Week[valname],
            colorbar = dict( tickformat = "%{n}f", tickprefix = '', title = valname)
            #colorbar_title = "Growth in Number of Cases past week"
            ))

    fig.update_layout(
            geo_scope='usa', # limite map scope to USA
            )
    return fig

US_layout = html.Div([
        html.H1('US COVID-19 Dashboard'), 
            html.Br(),
            dbc.Row([dbc.Col(id='card1', children=[total_cases_card]), 
                     dbc.Col(id='card2', children=[total_deaths_card]), 
                     dbc.Col(id='card3', children=[total_hospitalized_card]), 
                     dbc.Col(id='card4', children=[total_recovered_card])]),
            html.Br(),
            dbc.Row([dbc.Col(html.Label('Select Value'), width={"size": 2, "offset": 1}),
                     dbc.Col(dcc.Dropdown(id='value-select', options=[{'label': i, 'value': i} for i in geo_values],
                           value='positive', style={'width': '140px'}), width=2),
                    ],justify="start"),
            dbc.Row([dbc.Col(dcc.Graph('geospatial-graph', config={'displayModeBar': False})), 
                     dbc.Col(dcc.Graph(figure=us_time_graph))]),
            dbc.Row([dbc.Col(html.Label('Select Value')), 
                     dbc.Col(dcc.Dropdown(id='top-value-select', options=[{'label': i, 'value': i} for i in geo_values],
                                          value='positive', style={'width': '140px'})),
                     dbc.Col(html.Label('Select Value')),
                     dbc.Col(dcc.Dropdown(id='weekly-select', options=[{'label': i, 'value': i} for i in Weekly_Selection],
                                          value='Weekly_New_Cases', style={'width': '140px'}))]),
            dbc.Row([dbc.Col(dcc.Graph('top-ten-graph', config={'displayModeBar': False})),
                     dbc.Col(dcc.Graph('WoW-graph', config={'displayModeBar': False}))])
            ])

State_layout = html.Div([
        html.H1('State COVID-19 Dashboard'),
        html.Label('Select State'),
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
    if pathname == '/US_Dashboard':
        return US_layout
    elif pathname == '/State_Dashboard':
        return State_layout
    elif pathname == '/Forecast_Dashboard':
        return Forecast_layout
    else:
        return US_layout
    
#run the app
if __name__ == "__main__":
    app.run_server()