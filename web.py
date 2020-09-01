import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import kody
from dash_table.Format import Format, Scheme, Sign, Symbol
from datetime import datetime as dt
from dash.dependencies import Input, Output
import datetime
import yfinance as yf
import numpy as np
import time
from dateutil.relativedelta import relativedelta
from layouts import portfolio
import mysql.connector

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
def get_data_news():
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    data_frame_newsGILD = pd.read_sql('SELECT source, published, title, url, sentiment, sentiment_vader FROM newsGILD ORDER BY published DESC', con=cnx)
    data_frame_newsGILD["ma_short"] = data_frame_newsGILD.sentiment.rolling(window=10).mean()
    data_frame_newsGILD["ma_long"] = data_frame_newsGILD.sentiment.rolling(window=30).mean()
    data_frame_newsGILD["vader_ma_short"] = data_frame_newsGILD.sentiment_vader.rolling(window=10).mean()
    data_frame_newsGILD["vader_ma_long"] = data_frame_newsGILD.sentiment_vader.rolling(window=30).mean()
    data_frame_newsGILD['epoch'] = data_frame_newsGILD['published'].astype(np.int64)
    data_frame_newsGILD["volume"] = 1
    links = data_frame_newsGILD['url'].to_list()
    rows = []
    for x in links:
        link = '[link](' +str(x) + ')'
        rows.append(link)#
    data_frame_newsGILD['url'] = rows
    return data_frame_newsGILD

def get_data_news_volume():
    df_G_volume = get_data_news().set_index(['published']).resample('720min').agg({'volume': np.sum, 'sentiment': np.mean,'sentiment_vader': np.mean})
    df_G_volume["epoch"] =  df_G_volume.index.astype(np.int64)
    return df_G_volume


def get_data(table_name):
    data_frame = pd.read_sql('SELECT time, username, tweet, followers,  sentiment, sentiment_vader FROM '+ table_name +' ORDER BY time ASC', con=kody.cnx)
    data_frame["ma_short"] = data_frame.sentiment.rolling(window=1000).mean()
    data_frame["ma_long"] = data_frame.sentiment.rolling(window=10000).mean()
    data_frame["vader_ma_short"] = data_frame.sentiment_vader.rolling(window=10).mean()
    data_frame["vader_ma_long"] = data_frame.sentiment_vader.rolling(window=100).mean()    
    data_frame['epoch'] = data_frame['time'].astype(np.int64)
    data_frame = data_frame.iloc[::100] #zobrazí každý n-tý bod v data-framu
    print("Get data called on ", table_name, " at: ", time.time())
    return data_frame
#print("dataframetweetTable",get_data("tweetTable")["time"])

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

