#Takes command line arguments: strategy-id, shortMA, longMA, stop-loss, take-profit

import sys
from datetime import datetime

import backtrader as bt

from strategy import MA_cross_Sentiment, MA_controll_strategy

cmd_params = {}
for arg in sys.argv[1:]:
    try:
        cmd_params[arg.split("=")[0]] = int(arg.split("=")[1])
    except ValueError:
        cmd_params[arg.split("=")[0]] = arg.split("=")[1]

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
    dataname="/home/stepan/stranka/backtrader/stocks_data/newsNET.csv" if "file" not in cmd_params else cmd_params["file"],
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
if "strat_id" not in cmd_params:
    # Without arguments or invalid amount of them
    cerebro.addstrategy(MA_cross_Sentiment)
else:
    # With valid amount of arguments
    strategies = [MA_cross_Sentiment, MA_controll_strategy]
    cerebro.addstrategy(strategies[int(cmd_params["strat_id"])], **cmd_params)
# fixed number of assets to buy
# cerebro.addsizer(bt.sizers.FixedSize, stake = stake)
# analyzers
# cerebro.addanalyzer(bt.analyzers.Transactions, _name="TT")
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DD")
cerebro.addwriter(bt.WriterFile, csv=True, out="/home/stepan/stranka/web_writer_backtrader.csv")
# run strategy backtesting
strats = cerebro.run()
stats = strats[0]

PnL = cerebro.broker.getvalue() - startcash
PnLpercentage = (PnL / startcash) * 100
DDDD = stats.analyzers.DD.get_analysis()
# TTTT = stats.analyzers.TT.get_analysis()
try:
    print("startcash: ", startcash)
    print("PnL: ", PnL)
    print("PnL percentage: ", PnLpercentage, "%")
    print("total trades:", stats.analyzers.ta.get_analysis()["total"]["total"])
    print("long trades won:", stats.analyzers.ta.get_analysis()["long"]["won"])
    print("long trades lost:", stats.analyzers.ta.get_analysis()["long"]["lost"])
    print("short trades won:", stats.analyzers.ta.get_analysis()["short"]["won"])
    print("short trades lost:", stats.analyzers.ta.get_analysis()["short"]["lost"])
    print("DrawDown:", stats.analyzers.DD.get_analysis()["max"]["drawdown"], "%")
    print(
        "winning streak:", stats.analyzers.ta.get_analysis()["streak"]["won"]["longest"]
    )
    print(
        "losing streak:", stats.analyzers.ta.get_analysis()["streak"]["lost"]["longest"]
    )
except KeyError:
    print("Analyzer Error")

#cerebro.plot(style="candle", volume= False)[0][0]

# mpld3.save_html(fig, 'backtrader/savefig_TEST.html')
# py.plot_mpl(fig).show()
# print(time, datetime.now().isoformat())