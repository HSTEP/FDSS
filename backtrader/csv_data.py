import yfinance as yf
import pandas as pd
import sys
import kody
import numpy as np
import plotly.express as px

#def bt_data(ticker,intervl):
#    """
#    ticker = stock name = "NET"
#    intervl = candle duration = 2m = dvouminutová svíčka
#    """
#    stock = yf.Ticker(ticker)
#    data = stock.history(start="2021-04-13", interval=intervl)
#    # remove timezone:
#    data.index = data.index.tz_convert(tz=None)
#    data.resample("30min")
#    print(data)
#    # data.index = pd.to_datetime(data.index.astype(str), format="%Y.%m.%d %H:%M:%S"),
#    ###twitter = pd.read_sql("""
#    ###                        SELECT 
#    ###                            time, sentiment, sentiment_vader 
#    ###                        FROM 
#    ###                            tweetTable_resampled_5m 
#    ###                        WHERE 
#    ###                            (time >= "2021-01-07 14:30:00" ) AND (time <  "2021-02-24 20:58:00") 
#    ###                        ORDER BY 
#    ###                            time ASC
#    ###                        """, 
#    ###                        con=kody.cnx)
#
#    data_frame = pd.read_sql('SELECT published, sentiment, sentiment_vader FROM newsNET WHERE published > "2021-04-13 00:00:00" ORDER BY published DESC', con=kody.cnx)
#    data_frame = data_frame.set_index(['published']) #aby fungovalo data_frame.resample
#    print(data_frame)
#    data_frame["volume"] = 1    #u každého tweetu přidá řádek s volume -> 1 řádek = 1 tweet, proto 1
#    df_mean = data_frame.resample("30min").agg({'sentiment_vader': np.mean, 'sentiment': np.mean,'volume': np.sum})    #to dělám aby candlestick něměly high=1 a low=0
#    print(df_mean)
#    ###twitter = twitter.set_index("time")
#    data = data.join(df_mean)
#    data = data.interpolate(method='polynomial', order=2)
#    #data = data.fillna(0)
#    return data

def bt_data_sentiment_interpolate(database, time_from,resampling):
    """
    database = ("newsNET")

    time_from = selecting from DB since time_from = ("2021-02-21 00:00:00")

    resampling = period for resampling DB data = ("2min")
    """

    data_frame = pd.read_sql("SELECT published, sentiment, sentiment_vader FROM "+ database +" WHERE published > \""+ time_from +"\" ORDER BY published DESC", con=kody.cnx)
    data_frame = data_frame.set_index(['published']) #aby fungovalo data_frame.resample
    print(data_frame)
    data_frame["volume"] = 1    #u každého tweetu přidá řádek s volume -> 1 řádek = 1 tweet, proto 1
    df_mean = data_frame.resample(""+resampling+"in").agg({'sentiment_vader': np.average, 'sentiment': np.average,'volume': np.sum})    #to dělám aby candlestick něměly high=1 a low=0
    df_mean = df_mean.interpolate(method='polynomial', order = 2)
    df_mean["sentiment_vader"].clip(lower=-1,upper=1, inplace = True)
    print(df_mean)
    return df_mean

def get_bt_data(ticker, database, time_from,interval):
    """
    ticker = ("NET")

    time_from = ("2021-02-21")

    intervl = ("2m")
    """

    stock = yf.Ticker(ticker)
    data = stock.history(start=time_from, interval=interval)
    # remove timezone:
    data.index = data.index.tz_convert(tz="UTC")
    data.index = data.index.tz_convert(tz=None)
    data = data.join(bt_data_sentiment_interpolate(database, time_from, interval))
    data[["Open","High","Low", "Close", "sentiment", "sentiment_vader"]].to_csv("stocks_data/"+database+".csv")
    print(data)
    #fig = px.line(x=data.index, y=data["sentiment_vader"])
    #fig.show()

    return

get_bt_data("AIR", "newsAIRBUS", "2021-02-21", "2m")
get_bt_data("AMC", "newsAMC", "2021-02-21", "2m")
get_bt_data("AZN", "newsAMC", "2021-02-21", "2m")
get_bt_data("BA", "newsBOEING", "2021-02-21", "2m")
get_bt_data("F", "newsF", "2021-02-21", "2m")
get_bt_data("NET", "newsNET", "2021-02-21", "2m")
get_bt_data("ORCL", "newsORCL", "2021-02-21", "2m")
get_bt_data("PFE", "newsPFE", "2021-02-21", "2m")
get_bt_data("RACE", "newsRACE", "2021-02-21", "2m")
get_bt_data("TOYOF", "newsTOYOF", "2021-02-21", "2m")

#bt_data("NET", "30m")[["Open","High","Low", "Close", "sentiment", "sentiment_vader"]].to_csv('csv_TEST.csv')