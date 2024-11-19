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
    try:
        brewings = BrewingRepository().get_all_brewings()
        # Order by date_start ASC
        brewings.sort(key=lambda x: x['date_start'], reverse=True)
        return brewings
    except Exception as e:
        print("There was an error with the get_brewings method")
        return []

def get_options():
    # Sort by brewing_id desc
    return [{"label": f"{brewing['name']} - Starting {brewing['date_start']}", "value": brewing["brewing_id"]} for brewing in brewings]
brewings = get_brewings()

app.layout = html.Div(style={'backgroundColor': colors['background'], 'padding': '20px'}, children=[
    dcc.Dropdown(
        id="ticker",
        options=get_options(),
        value=brewings[0]['brewing_id'],
        clearable=False,
    ),
    # Add scorecard container
    html.Div(style={
        'display': 'flex',
        'justifyContent': 'space-around',
        'margin': '20px 0'
    }, children=[
        html.Div([
            html.H3('Current Metrics', style={'color': colors['text'], 'textAlign': 'center'}),
            html.Div(id='current-metrics', style={
                'display': 'flex',
                'gap': '20px',
                'justifyContent': 'center'
            })
        ])
    ]),
    dcc.Graph(id="main-line-chart"),
    html.H2(
        children='Hourly increment of alcohol',
        style={
            'textAlign': 'center',
            'color': colors['text'],
            'background': colors['background']
        }
    ),
    dcc.Graph(id="increments-bar-chart"),
    dcc.Interval(
        id='interval-component',
        interval=60*1000*15,
        n_intervals=0
    )
])



@app.callback(
    Output("main-line-chart", "figure"), 
    Output("increments-bar-chart", "figure"),
    Output("current-metrics", "children"),
    Input("ticker", "value"),
    Input('interval-component', 'n_intervals'))
def update_charts(ticker, n_intervals):
    print(f"ticker: {ticker}")
    brewing = next((item for item in brewings if item["brewing_id"] == ticker), None)
    if brewing is None:
        return None, None, None

    ping_repository = PingRepository()
    pings = ping_repository.get_metrics_history(date_start=brewing['date_start'], date_end=brewing['date_end'])
    pings_df = pd.DataFrame(pings) 

    increments = ping_repository.get_metrics_increments(date_start=brewing['date_start'], date_end=brewing['date_end'])
    increments_df = pd.DataFrame(increments)

    # Create scorecards for current metrics
    current_metrics = []
    if len(pings_df) > 0:
        latest_data = pings_df.iloc[0]
        metrics = [
            {'name': 'Alcohol', 'value': f"{latest_data['alcool']:.2f}%", 'color': '#4CAF50'},
            {'name': 'Density', 'value': f"{latest_data['gravity']:.3f}", 'color': '#2196F3'},
            {'name': 'Temperature', 'value': f"{latest_data['temperature']:.1f}°C", 'color': '#FF9800'}
        ]
        
        current_metrics = [
            html.Div([
                html.H4(metric['name'], style={'color': colors['text'], 'margin': '0'}),
                html.Div(metric['value'], style={
                    'fontSize': '24px',
                    'fontWeight': 'bold',
                    'color': metric['color'],
                    'padding': '10px',
                    'borderRadius': '5px',
                    'backgroundColor': '#2a2a2a',
                    'margin': '5px 0'
                })
            ], style={'textAlign': 'center'})
            for metric in metrics
        ]

    return display_time_series(pings_df, 'date_formatted', ["gravity", "alcool"]), \
           display_bar_chart(increments_df, 'datetime_plus', ["alcool_increment", "density_increment"]), \
           current_metrics


def display_bar_chart(data, x, y):
    fig = go.Figure()
    if len(data) == 0:
        return fig
    # fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=data[x],
        y=data[y[0]],
        name=y[0],
        marker_color='indianred',
        yaxis="y"
    ))    
    # fig.add_trace(go.Scatter(
    #     x=data[x],
    #     y=data[y[1]],
    #     name=y[1],
    #     marker_color='blue',
    #     yaxis="y2"
    # ))

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin=dict(l=0, r=0, t=10, b=0)
        )
    
    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            # title=dict(text="Alcool Increment"),
            side="left",
        ),
        yaxis2=dict(
            # title=dict(text="Density increment"),
            side="right",
            overlaying="y",
            tickmode="sync",
        ),
    )
    return fig


def display_time_series(data, x, y):
    if len(data) == 0:
        data = pd.DataFrame(columns=[x, *y])

    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data[x],
        y=data[y[0]],
        name=y[0],
        mode='lines+markers'
    ))
    
    if len(y) > 1:
        fig.add_trace(go.Scatter(
            x=data[x],
            y=data[y[1]],
            name=y[1],
            mode='lines+markers',
            yaxis="y2"
        ))

    fig.update_layout(
        plot_bgcolor=colors['background'],
        paper_bgcolor=colors['background'],
        font_color=colors['text'],
        margin=dict(l=0, r=0, t=20, b=0),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="right",
            x=1
        ),
        yaxis=dict(
            # title=dict(text="Alcool Increment"),
            side="left",
        ),
        yaxis2=dict(
            # title=dict(text="Density increment"),
            side="right",
            overlaying="y",
            tickmode="sync",
        ),
    )

    
    return fig

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8050)))