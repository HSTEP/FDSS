import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io
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
#from layouts import portfolio
import mysql.connector
import multidict as multidict
from wordcloud import WordCloud
import matplotlib
import matplotlib.pyplot as plt
import io
import base64
import re
from PIL import Image
import bt_for_web

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

def get_data_news(table_name):
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    #Order by musí být ASC, jinak nejsou klouzavé průměry až do konce:
    df = pd.read_sql('SELECT source, published, title, url, sentiment, sentiment_vader FROM '+ table_name +' ORDER BY published ASC', con=cnx)
    df = df.set_index(['published'])
    df["ma_short"] = df.sentiment.rolling(window=10).mean()
    df["ma_long"] = df.sentiment.rolling(window=30).mean()
    df["vader_ma_short"] = df.sentiment_vader.rolling(window=10).mean()
    df["vader_ma_long"] = df.sentiment_vader.rolling(window=30).mean()
    df['epoch'] = df.index.astype(np.int64)
    df["volume"] = 1
    links = df['url'].to_list()
    rows = []
    for x in links:
        link = '[link](' +str(x) + ')'
        rows.append(link)#
    df['url'] = rows
    return df

def get_data_reddit(table_name):
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    df= pd.read_sql('SELECT time, subreddit, post, username, karma_post, ups, topic_comment, sentiment_textblob, sentiment_vader, url FROM '+ table_name +' ORDER BY time ASC', con=cnx)
    df= df.set_index(['time'])
    df["ma_short"] = df.sentiment_textblob.rolling(window=10).mean()
    df["ma_long"] = df.sentiment_textblob.rolling(window=30).mean()
    df["vader_ma_short"] = df.sentiment_vader.rolling(window=10).mean()
    df["vader_ma_long"] = df.sentiment_vader.rolling(window=30).mean()
    df['epoch'] = df.index.astype(np.int64)
    df["volume"] = 1
    links = df['url'].to_list()
    rows = []
    for x in links:
        link = '[link](' +str(x) + ')'
        rows.append(link)#
    df['url'] = rows
    return df

def get_data_reddit_volume(table_name):
    df_volume = get_data_reddit(table_name).resample('720min').agg({'volume': np.sum, 'sentiment_textblob': np.mean,'sentiment_vader': np.mean})
    df_volume["epoch"] =  df_volume.index.astype(np.int64)
    df_volume["MA"] = df_volume.volume.rolling(window=10).mean()
    return df_volume

