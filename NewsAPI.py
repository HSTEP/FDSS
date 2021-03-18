from newsapi import NewsApiClient
from textblob import TextBlob
from datetime import datetime
import kody
import time
import datetime as dt
from dateutil.relativedelta import relativedelta
from newsapi import newsapi_client
from tqdm import tqdm
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyser = SentimentIntensityAnalyzer()

newsapi = NewsApiClient(api_key = kody.newsAPI_key)

time_from = dt.datetime.now() - relativedelta(months=1)
time_from = time_from.replace(microsecond=0).isoformat()
time_to = dt.datetime.now().replace(microsecond=0).isoformat()

print(dt.datetime.now().isoformat())
cursor=kody.cnx.cursor()
all_articles = newsapi.get_everything(qintitle='cloudflare',   #(ethereum OR litecoin) NOT bitcoin #qintitle nebo q - všude
                                      #sources='associated-press, bbc-news, bloomberg, business-insider, cbc-news, cnn, engadget, financial-post, fortune, fox-news, google-news, hacker-news, recode, reuters, techcrunch, the-next-web, the-verge, the-wall-street-journal, the-washington-post, the-washington-times, time, wired',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param= "2021-02-18T12:44:32",  #ISO 8601 format
                                      to= "2021-03-18T12:44:32",  #ISO 8601 format
                                      language='en',
                                      sort_by='publishedAt',
                                      page_size=100,
                                      page=1)

def news(database):
    while True:
        #cursor=kody.cnx.cursor()
        #cursor.execute("""SELECT published FROM newsNET ORDER BY published ASC LIMIT 1""")
        #for row in cursor.fetchall():
        #    result = row
        #datetimeto = result[0].strftime('%Y-%m-%dT%H:%M:%S')
        #all_articles = newsapi.get_everything(qintitle='cloudflare',   #(ethereum OR litecoin) NOT bitcoin #qintitle nebo q - všude
        #                              #sources='associated-press, bbc-news, bloomberg, business-insider, cbc-news, cnn, engadget, financial-post, fortune, fox-news, google-news, hacker-news, recode, reuters, techcrunch, the-next-web, the-verge, the-wall-street-journal, the-washington-post, the-washington-times, time, wired',
        #                              #domains='bbc.co.uk,techcrunch.com',
        #                              from_param= "2021-02-18T12:44:32",  #ISO 8601 format
        #                              to= datetimeto,  #ISO 8601 format
        #                              language='en',
        #                              sort_by='publishedAt',
        #                              page_size=100,
        #                              page=1)
        for article in all_articles["articles"]:
            source = article["source"]["name"]
            published_at = article["publishedAt"]
            title = article["title"]
            url = article["url"]
            try:
                content = article["content"]
                content_sentiment = TextBlob(content).polarity
                vader = analyser.polarity_scores(content)
                content_sentiment_vader = vader["compound"]
            except:
                content = "chyba"
                content_sentiment = 0
                content_sentiment_vader = 0
            sentiment = TextBlob(title).polarity
            vader = analyser.polarity_scores(title)
            sentiment_vader = vader["compound"]
            new_published_at = datetime.strftime(datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ'),
                                                     '%Y-%m-%d %H:%M:%S')
            #print(source, published_at, title, url, sentiment)
            cursor.execute(
                    """
                    INSERT INTO """+ database +""" (source, published, title, url, sentiment, sentiment_vader, content, content_sentiment, content_sentiment_vader) 
                    SELECT * FROM (SELECT %s AS source,%s AS published,%s AS title,%s AS url,%s AS sentiment,%s AS sentiment_vader,%s AS content,%s AS content_sentiment,%s AS content_sentiment_vader) 
                    AS tmp 
                    WHERE NOT EXISTS (SELECT title FROM """+ database +""" WHERE title = %s) 
                    LIMIT 1
                    """,
                    (source, new_published_at, title, url, sentiment, sentiment_vader, content, content_sentiment, content_sentiment_vader, title))
            kody.cnx.commit()   
            print(new_published_at) 
            print("for")
            #time.sleep(0.2)
        time.sleep(5)    
        print("while")
        
news('newsNET')
#news('Pfizer OR PFE OR BNT162b2', 'newsPFE')

print(dt.datetime.now().isoformat())
#while True:
#    gild_news()
#    time.sleep(5)