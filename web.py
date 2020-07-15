import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import pandas as pd
import kody
from dash_table.Format import Format, Scheme, Sign, Symbol
from datetime import datetime as dt
from dash.dependencies import Input, Output
import datetime
import yfinance as yf
import numpy as np
import time

app = dash.Dash(__name__, suppress_callback_exceptions=True) #jinak callback nefunguje u multipage apps
server = app.server
app.title = "StepanH"

colors = {
    "background": "black",
    "text": "#ff8000",
    "button_background" : "#663300",
    "button_text" : "#01ff70",
    "button_border" : "1px solid #ff8000",
}

data_frame_news = pd.read_sql('SELECT source, published, title, url, sentiment FROM newsGILD ORDER BY published ASC', con=kody.cnx)
data_frame_news["ma_short"] = data_frame_news.sentiment.rolling(window=5).mean()
data_frame_news["ma_long"] = data_frame_news.sentiment.rolling(window=10).mean()
data_frame_news['epoch'] = data_frame_news['published'].astype(np.int64)
data_frame_for_news = data_frame_news
#data_frame = data_frame.iloc[::100] #zobrazí každý n-tý bod v data-framu    
print(data_frame_for_news)

def get_data(table_name):
    data_frame = pd.read_sql('SELECT time, username, tweet, followers,  sentiment FROM '+ table_name +' ORDER BY time ASC', con=kody.cnx)
    data_frame["ma_short"] = data_frame.sentiment.rolling(window=1000).mean()
    data_frame["ma_long"] = data_frame.sentiment.rolling(window=10000).mean()
    data_frame['epoch'] = data_frame['time'].astype(np.int64)
    data_frame = data_frame.iloc[::100] #zobrazí každý n-tý bod v data-framu
    return data_frame

gild = yf.download("GILD")
data_gild = pd.DataFrame(data=gild)

fig_gild = px.scatter(render_mode="webgl")
fig_gild.add_scatter(y=data_gild["Close"], mode="lines", name="Gild closing price")
fig_gild.update_layout(title_text="GILD stock price",
                    title_x=0.5,
                    template="plotly_dark", 
                    legend_title_text="", 
                    legend_orientation="h", 
                    legend=dict(x=0, y=1))

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index = html.Div(style={"backgroundColor": "black"},children=[
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('GILD sentiment', href='/GILD_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.H1(
    children='index',
    style={
        "color": colors["text"],
        "textAlign": "center"
        }),
])

