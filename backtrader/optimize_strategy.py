import backtrader as bt
import yfinance as yf
from strategy import MA_cross_Sentiment
import pandas as pd
import os
import csv

class GenericCSV_X(bt.feeds.GenericCSVData):
    # přidání dat sentimentu pro vytváření MA
    lines = ("sentiment",)
    params = {"sentiment": 6}

if __name__ == '__main__':
    stock = "GILD"
    #period = "60d" #time period
    #interval = "2m" #candlestick
    startcash = 1000
    stake = 1 #number of assets to buy

    cerebro = bt.Cerebro(optreturn=False)

    cerebro.broker.setcash(startcash)
    '''
    def get_stock_data(stock):
        #Download stock data from yahoo finance
        msft = yf.Ticker(stock)
        df = msft.history(period=period, interval=interval)
        data = bt.feeds.PandasData(dataname=df)
        return data
    '''

    data = GenericCSV_X(
        dataname="stocks_data/newsNET.csv",
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
    #data
    cerebro.adddata(data)
    #optimize strategy
    cerebro.optstrategy(MA_cross_Sentiment, 
                        period_long=range(199,201), 
                        period_short=range(20,22), 
                        stop_loss=range(1,2)
                        )
    #fixed number of assets to buy
    cerebro.addsizer(bt.sizers.FixedSize, stake = stake)
    #analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DD")
    #run strategy backtesting
    strats = cerebro.run()

    for x in strats:
        print(x[0].analyzers.DD.get_analysis()["max"]["drawdown"])

    final_results_list = []
    for run in strats:
        dd = run[0].analyzers.DD.get_analysis()["max"]["drawdown"]
        for strategy in run:
            value = round(strategy.broker.get_value(),2)
            PnL = round(value - startcash,2)
            period_long = strategy.params.period_long
            period_short = strategy.params.period_short
            stop_loss = strategy.params.stop_loss
            final_results_list.append([period_long, period_short, stop_loss, dd, PnL])
            
    #Sort Results List
    by_period = sorted(final_results_list, key=lambda x: x[0])
    by_PnL = sorted(final_results_list, key=lambda x: x[4], reverse=True)

    #Save to csv
    with open("optimalization_results/TEST_OPTs.csv", "w") as f:
        writer=csv.writer(f, delimiter=',')
        writer.writerow(["Period_long", "Period_short", "Stop_loss%", "dd", "PnL"])
        for result in by_period:
            row = result[0], result[1], result[2], result[3], result[4]
            writer.writerow(row)
    #Print results
    print('Results: Ordered by period:')
    for result in by_period:
        print('Period_long: {}, Period_short: {}, Stop_loss: {}%, dd: {}, PnL: {}'.format(result[0], result[1], result[2], result[3], result[4]))
    print('Results: Ordered by Profit:')
    for result in by_PnL:
        print('Period_long: {}, Period_short: {}, Stop_loss: {}%, dd: {}, PnL: {}'.format(result[0], result[1], result[2], result[3], result[4]))
    

    ## saving dataframe
    # df = pd.DataFrame(by_PnL) 
    # df.to_excel('TEST_optstrategy_results.xlsx') 