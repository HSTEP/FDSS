import backtrader as bt
import yfinance as yf
from strategy import MA_cross_Sentiment, MA_controll_strategy, sentiment_0_strategy
from datetime import datetime
import warnings
from plotly.tools import mpl_to_plotly

startcash = 1000
stake = 1  # number of assets to buy

time = datetime.now().isoformat()
cerebro = bt.Cerebro(preload=True, runonce=True, quicknotify=True)

cerebro.broker.setcash(startcash)


class GenericCSV_X(bt.feeds.GenericCSVData):
    # přidání dat sentimentu pro vytváření MA
    lines = ("sentiment",)
    params = {"sentiment": 6}


data = GenericCSV_X(
    dataname="data_news/newsNET.csv",
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
cerebro.broker.setcommission(commission=0.002)
# data
cerebro.adddata(data)
# add observer
cerebro.addobserver(bt.observers.DrawDown)
# addstrategy
cerebro.addstrategy(sentiment_0_strategy)
# fixed number of assets to buy
# cerebro.addsizer(bt.sizers.FixedSize, stake = stake)
# analyzers
#cerebro.addanalyzer(bt.analyzers.Transactions, _name="TT")
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DD")
cerebro.addwriter(bt.WriterFile, csv=True, out="terminal_writer_backtrader.csv")
# run strategy backtesting
strats = cerebro.run()
stats = strats[0]

PnL = cerebro.broker.getvalue() - startcash
PnLpercentage = (PnL / startcash) * 100
DDDD = stats.analyzers.DD.get_analysis()
#TTTT = stats.analyzers.TT.get_analysis()
try:
    print("startcash: ", startcash)
    print("PnL: ", PnL)
    print("PnL percentage: ", PnLpercentage, "%")
    print("total trades:", stats.analyzers.ta.get_analysis()["total"]["total"])
    print("long trades won:", stats.analyzers.ta.get_analysis()["long"]["won"])
    print("long trades lost:", stats.analyzers.ta.get_analysis()["long"]["lost"])
    print("short trades won:", stats.analyzers.ta.get_analysis()["short"]["won"])
    print("short trades lost:", stats.analyzers.ta.get_analysis()["short"]["lost"])
    print("DrawDown:", stats.analyzers.DD.get_analysis()["max"]["drawdown"])
    print(
        "winning streak:", stats.analyzers.ta.get_analysis()["streak"]["won"]["longest"]
    )
    print(
        "losing streak:", stats.analyzers.ta.get_analysis()["streak"]["lost"]["longest"]
    )
except KeyError:
    print("Analyzer Error")
    
#cerebro.plot(style="candle", volume= False)[0][0]
