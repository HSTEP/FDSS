import backtrader as bt
from strategy import MA_cross_Sentiment, sentiment_0_strategy, MA_controll_strategy
import os
from datetime import datetime

begin_time = datetime.now()

class GenericCSV_X(bt.feeds.GenericCSVData):
    # přidání dat sentimentu pro vytváření MA
    lines = ("sentiment",)
    params = {"sentiment": 6}


def backtrade_stock(datapath, file_name):
    data = GenericCSV_X(
        dataname=datapath,
        dtformat="%Y-%m-%d %H:%M:%S",
        datetime=0,
        high=2,
        low=3,
        open=1,
        close=4,
        volume=5,
        openinterest=-1,
        sentiment=6,
        timeframe=bt.TimeFrame.Minutes,
    )

    startcash = 1000
    stake = 1  # number of assets to buy

    cerebro = bt.Cerebro(preload=True, runonce=True, quicknotify=True)

    cerebro.broker.setcash(startcash)

    # data
    cerebro.adddata(data)
    # add observer
    cerebro.addobserver(bt.observers.DrawDown)
    # addstrategy
    cerebro.addstrategy(MA_cross_Sentiment)
    # fixed number of assets to buy
    # cerebro.addsizer(bt.sizers.FixedSize, stake = stake)
    # analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")

    cerebro.addwriter(bt.WriterFile, csv=True, out="csv_multistocks/"+file_name)

    # run strategy backtesting
    strats = cerebro.run()
    stats = strats[0]

    PnL = cerebro.broker.getvalue() - startcash
    PnLpercentage = (PnL / startcash) * 100
    try:
        print("startcash: ", startcash)
        print("PnL: ", PnL)
        print("PnL percentage: ", PnLpercentage, "%")
        print("total trades:", stats.analyzers.ta.get_analysis()["total"]["total"])
        print("long trades won:", stats.analyzers.ta.get_analysis()["long"]["won"])
        print("long trades lost:", stats.analyzers.ta.get_analysis()["long"]["lost"])
        print("short trades won:", stats.analyzers.ta.get_analysis()["short"]["won"])
        print("short trades lost:", stats.analyzers.ta.get_analysis()["short"]["lost"])
        print(
            "winning streak:", stats.analyzers.ta.get_analysis()["streak"]["won"]["longest"]
        )
        print(
            "losing streak:", stats.analyzers.ta.get_analysis()["streak"]["lost"]["longest"]
        )
    except KeyError:
        print("Analyzer Error")

path = "stocks_data/"
filepaths = os.listdir(path)

datapaths = []

for file in filepaths:
    datapaths.append(path+file)
print(datapaths)

csv_multistocks_file_name = []
for i in datapaths:
    csv_multistocks_file_name.append(i[12:])
print(csv_multistocks_file_name)

zip_iterator = zip(datapaths, csv_multistocks_file_name)
a_dict = dict(zip_iterator)
print(a_dict)

for key in a_dict:
    print(key, a_dict[key])

for key in a_dict:
    backtrade_stock(key,a_dict[key])

print("duration: ", datetime.now() - begin_time)