now_minus_one_hour = dt.now() - relativedelta(hours=1)
data_frame_is_it_running = pd.read_sql('SELECT script, time FROM running_scripts ORDER BY time ASC', con=kody.cnx)
data_frame_is_it_running["status"] = np.where(data_frame_is_it_running["time"] > now_minus_one_hour, "YES","NO")

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index = html.Div(style={"backgroundColor": "black"},children=[
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('GILD sentiment', href='/GILD_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Running Scripts', href='/running_scripts',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"], "float":"right"}),
    html.H1(
    children='index',
    style={
        "color": colors["text"],
        "textAlign": "center"
        }),
    html.Button(html.A('GitHub Code', href='https://github.com/HSTEP/twitter_sentiment', target='_blank'), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
])

twitter_sentiment = html.Div(style={"backgroundColor": colors["background"]}, children=[
    
    html.Div(id='page-1-content'),
    html.Button(dcc.Link('Index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('GILD sentiment', href='/GILD_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Running Scripts', href='/running_scripts',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"], "float":"right"}),
    html.H1(
        children='Twitter sentiment',
        style={
            "color": colors["text"],
            "textAlign": "center"
            }
        ),
    
    html.Div(
        [
            dcc.Checklist(
                id = 'sentiment_ma',
                options = [
                    {"label" : "Long MA TextBlob", "value" : "long_ma"},
                    {"label" : "Short MA TextBlob", "value" : "short_ma"},
                    {"label" : "Long MA Vader", "value" : "vader_ma_long"},
                    {"label" : "Short MA Vader", "value" : "vader_ma_short"},
                    {"label" : "Scatter TextBlob", "value" : "scatter"}
                ],
                value = ["scatter"],
                labelStyle = {"display" : "inline-block", "background-color": colors["button_background"], "color" : colors["button_text"], "border" : "black"}
            ),
        ],
    ),

    html.Div([
        dcc.Graph(id='chart-with-slider'),
        dcc.Slider(
        id='year-slider',
        min=1593560870000000000,
        max=time.time()*10**9,
        value=time.time()*10**9 - 259200*10**9,
        step=86400*10**9,
        ),
    dcc.Interval(
            id='interval-component-chart',
            interval=30*1000, # in milliseconds
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
        interval=30*1000
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
    html.Button(dcc.Link('index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Running Scripts', href='/running_scripts',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"], "float":"right"}),
    html.H1(children='GILD Sentiment',
        style=
        {
        "color": colors["text"],
        "textAlign": "center"
        }),
    html.Div(
        [
            dcc.Checklist(
                id = 'checklist_gild',
                options = [
                    {"label" : "Long MA TextBlob", "value" : "long_ma"},
                    {"label" : "Short MA TextBlob", "value" : "short_ma"},
                    {"label" : "Long MA Vader", "value" : "vader_ma_long"},
                    {"label" : "Short MA Vader", "value" : "vader_ma_short"},
                    {"label" : "Scatter TextBlob", "value" : "scatter"}
                ],
                value = ["scatter"],
                labelStyle = {"display" : "inline-block", "background-color": colors["button_background"], "color" : colors["button_text"], "border" : "black"}
            ),
        ],
    ),    
    html.Div([dcc.Graph(id='chart-with-slider-news'),
        dcc.Slider(
        id='year-slider',
        min=1594412760000000000,
        max=time.time()*10**9,
        value=time.time()*10**9 - 432000*10**9,
        step=86400*10**9,
        ),
    dcc.Interval(
            id='interval-component-news-chart',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )
        ], style={'width': '69%', 'display': 'inline-block'}),

    html.Div(html.Img(src=app.get_asset_url('wordcloud_news_gild.svg'), height = "500px"),style={'width': '29%', 'display': 'inline-block'}),

    html.Div(dash_table.DataTable(
        id="table_newsGILD",
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
            "type" : "text",
            "presentation" : "markdown"
            },{
            "id" : "sentiment",
            "name" : "TextBlob",
            "type" : "numeric",
            "format" : Format(
                precision = 5,
            )},{
            "id" : "sentiment_vader",
            "name" : "Vader",
            "type" : "numeric",
            "format" : Format(
                precision = 5,
            ),}
            ],

        filter_action='native',
        css=[{'selector': '.dash-filter > input', 'rule': 'color: #01ff70; text-align : left'}],
        style_filter={"backgroundColor" : "#663300"}, #styly filtrů fungujou divně proto je zbytek přímo v css
        data=get_data_news().to_dict('records'),
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
    dcc.Interval(
        id='interval-component-newsGILD',
        interval=70*1000, # in milliseconds
        n_intervals=0
    )
])

running_scripts = html.Div(style={"backgroundColor": "black"},children=[
    html.Button(dcc.Link('Index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('GILD sentiment', href='/GILD_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.H1(
    children='Running Scripts',
    style={
        "color": colors["text"],
        "textAlign": "center"
        }),
    html.Div(dash_table.DataTable(
        id="table_running_scripts",
        columns=[{
            "id" : "script",
            "name" : "Script",
            "type" : "text"
            },{
            "id" : "time",
            "name" : "Last Update",
            "type" : "datetime"
            },{
            "id" : "status",
            "name" : "Updated Last Hour",
            "type" : "text"
            }],

        #filter_action='native',
        css=[{'selector': '.dash-filter > input', 'rule': 'color: #01ff70; text-align : left'}],
        #style_filter={"backgroundColor" : "#663300"}, #styly filtrů fungujou divně proto je zbytek přímo v css
        data=data_frame_is_it_running.to_dict('records'),
        fixed_rows={ 'headers': True, 'data': 0 },
        sort_action="native",
        page_size= 5,
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
        'minWidth': '100px',
        },
        style_cell_conditional=[
            {
            'if': {'column_id': 'script'},
            'width': '90px'
            },
            {
            'if': {'column_id': 'time'},
            'width': '90px'
            },
            {
            'if': {'column_id':'status'},
            'width':'90px'    
            },
        ],
        style_data_conditional=[
            {
            'if': {'filter_query': '{status} = YES', 'column_id': 'status'},
            "color" : colors["button_text"],
            "textAlign":"center"
            }
        ],
        style_as_list_view=True,
        #virtualization=True,
        page_action="none"
        ),style={
            #"width": "48%",
            "margin-left": "20px",
            "margin-right": "20px",
            #"display": "inline-block"
            }),
    dcc.Interval(
        id='interval-component-iir',
        interval=10*1000, # in milliseconds
        n_intervals=0
    ) 
])

#--------------------callback pro otevření cesty k jiné Dash stránce--------------------
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])     #callbak pro víc stránek
def display_page(pathname):
    if pathname == '/twitter_sentiment':
        return twitter_sentiment
    elif pathname == '/GILD_sentiment':
        return GILD_sentiment
    elif pathname =='/running_scripts':
        return running_scripts
    elif pathname =='/portfolio':
        return portfolio.portfolio_layout
    else:
        return index

#--------------------callback pro update grafu z MySQL tweetTable-----------------------
old_fig = None
@app.callback(
    Output('chart-with-slider', 'figure'),
    [Input('year-slider', 'value'),Input('interval-component-chart', 'n_intervals'),Input('sentiment_ma', 'value')]) #input pro slider, auto-update, checklist
def update_figure(selected_time, n_interval, selector):
    global old_fig
    if n_interval % 2 == 1:
        return old_fig
    else:
        data_frame = get_data("tweetTable")
        print("tweettable dataframe: ",data_frame.tail())
        data_frame_filtered = data_frame[data_frame.epoch > selected_time]
        data_frame_filtered_scatter = data_frame.tail(1000) #zobrazí posledních n-tweetů v grafu jako body*
        fig = px.scatter()
        if "scatter" in selector:
            fig.add_scatter(x=data_frame_filtered_scatter["time"], y=data_frame_filtered_scatter["sentiment"], mode="markers", name="Scatter TextBlob", marker={"size":4}, text=data_frame["tweet"]) #*
        if "short_ma" in selector:
            fig.add_scatter(x=data_frame_filtered["time"], y=data_frame["ma_short"], mode="lines", name="1k tweets MA")
        if "long_ma" in selector:    
            fig.add_scatter(x=data_frame_filtered["time"], y=data_frame["ma_long"], mode="lines", name="10k tweets MA")
        if "vader_ma_short" in selector:
            fig.add_scatter(x=data_frame_filtered["time"], y=data_frame["vader_ma_short"], mode="lines", name="10 tweets MA Vader")
        if "vader_ma_long" in selector:    
            fig.add_scatter(x=data_frame_filtered["time"], y=data_frame["vader_ma_long"], mode="lines", name="100 tweets MA Vader")                    
        fig.update_layout(title_text="xrp OR ripple",
                            title_x=0.5,
                            template="plotly_dark", 
                            legend_title_text="", 
                            legend_orientation="h", 
                            legend=dict(x=0, y=-1.2))
        fig.update_layout(transition_duration=500)
        #print("Pocet tweetu v db: ", len(data_frame["time"]))
        old_fig = fig
        return fig

#--------------------callback pro update tabulky z MySQL tweetTable---------------------
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

#--------------------callback pro update tabulky z MySQL newsGILD-----------------------
@app.callback(dash.dependencies.Output('table_newsGILD', 'data'),
              [dash.dependencies.Input('interval-component-newsGILD', 'n_intervals')])
def update_table_gild(n_interval):
    data_frame_newsGILD = get_data_news()
    print("NGt update")
    return data_frame_newsGILD.to_dict('records')

#--------------------callback pro update grafu z MYSQL newsGILD-------------------------
@app.callback(
    Output('chart-with-slider-news', 'figure'),
    [Input('year-slider', 'value'),Input('interval-component-news-chart','n_intervals'),Input('checklist_gild', 'value')]) #Zavolá tu funkci update_figure(valuecasu, n_intrval) - callback pro slider a auto-update grafu
def update_news_figure(selected_time, n_interval, selector):
    print("NGg update")
    data_frame_newsGILD = get_data_news()
    df_G_volume = get_data_news_volume()
    data_frame_newsGILD_filtered = data_frame_newsGILD[data_frame_newsGILD.epoch > selected_time]
    df_G_volume_filtered = df_G_volume[df_G_volume.epoch > selected_time]
    #data_frame_newsGILD_filtered_scatter = data_frame_newsGILD.tail(1000) #zobrazí posledních n-tweetů v grafu jako body*
    fig = make_subplots(rows=2, 
            cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0, #to když se změní tak nefunguje row_heights
            row_heights=[0.8, 0.2],
            )
    if "scatter" in selector:    
        scatter = go.Scatter(x=data_frame_newsGILD_filtered["published"], y=data_frame_newsGILD_filtered["sentiment"],marker_color="#ff8000", mode="markers", name="sentiment", marker={"size":4}, text=data_frame_newsGILD_filtered["title"]) #*
        fig.append_trace(scatter, 1, 1)
    if "short_ma" in selector:
        short_ma = go.Scatter(x=data_frame_newsGILD_filtered["published"], y=data_frame_newsGILD_filtered["ma_short"],line_color="#ffff00", mode="lines", name="Short MA TextBlob")
        fig.append_trace(short_ma, 1, 1)
    if "long_ma" in selector: 
        long_ma = go.Scatter(x=data_frame_newsGILD_filtered["published"], y=data_frame_newsGILD_filtered["ma_long"], line_color="#00ffff", mode="lines", name="Long MA TextBlob")
        fig.append_trace(long_ma, 1, 1)
    if "vader_ma_short" in selector:
        vader_ma_short = go.Scatter(x=data_frame_newsGILD_filtered["published"], y=data_frame_newsGILD_filtered["vader_ma_short"], line_color="#8000ff", mode="lines", name="10 news MA Vader")
        fig.append_trace(vader_ma_short, 1, 1)
    if "vader_ma_long" in selector:    
        vader_ma_long = go.Scatter(x=data_frame_newsGILD_filtered["published"], y=data_frame_newsGILD_filtered["vader_ma_long"], line_color="#ff007f", mode="lines", name="30 news MA Vader")          
        fig.append_trace(vader_ma_long, 1, 1)
    volume = go.Bar(x=df_G_volume_filtered.index, y=df_G_volume_filtered["volume"], marker_color="#ff8000", name="12h Volume", text = df_G_volume_filtered["volume"])
    fig.append_trace(volume, 2, 1)

    fig.layout.template = 'plotly_dark'
    fig["layout"].update(title_text="GILD OR Gilead OR Remdesivir - newsAPI",
                        title_x=0.5,
                        template="plotly_dark", 
                        legend_title_text="", 
                        legend_orientation="h", 
                        legend=dict(x=0, y=-0.13),
                        transition_duration=500
                        )
    #print("Pocet tweetu v db: ", len(data_frame["time"]))
    return fig

#--------------------callback pro update tabulky z MySQL running_scripts----------------
@app.callback(dash.dependencies.Output('table_running_scripts', 'data'),
              [dash.dependencies.Input('interval-component-iir', 'n_intervals')])
def update_is_it_running(n_intervals):
    now_minus_one_hour = dt.now() - relativedelta(hours=1)
    data_frame_is_it_running = pd.read_sql('SELECT script, time FROM running_scripts ORDER BY time ASC', con=kody.cnx)
    data_frame_is_it_running["status"] = np.where(data_frame_is_it_running["time"] > now_minus_one_hour, "YES","NO")
    data_frame_is_it_running = data_frame_is_it_running.to_dict('records')
    return data_frame_is_it_running

if __name__ == '__main__':
    app.run_server(debug=True, host="192.168.1.150")
