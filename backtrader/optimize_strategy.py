import backtrader as bt
import yfinance as yf
from strategy import RSI_buy_strategy

if __name__ == '__main__':
    stock = "GILD"
    period = "60d" #time period
    interval = "2m" #candlestick
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
    data = bt.feeds.GenericCSVData(
    dataname='csv_GILD.csv',
    dtformat='%Y-%m-%d %H:%M:%S',
    datetime=0,
    high=2,
    low=3,
    open=1,
    close=4,
    volume=5,
    openinterest=-1)
    #data
    cerebro.adddata(data)
    #optimize strategy
    cerebro.optstrategy(RSI_buy_strategy, period=range(15,29))
    #fixed number of assets to buy
    cerebro.addsizer(bt.sizers.FixedSize, stake = stake)
    #analyzers
    cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="ta")
    #run strategy backtesting
    strats = cerebro.run()

    final_results_list = []
    for run in strats:
        for strategy in run:
            value = round(strategy.broker.get_value(),2)
            PnL = round(value - startcash,2)
            period = strategy.params.period
            final_results_list.append([period,PnL])

    #Sort Results List
    by_period = sorted(final_results_list, key=lambda x: x[0])
    by_PnL = sorted(final_results_list, key=lambda x: x[1], reverse=True)

    #Print results
    print('Results: Ordered by period:')
    for result in by_period:
        print('Period: {}, PnL: {}'.format(result[0], result[1]))
    print('Results: Ordered by Profit:')
    for result in by_PnL:
        print('Period: {}, PnL: {}'.format(result[0], result[1]))