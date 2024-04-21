# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd


from models.ping_repository import PingRepository

import os
from dotenv import load_dotenv

pt = 'config/.env'
load_dotenv(pt)

assets_path = os.getcwd() + "/app/viz/assets"
print(assets_path)

app = Dash(assets_folder=assets_path)

colors = {
    'background': '#161a1d',
    'text': '#ffffff'
}

pings = PingRepository().get_metrics_history()
pings_df = pd.DataFrame(pings)


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

def display_time_series(data, x, y):
    fig = px.line(data, x=x, y=y, markers=True)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
        )
    return fig

if __name__ == '__main__':
    app.run(debug=True)