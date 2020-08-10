import pandas as pd
from datetime import datetime
from kody_reddit import reddit
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import kody
cursor=kody.cnx.cursor()

subreddit = reddit.subreddit('Investing')
top_subreddit = subreddit.search(query="GILD", sort="new", limit=1000)

analyser = SentimentIntensityAnalyzer()
print("start: ", datetime.now().isoformat())
for submission in top_subreddit:
    timestamp = submission.created_utc
    created = datetime.utcfromtimestamp(timestamp)
    adult = submission.over_18
    username = submission.author.name
    post = submission.title
    url = submission.url

    sentiment_textblob = TextBlob(post).polarity

    try:
        redditor = reddit.redditor(username)
        karma_post = redditor.link_karma 
    except AttributeError:
        karma_post = "0"
    
    vader = analyser.polarity_scores(post)
    vader = json.dumps(vader)
    vader = json.loads(vader)
    sentiment_vader = vader["compound"]
    
    try:
        cursor.execute(
                "INSERT INTO redditGILD (time, username, adult, post, post_karma, url, sentiment_textblob, sentiment_vader) SELECT * FROM (SELECT %s AS time,%s AS username,%s AS adult,%s AS post,%s AS post_karma,%s AS url,%s AS sentiment_textblob,%s AS sentiment_vader) AS tmp WHERE NOT EXISTS (SELECT post FROM redditGILD WHERE post = %s) LIMIT 1",
                (created, username, adult, post, karma_post, url, sentiment_textblob, sentiment_vader, post))
        kody.cnx.commit()
    except:
        print("error")

    print(username)

print("done: ", datetime.now().isoformat())