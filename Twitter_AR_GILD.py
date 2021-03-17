import requests
import os
import json
import kody
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from datetime import datetime as dt
import time
import mysql
import re

# To set your environment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
bearer_token = kody.Twitter_AR_bearer_token
search_url = "https://api.twitter.com/2/tweets/search/all"
cursor = kody.cnx.cursor()
analyser = SentimentIntensityAnalyzer()

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'max_results' : 500,
                'start_time' : '2021-01-29T00:00:00Z',
                'query' : '(gild OR gilead) lang:en',
                'end_time' : '2021-03-17T00:00:00Z',
                'tweet.fields' : 'created_at,public_metrics,geo',
                'expansions' : 'author_id', #aby fungovalo user.fields
                'user.fields' : 'name,username,public_metrics,verified,location'
                }

def deEmojify(raw_tweet):
    if raw_tweet:
        return raw_tweet.encode('ascii', 'ignore').decode('ascii')
    else:
        return None

def clean_tweet(text):
    try:
        text = deEmojify(text)
        text = re.sub(r'(https|http)?:\/\/(\t|\.|\/|\?|\=|\&|\%)*\b', '', text)
        text = re.sub(r'@', '', text)
        text = re.sub(r't.co/', '', text)
        text = text.lower()
    except:
        text = "missing"
    return text

def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def connect_to_endpoint(url, headers, params):
    response = requests.request("GET", search_url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def main():
    headers = create_headers(bearer_token)
    amount_of_tweets=0
    while True:
        amount_of_tweets += 1
        if amount_of_tweets % 500 == 0:
            print(amount_of_tweets)

        json_response = connect_to_endpoint(search_url, headers, query_params)  

        is_next_page = True

        if "next_token" not in json_response["meta"]:
            is_next_page = False
        else:
            query_params["next_token"] = json_response["meta"]["next_token"]
            
        for i in range(len(json_response["data"])-1):
            tweet_id = json_response["data"][i]["id"]
            author_id = json_response["data"][i]["author_id"]

            tweet = clean_tweet(json_response["data"][i]["text"])
            sentiment_textblob = TextBlob(tweet).polarity
            vader = analyser.polarity_scores(tweet)
            sentiment_vader = vader["compound"]

            created_at_str = json_response["data"][i]["created_at"]
            created_at = dt.strptime(created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ')
            retweet_count = json_response["data"][i]["public_metrics"]["retweet_count"]
            reply_count = json_response["data"][i]["public_metrics"]["reply_count"]
            like_count = json_response["data"][i]["public_metrics"]["like_count"]
            quote_count = json_response["data"][i]["public_metrics"]["quote_count"]        

            author = {}
            for user in json_response["includes"]["users"]:
                if user["id"] == author_id:
                    author = user

            verified = author["verified"]
            username = clean_tweet(author["name"])
            name = author["username"]
            try:
                location = clean_tweet(author["location"])
            except:
                location = "missing"
            followers_count =  author["public_metrics"]["followers_count"]
            following_count = author["public_metrics"]["following_count"]
            tweet_count = author["public_metrics"]["tweet_count"]
            cursor.execute(
                """
                INSERT INTO tweetTable_AR_GILD 
                    (tweet_id, author_id, tweet, sentiment_textblob, sentiment_vader, created_at, retweet_count, reply_count, like_count, quote_count, verified, username, name, location, followers_count, following_count, tweet_count) 
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """,
                (tweet_id, author_id, tweet, sentiment_textblob, sentiment_vader, created_at, retweet_count, reply_count, like_count, quote_count, verified, username, name, location, followers_count, following_count, tweet_count))
            kody.cnx.commit()                
        time.sleep(3.5)
        
        if not is_next_page:
            break

if __name__ == "__main__":
    main()


#    CREATE TABLE `tweetTable_AR_GILD` (
#    `tweet_id` BIGINT NOT NULL,
#	`author_id` BIGINT NOT NULL,
#	`tweet` VARCHAR(1000) NOT NULL,
#	`sentiment_textblob` FLOAT NOT NULL,
#	`sentiment_vader` FLOAT NOT NULL,
#	`created_at` TIMESTAMP NOT NULL,
#	`retweet_count` INT NOT NULL,
#	`reply_count` INT NOT NULL,
#	`like_count` INT NOT NULL,
#	`quote_count` INT NOT NULL,
#	`verified` tinyint NOT NULL,
#	`username` VARCHAR(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
#	`name` VARCHAR(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
#	`location` VARCHAR(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
#	`followers_count` INT NOT NULL,
#	`following_count` INT NOT NULL,
#	`tweet_count` INT NOT NULL,
#	PRIMARY KEY (`tweet_id`),
#	UNIQUE KEY `id` (`tweet_id`)
#) ENGINE = INNODB DEFAULT CHARSET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci;