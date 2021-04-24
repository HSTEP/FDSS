import backtrader as bt
import datetime
import argparse
import csv

class MA_cross_Sentiment(bt.Strategy):
    params = dict(
        period_long=199,
        period_short=20,
        stop_loss= 1,
        take_profit=8
    )

    def log(self, txt, dt=None):
        """ datetime  """
        #dt = self.datas[0].datetime.datetime(0)
        #print("%s, %s" % (dt.isoformat().replace("T", " "), txt))

    def __init__(self):
        # Vytváření klouzavého průměru z ceny
        self.ema200 = bt.indicators.ExponentialMovingAverage(
            (self.datas[0].close), period=200, plotname="EMA"
        )
        self.ema50 = bt.indicators.ExponentialMovingAverage(
            (self.datas[0].close), period=50, plotname="EMA"
        )

        # Vytváření klouzavého průměru z hodoty sentimentu
        # plotmaster = zobrazení druhého klouzavého průměru ve stejném grafu jako je první
        self.ema200_sentiment = bt.indicators.SimpleMovingAverage(
            self.data.lines.sentiment, period=self.params.period_long, subplot=True
        )
        self.ema50_sentiment = bt.indicators.SimpleMovingAverage(
            self.data.lines.sentiment, period=self.params.period_short, plotmaster=self.ema200_sentiment
        )

        self.orefs = list()
        self.order = None

        self.stoploss_percentage = self.params.stop_loss/100
        self.takeprofit_percentage = self.params.take_profit/100
        self.stake = 1  # Kolik nakupuju nebo prodávám

        self.can_buy: bool = True  # Na začátku se může nakupovat
        self.can_sell: bool = True  # Na začátku se může prodávat


    def notify_order(self, order):
        #print(
        #    "{}: Order ref: {} / Type {} / Status {}".format(
        #        self.data.datetime.datetime(0),
        #        order.ref,
        #        "Buy" * order.isbuy() or "Sell",
        #        order.getstatusname(),
        #    )
        #)

        if order.status == order.Completed:
            self.order = None  # Po dokončení obchodu není žádný obchod

        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)  # není žádný čekající pokyn

    def crossup(self):
        """Klouzavý průměr s kratší periodou je NAD klouzavým průměrem s vyšší periodou"""
        self.order = self.buy(size=self.stake)
        self.can_sell = True

    def crossdown(self):
        """Klouzavý průměr s kratší periodou je POD klouzavým průměrem s vyšší periodou"""
        self.order = self.sell(size=self.stake)
        self.can_buy = True

    # position.price - cena při otevření obchodu
    # .adjbase - současná cena
    def check_stoploss(self):
        """pokud se dostaneme na stoploss

        position.price - cena při otevření obchodu

        position.adjbase - současná cena
        """
        # když je pozice BUY a cena se dostane na hodnotu stoplosu
        # uzavře se obchod a do dalšího překřížení klouzavých průměrů není možné znovu koupit
        if (
            self.position.size > 0
            and self.position.price * (1 - self.stoploss_percentage)
            > self.position.adjbase
        ):
            self.order = self.sell(size=self.stake)
            print("Buy stoploss triggered")
            self.can_buy = False
        # Nebo když je pozice SELL a cena se dostane na stop_loss...
        elif (
            self.position.size < 0
            and self.position.price * (1 + self.stoploss_percentage)
            < self.position.adjbase
        ):
            self.order = self.buy(size=self.stake)
            print("Sell stoploss triggered")
            self.can_sell = False

    def check_takeprofit(self):
        """pokud se dostaneme na takeprofit

        (podobně jako check_stoploss)
        """
        if (
            self.position.size > 0
            and self.position.price * (1 + self.takeprofit_percentage)
            < self.position.adjbase
        ):
            self.order = self.sell(size=self.stake)
            print("Buy takeprofit triggered")
            self.can_buy = False

        elif (
            self.position.size < 0
            and self.position.price * (1 - self.takeprofit_percentage)
            > self.position.adjbase
        ):
            self.order = self.buy(size=self.stake)
            print("Sell takeprofit triggered")
            self.can_sell = False

    def next(self):
        if self.order:
            # Pokud čeká order na dokončení, nedělat nic
            return

        if (
            self.ema50_sentiment[-1] >= self.ema200_sentiment[-1]
            and self.position.size < 1
            and self.can_buy
        ):
            self.crossup()
            return

        elif (
            self.ema50_sentiment[-1] < self.ema200_sentiment[-1]
            and self.position.size > -1
            and self.can_sell
        ):
            self.crossdown()
            return

        # při každé nové svíčce se kontroluje,
        # zdali cena není na hodnotě stop-loss či take-profit
        self.check_stoploss()
        self.check_takeprofit()

    def notify_trade(self, trade):
        """ Print zisku nebo ztráty po uzavření obchodu
        """
        if not trade.isclosed:
            return

        #print("-" * 32, " NOTIFY TRADE ", "-" * 32)
        #self.log("OPERATION PROFIT, price %.2f, Profit %.2f" % (trade.price, trade.pnl))
        #print("-" * 32, " ⬇︎ NEXT TRADE ⬇︎ ", "-" * 32)



class MA_controll_strategy(bt.Strategy):
    params = dict(
        period_long=196,
        period_short=21,
        stop_loss= 1,
        take_profit=8
    )

    def log(self, txt, dt=None):
        """ datetime  """
        dt = self.datas[0].datetime.datetime(0)
        print("%s, %s" % (dt.isoformat().replace("T", " "), txt))

    def __init__(self):
        # Vytváření klouzavého průměru z ceny
        self.ema200 = bt.indicators.SimpleMovingAverage(
            (self.datas[0].close), period=233, plotname="SMA_long_p"
        )
        self.ema50 = bt.indicators.SimpleMovingAverage(
            (self.datas[0].close), period=21, plotname="SMA_short_p"
        )

        # Vytváření klouzavého průměru z hodoty sentimentu
        # plotmaster = zobrazení druhého klouzavého průměru ve stejném grafu jako je první
        self.ema200_sentiment = bt.indicators.SimpleMovingAverage(
            self.data.lines.sentiment, period=self.params.period_long, subplot=True
        )
        self.ema50_sentiment = bt.indicators.SimpleMovingAverage(
            self.data.lines.sentiment, period=self.params.period_short, plotmaster=self.ema200_sentiment
        )

        self.orefs = list()
        self.order = None

        self.stoploss_percentage = self.params.stop_loss/100
        self.takeprofit_percentage = self.params.take_profit/100
        self.stake = 1  # Kolik nakupuju nebo prodávám

        self.can_buy: bool = True  # Na začátku se může nakupovat
        self.can_sell: bool = True  # Na začátku se může prodávat


    def notify_order(self, order):
        print(
            "{}: Order ref: {} / Type {} / Status {}".format(
                self.data.datetime.datetime(0),
                order.ref,
                "Buy" * order.isbuy() or "Sell",
                order.getstatusname(),
            )
        )

        if order.status == order.Completed:
            self.order = None  # Po dokončení obchodu není žádný obchod

        if not order.alive() and order.ref in self.orefs:
            self.orefs.remove(order.ref)  # není žádný čekající pokyn

    def crossup(self):
        """Klouzavý průměr s kratší periodou je NAD klouzavým průměrem s vyšší periodou"""
        self.order = self.buy(size=self.stake)
        self.can_sell = True

    def crossdown(self):
        """Klouzavý průměr s kratší periodou je POD klouzavým průměrem s vyšší periodou"""
        self.order = self.sell(size=self.stake)
        self.can_buy = True

    # position.price - cena při otevření obchodu
    # .adjbase - současná cena
    def check_stoploss(self):
        """pokud se dostaneme na stoploss

        position.price - cena při otevření obchodu

        position.adjbase - současná cena
        """
        # když je pozice BUY a cena se dostane na hodnotu stoplosu
        # uzavře se obchod a do dalšího překřížení klouzavých průměrů není možné znovu koupit
        if (
            self.position.size > 0
            and self.position.price * (1 - self.stoploss_percentage)
            > self.position.adjbase
        ):
            self.order = self.sell(size=self.stake)
            print("Buy stoploss triggered")
            self.can_buy = False
        # Nebo když je pozice SELL a cena se dostane na stop_loss...
        elif (
            self.position.size < 0
            and self.position.price * (1 + self.stoploss_percentage)
            < self.position.adjbase
        ):
            self.order = self.buy(size=self.stake)
            print("Sell stoploss triggered")
            self.can_sell = False

    def check_takeprofit(self):
        """pokud se dostaneme na takeprofit

        (podobně jako check_stoploss)
        """
        if (
            self.position.size > 0
            and self.position.price * (1 + self.takeprofit_percentage)
            < self.position.adjbase
        ):
            self.order = self.sell(size=self.stake)
            print("Buy takeprofit triggered")
            self.can_buy = False

        elif (
            self.position.size < 0
            and self.position.price * (1 - self.takeprofit_percentage)
            > self.position.adjbase
        ):
            self.order = self.buy(size=self.stake)
            print("Sell takeprofit triggered")
            self.can_sell = False

    def next(self):
        if self.order:
            # Pokud čeká order na dokončení, nedělat nic
            return

        if (
            self.ema50[-1] >= self.ema200[-1]
            and self.position.size < 1
            and self.can_buy
        ):
            self.crossup()
            return

        elif (
            self.ema50[-1] < self.ema200[-1]
            and self.position.size > -1
            and self.can_sell
        ):
            self.crossdown()
            return

        # při každé nové svíčce se kontroluje,
        # zdali cena není na hodnotě stop-loss či take-profit
        self.check_stoploss()
        self.check_takeprofit()

    def notify_trade(self, trade):
        """ Print zisku nebo ztráty po uzavření obchodu
        """
        if not trade.isclosed:
            return

        print("-" * 32, " NOTIFY TRADE ", "-" * 32)
        self.log("OPERATION PROFIT, price %.2f, Profit %.2f" % (trade.price, trade.pnl))
        print("-" * 32, " ⬇︎ NEXT TRADE ⬇︎ ", "-" * 32)
