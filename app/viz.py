# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.


from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from plotly.subplots import make_subplots

from models.ping_repository import PingRepository
from models.brewing_repository import BrewingRepository
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

def get_brewings():
    brewings = BrewingRepository().get_all_brewings()
    # Order by date_start ASC
    brewings.sort(key=lambda x: x['date_start'])

    return brewings

def get_options():
    brewings = get_brewings()
    return [{"label": f"{brewing['name']} - Starting {brewing['date_start']}", "value": brewing["brewing_id"]} for brewing in brewings]
brewings = get_brewings()

app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px'}, children=[
    html.H1(
        children='iSpindel Dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'background': colors['background']
        }
    ),
    html.P("Select Brewing:"),
    dcc.Dropdown(
        id="ticker",
        options=get_options(),
        value=brewings[0]['brewing_id'],
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
    Output("gravity-line-chart", "figure"), 
    Output("increments-bar-chart", "figure"), 
    Input("ticker", "value"))
def update_charts(ticker):
    print(f"ticker: {ticker}")
    brewing = next((item for item in brewings if item["brewing_id"] == ticker), None)
    if brewing is None:
        return None, None, None

    ping_repository = PingRepository()
    pings = ping_repository.get_metrics_history(date_start=brewing['date_start'], date_end=brewing['date_end'])
    pings_df = pd.DataFrame(pings) 

    increments = ping_repository.get_metrics_increments(date_start=brewing['date_start'], date_end=brewing['date_end'])
    increments_df = pd.DataFrame(increments)


    return display_time_series(pings_df, 'date_formatted', ["gravity", "alcool"]), display_time_series(pings_df, 'date_formatted', ["gravity"]), display_bar_chart(increments_df, 'date', ["alcool_increment", "density_increment"])


def display_bar_chart(data, x, y):
    fig = go.Figure()
    if len(data) == 0:
        return fig
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
    if len(data) == 0:
        data = pd.DataFrame(columns=[x, *y])

    fig = px.line(data, x=x, y=y, markers=True)
    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text']
        )
    return fig

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))