now_minus_one_hour = dt.now() - relativedelta(hours=1)
data_frame_is_it_running = pd.read_sql('SELECT script, time FROM running_scripts ORDER BY time ASC', con=kody.cnx)
data_frame_is_it_running["status"] = np.where(data_frame_is_it_running["time"] > now_minus_one_hour, "YES","NO")

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index = html.Div(
    style={"backgroundColor": "black"},children=[
    html.Button(
        dcc.Link(
            'Twitter sentiment', 
            href='/twitter_sentiment',
            style={
                "color" : colors["button_text"]
                }
        ), 
        style={
            "background-color" : colors["button_background"], 
            "border" : colors["button_border"]
        }
    ),
    html.Button(dcc.Link('News Sentiment', href='/news_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Reddit Sentiment', href='/reddit_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Backtesting', href='/backtesting', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"],"float": "right"}),
    html.Button(dcc.Link('Running Scripts', href='/running_scripts',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"], "float":"right"}),
    html.H1(
    children='index',
    style={
        "color": colors["text"],
        "textAlign": "center"
        }),
    html.Button(html.A('GitHub Code', href='https://github.com/HSTEP/twitter_sentiment', target='_blank'), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(html.A('backtesting_results', href='/backtesting_results'), style={"background-color" : colors["button_background"], "border" : colors["button_border"], "float":"right"}),
])

twitter_sentiment = html.Div(
    style={"backgroundColor": colors["background"]}, children=[
    
    html.Div(id='page-1-content'),
    html.Button(dcc.Link('Index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('News Sentiment', href='/news_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Reddit Sentiment', href='/reddit_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Backtesting', href='/backtesting', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"],"float": "right"}),
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
            dcc.Dropdown(
                id='twitter-dropdown',
                options=[
                    {'label': 'Airbus', 'value': 'tweetTable_AR_AB_r'},
                    {'label': 'AMC', 'value': 'tweetTable_AR_AMC_r'},
                    {'label': 'AstraZeneca OR AZN', 'value': 'tweetTable_AR_AZN_r'},
                    {'label': 'Boeing', 'value': 'tweetTable_AR_BOEING_r'},
                    {'label': 'Ford', 'value': 'tweetTable_AR_F_r'},
                    {'label': 'Gilead OR GILD', 'value': 'tweetTable_AR_GILD_r'},
                    {'label': 'Cloudflare', 'value': 'tweetTable_AR_NET_r'},
                    {'label': 'Oracle OR ORCL', 'value': 'tweetTable_AR_ORCL_r'},
                    {'label': 'Pfizer OR PFE', 'value': 'tweetTable_AR_PFE_r'},
                    {'label': 'Ferrari', 'value': 'tweetTable_AR_RACE_r'},
                    {'label': 'Toyota OR TOYOF', 'value': 'tweetTable_AR_TOYOF_r'}
                ],
                value='tweetTable_AR_AB_r',
                clearable=False,
                style = {
                        'width': '300px',
                        #'padding-left' : '100px',
                        #'color' : colors["button_text"],
                        #'background-color' : colors["button_background"],
                        },
            ),
            html.Div(dcc.Input(
                id='t-ma-long',
                placeholder="MA [2min]",
                type="number",
                min=0, max=1000,
                step=1,
                value = 200,
                style={
                "color": colors["button_text"],
                "width": "150px",
                "text-align": "center",
                "background-color": colors["button_background"],
                "border": colors["button_border"],
                "border": "2px solid " + colors["button_text"]
                })
            ),
            html.Div(dcc.Input(
                id='t-ma-short',
                placeholder="MA [2min]",
                type="number",
                min=0, max=1000,
                step=1,
                value = 200,
                style={
                "color": colors["button_text"],
                "width": "150px",
                "text-align": "center",
                "background-color": colors["button_background"],
                "border": colors["button_border"],
                "border": "2px solid " + colors["button_text"]
                })
            ),
            html.Div(html.Button(
                "Generate MA",
                id='t-ma',
                style={
                    "color": colors["button_text"],
                    "background-color": colors["button_background"],
                    "border": "2px solid " + colors["button_text"]})
            ),
        ],
        style = {
            "display": "flex",
            "flex-direction": "row"
        },
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
                    {"label" : "Scatter TextBlob", "value" : "sentiment_textblob"},
                    {"label" : "Scatter Vader", "value" : "sentiment_vader"}
                ],
                value = ["vader_ma_short"],
                labelStyle = {"display" : "inline-block", "background-color": colors["button_background"], "color" : colors["button_text"], "border" : "black"}
            ),
        ],
    ),

    dcc.Loading(id='load-component-tweetGraph', color=colors["button_text"], children=[
        html.Div([
            dcc.Graph(id='chart-with-slider-tweetTable'),
            ])
        ]),
    html.Div(
        dcc.Slider(
        id='year-slider-tweetTable',
        min=1593560870000000000,
        max=time.time()*10**9,
        value=(datetime.datetime.now() - relativedelta(days=20)).timestamp()*10**9,
        step=86400*10**9,
        #updatemode="mouseup",
        ),
    ),
    html.Div(id="year-slider-value-tweetTable", style={
        "color": colors["text"],
        "textAlign": "center"
        }),
    dcc.Interval(
        id='interval-component-chart',
        interval=30*1000, # in milliseconds
        n_intervals=0
        ),
    html.Div(dcc.Loading(color=colors["text"], type="dot", children=[html.P(id = "count-tweetTable",
                    style={
                        "color": colors["text"]
                        }
                    ),
                ],
            ),
        style={
            "width":"750px",
        }
    ),
    html.Div(
        children=[
            html.Div(dcc.Dropdown(
                id='t-database',
                options=[
                    {'label': 'Airbus', 'value': 'tweetTable_AR_AB'},
                    {'label': 'AMC', 'value': 'tweetTable_AR_AMC'},
                    {'label': 'Boeing', 'value': 'tweetTable_AR_BOEING'},
                    {'label': 'Ford', 'value': 'tweetTable_AR_F'},
                    {'label': 'Gilead OR GILD', 'value': 'tweetTable_AR_GILD'},
                    {'label': 'Cloudflare', 'value': 'tweetTable_AR_NET'},
                    {'label': 'Oracle OR ORCL', 'value': 'tweetTable_AR_ORCL'},
                    {'label': 'Pfizer OR PFE', 'value': 'tweetTable_AR_PFE'},
                    {'label': 'Ferrari', 'value': 'tweetTable_AR_RACE'},
                    {'label': 'Toyota OR TOYOF', 'value': 'tweetTable_AR_TOYOF'}
                ],
                value='tweetTable_AR_NET',
                clearable=False,
                style = {
                        'width': '300px',
                        #'padding-left' : '100px',
                        #'color' : colors["button_text"],
                        #'background-color' : colors["button_background"],
                        },
                )
            ),
            html.Div(dcc.Input(
                id='t-time-delta',
                placeholder="Time Delta [days]",
                type="number",
                min=0, max=100,
                step=1,
                value = 20,
                style={
                "color": colors["button_text"],
                "width": "150px",
                "text-align": "center",
                "background-color": colors["button_background"],
                "border": colors["button_border"],
                "border": "2px solid " + colors["button_text"]
                })
            ),
            html.Div(dcc.Dropdown(
                id='t-sort-by',
                options=[
                    {'label': 'retveet_count', 'value': 'retveet_count'},
                    {'label': 'reply_count', 'value': 'reply_count'},
                    {'label': 'like_count', 'value': 'like_count'},
                    {'label': 'quote_count', 'value': 'quote_count'},
                    {'label': 'followers_count', 'value': 'followers_count'},
                    {'label': 'following_count', 'value': 'following_count'},
                    {'label': 'tweet_count', 'value': 'tweet_count'},
                ],
                value='tweet_count',
                clearable=False,
                style = {
                        'width': '200px',
                        #'padding-left' : '100px',
                        #'color' : colors["button_text"],
                        #'background-color' : colors["button_background"],
                        },
                )
            ),
            html.Div(dcc.Input(
                id='t-best',
                placeholder="with highest value",
                type="number",
                min=0, max=100,
                step=1,
                style={
                    "color": colors["button_text"],
                    "width": "150px",
                    "text-align": "center",
                    "background-color": colors["button_background"],
                    "border": colors["button_border"],
                    "display":"inline-block",
                    "border": "2px solid " + colors["button_text"]
                })
            ),
            html.Div(dcc.Input(
                id='t-worst',
                placeholder="with lowest value",
                type="number",
                min=0, max=100,
                step=1,
                style={
                    "color": colors["button_text"],
                    "width": "150px",
                    "text-align": "center",
                    "background-color": colors["button_background"],
                    "border": colors["button_border"],
                    "display":"inline-block",
                    "border": "2px solid " + colors["button_text"]
                })
            ),
            html.Div(html.Button(
                "Search",
                id='t-search',
                style={
                    "color": colors["button_text"],
                    "background-color": colors["button_background"],
                    "border": "2px solid " + colors["button_text"]})
            ),
        ], 
        style = {
            "display":"flex",
            "margin-bottom": "4px",
        }
    ),

    dcc.Loading(id='load-component-tweetTable', color=colors["button_text"], children=[
        html.Div(dash_table.DataTable(
            id="table",
            columns=[{
                "id" : "created_at",
                "name" : "Time",
                "type" : "datetime"
                },{
                "id" : "name",
                "name" : "Name",
                "type" : "text"
                },{
                "id" : "url",
                "name" : "url",
                "type" : "text",
                "presentation" : "markdown"
                },{
                "id" : "tweet",
                "name" : "Tweet",
                "type" : "text"
                },{
                "id" : "sentiment_textblob",
                "name" : "TextBlob",
                "type" : "numeric",
                "format" : Format(
                precision = 3,
                )},{
                "id" : "sentiment_vader",
                "name" : "Vader",
                "type" : "numeric",
                "format" : Format(
                precision = 3,
                )},{
                "id" : "retweet_count",
                "name" : "Retweeted",
                "type" : "numeric"
                },{
                "id" : "reply_count",
                "name" : "Replyed",
                "type" : "numeric"
                },{
                "id" : "like_count",
                "name" : "Liked",
                "type" : "numeric"
                },{
                "id" : "quote_count",
                "name" : "Quoted",
                "type" : "numeric"
                },{
                "id" : "followers_count",
                "name" : "followers",
                "type" : "numeric"
                },{
                "id" : "following_count",
                "name" : "Following",
                "type" : "numeric"
                },{
                "id" : "tweet_count",
                "name" : "Tweets",
                "type" : "numeric"
                }],

            filter_action='native',
            css=[{'selector': '.dash-filter > input', 'rule': 'color: #01ff70; text-align : left'}],
            style_filter={"backgroundColor" : "#663300"}, #styly filtrů fungujou divně proto je zbytek přímo v css
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

        #html.Div(dcc.Graph(id="chart_gild",figure=fig_gild)),

        dcc.Interval(
            id="interval-component",
            interval=30*1000
        ),],),

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

news_sentiment = html.Div(
    style={"backgroundColor": "black"},children=[
    html.Div(id='page-2-content'),
    html.Button(dcc.Link('index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Reddit Sentiment', href='/reddit_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Running Scripts', href='/running_scripts',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"], "float":"right"}),
    html.Button(dcc.Link('Backtesting', href='/backtesting', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"],"float": "right"}),
    html.H1(children='News Sentiment',
        style=
        {
        "color": colors["text"],
        "textAlign": "center"
        }),
    html.Div(
        [
            dcc.Dropdown(
                id='news-dropdown',
                options=[
                    {'label': 'Airbus', 'value': 'newsAIRBUS'},
                    {'label': 'AMC', 'value': 'newsAMC'},
                    {'label': 'AZN OR AstraZeneca', 'value': 'newsAZN'},
                    {'label': 'Cloudflare', 'value': 'newsNET'},
                    {'label': 'Boeing', 'value': 'newsBOEING'},
                    {'label': 'Ferrari', 'value': 'newsRACE'},
                    {'label': 'Ford', 'value': 'newsF'},
                    {'label': 'GILD or Gilead or Remdesivir', 'value': 'newsGILD'},
                    {'label': 'Oracle or ORCL', 'value': 'newsORCL'},
                    {'label': 'PFE OR Pfizer', 'value': 'newsPFE'},
                    {'label': 'Toyota', 'value': 'newsTOYOF'}
                ],
                value='newsGILD',
                clearable=False,
                style = {
                        'width': '300px',
                        #'padding-left' : '100px',
                        #'color' : colors["button_text"],
                        #'background-color' : colors["button_background"],
                        },
            ),
        ]),
    html.Div(
        [
            dcc.Checklist(
                id = 'checklist_gild',
                options = [
                    {"label" : "Long MA TextBlob", "value" : "long_ma"},
                    {"label" : "Short MA TextBlob", "value" : "short_ma"},
                    {"label" : "Long MA Vader", "value" : "vader_ma_long"},
                    {"label" : "Short MA Vader", "value" : "vader_ma_short"},
                    {"label" : "Scatter TextBlob", "value" : "sentiment_textblob"},
                    {"label" : "Scatter Vader", "value" : "sentiment_vader"}
                ],
                value = ["sentiment_textblob"],
                labelStyle = {"display" : "inline-block", "background-color": colors["button_background"], "color" : colors["button_text"], "border" : "black"},
                inputStyle={"margin-left": "8px"}
            ),
        ],
    ),
    html.Div(
        children=[
            html.Div(dcc.Loading(id='load-component-tweetGraph', color=colors["button_text"], children=[
                dcc.Graph(id='chart-with-slider-news')]),
                style = {
                    'width': '69%',
                    'text-align' : 'left',
                    'display' : 'inline-block'
                    }
                ),
        html.Div(dcc.Loading(color=colors["button_text"], children=[html.Img(
            id = "wordcloud_with_slider_news",
            width = "100%")]),style = {
                'flex-shrink':'1',
                'flex-grow':'1',
                'width': '29%',
                'display' : 'inline-block',
                })],
            style = {
                'display':'flex',
                'width': '100%',
                'align-items' : 'center',
                },
    ),
    html.Div(
        dcc.Slider(
        id='year-slider-news',
        min=1594412760000000000,
        max=time.time()*10**9,
        value=(datetime.datetime.now() - relativedelta(days=20)).timestamp()*10**9,
        step=86400*10**9,
        ), style={'width': '69%','text-align' : 'left'}),
    html.Div(id="year-slider-value-news", style={
            "color": colors["text"],
            'width': '69%',
            'text-align' : 'center'}),
    dcc.Interval(
            id='interval-component-news-chart',
            interval=60*1000, # in milliseconds
            n_intervals=0
        ),
    html.Div([html.P(id = "count-news",
                    style={
                        "color": colors["text"]
                        }
                    ),
                dcc.Interval(id='interval-component-count',
                        interval=10*1000, # in milliseconds
                        n_intervals=0)
        ]),
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
        data=get_data_news("newsGILD").to_dict('records'),
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
        style_data_conditional=[                
            {
                "if": {"state": "selected"},              # 'active' | 'selected'
                "backgroundColor": "#003855",
                "border": "white",
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

reddit_layout = html.Div(
    style={"backgroundColor": "black"},children=[
    html.Button(dcc.Link('index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('News Sentiment', href='/news_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Running Scripts', href='/running_scripts',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"], "float":"right"}),
    html.Button(dcc.Link('Backtesting', href='/backtesting', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"],"float": "right"}),
    html.H1(children='Reddit Sentiment',
        style=
        {
        "color": colors["text"],
        "textAlign": "center"
        }),
    html.Div(
        [
            dcc.Dropdown(
                id='reddit-dropdown',
                options=[
                    {'label': 'GILD or Gilead or Remdesivir', 'value': 'redditGILD'},
                    #{'label': 'AMD', 'value': 'redditAMD'},
                    #{'label': 'San Francisco', 'value': 'SF'}
                ],
                value='redditGILD',
                clearable=False,
                style = {
                        'width': '300px',
                        #'padding-left' : '100px',
                        #'color' : colors["button_text"],
                        #'background-color' : colors["button_background"],
                        },
            ),
        ]),
    html.Div(
        [
            dcc.Checklist(
                id = 'checklist_gild',
                options = [
                    {"label" : "Long MA TextBlob", "value" : "long_ma"},
                    {"label" : "Short MA TextBlob", "value" : "short_ma"},
                    {"label" : "Long MA Vader", "value" : "vader_ma_long"},
                    {"label" : "Short MA Vader", "value" : "vader_ma_short"},
                    {"label" : "Scatter TextBlob", "value" : "sentiment_textblob"},
                    {"label" : "Scatter Vader", "value" : "sentiment_vader"}
                ],
                value = ["sentiment_textblob"],
                labelStyle = {"display" : "inline-block", "background-color": colors["button_background"], "color" : colors["button_text"], "border" : "black"},
                inputStyle={"margin-left": "8px"}
            ),
        ],
    ),
    html.Div([dcc.Graph(id='chart-with-slider-reddit'),
        dcc.Slider(
        id='year-slider-reddit',
        min=132541261000000000,
        max=time.time()*10**9,
        value=(datetime.datetime.now() - relativedelta(days=20)).timestamp()*10**9,
        step=86400*10**9,
        ),
    dcc.Interval(
            id='interval-component-reddit-chart',
            interval=60*1000, # in milliseconds
            n_intervals=0
        )
        ], style={'width': '100%', 'display': 'inline-block'}),

    #    html.Div(html.Img(
    #        id = "wordcloud_reddit",
    #        src = app.get_asset_url('wordcloud_reddit_gild.svg'), 
    #        height = "500px"),
    #        style = {
    #            'width': '29%', 
    #            'display': 'inline-block', 
    #            'text-align' : 'center'
    #            }
    #        ),
    html.Div([html.P(id = "count-reddit",
                    style={
                        "color": colors["text"]
                        }
                    ),
                dcc.Interval(id='interval-component-count',
                        interval=10*1000, # in milliseconds
                        n_intervals=0)
        ]),
    html.Div(dash_table.DataTable(
        id="table_redditGILD",
        columns=[{
            "id" : "time",
            "name" : "Time",
            "type" : "datetime"
            },{
            "id" : "subreddit",
            "name" : "Subreddit",
            "type" : "text"
            },{
            "id" : "post",
            "name" : "Post",
            "type" : "text"
            },{
            "id" : "username",
            "name" : "Username",
            "type" : "text"
            },{
            "id" : "karma_post",
            "name" : "Post Karma",
            "type" : "numeric",
            },{
            "id" : "ups",
            "name" : "Upvotes",
            "type" : "numeric",
            },{
            "id" : "topic_comment",
            "name" : "Comment",
            "type" : "text"
            },{
            "id" : "sentiment_textblob",
            "name" : "TextBlob",
            "type" : "numeric",
            "format" : Format(
                precision = 5,
            ),},{
            "id" : "sentiment_vader",
            "name" : "Vader",
            "type" : "numeric",
            "format" : Format(
                precision = 5,
            ),},{
            "id" : "url",
            "name" : "url",
            "type" : "text",
            "presentation" : "markdown"
            }
            ],

        filter_action='native',
        css=[{'selector': '.dash-filter > input', 'rule': 'color: #01ff70; text-align : left'}],
        style_filter={"backgroundColor" : "#663300"}, #styly filtrů fungujou divně proto je zbytek přímo v css
        data=get_data_reddit("redditGILD").to_dict('records'),
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
            'if': {'column_id': 'ups'},
            'width': '50px'
            },
            {
            'if': {'column_id': 'username'},
            'width': '90px'
            },
        ],
        style_data_conditional=[                
            {
                "if": {"state": "selected"},              # 'active' | 'selected'
                "backgroundColor": "#003855",
                "border": "white",
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
        id='interval-component-reddit',
        interval=70*1000, # in milliseconds
        n_intervals=0
    )
])

backtesting = html.Div(
    style={"backgroundColor": "black"}, children=[
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"]}),
    html.Button(dcc.Link('News Sentiment', href='/news_sentiment', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"]}),
    html.Button(dcc.Link('Reddit Sentiment', href='/reddit_sentiment', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"]}),
    html.Button(dcc.Link('Running Scripts', href='/running_scripts', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"],"float": "right"}),
    html.H1(
        children='Backtesting',
        style={
            "color": colors["text"],
            "textAlign": "center"
        }),

    html.Div(
        [
            dcc.Dropdown(
                id='bt-dropdown',
                options=[
                    {'label': 'News Airbus', 'value': '/home/stepan/stranka/backtrader/data_news/newsAIR.csv'},
                    {'label': 'News AMC', 'value': '/home/stepan/stranka/backtrader/data_news/newsAMC.csv'},
                    {'label': 'News AZN OR AstraZeneca', 'value': '/home/stepan/stranka/backtrader/data_news/newsAZN.csv'},
                    {'label': 'News Boeing', 'value': '/home/stepan/stranka/backtrader/data_news/newsBA.csv'},
                    {'label': 'News Ford', 'value': '/home/stepan/stranka/backtrader/data_news/newsF.csv'},
                    {'label': 'News Cloudflare', 'value': '/home/stepan/stranka/backtrader/data_news/newsNET.csv'},
                    {'label': 'News Oracle or ORCL', 'value': '/home/stepan/stranka/backtrader/data_news/newsORCL.csv'},
                    {'label': 'News PFE OR Pfizer', 'value': '/home/stepan/stranka/backtrader/data_news/newsPFE.csv'},
                    {'label': 'News Ferrari', 'value': '/home/stepan/stranka/backtrader/data_news/newsRACE.csv'},
                    {'label': 'News Toyota', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterTM.csv'},
                    {'label': 'Tweets Airbus', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterAIR.csv'},
                    {'label': 'Tweets AMC', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterAMC.csv'},
                    {'label': 'Tweets Boeing', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterBA.csv'},
                    {'label': 'Tweets Ford', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterF.csv'},
                    {'label': 'Tweets Gilead', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterGILD.csv'},
                    {'label': 'Tweets Cloudflare', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterNET.csv'},
                    {'label': 'Tweets Oracle or ORCL', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterORCL.csv'},
                    {'label': 'Tweets PFE OR Pfizer', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterPFE.csv'},
                    {'label': 'Tweets Ferrari', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterRACE.csv'},
                    {'label': 'Tweets Toyota', 'value': '/home/stepan/stranka/backtrader/data_twitter/twitterTM.csv'},
                ],
                value='/home/stepan/stranka/backtrader/data_news/newsNET.csv',
                clearable=False,
                style = {
                        'width': '300px',
                        'text-align' : 'center',
                        #'color' : colors["button_text"],
                        #'background-color' : colors["button_background"],
                        },
            ),
        ], 
        style={
        "display" : "flex",
        "align-items" : "center",
        "justify-content" : "center",
        }
    ),
    html.Div(
        children=[
            html.Div(
                children=[
                    html.Div(
                        id="buttons",
                        children=[
                            html.Div(id="bt-strategy-text",
                                     style={
                                         "color": colors["button_text"],
                                         "margin-left": "13px",
                                     }
                                     ),
                            html.Div(dcc.Input(
                                id='bt-strategy',
                                placeholder="Select Strategy",
                                type="number",
                                min=0, max=2,
                                step=1,
                                style={
                                    "color": colors["button_text"],
                                    "width": "150px",
                                    "margin-bottom": "4px",
                                    "margin-left": "13px",
                                    "text-align": "center",
                                    "background-color": colors["button_background"],
                                    "border": colors["button_border"]
                                })
                            ),
                            html.Div(id="short-ma-text",
                                     style={
                                         "color": colors["text"],
                                         "margin-left": "13px",
                                     }
                                     ),
                            html.Div(dcc.Input(
                                id='short-ma',
                                placeholder="Short MA Period",
                                type="number",
                                min=1, max=100000,
                                step=1,
                                style={
                                    "color": colors["button_text"],
                                    "width": "150px",
                                    "margin-bottom": "4px",
                                    "margin-left": "13px",
                                    "text-align": "center",
                                    "background-color": colors["button_background"],
                                    "border": colors["button_border"]
                                })
                            ),
                            html.Div(id="long-ma-text",
                                     style={
                                         "color": colors["text"],
                                         "margin-left": "13px",
                                     }
                                     ),
                            html.Div(dcc.Input(
                                id='long-ma',
                                placeholder="Long MA Period",
                                type="number",
                                min=1, max=100000,
                                step=1,
                                style={
                                    "color": colors["button_text"],
                                    "width": "150px",
                                    "margin-bottom": "4px",
                                    "margin-left": "13px",
                                    "text-align": "center",
                                    "background-color": colors["button_background"],
                                    "border": colors["button_border"]
                                })
                            ),
                            html.Div(id="stop-loss-text",
                                     style={
                                         "color": colors["text"],
                                         "margin-left": "13px",
                                     }
                                     ),
                            html.Div(dcc.Input(
                                id='stop-loss',
                                placeholder="Stop-Loss [%]",
                                type="number",
                                min=0, max=10000,
                                step=0.1,
                                style={
                                    "color": colors["button_text"],
                                    "width": "150px",
                                    "margin-bottom": "4px",
                                    "margin-left": "13px",
                                    "text-align": "center",
                                    "background-color": colors["button_background"],
                                    "border": colors["button_border"]
                                })
                            ),
                            html.Div(id="take-profit-text",
                                     style={
                                         "color": colors["text"],
                                         "margin-left": "13px",
                                     }
                                     ),
                            html.Div(dcc.Input(
                                id='take-profit',
                                placeholder="Take-Profit [%]",
                                type="number",
                                min=0, max=10000,
                                step=0.1,
                                style={
                                    "color": colors["button_text"],
                                    "width": "150px",
                                    "margin-bottom": "4px",
                                    "margin-left": "13px",
                                    "text-align": "center",
                                    "background-color": colors["button_background"],
                                    "border": colors["button_border"]
                                })
                            ),
                            html.Div(html.Button(
                                "start backtest",
                                id='bt-button',
                                style={
                                    "color": colors["button_text"],
                                    "background-color": colors["button_background"],
                                    "border": "2px solid " + colors["button_text"]})
                            ),
                        ],
                    ),
                    html.Div(
                        id="console-container",
                        children=[
                            html.Div(id="hidden-div", style={"display": "none"}),

                            html.Div(
                                id="console",
                                style={
                                    "width": 500,
                                    "height": 370,
                                    "color": colors["text"],
                                    "background-color": "black",
                                    "overflow": "scroll"
                                }
                            ),
                            dcc.Interval(
                                id='interval',
                                interval=0.5 * 1000,  # in milliseconds
                                n_intervals=0
                            ), ],
                        style={
                            "flex-grow": 1
                        }
                    )],
                style={
                    "display": "flex",
                    "flex-direction": "row",
                },
            ),],
        style={
            "align-items" : "center",
            "justify-content" : "center",
            "display": "flex",
        }),
    html.Div(children=[
        html.Div(
                children=[
                    html.Button("Make Chart",
                        id='bt-chart-button',
                        style={
                            "width" : 685,
                            "margin-bottom" : "30px",
                            "background-color": "red",
                            "color": colors["button_text"],
                            "background-color": colors["button_background"],
                            "border": "2px solid " + colors["button_text"]}),
                ],
                style={
                    "display" : "flex",
                    "align-items" : "center",
                    "justify-content" : "center",
                }
                ),
        html.Div(dcc.Loading(id="bt-chart",
                color=colors["button_text"], 
                children=[],)

        )],
        style={
        }),
]),

running_scripts = html.Div(
    style={"backgroundColor": "black"},children=[
    html.Button(dcc.Link('Index', href='/',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Twitter sentiment', href='/twitter_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('News Sentiment', href='/news_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Reddit Sentiment', href='/reddit_sentiment',style={"color" : colors["button_text"]}), style={"background-color" : colors["button_background"], "border" : colors["button_border"]}),
    html.Button(dcc.Link('Backtesting', href='/backtesting', style={"color": colors["button_text"]}),style={"background-color": colors["button_background"], "border": colors["button_border"],"float": "right"}),
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

backtesting_results = html.Div([
    dcc.Tabs(id='tabs', value='b-321-1', children=[
        dcc.Tab(label='Strategie MA sentimentu opt. 1',  value = 'b-321-1', selected_style={"font-weight": "bold"}),
        dcc.Tab(label='Strategie MA sentimentu multistocks',  value = 'b-321-3', selected_style={"font-weight": "bold"}),
        dcc.Tab(label='Strategie sentiment 0 opt. 1',  value = 'b-322-1', selected_style={"font-weight": "bold"}),
        dcc.Tab(label='Strategie sentiment 0 multistocks',  value = 'b-322-2', selected_style={"font-weight": "bold"}),
        dcc.Tab(label='Druhá kontrolní strategie opt. 1',  value = 'b-323-1', selected_style={"font-weight": "bold"}),
        dcc.Tab(label='Druhá kontrolní strategie multistocks',  value = 'b-323-2', selected_style={"font-weight": "bold"}),
    ],colors={
        "border": "white",
        "background": "#f1b450"
        }
    ),
    dcc.Loading(color=colors["button_text"], children=[html.Div(id='backtesting-results')]),
],style = {
    "margin-left" : "65px"})

#--------------------callback pro otevření cesty k jiné Dash stránce--------------------
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])     #callbak pro víc stránek
def display_page(pathname):
    if pathname == '/twitter_sentiment':
        return twitter_sentiment
    elif pathname == '/news_sentiment':
        return news_sentiment
    elif pathname == '/reddit_sentiment':
        return reddit_layout
    elif pathname =='/running_scripts':
        return running_scripts
    elif pathname =='/backtesting':
        return backtesting
    elif pathname == '/backtesting_results':
        return backtesting_results
    else:
        return index

#================================================================================================================
#-----------------------------callbacky pro backtesting---------------------------------

try:
    process
except NameError:
    process = None

lines = []

@app.callback(
    dash.dependencies.Output("hidden-div", 'children'),
    [dash.dependencies.Input('bt-button', 'n_clicks'),
     dash.dependencies.State('bt-dropdown', 'value'),
     dash.dependencies.State('bt-strategy', 'value'),
     dash.dependencies.State('short-ma', 'value'),
     dash.dependencies.State('long-ma', 'value'),
     dash.dependencies.State('stop-loss', 'value'),
     dash.dependencies.State('take-profit', 'value'),
    ],
    prevent_initial_call=True,)
def run_script_onClick(n_clicks, drop_stock, strat_id, shortMa, longMa, stopLoss, takeProfit):
    global process, lines
    args = []
    if drop_stock is not None:
        args.append(f"file={str(drop_stock)}")    
    if strat_id is not None:
        args.append(f"strat_id={int(strat_id)}")
    if shortMa is not None:
        args.append(f"shortMA={int(shortMa)}")
    if longMa is not None:
        args.append(f"longMA={int(longMa)}")
    if stopLoss is not None:
        args.append(f"stopLoss={int(stopLoss)}")
    if takeProfit is not None:
        args.append(f"takeProfit={int(takeProfit)}")

    lines = []
    print("Running the script")
    if process is not None:
        process.terminate()
        process = None
    process = bt_for_web.run_strategy(*args)

@app.callback(
    dash.dependencies.Output("console", "children"),
    [Input("interval", "n_intervals")]
)
def get_output_of_process(n_intervals):
    if process is not None:
        for _ in range(50):
            line = process.stdout.readline()
            line = line.decode("utf-8")
            lines.insert(0,line)
    return [html.P(line, style={"margin": 0, "line-height": 13}) for line in lines]

@app.callback(
    dash.dependencies.Output('bt-strategy-text', 'children'),
    [dash.dependencies.Input('bt-strategy', 'value'),
     ])
def strategy_is(strategy_name):
    if strategy_name == 0:
        strategy_name = "MA_cross_Sentiment"
    if strategy_name == 1:
        strategy_name = "MA_control_strategy"
    if strategy_name == 2:
        strategy_name = "sentiment_0_strategy"
    return '{}'.format(strategy_name)

@app.callback(
    dash.dependencies.Output('short-ma-text', 'children'),
    [dash.dependencies.Input('short-ma', 'value'),
     ])
def short_ma_text(short_ma):
    return 'Short MA= {}'.format(short_ma)

@app.callback(
    dash.dependencies.Output('long-ma-text', 'children'),
    [dash.dependencies.Input('long-ma', 'value'),
     ])
def long_ma_text(long_ma):
    return 'Long MA= {}'.format(long_ma)

@app.callback(
    dash.dependencies.Output('stop-loss-text', 'children'),
    [dash.dependencies.Input('stop-loss', 'value'),
     ])
def stop_loss_text(stop_loss):
    return 'Stop Loss= {}%'.format(stop_loss)

@app.callback(
    dash.dependencies.Output('take-profit-text', 'children'),
    [dash.dependencies.Input('take-profit', 'value'),
     ])
def take_profit_text(take_profit):
    return 'Take Profit= {}%'.format(take_profit)

@app.callback(
    Output('bt-chart', 'children'),
    [Input('bt-chart-button','n_clicks') #callback pro checklist
    ],
    prevent_initial_call=True,)

def bt_chart_maker(n_clicks):
    fig = bt_for_web.bt_make_chart()
    return  dcc.Graph(id='bt-chart',
                figure = fig,
                style = {
                    "height":"1000px",
            },),

    

#--------------------callback pro update grafu z MySQL tweetTable-----------------------
@app.callback(
    Output('chart-with-slider-tweetTable', 'figure'),
    [Input("t-ma" , "n_clicks"),
     Input('year-slider-tweetTable', 'value'), #callback pro chart slider
     Input('sentiment_ma', 'value'), #callback pro checklist
     #Input('interval-component-chart','n_intervals'), #callbak pro update grafu
     Input('twitter-dropdown', 'value'), #callback pro dropdown
     dash.dependencies.State("t-ma-long" , "value"),
     dash.dependencies.State("t-ma-short" , "value"),
     ]) 

def update_tweetTable(n_clicks, selected_time, selector, keyword, t_ma_long, t_ma_short): #(n_intervals) pro auto update
    selected_time_datetime = datetime.datetime.fromtimestamp(selected_time/1000000000).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')    
    df_filtered = pd.read_sql('SELECT created_at, sentiment_textblob, volume, sentiment_vader FROM '+ keyword +' WHERE created_at >= "'+selected_time_datetime+'"ORDER BY created_at ASC', con=cnx)
    df_filtered = df_filtered.set_index(["created_at"])
    df_filtered["sentiment_textblob"] = df_filtered["sentiment_textblob"].fillna(method="ffill")
    df_filtered["sentiment_vader"] = df_filtered["sentiment_vader"].fillna(method="ffill")
    df_filtered["ma_short"] = df_filtered.sentiment_textblob.rolling(window=t_ma_short).mean()
    df_filtered["ma_long"] = df_filtered.sentiment_textblob.rolling(window=t_ma_long).mean()
    df_filtered["vader_ma_short"] = df_filtered.sentiment_vader.rolling(window=t_ma_short).mean()
    df_filtered["vader_ma_long"] = df_filtered.sentiment_vader.rolling(window=t_ma_long).mean()    
    df_filtered['epoch'] = df_filtered.index.astype(np.int64)
    df_volume_filtered = df_filtered.resample('60min').agg({'volume': np.sum})
    df_volume_filtered["epoch"] =  df_volume_filtered.index.astype(np.int64)
    #df_volume["MA"] = df_volume.volume.rolling(window=100).mean()
    #df_filtered = df[df.epoch > selected_time]
    #df_volume = get_data_twitter_volume(keyword)
    #df_volume_filtered = df_volume[df_volume.epoch > selected_time]
    fig = make_subplots(rows=2, 
            cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0, #to když se změní tak nefunguje row_heights
            row_heights=[0.8, 0.2],
            )
    if "sentiment_textblob" in selector:    
        scatter = go.Scatter(x=df_filtered.index, y=df_filtered["sentiment_textblob"],marker_color="#ff8000", mode="markers", name="10 min Sentiment TextBlob", marker={"size":4}) #*
        fig.append_trace(scatter, 1, 1)
    if "sentiment_vader" in selector:    
        scatter = go.Scatter(x=df_filtered.index, y=df_filtered["sentiment_vader"],marker_color="#ff0000", mode="markers", name="10 min Sentiment Vader", marker={"size":4},) #*
        fig.append_trace(scatter, 1, 1)
    if "short_ma" in selector:
        short_ma = go.Scatter(x=df_filtered.index, y=df_filtered["ma_short"],line_color="#ffff00", mode="lines", name=str(t_ma_short*10)+"min TextBlob MA")
        fig.append_trace(short_ma, 1, 1)
    if "long_ma" in selector: 
        long_ma = go.Scatter(x=df_filtered.index, y=df_filtered["ma_long"], line_color="#00ffff", mode="lines", name=str(t_ma_long*10)+"min TextBlob MA")
        fig.append_trace(long_ma, 1, 1)
    if "vader_ma_short" in selector:
        vader_ma_short = go.Scatter(x=df_filtered.index, y=df_filtered["vader_ma_short"], line_color="#8000ff", mode="lines", name=str(t_ma_short*10)+" min ader MA")
        fig.append_trace(vader_ma_short, 1, 1)
    if "vader_ma_long" in selector:    
        vader_ma_long = go.Scatter(x=df_filtered.index, y=df_filtered["vader_ma_long"], line_color="#ff007f", mode="lines", name=str(t_ma_long*10)+"min Vader MA")          
        fig.append_trace(vader_ma_long, 1, 1)
    volume = go.Bar(x=df_volume_filtered.index, y=df_volume_filtered["volume"], marker_color="#ff8000", name="2m Volume", text = df_volume_filtered["volume"])
    fig.append_trace(volume, 2, 1)
    #volume_MA = go.Scatter(x=df_filtered.index, y=df_filtered["MA"], fill="tozeroy", mode="none", fillcolor="rgba(255, 128, 0, 0.4)", name="Volume MA 1O")
    #fig.append_trace(volume_MA, 2, 1)

    fig["layout"].update(#title_text="test",
                        template="plotly_dark", 
                        legend_title_text="", 
                        legend_orientation="h", 
                        legend=dict(x=0, y=-0.13),
                        transition_duration=0,
                        margin=dict(l=0, r=0, t=20, b=0),
                        paper_bgcolor="black",
                        plot_bgcolor="black",
                        title={
                            "yref": "paper",
                            "y" : 1,
                            "x" : 0.5,
                            "yanchor" : "bottom"},
                            )
    #print("Pocet tweetu v db: ", len(data_frame["time"]))
    return fig

#--------------------callback pro update hodnoty slider_value-tweetTable-----------------
@app.callback(Output('year-slider-value-tweetTable', 'children'),
                [Input("year-slider-tweetTable", "drag_value")
                ])
def slider_twitter(drag_value):
    if drag_value == None:  #first load == None
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
        drag_value_datetime = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    else:
        drag_value_datetime = datetime.datetime.fromtimestamp(drag_value/1000000000).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    return 'Slider Value: {}'.format(drag_value_datetime)

#--------------------callback pro update tabulky z MySQL tweetTable----------------------
@app.callback(Output('table', 'data'),
             [Input('t-search', 'n_clicks'),
              dash.dependencies.State('t-database', 'value'),
              dash.dependencies.State('t-time-delta', 'value'),
              dash.dependencies.State('t-sort-by', 'value'),
              dash.dependencies.State('t-best', 'value'),
              dash.dependencies.State('t-worst', 'value'),
             ],
              prevent_initial_call=True,)       
def update_table(n_clicks, t_database, t_time_delta, t_sort_by, t_best, t_worst): #(n_intervals) pro auto update

    yesterday = datetime.datetime.now() - datetime.timedelta(days=t_time_delta)
    yesterday = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    df = pd.read_sql('SELECT created_at, tweet_id, name, tweet, sentiment_textblob, sentiment_vader, retweet_count, reply_count, like_count, quote_count, followers_count, following_count, tweet_count  FROM '+t_database+' WHERE created_at >= "'+yesterday+'" ORDER BY '+t_sort_by+' DESC', con=kody.cnx)
    df = df.set_index(['created_at'])#aby fungovalo data_frame.resample
    result = [group[1] for group in df.groupby(df.index.hour)] #vytvoří list s tabulkami rozdělených po dnech
    dfs_selection = pd.DataFrame()
    for frame in result:
        dfW = pd.concat([frame.head(t_best), frame.tail(t_worst)]).drop_duplicates()
        dfs_selection = dfs_selection.append(dfW)
    dfs_selection = dfs_selection.reset_index()

    links = dfs_selection['tweet_id'].to_list()
    rows = []
    for x in links:
        link = '[link](https://twitter.com/i/status/' +str(x) + ')'
        rows.append(link)#
    dfs_selection['url'] = rows

    print(dfs_selection)
    return dfs_selection.to_dict('records')

#================================================================================================================


#--------------------callback pro update tabulky z MySQL news----------------------------
@app.callback(Output('table_newsGILD', 'data'),
             [Input('news-dropdown', 'value'), #callback pro dropdown
              Input('interval-component-newsGILD', 'n_intervals')])
def update_table_gild(news, n_interval):
    df = get_data_news(news).sort_index(ascending=False)#nejdřív seřadím pro default sort v datatablu
    df = df.reset_index().rename(columns={df.index.name:'published'}) #protože index nejde zobrazit v datatablu
    print("news table update")
    return df.to_dict('records')

#--------------------callback pro update grafu z MYSQL newsG-----------------------------
@app.callback(
    Output('chart-with-slider-news', 'figure'),
    [Input('year-slider-news', 'value'), #callback pro chart slider
     Input('interval-component-news-chart','n_intervals'), #callbak pro update grafu
     Input('news-dropdown', 'value'), #callback pro dropdown
     Input('checklist_gild', 'value')]) #callback pro checklist
def update_news_figure(selected_time, n_interval, keyword, selector):
    selected_time_datetime = datetime.datetime.fromtimestamp(selected_time/1000000000).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    print("news chart update")
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    df_filtered = pd.read_sql('SELECT source, published, title, url, sentiment, sentiment_vader FROM '+ keyword +' WHERE published >= "'+selected_time_datetime+'" ORDER BY published ASC', con=cnx)
    df_filtered = df_filtered.set_index(['published'])
    df_filtered["ma_short"] = df_filtered.sentiment.rolling(window=10).mean()
    df_filtered["ma_long"] = df_filtered.sentiment.rolling(window=30).mean()
    df_filtered["vader_ma_short"] = df_filtered.sentiment_vader.rolling(window=10).mean()
    df_filtered["vader_ma_long"] = df_filtered.sentiment_vader.rolling(window=30).mean()
    df_filtered['epoch'] = df_filtered.index.astype(np.int64)
    df_filtered["volume"] = 1
    links = df_filtered['url'].to_list()
    rows = []
    for x in links:
        link = '[link](' +str(x) + ')'
        rows.append(link)#
    df_filtered['url'] = rows
    df_volume_filtered = df_filtered.resample('360min').agg({'volume': np.sum})
    df_volume_filtered["epoch"] =  df_volume_filtered.index.astype(np.int64)
    df_volume_filtered["MA"] = df_volume_filtered.volume.rolling(window=4).mean()
    fig = make_subplots(rows=2, 
            cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0, #to když se změní tak nefunguje row_heights
            row_heights=[0.8, 0.2],
            )
    if "sentiment_textblob" in selector:    
        scatter = go.Scatter(x=df_filtered.index, y=df_filtered["sentiment"],marker_color="#ff8000", mode="markers", name="Sentiment TextBlob", marker={"size":4}, text=df_filtered["title"]) #*
        fig.append_trace(scatter, 1, 1)
    if "sentiment_vader" in selector:    
        scatter = go.Scatter(x=df_filtered.index, y=df_filtered["sentiment_vader"],marker_color="#ff0000", mode="markers", name="Sentiment Vader", marker={"size":4}, text=df_filtered["title"]) #*
        fig.append_trace(scatter, 1, 1)
    if "short_ma" in selector:
        short_ma = go.Scatter(x=df_filtered.index, y=df_filtered["ma_short"],line_color="#ffff00", mode="lines", name="10 news MA TextBlob")
        fig.append_trace(short_ma, 1, 1)
    if "long_ma" in selector: 
        long_ma = go.Scatter(x=df_filtered.index, y=df_filtered["ma_long"], line_color="#00ffff", mode="lines", name="30 news MA TextBlob")
        fig.append_trace(long_ma, 1, 1)
    if "vader_ma_short" in selector:
        vader_ma_short = go.Scatter(x=df_filtered.index, y=df_filtered["vader_ma_short"], line_color="#8000ff", mode="lines", name="10 news MA Vader")
        fig.append_trace(vader_ma_short, 1, 1)
    if "vader_ma_long" in selector:    
        vader_ma_long = go.Scatter(x=df_filtered.index, y=df_filtered["vader_ma_long"], line_color="#ff007f", mode="lines", name="30 news MA Vader")          
        fig.append_trace(vader_ma_long, 1, 1)
    volume = go.Bar(x=df_volume_filtered.index, y=df_volume_filtered["volume"], marker_color="#ff8000", name="6h Volume", text = df_volume_filtered["volume"])
    fig.append_trace(volume, 2, 1)
    volume_MA = go.Scatter(x=df_volume_filtered.index, y=df_volume_filtered["MA"], fill="tozeroy", mode="none", fillcolor="rgba(255, 128, 0, 0.6)", name="Volume 1D MA")
    fig.append_trace(volume_MA, 2, 1)

    fig["layout"].update(#title_text=news,
                        template="plotly_dark", 
                        legend_title_text="", 
                        legend_orientation="h", 
                        legend=dict(x=0, y=-0.13),
                        transition_duration=0,
                        margin=dict(l=0, r=0, t=20, b=0),
                        paper_bgcolor="black",
                        plot_bgcolor="black",
                        title={
                            "yref": "paper",
                            "y" : 1,
                            "x" : 0.5,
                            "yanchor" : "bottom"},
                            )
    #print("Pocet tweetu v db: ", len(data_frame["time"]))
    return fig

#--------------------callback pro update hodnoty slider_value-news----------------------
@app.callback(Output('year-slider-value-news', 'children'),
                [Input("year-slider-news", "drag_value")
                ])
def slider_news(drag_value):
    if drag_value == None:  #first load == None
        yesterday = datetime.datetime.now() - datetime.timedelta(days=10)
        drag_value_datetime = yesterday.strftime("%Y-%m-%d %H:%M:%S")
    else:
        drag_value_datetime = datetime.datetime.fromtimestamp(drag_value/1000000000).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    return 'Slider Value: {}'.format(drag_value_datetime)

#--------------------callback pro update tabulky z MySQL running_scripts----------------
@app.callback(dash.dependencies.Output('table_running_scripts', 'data'),
              [dash.dependencies.Input('interval-component-iir', 'n_intervals')])
def update_is_it_running(n_intervals):
    now_minus_one_hour = dt.now() - relativedelta(hours=1)
    data_frame_is_it_running = pd.read_sql('SELECT script, time FROM running_scripts ORDER BY time ASC', con=kody.cnx)
    data_frame_is_it_running["status"] = np.where(data_frame_is_it_running["time"] > now_minus_one_hour, "YES","NO")
    data_frame_is_it_running = data_frame_is_it_running.to_dict('records')
    return data_frame_is_it_running

#--------------------callback pro update wordcloudu news--------------------------------

@app.callback(
    Output('wordcloud_with_slider_news', 'src'),
    [Input('year-slider-news', 'value'), #callback pro chart slider
     Input('news-dropdown', 'value')]) #callback pro dropdown
def update_wordcloud_news_html(selected_time, keyword):
    selected_time_datetime = datetime.datetime.fromtimestamp(selected_time/1000000000).replace(microsecond=0).strftime("%Y-%m-%d %H:%M:%S")
    print("news wc update")
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    data = pd.read_sql("SELECT title FROM "+ keyword +" WHERE published > \""+ selected_time_datetime +"\" ", con=cnx)
    
    sentence = ' '.join(data["title"].tolist())

    fullTermsDict = multidict.MultiDict()
    tmpDict = {}

    # making dict for counting frequencies
    for text in sentence.split(" "):
        if re.match("rt|stock|a|the|an|the|to|in|for|of|or|by|with|is|on|that|be", text):
            continue
        val = tmpDict.get(text, 0)
        tmpDict[text.lower()] = val + 1
    for key in tmpDict:
        fullTermsDict.add(key, tmpDict[key])

    wordcloud = WordCloud(height=500, width=500, background_color="black", contour_color='white', colormap="autumn").generate_from_frequencies(fullTermsDict)
    buf = io.BytesIO() # in-memory files
    plt.figure()
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.savefig(buf, format = "png", dpi=600, bbox_inches = 'tight', pad_inches = 0) # save to the above file object
    data = base64.b64encode(buf.getbuffer()).decode("utf8") # encode to html elements
    plt.close()
    return "data:image/png;base64,{}".format(data)

#================================================================================================================

#--------------------callback pro update tabulky z MySQL redditGILD-----------------------
@app.callback(
        Output('table_redditGILD', 'data'),
    [
        Input('reddit-dropdown', 'value'), #callback pro dropdown
        Input('interval-component-reddit', 'n_intervals')
    ])
def update_table_reddit(reddit, n_interval):
    df = get_data_reddit(reddit).sort_index(ascending=False)#nejdřív seřadím pro default sort v datatablu
    df = df.reset_index().rename(columns={df.index.name:'time'}) #protože index nejde zobrazit v datatablu
    print("news table update")
    return df.to_dict('records')

#--------------------callback pro update grafu z MYSQL redditGILD-------------------------
@app.callback(
    Output('chart-with-slider-reddit', 'figure'),
    [Input('year-slider-reddit', 'value'), #callback pro chart slider
     Input('interval-component-reddit-chart','n_intervals'), #callbak pro update grafu
     Input('reddit-dropdown', 'value'), #callback pro dropdown
     Input('checklist_gild', 'value')]) #callback pro checklist
def update_reddit_figure(selected_time, n_interval, reddit, selector):
    print("reddit chart update")
    df = get_data_reddit(reddit)
    df_volume = get_data_reddit_volume(reddit)
    df_filtered = df[df.epoch > selected_time]
    df_volume_filtered = df_volume[df_volume.epoch > selected_time]
    #df_filtered_scatter = df.tail(1000) #zobrazí posledních n-tweetů v grafu jako body*
    fig = make_subplots(rows=2, 
            cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0, #to když se změní tak nefunguje row_heights
            row_heights=[0.8, 0.2],
            )
    if "sentiment_textblob" in selector:    
        scatter = go.Scatter(x=df_filtered.index, y=df_filtered["sentiment_textblob"],marker_color="#ff8000", mode="markers", name="Sentiment TextBlob", marker={"size":4}, text=df_filtered["topic_comment"]) #*
        fig.append_trace(scatter, 1, 1)
    if "sentiment_vader" in selector:    
        scatter = go.Scatter(x=df_filtered.index, y=df_filtered["sentiment_vader"],marker_color="#ff0000", mode="markers", name="Sentiment Vader", marker={"size":4}, text=df_filtered["topic_comment"]) #*
        fig.append_trace(scatter, 1, 1)
    if "short_ma" in selector:
        short_ma = go.Scatter(x=df_filtered.index, y=df_filtered["ma_short"],line_color="#ffff00", mode="lines", name="Short MA TextBlob")
        fig.append_trace(short_ma, 1, 1)
    if "long_ma" in selector: 
        long_ma = go.Scatter(x=df_filtered.index, y=df_filtered["ma_long"], line_color="#00ffff", mode="lines", name="Long MA TextBlob")
        fig.append_trace(long_ma, 1, 1)
    if "vader_ma_short" in selector:
        vader_ma_short = go.Scatter(x=df_filtered.index, y=df_filtered["vader_ma_short"], line_color="#8000ff", mode="lines", name="10 reddit MA Vader")
        fig.append_trace(vader_ma_short, 1, 1)
    if "vader_ma_long" in selector:    
        vader_ma_long = go.Scatter(x=df_filtered.index, y=df_filtered["vader_ma_long"], line_color="#ff007f", mode="lines", name="30 reddit MA Vader")          
        fig.append_trace(vader_ma_long, 1, 1)
    volume = go.Bar(x=df_volume_filtered.index, y=df_volume_filtered["volume"], marker_color="#ff8000", name="12h Volume", text = df_volume_filtered["volume"])
    fig.append_trace(volume, 2, 1)
    volume_MA = go.Scatter(x=df_volume_filtered.index, y=df_volume_filtered["MA"], fill="tozeroy", mode="none", fillcolor="rgba(255, 128, 0, 0.4)", name="Volume MA 1O")
    fig.append_trace(volume_MA, 2, 1)

    fig["layout"].update(title_text=reddit,
                        template="plotly_dark", 
                        legend_title_text="", 
                        legend_orientation="h", 
                        legend=dict(x=0, y=-0.13),
                        transition_duration=0,
                        margin=dict(l=0, r=0, t=20, b=0),
                        paper_bgcolor="black",
                        plot_bgcolor="black",
                        title={
                            "yref": "paper",
                            "y" : 1,
                            "x" : 0.5,
                            "yanchor" : "bottom"},
                            )
    #print("Pocet tweetu v db: ", len(data_frame["time"]))
    return fig

#================================================================================================================

#--------------------twitter callback pro update "Database contains ... rows"-------------------
@app.callback(Output("count-tweetTable", "children"),
             [Input('t-database', 'value')])
def count_row(keyword):
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    cursor = cnx.cursor()
    cursor.execute("""
                   SELECT COUNT(*) 
                   FROM """+ keyword +""";
                   """
                   )
    count = str(cursor.fetchone()[0])
    cursor.execute("""SELECT created_at FROM """+ keyword +""" ORDER BY created_at ASC LIMIT 1""")
    cursor.close
    for firstrow in cursor.fetchall():
        firstresult = firstrow
    datetime_from = firstresult[0].strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""SELECT created_at FROM """+ keyword +""" ORDER BY created_at DESC LIMIT 1""")
    for lastrow in cursor.fetchall():
        lastresult = lastrow
    datetime_to = lastresult[0].strftime('%Y-%m-%d %H:%M:%S')
    p = "Database contains "
    p3 = " rows; "
    datetime_fromtext = "  Since: "
    datetime_totext = ";  Until: "
    info = "".join([p,count,p3,datetime_fromtext,datetime_from,datetime_totext,datetime_to])
    return info

#--------------------news callback pro update "Database contains ... rows"-------------------
@app.callback(Output("count-news", "children"),
             [Input('news-dropdown', 'value'),
              Input("interval-component-count", "n_intervals")])
def count_row(news, n_intervals):
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    cursor = cnx.cursor()
    cursor.execute("""
                   SELECT COUNT(*) 
                   FROM """+ news +""";
                   """
                   )
    count = str(cursor.fetchone()[0])
    cursor.execute("""SELECT published FROM """+ news +""" ORDER BY published ASC LIMIT 1""")
    cursor.close
    for firstrow in cursor.fetchall():
        firstresult = firstrow
    datetime_from = firstresult[0].strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("""SELECT published FROM """+ news +""" ORDER BY published DESC LIMIT 1""")
    for lastrow in cursor.fetchall():
        lastresult = lastrow
    datetime_to = lastresult[0].strftime('%Y-%m-%d %H:%M:%S')
    p = "Database contains "
    p3 = " rows;"
    datetime_fromtext = "  Since: "
    datetime_totext = ";  Until: "
    info = "".join([p,count,p3,datetime_fromtext,datetime_from,datetime_totext,datetime_to])
    return info

#--------------------reddit callback pro update "Database contains ... rows"-------------------
@app.callback(Output("count-reddit", "children"),
             [Input('reddit-dropdown', 'value'),
              Input("interval-component-count", "n_intervals")])
def count_row(news, n_intervals):
    cursor=kody.cnx.cursor()
    cursor.execute("""
                   SELECT COUNT(*) 
                   FROM """+ news +""";
                   """
                   )
    count = str(cursor.fetchone()[0])
    p = "Database contains "
    p3 = " rows "
    info = "".join([p,count,p3])
    return info

@app.callback(Output('backtesting-results', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    
    if tab == 'b-321-1':
        with open('/home/stepan/stranka/backtrader/figures/newsF12.json', 'r') as f:
            fig = plotly.io.from_json(f.read())
    if tab == 'b-321-3':
        with open('/home/stepan/stranka/backtrader/figures/newsF12m.json', 'r') as f:
            fig = plotly.io.from_json(f.read())
    if tab == 'b-322-1':
        with open('/home/stepan/stranka/backtrader/figures/news0G1j.json', 'r') as f:
            fig = plotly.io.from_json(f.read())
    if tab == 'b-322-2':
        with open('/home/stepan/stranka/backtrader/figures/twitter0m.json', 'r') as f:
            fig = plotly.io.from_json(f.read())
    if tab == 'b-323-1':
        with open('/home/stepan/stranka/backtrader/figures/twitterAIR1.json', 'r') as f:
            fig = plotly.io.from_json(f.read())
    if tab == 'b-323-2':
        with open('/home/stepan/stranka/backtrader/figures/twitterAIR1m.json', 'r') as f:
            fig = plotly.io.from_json(f.read())

    fig["layout"].update(
                    margin=dict(l=0, r=0, t=40, b=0),)
    return html.Div(children=[
                dcc.Graph(
                    figure = fig,
                    style = {
                        "height":"900px",}
                    )])

if __name__ == '__main__':
    app.run_server(debug=True, host="0.0.0.0")
