# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from models.ping_repository import PingRepository

import os
from dotenv import load_dotenv

load_dotenv()
assets_path = os.getcwd() + "/viz/assets"
app = Dash(assets_folder=assets_path)
server = app.server
colors = {
    'background': '#161a1d',
    'text': '#ffffff'
}

ping_repository = PingRepository()

pings = ping_repository.get_metrics_history()
pings_df = pd.DataFrame(pings)

increments = ping_repository.get_metrics_increments()
increments_df = pd.DataFrame(increments)


def get_devices():
    devices = pings_df['device_id'].unique()
    return devices

print(get_devices())

app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px'}, children=[
    html.H1(
        children='iSpindel Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'background': colors['background']
        }
    ),
    html.P("Select Device:"),
    dcc.Dropdown(
        id="ticker",
        options=get_devices(),
        value=get_devices()[0],
        clearable=False,
    ),
    dcc.Graph(id="main-line-chart"),
    html.H2(
        children='Density evolution over time',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'background': colors['background']
        }
    ),
    dcc.Graph(id="gravity-line-chart"),
    html.H2(
        children='Daily increment of density and alcohol content',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'background': colors['background']
        }
    ),
    dcc.Graph(id="increments-bar-chart"),
])

@app.callback(
    Output("main-line-chart", "figure"), 
    Input("ticker", "value"))
def display_main_line(ticker):
    filtered = pings_df[pings_df['device_id'] == ticker]
    return display_time_series(filtered, 'date_formatted', ["gravity", "alcool"])

@app.callback(
    Output("gravity-line-chart", "figure"), 
    Input("ticker", "value"))
def display_main_line(ticker):
    filtered = pings_df[pings_df['device_id'] == ticker]
    return display_time_series(filtered, 'date_formatted', ["gravity"])

@app.callback(
    Output("increments-bar-chart", "figure"), 
    Input("ticker", "value"))
def display_increments(ticker):
    filtered = increments_df[increments_df['device_id'] == ticker]
    return display_bar_chart(filtered, 'date', ["alcool_increment", "density_increment"])

def display_bar_chart(data, x, y):
    fig = go.Figure()
    # fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=data[x],
        y=data[y[0]],
        name=y[0],
        marker_color='indianred'
    ))    
    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[y[1]],
        name=y[1],
        marker_color='blue',
        yaxis="y2"
    ))

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
        )
    fig.update_layout(
        legend=dict(orientation="h"),
        yaxis=dict(
            title=dict(text="Alcool Increment"),
            side="left",
        ),
        yaxis2=dict(
            title=dict(text="Density increment"),
            side="right",
            overlaying="y",
            tickmode="sync",
        ),
    )
    return fig


def display_time_series(data, x, y):
    fig = px.line(data, x=x, y=y, markers=True)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
        )
    return fig

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))