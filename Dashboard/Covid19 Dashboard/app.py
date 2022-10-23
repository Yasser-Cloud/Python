#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 27 17:58:50 2021

@author: mahmoud
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pycountry as pc

import dash
from dash import html
from dash import dcc
import plotly.express as px
import pandas as pd
from dash.dependencies import Input,Output,State



def to_snakecase (cols):
  map_dict = {}
  for col in cols:
    map_dict[col] = col.lower().strip().replace(' ', '_')
  return map_dict

def normalize_country (data):
  if pc.countries.get(official_name=data):
    return pc.countries.get(official_name=data).name
  elif pc.countries.get(name=data):
    return pc.countries.get(name=data).name
  elif pc.countries.get(alpha_3=data):
    return pc.countries.get(alpha_3=data).name
  elif pc.countries.get(alpha_2=data):
    return pc.countries.get(alpha_2=data).name


hci_df = pd.read_csv('hci_MaleFemale_september_2020.csv', 
                     usecols=['Country Name', 'Income Group', 
                              'Expected Years of School'])
covid_df = pd.read_csv('Covid_19.csv',  usecols=[ 1,2, 3, 4, 5, 6,12,14])

#print(covid_df.head()) # Worldometer's Daily Snapshots
#print(hci_df.head()) # 2020 Human Capital Index

covid_df.rename(to_snakecase(covid_df.columns), axis=1, inplace=True)
covid_df.country = covid_df.country.apply(normalize_country)


hci_df.rename(to_snakecase(hci_df.columns), axis=1, inplace=True)
hci_df.rename({'country_name':'country'}, axis=1, inplace=True)
hci_df.country = hci_df.country.apply(normalize_country)


#print(covid_df.head()) # Worldometer's Daily Snapshots
#print(hci_df.head()) # 2020 Human Capital Index

data = pd.merge(left=covid_df, right=hci_df, on='country')
data = data[data.country.notnull()].reset_index(drop=True)
print(data.columns)






########## Dash part ################




external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__ ,external_stylesheets= external_stylesheets)

colors = {
    'background': '#FFFFFF',
    'text': '#7FDBFF'
}

dash_colors = {
    'background': '#111111',
    'text': '#BEBEBE',
    'grid': '#333333',
    'red': '#BF0000',
    'blue': '#466fc2',
    'green': '#5bc246'
}

# Defining App Layout 

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
      html.H1('Studying The Pandemic Worldwide', style={'textAlign':'center'}),
        html.Div([ html.Div(dcc.Graph(id='confirmed_ind'),
        style={
            'textAlign': 'center',
            'color': dash_colors['red'],
            'width': '25%',
            
            'display': 'inline-block'
            }
        ),
      html.Div(dcc.Graph(id='active_ind'),
        style={
            'textAlign': 'center',
            'color': dash_colors['red'],
            
            'width': '30%',
           
            'display': 'inline-block'
            }
        ),
      html.Div(dcc.Graph(id='unemploy_ind'),
        style={
            'textAlign': 'center',
            'color': dash_colors['red'],
            'width': '25%',
            
            'display': 'inline-block'
            }
        )], style={
            
            'color': dash_colors['red'],
            
            'margin':'auto',
            'textAlign' : 'center'
            
            
            }),
      html.Div([
        
          html.Div([ 
              html.Label('Population'),
              dcc.Slider(
                  id='population-slider',
                  min=data.population.min(),
                  max=data.population.max(),
                  marks={
                    72037 : '72K',
                    80000000 : '80M',
                    150000000 : '150M',
                    300000000 : '300M',
                    700000000 : '700M',
                    1000000000 : '1B',
                    1439323776 : '1.4B' 
                  },
                  value=80000000,
                  step=100000000,
                  updatemode='drag'
              )
          ]),
          html.Div([
              html.Label('Interest Variable'),
              dcc.Dropdown(
                  id='interest-variable',
                  options=[{'label':'Total Cases', 'value':'total_cases'},
                           {'label': 'Total Tests', 'value':'total_tests'},
                           {'label': 'Total Deaths', 'value':'total_deaths'},
                           {'label': 'Total Recovered', 'value':'total_recovered'}],
                  value='total_cases' 
              )
          ])
      ], style = {'width':'90%','margin':'auto'}),      
      html.Div([ 
              dcc.Graph(
                  id='covid-vs-edu',
              ),    
          html.Div(
              dcc.Graph(
                  id='covid-vs-income',
              )
      , style = {'width': '50%', 'display': 'inline-block'}),
          html.Div( 
              dcc.Graph(
                  id='covid-vs-income2',
              )
      , style = {'width': '50%', 'display': 'inline-block'})
      ], style = {'width':'90%','margin':'auto'})
])

