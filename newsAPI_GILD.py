from newsapi import NewsApiClient
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime
import kody
import time
import datetime as dt
from dateutil.relativedelta import relativedelta

cursor=kody.cnx.cursor()

analyser = SentimentIntensityAnalyzer()

newsapi = NewsApiClient(api_key = kody.newsAPI_key)

time_from = dt.datetime.now() - relativedelta(days=28)
time_from = time_from.replace(microsecond=0).isoformat()
time_to = dt.datetime.now() - relativedelta(days=0)
time_to = time_to.replace(microsecond=0).isoformat()
print(time_from, time_to)

def gild_news():
    all_articles = newsapi.get_everything(qintitle='GILD OR gilead OR remdesivir',   #(ethereum OR litecoin) NOT bitcoin #qintitle nebo q - všude
                                      #sources='associated-press, bbc-news, bloomberg, business-insider, cbc-news, cnn, engadget, financial-post, fortune, fox-news, google-news, hacker-news, recode, reuters, techcrunch, the-next-web, the-verge, the-wall-street-journal, the-washington-post, the-washington-times, time, wired',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param= time_from,  #ISO 8601 format
                                      to= time_to,  #ISO 8601 format
                                      language='en',
                                      sort_by='publishedAt',
                                      page_size=100,
                                      page=1)

    for article in all_articles["articles"]:
        source = article["source"]["name"]
        published_at = article["publishedAt"]
        title = article["title"]
        url = article["url"]
        sentiment = TextBlob(article["title"]).polarity
        vader = analyser.polarity_scores(article["title"])
        sentiment_vader = vader["compound"]
        new_published_at = datetime.strftime(datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ'),
                                                 '%Y-%m-%d %H:%M:%S')
        #print(source, published_at, title, url, sentiment)

        cursor.execute(
                "INSERT INTO newsGILD (source, published, title, url, sentiment, sentiment_vader) SELECT * FROM (SELECT %s AS source,%s AS published,%s AS title,%s AS url,%s AS sentiment,%s AS sentiment_vader) AS tmp WHERE NOT EXISTS (SELECT title FROM newsGILD WHERE title = %s) LIMIT 1",
                (source, new_published_at, title, url, sentiment, sentiment_vader, title))
        kody.cnx.commit()

def is_it_running():
    script_name = "newsAPI_GILD.py"
    now = datetime.now().isoformat()
    cursor.execute(
            "UPDATE running_scripts SET script = %s, time = %s WHERE script = %s",
            (script_name, now, script_name))
    kody.cnx.commit()

while True:
    gild_news()
    is_it_running()
    print(datetime.now().isoformat())
    time.sleep(3600)