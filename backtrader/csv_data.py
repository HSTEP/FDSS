import yfinance as yf
import pandas as pd
import sys
import kody

msft = yf.Ticker("XRP-USD")
data = msft.history(period="60d", interval="2m")
# remove timezone:
data.index = data.index.tz_convert(tz=None)
# data.index = pd.to_datetime(data.index.astype(str), format="%Y.%m.%d %H:%M:%S"),
twitter = pd.read_sql("""
                        SELECT 
                            time, sentiment, sentiment_vader 
                        FROM 
                            tweetTable_resampled_5m 
                        WHERE 
                            (time >= "2021-01-07 14:30:00" ) AND (time <  "2021-02-24 20:58:00") 
                        ORDER BY 
                            time ASC
                        """, 
                        con=kody.cnx)
twitter = twitter.set_index("time")
data = data.join(twitter)
data = data.interpolate(method='polynomial', order=2)
data = data.fillna(0)
print(data)

#data[["Open","High","Low", "Close","Volume", "sentiment", "sentiment_vader"]].to_csv('csv_GILD.csv')