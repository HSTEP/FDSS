from newsapi import NewsApiClient
from textblob import TextBlob
from datetime import datetime
import kody
import time
import datetime as dt
from dateutil.relativedelta import relativedelta

cursor=kody.cnx.cursor()

newsapi = NewsApiClient(api_key = kody.newsAPI_key)

time_from = dt.datetime.now() - relativedelta(months=1)
time_from = time_from.replace(microsecond=0).isoformat()
time_to = dt.datetime.now().replace(microsecond=0).isoformat()

print(time_from, time_to)

all_articles = newsapi.get_everything(qintitle='GILD OR gilead OR remdesivir',   #(ethereum OR litecoin) NOT bitcoin #qintitle nebo q - všude
                                      #sources='associated-press, bbc-news, bloomberg, business-insider, cbc-news, cnn, engadget, financial-post, fortune, fox-news, google-news, hacker-news, recode, reuters, techcrunch, the-next-web, the-verge, the-wall-street-journal, the-washington-post, the-washington-times, time, wired',
                                      #domains='bbc.co.uk,techcrunch.com',
                                      from_param= time_from,  #ISO 8601 format
                                      to= time_to,  #ISO 8601 format
                                      language='en',
                                      sort_by='publishedAt',
                                      page_size=100,
                                      page=1)
def gild_news():
    for article in all_articles["articles"]:
        source = article["source"]["name"]
        published_at = article["publishedAt"]
        title = article["title"]
        url = article["url"]
        sentiment = TextBlob(article["title"]).polarity
        new_published_at = datetime.strftime(datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ'),
                                                 '%Y-%m-%d %H:%M:%S')
        print(source, published_at, title, url, sentiment)

        cursor.execute(
                "INSERT INTO newsGILD (source, published, title, url, sentiment) SELECT * FROM (SELECT %s,%s,%s,%s,%s) AS tmp WHERE NOT EXISTS (SELECT title FROM newsGILD WHERE title = %s) LIMIT 1",
                (source, new_published_at, title, url, sentiment, title))
        kody.cnx.commit()
while True:
    gild_news()
    time.sleep(3600)