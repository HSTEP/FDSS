import subprocess
import pandas as pd
import plotly.graph_objects as go
import csv
from plotly.subplots import make_subplots
import numpy as np

def run_strategy(*args):

    proc = subprocess.Popen(["/home/stepan/twitter/bin/python3", "/home/stepan/stranka/backtrader/backtrader_web/run_strategy.py"]+list(args), stdout=subprocess.PIPE, cwd="..")
    return proc

def bt_make_chart():

    with open("/home/stepan/stranka/web_writer_backtrader.csv") as f:
        reader = csv.reader(f, delimiter=",")
        rows = []
        reader.__next__()  # Skip first line
        for row in reader:
            if "======" in row[0]:
                break
            rows.append(row[:13] + row[14:])
        df = pd.DataFrame(rows[1:], columns=rows[0])  # [start:stop:step]
        df = df.set_index("datetime")
    df = df.replace(r'^\s*$', np.nan, regex=True)

    try:
        cols = []
        count = 1
        for column in df.columns:
            if column == 'sma':
                cols.append(f'sma{count}')
                count+=1
                continue
            cols.append(column)
        df.columns = cols
    except:
        pass

    fig = make_subplots(rows=4, 
            cols=1, 
            shared_xaxes=True, 
            vertical_spacing=0.01, #to když se změní tak nefunguje row_heights
            row_heights=[0.7, 0.15, 0.15, 0.15],
            )

    fig_ohlc = go.Ohlc(x=df.index,
                    open=df["open"].astype(float),
                    high=df["high"].astype(float),
                    low=df["low"].astype(float),
                    close=df["close"].astype(float),
                    name="0HLC")
    fig.append_trace(fig_ohlc, 1, 1)

    fig_buy = go.Scatter(x = df.index,
                        y = df["buy"].astype(float),
                        marker_symbol="triangle-up",
                        mode = 'markers',
                        name="buy [1 Stock]",
                        marker=dict(
                            color='green',
                            size=10,))
    fig.append_trace(fig_buy, 1, 1)

    fig_sell = go.Scatter(x = df.index,
                        y = df["sell"].astype(float),
                        marker_symbol="triangle-down",
                        mode = 'markers',
                        name="sell [1 Stock]",
                        marker=dict(
                            color='red',
                            size=10,))
    fig.append_trace(fig_sell, 1, 1)

    try:
        fig_sma1 = go.Scatter(x = df.index,
                            y = df["sma1"].astype(float),
                            mode = 'lines',
                            name="Slow MA",)
        fig.append_trace(fig_sma1, 2, 1)

        fig_sma2 = go.Scatter(x = df.index,
                            y = df["sma2"].astype(float),
                            mode = 'lines',
                            name="Fast MA",)
        fig.append_trace(fig_sma2, 2, 1)
    except:
        fig_sentiment = go.Scatter(x = df.index,
                            y = df["sentiment"].astype(float),
                            mode = 'lines',
                            name="sentiment",)
        fig.append_trace(fig_sentiment, 2, 1)

    fig_value = go.Scatter(x = df.index,
                        y = df["value"].astype(float),
                        mode = 'lines',
                        name="Value [$]",)
    fig.append_trace(fig_value, 3, 1)

    fig_value = go.Scatter(x = df.index,
                        y = df["drawdown"].astype(float),
                        mode = 'lines',
                        name="DrawDown [%]",)
    fig.append_trace(fig_value, 4, 1)

    fig.update(layout_xaxis_rangeslider_visible=False)
    fig.update_xaxes(
        rangebreaks=[
            {'pattern': 'day of week', 'bounds': [6, 1]},
            {'pattern': 'hour', 'bounds':[21,13]}
        ])

    fig["layout"].update(title_text="Backtest restult for: "+str((df.iloc[1:1, 10:11]).to_json())[2:-5],
                        title_font_color="#01ff70",
                        template="plotly_dark", 
                        legend_title_text="Legenda: ", 
                        legend_orientation="h", 
                        #legend=dict(x=0, y=0.13),
                        transition_duration=0,
                        margin=dict(l=0, r=0, t=20, b=0),
                        paper_bgcolor="#663300",
                        plot_bgcolor="black",
                        title={
                            "yref": "paper",
                            "y" : 1,
                            "x" : 0.5,
                            "yanchor" : "bottom"},
                            )

    #fig.show()
    #fig.write_html("stranka/backtrader/backtrader_web/backtrader_chart.html")
    return fig