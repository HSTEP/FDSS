from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import json
import kody
import pandas as pd
import time
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
cursor=kody.cnx.cursor(buffered=True)
cursor2=kody.cnx.cursor(buffered=True)
analyser = SentimentIntensityAnalyzer()

counter = 0

def foo(row):
    global counter
    counter += 1
    print(counter)
    return analyser.polarity_scores(row)["compound"]

cursor=kody.cnx.cursor(buffered=True)
cursor2=kody.cnx.cursor(buffered=True)
analyser = SentimentIntensityAnalyzer()

cursor.execute("SELECT title FROM newsGILD")

cursor2.executemany(
   "UPDATE newsGILD SET sentiment_vader = %s WHERE title = %s LIMIT 1",
   [(foo(row), row[0]) for row in cursor]
)

kody.cnx.commit()
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!
#!!!!!!!!!!!!!!!!!!!!!!!!!!!před spuštěním zkontrolovat nastavení mysql time/published ON UPDATE CURRENT TIMESTAMP při updatu sql změní i hodnotu času!!!!!


#def sentiment_analyzer_scores(sentence):
#    score = analyser.polarity_scores(sentence)
#    score = json.dumps(score)
#    json_score = json.loads(score)
#    print(json_score["compound"])
#
#sentiment_analyzer_scores("The phone is super cool.")
#
#
#data_frame = pd.read_sql('SELECT time, username, tweet, followers,  sentiment FROM tweetTable ORDER BY time ASC', con=kody.cnx)
#data_frame['vader_compound'] = [analyser.polarity_scores(x)['compound'] for x in data_frame['tweet']]
##counter = 0
##cursor.execute("SELECT tweet FROM tweetTable")
##row = cursor.fetchone()
##while row is not None:
##    if counter % 200 == 0:
##        print(counter, time.time() - time1)
##        time1 = time.time()
##    counter = counter + 1
##    vader = analyser.polarity_scores(row)
##    sentiment_vader = vader["compound"]
##    cursor2.execute(
##            "UPDATE tweetTable SET sentiment_vader = %s WHERE tweet = %s LIMIT 1",
##            (sentiment_vader, row[0]))
##    kody.cnx.commit()
##    row = cursor.fetchone()





#from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
#import json
#import kody
#import pandas as pd
#
#analyser = SentimentIntensityAnalyzer()
#
#def sentiment_analyzer_scores(sentence):
#    score = analyser.polarity_scores(sentence)
#    score = json.dumps(score)
#    json_score = json.loads(score)
#    print(json_score["compound"])
#
#sentiment_analyzer_scores("The phone is super cool.")
#
#data_frame = pd.read_sql('SELECT time, username, tweet, followers,  sentiment FROM tweetTable ORDER BY time ASC', con=kody.cnx)
#data_frame['vader_compound'] = [analyser.polarity_scores(x)['compound'] for x in data_frame['tweet']]
#
#print(data_frame)
