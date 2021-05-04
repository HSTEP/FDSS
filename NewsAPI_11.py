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

begin_time = datetime.now()
cursor=kody.cnx.cursor()
#all_articles = newsapi.get_everything(qintitle='pfe OR pfizer',   #(ethereum OR litecoin) NOT bitcoin #qintitle nebo q - všude
#                                      #sources='associated-press, bbc-news, bloomberg, business-insider, cbc-news, cnn, engadget, financial-post, fortune, fox-news, google-news, hacker-news, recode, reuters, techcrunch, the-next-web, the-verge, the-wall-street-journal, the-washington-post, the-washington-times, time, wired',
#                                      #domains='bbc.co.uk,techcrunch.com',
#                                      from_param= "2021-02-28T12:44:32",  #ISO 8601 format
#                                      to= "2021-03-29T12:44:32",  #ISO 8601 format
#                                      language='en',
#                                      sort_by='publishedAt',
#                                      page_size=100,
#                                      page=1)

def news(database, keywords):
    cursor=kody.cnx.cursor()
    #try:
    cursor.execute("""SELECT published FROM """+ database +""" ORDER BY published DESC LIMIT 1""")
    for row in cursor.fetchall():
        result = row
    last_article_in_db = result[0].strftime('%Y-%m-%dT%H:%M:%S')
    datetimeto = (datetime.now()-relativedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
    while True:
        print(keywords, last_article_in_db, datetimeto)
        time.sleep(2)
        #except:
        #    datetimeto = (dt.datetime.now() - relativedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
        all_articles = newsapi.get_everything(qintitle=keywords,   #(ethereum OR litecoin) NOT bitcoin #qintitle nebo q - všude
                                      #sources='associated-press, bbc-news, bloomberg, business-insider, cbc-news, cnn, engadget, financial-post, fortune, fox-news, google-news, hacker-news, recode, reuters, techcrunch, the-next-web, the-verge, the-wall-street-journal, the-washington-post, the-washington-times, time, wired',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param = last_article_in_db,  #ISO 8601 format, oldest article allowed
                                      to =  datetimeto,# newest article allowed
                                      language='en', 
                                      sort_by='publishedAt',
                                      page_size=100,
                                      page=1)
        if len(all_articles["articles"]) == 1 or last_article_in_db == datetimeto:
            print("len == 1")
            return

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
            datetimeto = datetime.strftime(datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ'),
                                                     '%Y-%m-%dT%H:%M:%S')
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
            #time.sleep(0.2)
        time.sleep(2)


def news_GILD(database, keywords):
    cursor=kody.cnx.cursor()
    #try:
    cursor.execute("""SELECT published FROM """+ database +""" ORDER BY published DESC LIMIT 1""")
    for row in cursor.fetchall():
        result = row
    last_article_in_db = result[0].strftime('%Y-%m-%dT%H:%M:%S')
    datetimeto = (datetime.now()-relativedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
    while True:
        print(keywords, last_article_in_db, datetimeto)
        time.sleep(2)
        #except:
        #    datetimeto = (dt.datetime.now() - relativedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S')
        all_articles = newsapi.get_everything(qintitle=keywords,   #(ethereum OR litecoin) NOT bitcoin #qintitle nebo q - všude
                                      #sources='associated-press, bbc-news, bloomberg, business-insider, cbc-news, cnn, engadget, financial-post, fortune, fox-news, google-news, hacker-news, recode, reuters, techcrunch, the-next-web, the-verge, the-wall-street-journal, the-washington-post, the-washington-times, time, wired',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param = last_article_in_db,  #ISO 8601 format, oldest article allowed
                                      to =  datetimeto,# newest article allowed
                                      language='en', 
                                      sort_by='publishedAt',
                                      page_size=100,
                                      page=1)
        if len(all_articles["articles"]) == 1 or last_article_in_db == datetimeto:
            print("len == 1")
            return

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
            datetimeto = datetime.strftime(datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ'),
                                                     '%Y-%m-%dT%H:%M:%S')
            #print(source, published_at, title, url, sentiment)
            cursor.execute(
                    """
                    INSERT INTO """+ database +""" (source, published, title, url, sentiment, sentiment_vader) 
                    SELECT * FROM (SELECT %s AS source,%s AS published,%s AS title,%s AS url,%s AS sentiment,%s AS sentiment_vader) 
                    AS tmp 
                    WHERE NOT EXISTS (SELECT title FROM """+ database +""" WHERE title = %s) 
                    LIMIT 1
                    """,
                    (source, new_published_at, title, url, sentiment, sentiment_vader, title))
            kody.cnx.commit()   
            print(new_published_at)
            #time.sleep(0.2)
        time.sleep(2)

#INSERT INTO running_scripts VALUES ("NewsAPI_11.py", "2020-12-01 00:01:56")
def is_it_running():
    script_name = "NewsAPI_11.py"
    now = datetime.now().isoformat()
    cursor.execute("""
                    UPDATE 
                        running_scripts 
                    SET 
                        script = %s, time = %s 
                    WHERE 
                        script = %s""",
                    (script_name, now, script_name))
    kody.cnx.commit()
while True:
    news('newsAIRBUS', "Airbus")
    news('newsAMC', "AMC")
    news('newsAZN', "AZN OR AstraZeneca")
    news('newsBOEING', "Boeing")
    news('newsF', "Ford")
    news('newsNET', "Cloudflare")
    news('newsORCL', "ORCL OR Oracle")
    news('newsPFE', "PFE OR Pfizer")
    news('newsRACE', "Ferrari")
    news('newsTOYOF', "TOYOF OR Toyota")
    news_GILD('newsGILD', "GILD OR Gilead")
    is_it_running()
    print("run: ",datetime.now().isoformat())
    time.sleep(22000)