twitter_sentiment = html.Div(style={"backgroundColor": colors["background"]}, children=[
    
    html.Div(id='page-1-content'),
    html.Button(dcc.Link('Index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('GILD sentiment', href='/GILD_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    
    html.H1(
    children='Twitter sentiment',
    style={
        "color": colors["text"],
        "textAlign": "center"
        }),
    
    html.Div([
        dcc.Graph(id='chart-with-slider'),
        dcc.Slider(
        id='year-slider',
        min=1593560870000000000,
        max=time.time()*10**9,
        value=1593560870000000000,
        #value=(time.time()-50400)*30**9,
        ),
    dcc.Interval(
            id='interval-component-chart',
            interval=10*1000, # in milliseconds
            n_intervals=0
        )    
    ]),

    html.Div(dash_table.DataTable(
        id="table",
        columns=[{
            "id" : "username",
            "name" : "Username",
            "type" : "text"
            },{
            "id" : "followers",
            "name" : "Followers",
            "type" : "text"
            },{
            "id" : "time",
            "name" : "Time",
            "type" : "datetime"
            },{
            "id" : "tweet",
            "name" : "Tweet",
            "type" : "text"
            },{
            "id" : "sentiment",
            "name" : "Sentiment",
            "type" : "numeric",
            "format" : Format(
                precision = 5,
            ),
            }],

        filter_action='native',
        css=[{'selector': '.dash-filter > input', 'rule': 'color: #01ff70; text-align : left'}],
        style_filter={"backgroundColor" : "#663300"}, #styly filtrů fungujou divně proto je zbytek přímo v css
        data=get_data("tweetTable").to_dict('records'),
        fixed_rows={ 'headers': True, 'data': 0 },
        sort_action="native",
        page_size= 10,
        style_header={
            "fontWeight" : "bold",
            "textAlign" : "center"
        },
        style_cell={
            "textAlign" : "left",
            "backgroundColor" : colors["background"],
            "color" : colors["text"],

        },
        style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
        'maxWidth': '500px',
        'minWidth': '50px',
        },
        style_cell_conditional=[
            {
            'if': {'column_id': 'followers'},
            'width': '90px'
            },
            {
            'if': {'column_id': 'time'},
            'width': '90px'
            },
        ],
        style_as_list_view=True,
        virtualization=True,
        page_action="none"
        ),style={
            #"width": "48%",
            #"align": "right",
            #"display": "inline-block"
            }),

    html.Div(dcc.Graph(id="chart_gild",figure=fig_gild)),

    dcc.Interval(
        id="interval-component",
        interval=1000
    ),

    # html.Iframe(srcDoc='''
    # <div class="tradingview-widget-container">
    # <div id="tradingview_20db9"></div>
    # <div class="tradingview-widget-copyright"><a href="https://www.tradingview.com/symbols/NASDAQ-AAPL/" rel="noopener" #target="_blank"><span class="blue-text">AAPL Chart</span></a> by TradingView</div>
    # <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    # <script type="text/javascript">
    # new TradingView.widget(
    # {
    # "height": 700,
    # "width" : 900,
    # "symbol": "NASDAQ:GILD",
    # "interval": "D",
    # "timezone": "Etc/UTC",
    # "theme": "dark",
    # "style": "1",
    # "locale": "en",
    # "toolbar_bg": "#f1f3f6",
    # "enable_publishing": false,
    # "allow_symbol_change": true,
    # "container_id": "tradingview_20db9"               source, published, title, url, sentiment
    # }
    # );
    # </script>''', style={
    #                 "height": 700,
    #                 "width" : 900
    #                 })
])

GILD_sentiment = html.Div(style={"backgroundColor": "black"},children=[
    html.Div(id='page-2-content'),
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.H1(children='GILD Sentiment',
        style=
        {
        "color": colors["text"],
        "textAlign": "center"
        }),
    html.Div([
        dcc.Graph(id='chart-with-slider-news'),
        dcc.Slider(
        id='year-slider',
        min=1594412760000000000,
        max=time.time()*10**9,
        value=1593560870000000000,
        #value=(time.time()-50400)*30**9,
        ),
    ]),
    html.Div(dash_table.DataTable(
        id="table",
        columns=[{
            "id" : "source",
            "name" : "Source",
            "type" : "text"
            },{
            "id" : "published",
            "name" : "Published",
            "type" : "datetime"
            },{
            "id" : "title",
            "name" : "Title",
            "type" : "text"
            },{
            "id" : "url",
            "name" : "url",
            "type" : "text"
            },{
            "id" : "sentiment",
            "name" : "Sentiment",
            "type" : "numeric",
            "format" : Format(
                precision = 5,
            ),
            }],

        filter_action='native',
        css=[{'selector': '.dash-filter > input', 'rule': 'color: #01ff70; text-align : left'}],
        style_filter={"backgroundColor" : "#663300"}, #styly filtrů fungujou divně proto je zbytek přímo v css
        data=data_frame_news.to_dict('records'),
        fixed_rows={ 'headers': True, 'data': 0 },
        sort_action="native",
        page_size= 10,
        style_header={
            "fontWeight" : "bold",
            "textAlign" : "center"
        },
        style_cell={
            "textAlign" : "left",
            "backgroundColor" : colors["background"],
            "color" : colors["text"],

        },
        style_data={
        'whiteSpace': 'normal',
        'height': 'auto',
        'maxWidth': '500px',
        'minWidth': '50px',
        },
        style_cell_conditional=[
            {
            'if': {'column_id': 'followers'},
            'width': '90px'
            },
            {
            'if': {'column_id': 'time'},
            'width': '90px'
            },
        ],
        style_as_list_view=True,
        virtualization=True,
        page_action="none"
        ),style={
            #"width": "48%",
            #"align": "right",
            #"display": "inline-block"
            }),
    
])

@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])     #callbak pro víc stránek
def display_page(pathname):
    if pathname == '/twitter_sentiment':
        return twitter_sentiment
    elif pathname == '/GILD_sentiment':
        return GILD_sentiment
    else:
        return index

