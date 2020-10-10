import pandas as pd
from datetime import datetime
from kody_reddit import reddit
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import kody
from tqdm import tqdm
import praw
import mysql

def reddit_comments(sub_reddit, query, database):
    cursor=kody.cnx.cursor()

    subreddit = reddit.subreddit(sub_reddit)

    #time_filter – Can be one of: all, day, hour, month, week, year (default: all).
    top_subreddit = subreddit.search(query=query, sort="new", time_filter="all", limit=None) #limited to 1000 results

    analyser = SentimentIntensityAnalyzer()
    print("start: ", datetime.now().isoformat())
    for submission in top_subreddit:
        #timestamp = submission.created_utc
        #created = datetime.utcfromtimestamp(timestamp)
        #adult = submission.over_18
        #username = submission.author.name
        post = submission.title
        url = submission.url
        #sentiment_textblob = TextBlob(post).polarity
    #
        #try:
        #    redditor = reddit.redditor(username)
        #    karma_post = redditor.link_karma 
        #except AttributeError:
        #    karma_post = "0"
        #
        #vader = analyser.polarity_scores(post)
        #sentiment_vader = vader["compound"]
        try:
            submission = reddit.submission(url=url)
        except praw.exceptions.InvalidURL:
            continue
        try:
            submission.comments.replace_more(limit=None)
        except Exception as e:
            print(f"exception error: {e}")
            continue
        for comment in tqdm(submission.comments.list()):
            try:
                time = datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d %H:%M:%S')
            except mysql.connector.errors.DataError as e:
                print(f"mysql error: {e}")
                continue
            topic_comment = comment.body
            ups = comment.ups
            sentiment_textblob = TextBlob(topic_comment).polarity
            vader = analyser.polarity_scores(topic_comment)
            sentiment_vader = vader["compound"]
            comment_keywords=["GILD", "Remdesivir", "Gilead"]
            if any(s in topic_comment for s in comment_keywords):
                try:
                    username = comment.author.name
                except AttributeError:
                    username = "NoneType"
                try:
                    redditor = reddit.redditor(username)
                    karma_post = redditor.link_karma 
                except:
                    karma_post = "0"
                try:
                    cursor.execute(
                            """
                            INSERT INTO """+ database +""" 
                                (time, subreddit, post, username, karma_post, ups, topic_comment, sentiment_textblob, sentiment_vader, url) 
                            SELECT * FROM 
                                (SELECT %s AS time,%s AS subreddit,%s AS post ,%s AS username,%s AS karma_post,%s AS ups,%s AS topic_comment,%s AS sentiment_textblob,%s AS sentiment_vader,%s AS url) 
                            AS tmp 
                            WHERE NOT EXISTS 
                                (SELECT topic_comment FROM """+ database +""" WHERE topic_comment = %s) 
                            LIMIT 1
                            """,
                            (time, sub_reddit, post, username, karma_post, ups, topic_comment, sentiment_textblob, sentiment_vader, url, topic_comment))
                    kody.cnx.commit()
                except mysql.connector.errors.DatabaseError as e:
                    print("mysql error "+ str(e) +" ")
                    continue

searches = [
    ["Investing", "GILD", "redditGILD"],
    ["Investing", "Gilead", "redditGILD"],
    ["Investing", "Remdesivir", "redditGILD"],
    ["Wallstreetbets", "GILD", "redditGILD"],
    ["Wallstreetbets", "Gilead", "redditGILD"],
    ["Wallstreetbets", "Remdesivir", "redditGILD"],
    ["personalfinance", "GILD", "redditGILD"],
    ["personalfinance", "Gilead", "redditGILD"],
    ["personalfinance", "Remdesivir", "redditGILD"],
    ["news", "GILD", "redditGILD"],
    ["news", "Gilead", "redditGILD"],
    ["news", "Remdesivir", "redditGILD"],
]
def get_reddit():
    for sub_reddit, query, database in searches:
        reddit_comments(sub_reddit, query, database)

def is_it_running():
    script_name = "reddit_GILD"
    now = datetime.now().isoformat()
    cursor.execute(
            "UPDATE running_scripts SET script = %s, time = %s WHERE script = %s",
            (script_name, now, script_name))
    kody.cnx.commit()

get_reddit()

#    try:
#        cursor.execute(
#                """
#                INSERT INTO redditGILD 
#                    (time, username, adult, post, post_karma, url, sentiment_textblob, sentiment_vader) 
#                SELECT * FROM 
#                    (SELECT %s AS time,%s AS username,%s AS adult,%s AS post,%s AS post_karma,%s AS url,%s AS sentiment_textblob,%s AS sentiment_vader) 
#                AS tmp 
#                WHERE NOT EXISTS 
#                    (SELECT post FROM redditGILD WHERE post = %s) 
#                LIMIT 1
#                """,
#                (created, username, adult, post, karma_post, url, sentiment_textblob, sentiment_vader, post))
#        kody.cnx.commit()
#    except:
#        print("error")
#
#    #print(username)

print("done: ", datetime.now().isoformat())