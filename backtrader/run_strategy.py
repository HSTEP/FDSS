import backtrader as bt
import yfinance as yf
from strategy_tests import RSI_buy_strategy, MA_strategy
from strategy import MA_cross_Sentiment
from datetime import datetime
import warnings

stock = "GILD"
# perioda = "60d" #time period
# interval = "2m" #candlestick
startcash = 1000
stake = 1  # number of assets to buy

time = datetime.now().isoformat()
cerebro = bt.Cerebro(preload=True, runonce=True, quicknotify=True)
#       ``optreturn`` (default: ``True``)
#
#       If ``True`` the optimization results will not be full ``Strategy``
#       objects (and all *datas*, *indicators*, *observers* ...) but and object
#       with the following attributes (same as in ``Strategy``):
#
#         - ``params`` (or ``p``) the strategy had for the execution
#         - ``analyzers`` the strategy has executed
#
#       In most occassions, only the *analyzers* and with which *params* are
#       the things needed to evaluate a the performance of a strategy. If
#       detailed analysis of the generated values for (for example)
#       *indicators* is needed, turn this off
#
#       The tests show a ``13% - 15%`` improvement in execution time. Combined
#       with ``optdatas`` the total gain increases to a total speed-up of
#       ``32%`` in an optimization run.

cerebro.broker.setcash(startcash)


class GenericCSV_X(bt.feeds.GenericCSVData):
    # přidání dat sentimentu pro vytváření MA
    lines = ("sentiment",)
    params = {"sentiment": 6}


data = GenericCSV_X(
    dataname="csv_GILD.csv",
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

cerebro.plot(tight=False, style="candle", volume= False)
# print(time, datetime.now().isoformat())