old_fig = None
@app.callback(
    Output('chart-with-slider', 'figure'),
    [Input('year-slider', 'value'),Input('interval-component-chart', 'n_intervals'),]) #Zavolá tu funkci update_figure(valuecasu, n_intrval) - callback pro slider a auto-update grafu
def update_figure(selected_time, n_interval):
    global old_fig
    if n_interval % 2 == 1:
        return old_fig
    else:
        data_frame = get_data("tweetTable")
        data_frame_filtered = data_frame[data_frame.epoch > selected_time]
        #data_frame_filtered_scatter = data_frame.tail(30) #zobrazí posledních n-tweetů v grafu jako body*
        fig = px.scatter()
        #fig.add_scatter(x=data_frame_filtered_scatter["time"], y=data_frame_filtered_scatter["sentiment"], mode="markers", name="sentiment", marker={"size":4}, text=data_frame["tweet"]) #*
        fig.add_scatter(x=data_frame_filtered["time"], y=data_frame["ma_short"], mode="lines", name="1k tweets MA")
        fig.add_scatter(x=data_frame_filtered["time"], y=data_frame["ma_long"], mode="lines", name="10k tweets MA")
        fig.update_layout(title_text="xrp OR ripple",
                            title_x=0.5,
                            template="plotly_dark", 
                            legend_title_text="", 
                            legend_orientation="h", 
                            legend=dict(x=0, y=1.1))
        fig.update_layout(transition_duration=500)
        #print("Pocet tweetu v db: ", len(data_frame["time"]))
        old_fig = fig
        return fig

old_data = get_data("tweetTable").to_dict("records")
@app.callback(dash.dependencies.Output('table', 'data'),
              [dash.dependencies.Input('interval-component-chart', 'n_intervals')])
def update_table(n_interval):
    global old_data
    if n_interval % 2 == 1:
        old_data = get_data("tweetTable").to_dict('records')
        return old_data
    else:
        return old_data

@app.callback(
    Output('chart-with-slider-news', 'figure'),
    [Input('year-slider', 'value'),]) #Zavolá tu funkci update_figure(valuecasu, n_intrval) - callback pro slider a auto-update grafu
def update_news_figure(selected_time):
    data_frame_news = data_frame_for_news.to_dict('records')
    data_frame_news_filtered = data_frame_for_news[data_frame_for_news.epoch > selected_time]
    data_frame_news_filtered_scatter = data_frame_for_news.tail(100) #zobrazí posledních n-tweetů v grafu jako body*
    fig_newsGILD = px.scatter()
    fig_newsGILD.add_scatter(x=data_frame_news_filtered_scatter["published"], y=data_frame_news_filtered_scatter["sentiment"], mode="markers", name="sentiment", marker={"size":4}, text=data_frame_for_news["title"]) #*
    fig_newsGILD.add_scatter(x=data_frame_news_filtered["published"], y=data_frame_for_news["ma_short"], mode="lines", name="Short MA")
    fig_newsGILD.add_scatter(x=data_frame_news_filtered["published"], y=data_frame_for_news["ma_long"], mode="lines", name="Long MA")
    fig_newsGILD.update_layout(title_text="GILD OR Gilead OR Remdesivir - newsAPI",
                        title_x=0.5,
                        template="plotly_dark", 
                        legend_title_text="", 
                        legend_orientation="h", 
                        legend=dict(x=0, y=1.1))
    fig_newsGILD.update_layout(transition_duration=500)
    #print("Pocet tweetu v db: ", len(data_frame["time"]))
    return fig_newsGILD
    
if __name__ == '__main__':
    app.run_server(debug=True, host="192.168.1.150")