def scatter_y_label (var):
  if var == 'total_cases':
    return 'Percentage Infected'
  elif var == 'total_tests':
    return 'Percentage Tested'
  elif var == 'total_deaths':
    return 'Percentage Dead'
  elif var == 'total_recovered':
    return 'Percentage Recovered'

# Variable VS Education Level Scatter Plot

@app.callback(Output('covid-vs-edu', 'figure'),
              [Input('population-slider', 'value'),
               Input('interest-variable', 'value')])             
def update_scatter(selected_pop, interest_var):
  sorted = data[data.population <= selected_pop]
  fig = px.scatter(sorted,
                  x='expected_years_of_school',
                  y=sorted[interest_var]/sorted.population,
                  size='population',
                  color='income_group',
                  hover_name='country',
                  template='simple_white',
                  labels={'expected_years_of_school':'Expected Years of School',
                          'y': scatter_y_label(interest_var)},
                  title='Total Cases VS Education Level')
  fig.update_layout(transition_duration=500)
  return fig

# Variable Per Income Group Bar Chart

@app.callback(Output('covid-vs-income', 'figure'),
              [Input('population-slider', 'value'),
               Input('interest-variable', 'value')])             
def update_income_bar(selected_pop, interest_var):
  sorted = data[data.population <= selected_pop].groupby(by='income_group').sum().reset_index()
  fig = px.bar(sorted,
                  x='income_group',
                  y=interest_var,
                  color='income_group',
                  template='simple_white',
                  labels={'income_group':'Income Group',
                          'total_cases':'Total Cases',
                          'total_tests':'Total Tests',
                          'total_deaths':'Total Deaths',
                          'total_recovered':'Total Recovered'},
                  title='Total Cases By Income Group')
  fig.update_layout()
  return fig

# Variable Per Country Bar Chart

@app.callback(Output('covid-vs-income2', 'figure'),
              [Input('population-slider', 'value'),
               Input('interest-variable', 'value')])             
def update_country_bar(selected_pop, interest_var):
  sorted = data[data.population <= selected_pop]
  fig = px.bar(sorted, 
                x='country', 
                y=interest_var, 
                color='income_group',
                template='simple_white',
                labels={'country':'Country',
                        'total_cases':'Total Cases',
                        'total_tests':'Total Tests',
                        'total_deaths':'Total Deaths',
                        'total_recovered':'Total Recovered'},
                title='Total Cases per Country')
  fig.update_layout()
  return fig


@app.callback(
    Output('confirmed_ind', 'figure'),
    [Input('population-slider', 'value')])
def confirmed(view):
    

    value = covid_df.iloc[0,1]
    
    
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': 244808452,
                              'valueformat': ',',
                              'relative': False,
                              'increasing': {'color': dash_colors['blue']},
                              'decreasing': {'color': dash_colors['green']},
                              'font': {'size': 25}},
                    'number': {'valueformat': ',',
                              'font': {'size': 50,'color':'#466fc2'}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "Total Cases"},
                font=dict(color='#4169E1'),
                paper_bgcolor=colors['background'],
                plot_bgcolor= colors['background'],
                height=200
                )
            }

@app.callback(
    Output('active_ind', 'figure'),
    [Input('population-slider', 'value')])
def death(view):
    

    value = covid_df.iloc[0,3]
    delta = covid_df[covid_df.iloc[:,3] 
                     == covid_df.iloc[:,3].unique()[-2]]['total_deaths'].sum()
    
   
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': 4970210,
                              'valueformat': ',',
                              'relative': False,
                              'increasing': {'color': dash_colors['red']},
                              'decreasing': {'color': dash_colors['green']},
                              'font': {'size': 25}},
                    
                    'number': {'valueformat': ',',
                              'font': {'size': 50}},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "Total Deaths"},
                font=dict(color=dash_colors['red']),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                height=200
                )
            }


@app.callback(
    Output('unemploy_ind', 'figure'),
    [Input('population-slider', 'value')])
def unemploy(view):
    

    value = 6.47
    
   
    return {
            'data': [{'type': 'indicator',
                    'mode': 'number+delta',
                    'value': value,
                    'delta': {'reference': 5.37,
                              'valueformat': '.1f',
                              'relative': False,
                              'increasing': {'color': dash_colors['blue']},
                              'decreasing': {'color': dash_colors['green']},
                              'font': {'size': 25},
                              },
                    
                    'number': {'valueformat': ',',
                              'font': {'size': 50},
                              'suffix': "%"},
                    'domain': {'y': [0, 1], 'x': [0, 1]}}],
            'layout': go.Layout(
                title={'text': "Unemployment Rate"},
                font=dict(color='#4169E1'),
                paper_bgcolor=colors['background'],
                plot_bgcolor=colors['background'],
                height=200
                )
            }

if __name__ == '__main__':
    app.run_server(debug=False,use_reloader=False)




