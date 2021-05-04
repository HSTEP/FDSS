import yfinance as yf
import pandas as pd
import sys
import kody
import numpy as np
import plotly.express as px
from datetime import timedelta

def bt_data_sentiment_ffill_news(database, time_from,resampling):
    """
    database = ("newsNET")

    time_from = selecting from DB since time_from = ("2021-02-21 00:00:00")

    resampling = period for resampling DB data = ("2min")
    """

    df = pd.read_sql("SELECT published, sentiment, sentiment_vader FROM "+ database +" WHERE published > \""+ time_from +"\" ORDER BY published DESC", con=kody.cnx)
    df = df.set_index(['published']) #aby fungovalo df.resample
    print(df)
    df["volume"] = 1    #u každého tweetu přidá řádek s volume -> 1 řádek = 1 tweet, proto 1
    df = df.resample(""+resampling+"in").agg(
                                    {'sentiment_vader': np.mean, 
                                    'sentiment': np.average,
                                    'volume': np.sum})   
    #df_mean = df.interpolate(method='linear')
    df["sentiment"] = df["sentiment"].fillna(method="ffill")
    df["sentiment_vader"] = df["sentiment_vader"].fillna(method="ffill")
    df.to_csv("/Users/stepan/OneDrive/Diplomka/python/interpolacenebofillna.csv")
    #df_mean["sentiment"].clip(lower=-1,upper=1, inplace = True)
    #df_mean["sentiment_vader"].clip(lower=-1,upper=1, inplace = True)
    #print(df_mean)
    return df

def get_bt_data_news(ticker, database, time_from,interval):
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
    data = data.join(bt_data_sentiment_ffill_news(database, time_from, interval))
    #data[["Open","High","Low", "Close", "sentiment", "sentiment_vader"]].to_csv("backtrader/twitter_data/twitter"+ticker+".csv")
    print(data)
    fig = px.line(x=data.index, y=data["sentiment"])
    fig.show()
    return

def bt_data_sentiment_ffill_twitter(database, time_from,resampling):
    """
    database = ("newsNET")

    time_from = selecting from DB since time_from = ("2021-02-21 00:00:00")

    resampling = period for resampling DB data = ("2min")
    """

    df = pd.read_sql("SELECT created_at, sentiment_textblob, sentiment_vader FROM "+ database +" WHERE created_at > \""+ time_from +"\" ORDER BY created_at DESC", con=kody.cnx)
    df = df.set_index(['created_at']) #aby fungovalo df.resample
    df.index = df.index - timedelta(days=1) #časová prodleva
    print(df)
    df["volume"] = 1    #u každého tweetu přidá řádek s volume -> 1 řádek = 1 tweet, proto 1
    df = df.resample(""+resampling+"in").agg(
                                    {'sentiment_vader': np.mean, 
                                    'sentiment_textblob': np.average,
                                    'volume': np.sum})   
    #df_mean = df.interpolate(method='linear')
    df["sentiment_textblob"] = df["sentiment_textblob"].fillna(method="ffill")
    df["sentiment_vader"] = df["sentiment_vader"].fillna(method="ffill")
    #df.to_csv("/Users/stepan/OneDrive/Diplomka/python/interpolacenebofillna.csv")
    #df_mean["sentiment_textblob"].clip(lower=-1,upper=1, inplace = True)
    #df_mean["sentiment_vader"].clip(lower=-1,upper=1, inplace = True)
    #print(df_mean)
    return df

def get_bt_data_twitter(ticker, database, time_from,interval):
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
    data = data.join(bt_data_sentiment_ffill_twitter(database, time_from, interval))
    #data[["Open","High","Low", "Close", "sentiment_textblob", "sentiment_vader"]].to_csv("backtrader/twitter_data/twitter"+ticker+".csv")
    #print(data)
    #fig = px.line(x=data.index, y=data["sentiment_vader"])
    #fig.show()
    return

def get_data_news():
    get_bt_data_news("AIR", "newsAIRBUS", "2021-02-24", "2m")
    get_bt_data_news("AMC", "newsAMC", "2021-02-24", "2m")
    get_bt_data_news("AZN", "newsAZN", "2021-02-24", "2m")
    get_bt_data_news("BA", "newsBOEING", "2021-02-24", "2m")
    get_bt_data_news("F", "newsF", "2021-02-24", "2m")
    get_bt_data_news("NET", "newsNET", "2021-02-24", "2m")
    get_bt_data_news("ORCL", "newsORCL", "2021-02-24", "2m")
    get_bt_data_news("PFE", "newsPFE", "2021-02-24", "2m")
    get_bt_data_news("RACE", "newsRACE", "2021-02-24", "2m")
    get_bt_data_news("TOYOF", "newsTOYOF", "2021-02-24", "2m")
    return


def get_data_twitter():
    get_bt_data_twitter("AIR", "tweetTable_AR_AB", "2021-02-24", "2m")
    get_bt_data_twitter("AMC", "tweetTable_AR_AMC", "2021-02-24", "2m")
    get_bt_data_twitter("GILD", "tweetTable_AR_GILD", "2021-02-24", "2m")
    get_bt_data_twitter("BA", "tweetTable_AR_BOEING", "2021-02-24", "2m")
    get_bt_data_twitter("F", "tweetTable_AR_F", "2021-02-24", "2m")
    get_bt_data_twitter("NET", "tweetTable_AR_NET", "2021-02-24", "2m")
    get_bt_data_twitter("ORCL", "tweetTable_AR_ORCL", "2021-02-24", "2m")
    get_bt_data_twitter("PFE", "tweetTable_AR_PFE", "2021-02-24", "2m")
    get_bt_data_twitter("RACE", "tweetTable_AR_RACE", "2021-02-24", "2m")
    get_bt_data_twitter("TOYOF", "tweetTable_AR_TOYOF", "2021-02-24", "2m")
    return

def get_data_test():
    get_bt_data_twitter("NET", "tweetTable_AR_NET", "2021-03-05", "2m")
    return

get_data_test()

#bt_data("NET", "30m")[["Open","High","Low", "Close", "sentiment", "sentiment_vader"]].to_csv('csv_TEST.csv')