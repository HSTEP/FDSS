import kody
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objects as go
import os
import numpy as np
from plotly.subplots import make_subplots
from sqlalchemy import create_engine
from tqdm import tqdm
import plotly.express as px
import mysql.connector

begin_time = datetime.now()

engine = create_engine(kody.sqlalchemy_psswd)

def dataframe_r_twitter(source_sql_table, time_period, destination_sql_table):
    '''Create twitter 
    
    source_sql_table = z jaké tabulky vybrat data
    time_period = granualita po resamplingu
    destination_sql_table = do jaké databáze data uložit
    '''
    cnx = mysql.connector.connect(user=kody.mysql_username, password=kody.mysql_password,
                                  host='localhost',
                                  database='twitter',
                                  charset = 'utf8')
    #cursor.execute("""SELECT 
    #                    created_at 
    #                FROM """+source_sql_table+""" 
    #                ORDER BY 
    #                    created_at ASC LIMIT 1""")
    #for row in cursor.fetchall():
    #    result = row
    #datetimeto = result[0].strftime('%Y-%m-%dT%H:%M:%S')
    data_frame = pd.read_sql("""SELECT 
                                    sentiment_textblob, sentiment_vader, created_at 
                                FROM """+source_sql_table+""" 
                                ORDER BY 
                                    created_at ASC
                                """, 
                                con=cnx)
    data_frame = data_frame.set_index(['created_at']) #aby fungovalo data_frame.resample
    data_frame["volume"] = 1    #u každého tweetu přidá řádek s volume -> 1 řádek = 1 tweet, proto 1
    df_r = data_frame.resample(time_period).agg({'sentiment_vader': np.mean, 'sentiment_textblob': np.mean,'volume': np.sum})
    df_r.to_sql(destination_sql_table, con=engine, if_exists="append", index=True)
    return

def resample_t():
    dataframe_r_twitter("tweetTable_AR_AB", "10min", "tweetTable_AR_AB_r")
    dataframe_r_twitter("tweetTable_AR_AMC", "10min", "tweetTable_AR_AMC_r")
    dataframe_r_twitter("tweetTable_AR_BOEING", "10min", "tweetTable_AR_BOEING_r")
    dataframe_r_twitter("tweetTable_AR_F", "10min", "tweetTable_AR_F_r")
    dataframe_r_twitter("tweetTable_AR_GILD", "10min", "tweetTable_AR_GILD_r")
    dataframe_r_twitter("tweetTable_AR_NET", "10min", "tweetTable_AR_NET_r")
    dataframe_r_twitter("tweetTable_AR_ORCL", "10min", "tweetTable_AR_ORCL_r")
    dataframe_r_twitter("tweetTable_AR_PFE", "10min", "tweetTable_AR_PFE_r")
    dataframe_r_twitter("tweetTable_AR_RACE", "10min", "tweetTable_AR_RACE_r")
    dataframe_r_twitter("tweetTable_AR_TOYOF", "10min", "tweetTable_AR_TOYOF_r")
    dataframe_r_twitter("tweetTable_AR_AZN", "10min", "tweetTable_AR_AZN_r")
    return

resample_t()
print("duration: ", datetime.now() - begin_time)