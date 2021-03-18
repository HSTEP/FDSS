import kody
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
import numpy as np
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
from tqdm import tqdm

print("start: ", datetime.now().isoformat())

engine = create_engine(kody.sqlalchemy_psswd)

def dataframe_resampled_time(source_sql_table, time_period, destination_sql_table):
    '''snížení množství dat v databázi, pro dcc.Graph a Backtrader MA
    
    source_sql_table = z jaké tabulky vybrat data
    time_period = granualita po resamplingu
    destination_sql_table = do jaké databáze data uložit
    '''
    #yesterday = datetime.now() - timedelta(days=1)
    #yesterday = yesterday.strftime("%Y-%m-%d %H:%M:%S")

    #data_frame = pd.read_sql('SELECT * FROM tweetTable WHERE time >= "'+yesterday+'" ORDER BY time ASC', con=kody.cnx)
    data_frame = pd.read_sql('SELECT * FROM '+source_sql_table+' ORDER BY time ASC', con=kody.cnx)
    data_frame = data_frame.set_index(['time']) #aby fungovalo data_frame.resample
    data_frame["volume"] = 1    #u každého tweetu přidá řádek s volume -> 1 řádek = 1 tweet, proto 1
    df_mean = data_frame.resample(time_period).agg({'sentiment_vader': np.mean, 'sentiment': np.mean,'volume': np.sum})    #to dělám aby candlestick něměly high=1 a low=0
    df_mean.to_sql(destination_sql_table, con=engine, if_exists="append", index=True)
    return

def dataframe_resampled_selection(source_sql_table, time_delta, order_by, top_selection, bottom_selection, destination_sql_table):
    '''
    source_sql_table = z jaké tabulky vybrat data
    time_delta = čas od kterého se vybírá z tabulky
    order_by = čeho chceme nejvyšší a nejnižší hodnoty
    top_selection = kolik řádek ze zhora vybrat a uložit do databáze (bottom selection = zespoda)
    destination_sql_table = do jaké databáze data uložit
    '''
    df = pd.read_sql('SELECT * FROM '+source_sql_table+' WHERE time >= "'+yesterday+'" ORDER BY '+order_by+' DESC', con=kody.cnx)
    df = df.set_index(['time'])#aby fungovalo data_frame.resample
    result = [group[1] for group in df.groupby(df.index.hour)] #vytvoří list s tabulkami rozdělených po dnech
    print(result)
    for frame in tqdm(result):
        pd.concat([frame.head(top_selection), frame.tail(bottom_selection)]).drop_duplicates()\
            .to_sql(destination_sql_table, con=engine, if_exists="append", index=True)
    return

dataframe_resampled_selection("tweetTable",10,"followers",10,0,"tweetTable_resampled_sentiment")
print("stop: ", datetime.now().isoformat())
