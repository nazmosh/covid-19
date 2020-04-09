import dash
import dash_core_components as dcc 
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd

baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

def loadData (fileName, columnName) :
    data = pd.read_csv(baseURL + fileName) \
        .drop(['Lat', 'Long'], axis=1) \
        .melt (id_vars=['Province/State', 'Country/Region'],
            var_name='date', value_name=columnName) \
        .astype ({'date' : 'datetime64[ns]', columnName: 'Int64'}, 
            errors='ignore')
    data ['Province/State'].fillna('<all>', inplace=True)
    data [columnName].fillna(0, inplace=True)
    return data

allData = loadData(
    "time_series_covid19_confirmed_global.csv", "CumConfirmed").merge (
        loadData(
            "time_series_covid19_deaths_global.csv", "CumDeaths")).merge(
                loadData(
                    "time_series_covid19_recovered_global.csv", "CumRecovered"))

countries = allData ['Country/Region'].unique ()
countries.sort ()


external_stylessheets = ['style.css']

tickFont = {'size':12, 'color':"rgb (30, 30, 30)", \
    'family' : "Courier New, monospace"}

app = dash.Dash (__name__, external_stylesheets = external_stylessheets)

app.layout = html.Div(
    style={'font-family':"Courier New, monospace"}, children=[
        html.H1 ('Case History of the Coronavirus (COVID-19)'),
        html.Div (className="row", children =[
            html.H5 ('Country'), 
            dcc.Dropdown(
                id='country',
                options=[{'label':c, 'value':c} \
                    for c in countries],
                value='Italy'
            )
        ]),
        html.Div(className="four columns", children=[
            html.H5('State /  Province'),
            dcc.Checklist(
                id='metrics',
                options=[{'label':m, 'value':m}
                    for m in ['Confirmed', 'Deaths', 'Recovered']],
                value=['Confirmed', 'Deaths']
            )
        ])
    ]),

dcc.Graph (
    id="plot_new_metrics",
    config={'displayModeBar': False}
),
dcc.Graph (
    id="plot_cum_metrics",
    config={'displayModeBar': False}
)


def nonreactive_data (country, state):
    data = allData.loc[allData['Country/Region'] == country].drop('Country/Region', axis=1)
    if state == '<all>':
        data = data.drop ('Province/State', axis=1).groupby ("date").sum().reset_index()
    else:
        data = data.loc[data['Province/State'] == state]
    newCases = data.select_dtypes(include='Int64').diff().fillna(0)
    newCases.columns = [column.replace('Cum', 'New') for column in newCases.columns]
    
    data = data.join(newCases)
    data['dataStr'] = data['date'].dt.strftime('%b %d, %Y')
    return data

colors = {'Deaths':'rgb(200,30,30)', 'Recovered':'rgb(30,200,30)', 'Confirmed':'rgb(100,140,240)'}

def barchart (data, metrics, prefix="", yaxisTitle=""):
    figure = go.Figure (data=[go.Bar (
        name=metric, x=data.date, y=data[prefix + metric],
        marker_line_color='rgb(0,0,0)', marker_line_width=1,
        marker_color=colors[metric]
    ) for metric in metrics
    ])
    figure.update_layout( barmode='group', legend=dict(x=0.5, y=0.95), plot_bgcolor='#FFFFFF', font=tickFont)\
        .update_xaxes(
        title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date)\
        .update_yaxes(
        title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure




if __name__ == '__main__' :

        result = loadData ('time_series_covid19_confirmed_global.csv', 'Lat')
        print (result)
