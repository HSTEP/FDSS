import tweepy
import kody
import mysql.connector
from mysql.connector import errorcode
import json
from datetime import datetime
import re
from textblob import TextBlob
import time

auth = tweepy.OAuthHandler(kody.API_key, kody.API_secret_key)
auth.set_access_token(kody.Access_token, kody.Access_token_secret)
cursor=kody.cnx.cursor()

def deEmojify(raw_tweet):
    if raw_tweet:
        return raw_tweet.encode('ascii', 'ignore').decode('ascii')
    else:
        return None

def clean_tweet(text):
    text = deEmojify(text)
    text = re.sub(r'(https|http)?:\/\/(\t|\.|\/|\?|\=|\&|\%)*\b', '', text)
    text = re.sub(r'@', '', text)
    text = re.sub(r't.co/', '', text)
    text = text.lower()
    return text

def retweeted_json(tweet):
    return tweet["retweeted"]

class listener(tweepy.streaming.StreamListener):

    def on_data(self, data):
        all_data = json.loads(data)
        # check to ensure there is text in
        # the json data
        if not retweeted_json(all_data):
            if not all_data["truncated"]:
                tweet = all_data["text"]
            else:
                tweet = all_data["extended_tweet"]["full_text"]

            raw_tweet = clean_tweet(tweet)
            username = deEmojify(all_data["user"]["name"])
            time = all_data["created_at"]
            followers = all_data["user"]["followers_count"]
            sentiment = TextBlob(raw_tweet).polarity
            # print("Followers: ", followers)
            new_datetime = datetime.strftime(datetime.strptime(time, '%a %b %d %H:%M:%S +0000 %Y'),
                                             '%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO tweetTable (time, username, tweet, followers, sentiment) VALUES (%s,%s,%s,%s,%s)",
                (new_datetime, username, raw_tweet, followers, sentiment))

            kody.cnx.commit()

            #print(all_data["retweeted"], all_data["truncated"])
            print((username, raw_tweet))
            return True

    def on_error(self, status_code):
        '''
        Since Twitter API has rate limits, stop srcraping data as it exceed to the thresold.
        '''
        if status_code == 420:
            # return False to disconnect the stream
            return False

words = ["xrp, ripple"]

api = tweepy.API(auth)
tweets_search = api.search(q=words,lang="en", count=1000, tweet_mode="extended")
for tweet in tweets_search:
    if not tweet.retweeted:
        if not tweet.truncated:
            tweet_searched = tweet.full_text
        else:
            tweet_searched = tweet.text
        searched_sentiment = TextBlob(clean_tweet(tweet_searched)).polarity

        cursor.execute(
                "INSERT INTO tweetTable (time, username, tweet, followers, sentiment) VALUES (%s,%s,%s,%s,%s)",
                (tweet.created_at, tweet.author.screen_name, clean_tweet(tweet_searched), tweet.author.followers_count, searched_sentiment))
        kody.cnx.commit() 
    print(tweet.author.screen_name, clean_tweet(tweet_searched), tweet.created_at)

if __name__ == "__main__":
    while True:
        try:
            twitterStream = tweepy.Stream(auth, listener(), tweet_mode='extended')
            twitterStream.filter(track=words,
            languages = ["en"], stall_warnings = True) #čárka = OR; mezera = AND
        finally:
            print("Twitter Error")
            time.sleep(30)

