#!/usr/bin/python3
#
# SuperSimpleStock.py
#
# Elisa Antolini
#
# This script provides the follwing informations for 5 fixed stocks.
# a.	For eac stock :
#           i.	Calculates the dividend yield
#          ii.	Calculates the P/E Ratio
#         iii.	Records a trade, with timestamp, quantity of shares, buy or sell indicator and price
#          iv.	Calculate Stock Price based on trades recorded in past 15 minutes
#
# b.	Calculates the GBCE All Share Index using the geometric mean of prices for all stocks
#
#
#
#
# Questions: elyanto83@gmail.com
#
#     Copyright 2016, Elisa Antolini
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#


import os
import sys
sys.path.append('Packages/pyalgotrade')
sys.path.append('Packages/pandas')
sys.path.append('Packages/yahoo_finance')

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
import datetime
import pandas as pd
import pandas.io.data

from pyalgotrade import strategy
from yahoo_finance import Currency
from pyalgotrade.barfeed import yahoofeed
from pyalgotrade.barfeed import csvfeed
from pyalgotrade.technical import ma
from pyalgotrade.stratanalyzer import returns



##############################################
################### CLASSES ##################
##############################################


class MyPrices(strategy.BacktestingStrategy):
    
    def __init__(self, feed, instrument):
        
        strategy.BacktestingStrategy.__init__(self, feed)
        self.__instrument = instrument
        
        global  barDateTime
        global  barClosePrice
        
        barDateTime   = ["",""]
        barClosePrice = ["",""]
    
    
    def onBars(self, bars):

        bar = bars[self.__instrument]
        barDateTime.append(str(bar.getDateTime()))
        barClosePrice.append(float("%.2f" % bar.getClose()))




class MyStrategy(strategy.BacktestingStrategy):
  
    def __init__(self, feed, instrument, smaPeriod,quantity):
        strategy.BacktestingStrategy.__init__(self, feed, 10000)
        self.__position = None
        self.__instrument = instrument
        # We'll use adjusted close values instead of regular close values.
        self.setUseAdjustedValues(True)
        self.__sma = ma.SMA(feed[instrument].getPriceDataSeries(), smaPeriod)
        self.__quantity = quantity
    
        global  BuyDateList
        global  SellDateList
        
        global  BuyQuantityList
        global  SellQuantityList
        
        global  BuyPriceList
        global  SellPriceList
    
        BuyDateList   = ["",""]
        SellDateList  = ["",""]
    
        BuyQuantityList   = ["",""]
        SellQuantityList  = ["",""]
    
        BuyPriceList      = ["",""]
        SellPriceList     = ["",""]
    

    
    
    def onEnterOk(self, position):
        execInfo     = position.getEntryOrder().getExecutionInfo()
        BuyDateList.append(str(execInfo.getDateTime()))
        BuyQuantityList.append(float("%.2f" % execInfo.getQuantity()))
        BuyPriceList.append(float("%.2f" % execInfo.getPrice()))
        self.info("BUY at $%.2f" % (execInfo.getPrice()))
    
        
    def onEnterCanceled(self, position):
        self.__position = None
    
    def onExitOk(self, position):
        execInfo = position.getExitOrder().getExecutionInfo()
        SellDateList.append(str(execInfo.getDateTime()))
        SellQuantityList.append(float("%.2f" % execInfo.getQuantity()))
        SellPriceList.append(float("%.2f" % execInfo.getPrice()))
        self.info("SELL at $%.2f" % (execInfo.getPrice()))
        self.__position = None
        
    def onExitCanceled(self, position):
        # If the exit was canceled, re-submit it.
        self.__position.exitMarket()
            
    def onBars(self, bars):
        # Wait for enough bars to be available to calculate a SMA.
        if self.__sma[-1] is None:
            return
                
        bar = bars[self.__instrument]
        # If a position was not opened, check if we should enter a long position.
        if self.__position is None:
            if bar.getPrice() > self.__sma[-1]:
                # Enter a buy market order for "quantity" shares. The order is good till canceled.
                self.__position = self.enterLong(self.__instrument,self.__quantity,True)
        # Check if we have to exit the position.
        elif bar.getPrice() < self.__sma[-1]:
            self.__position.exitMarket()


###############################################################
################ STOCK PARAMETERS FUNCTIONS  ##################
###############################################################

## For each stok compute : Dividend yeld,P/E Ratio, Stock Price (for simulate trade prices and quantities), GBCE index ##

def Get_StockParameters(StockNum,StockTicker,StockType,TickerPrice,LastDividend,FixedDividend,ParValue):
    
    DividendYeld          = []
    PriceEarningRatio     = []
    StockPrices           = []
    GBCE                  = 0
    
    TradePrice=[]
    Quantity  =[]

    for i in range(0,StockNum):
        
        #GBP - USD Currency Conversion
        LastDividend[i] = GetCurrency_Exchange(LastDividend[i])
        ParValue[i]     = GetCurrency_Exchange(ParValue[i])
        
        #Compute Stock Dividend Yeld
        DividendYeld.append(Dividend_Yeld(TickerPrice[i],StockType[i],LastDividend[i],FixedDividend[i],ParValue[i]))
        
        #Compute Price_EarningRatio
        PriceEarningRatio.append(Price_EarningRatio(TickerPrice[i],DividendYeld[i]))
        
        # Simulate a Trade Price and quantity for each Stock
        for j in range(0,30):
            TradePrice.append(random.uniform(TickerPrice[i]-0.3,TickerPrice[i]+0.3))
            Quantity.append(random.randrange(10,15))
        
        StockPrices.append(Get_StockPrice(TradePrice,Quantity))
        TradePrice = []
        Quantity   = []
    
    #Compute GBCE index
    GBCE=Get_GBCEIndex(StockPrices)

    print("###############################################################################")
    print("# STOCK  : DIVIDEND YELD ,  PRICE-EARNING RATIO, STOCK PRICES (15 MintesTrade)#")
    print("###############################################################################\n")

    for i in range(0,StockNum):
        if PriceEarningRatio[i] != 0 :
            print(" {} :    {:.1f} % ,  {:.2f},  {:.2f} $ ".format(StockTicker[i],(DividendYeld[i]*100),PriceEarningRatio[i],StockPrices[i]))
        else :
            print(" {} :    {:.1f} % ,  Not Applicable, {:.2f} $  ".format(StockTicker[i],(DividendYeld[i]*100),StockPrices[i]))

    print("\n")
    print(" GBCE Index = {:.2f} ".format(GBCE))
    print("###############################################################################\n")


## Compute Dividend Yeld ##
def Dividend_Yeld(TickerPrice,StockType,LastDividend,FixedDividend,ParValue):
    
    #Using Common Type Formula
    if StockType=="Com" :
       return LastDividend/TickerPrice

    #Using Preferred Type Formula
    if StockType=="Pref" :
       return FixedDividend*ParValue/TickerPrice


## Compute Price/Earning Ratio ##
def Price_EarningRatio(TickerPrice,DividendYeld):
    #DividendYeld =  DividendYeld*100
    #TickerPrice  = TickerPrice *100
    if DividendYeld == 0 :
        return 0
    else :
        return TickerPrice/DividendYeld


## Get updated GBP - USD currency from yahoo finance ##
def GetCurrency_Exchange(GBP):
    
    gbp_usd = Currency('GBPUSD')
    gbp_usd.refresh()
    return (GBP * float(gbp_usd.get_rate()))


## Compute Stock Price  ##
def Get_StockPrice(TradePrice,Quantity):
    
    PriceNum = len(TradePrice)
    Num = 0
    Den = 0
    for i in range(0,PriceNum):
        Num += TradePrice[i]*Quantity[i]
        Den += Quantity[i]

    return Num/Den


## Compute GBCE Index ##
def Get_GBCEIndex(AllShare):
    
    ShareNum = len(AllShare)
    x = 1
    
    for i in range(0,ShareNum):
        x *= float(AllShare[i])

    return np.power(x,1/ShareNum)



###############################################################
################   TRADING FUNCTIONS         ##################
###############################################################


def Get_Trade(Stock,Filename):
    
    print("\n")
    print("##################################################")
    print("#                {} TRADING STRATEGY            #".format(Stock))
    print("##################################################")
    
    
    # Open cvs file
    feed = OpenCSVStockFile(Stock,Filename)
    
    # Get Prices for a given stock
    myPrices = MyPrices(feed,Stock)
    myPrices.run()
    
    print("\n")
    
    # Get Startegy for a given stocks
    run_strategy(15,Stock,Filename,random.randrange(5,12))


## Run the strategy for a given stock ##
def run_strategy(smaPeriod,Stock,filename,quantity):
    
    # Load yahoo feed from the CSV file
    feed = OpenCSVStockFile(Stock,filename)
    
    # Evaluate the strategy with the feed.
    myStrategy = MyStrategy(feed, Stock, smaPeriod,quantity)
    returnsAnalyzer = returns.Returns()
    myStrategy.attachAnalyzer(returnsAnalyzer)
    myStrategy.run()
    
    print ("Final portfolio value: $%.2f" % myStrategy.getBroker().getEquity())




## Load yahoo feed from the CSV file ##
def OpenCSVStockFile(Stock,Filename):
    feed = yahoofeed.Feed()
    feed.addBarsFromCSV(Stock, Filename)
    return(feed)



## Plotting the Trading ##
def Plot_StockTrade(Stock):
    
    DateTime   = barDateTime[2:]
    ClosePrice = barClosePrice[2:]
    
    BuyDate = BuyDateList[2:]
    BuyQuantity = BuyQuantityList[2:]
    BuyPrice    = BuyPriceList[2:]
    
    SellDate     = SellDateList[2:]
    SellQuantity = SellQuantityList[2:]
    SellPrice    = SellPriceList[2:]
    
    
    datefunc = lambda x: mdates.date2num(datetime.datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    
    dates = []
    for i in range(0,len(DateTime)):
        dates.append(datefunc(str(DateTime[i])))
    
    Buydates = []
    for i in range(0,len(BuyDate)):
        Buydates.append(datefunc(str(BuyDate[i])))
    
    Selldates = []
    for i in range(0,len(SellDate)):
        Selldates.append(datefunc(str(SellDate[i])))
    
    fig = plt.figure(figsize=(15, 8))
    ax  = fig.add_subplot(211)

    # Tickmark + label at every plotted point
    ax.set_xticks(dates)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    # tick on mondays every second week
    ax.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=matplotlib.dates.MO,interval=2))
    ax.plot_date(dates, ClosePrice, ls='-', marker='',label=Stock)
    ax.plot_date(Buydates, BuyPrice, ls='', marker='^',label='Buy')
    ax.plot_date(Selldates, SellPrice, ls='', marker='v',label='Sell')
    legend = ax.legend(loc='upper right', shadow=True)
    frame = legend.get_frame()
    ax.set_title('Trade Strategy')
    ax.set_ylabel('Prices($)')
    ax.grid(True)
    
    
    ax = fig.add_subplot(212)
    ax.set_xticks(dates) # Tickmark + label at every plotted point
    ax.set_xlim([dates[0], dates[250]])
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=matplotlib.dates.MO,interval=2))
    ax.set_ylim([0, 15])
    ax.set_ylabel('Quantity')
    ax.bar(Buydates, BuyQuantity,label='Buy',color = 'g')
    ax.bar(Selldates, SellQuantity,label='Sell',color = 'r')
    legend = ax.legend(loc='upper right', shadow=True)
    fig.autofmt_xdate(rotation=45)

    plotfile = "./TradePlot/{}_PlotTrade.png".format(Stock)

    fig.savefig(plotfile)
    
    plt.show()


## Download cvs files from yahoo finance ##
def Get_HistoricalStockData(StockNum,Filename,StartTime,StopTime):
    
    
    print("\n")
    print(" ..........DOWNLOADING HISTORICAL DATA FROM WEB...........")
    print("\n")
    
    TickerFile = ["YHOO","GOOG","AAPL","HOG","INTC"]
    
    Stock = TickerFile[StockNum]
    
    StockData = pd.io.data.get_data_yahoo(Stock,start=StartTime,end=StopTime)
    StockData.head()
    StockData.to_csv(Filename)


#------------------------------------------------------------------------------
# main
#
def _main():
    """
    This is the main routine.
    """
    ############### STOCK INPUT DATA #############
    
    StockTicker   = ["TEA","POP","ALE","GIN","JOE"]
    StockType     = ["Com","Com","Com","Pref","Com"]  #($)
    TickerPrice   = [2,1.5,3,1,1.8]  #(USD)
    LastDividend  = [0,0.08,0.23,0.08,0.13]  #(GBP)
    FixedDividend = [0,0,0,0.02,0]
    ParValue      = [1,1,0.6,1,2.5] #(GBP)

    
    ############# GET STOCK PARAMETERS ###########
    
    Get_StockParameters(len(StockTicker),StockTicker,StockType,TickerPrice,LastDividend,FixedDividend,ParValue)
   
    
    ############# PERFORM A TRADING FOR EACH STOCK ###########
    

    pathdir = "./DataFiles/StockTrde_"
    
    for i in range(0,len(StockTicker)):
        
        #Check if the data file exists
        datafile = pathdir+"{}.csv".format(i+1)
        if os.path.isfile(datafile) == False :
            Get_HistoricalStockData(i,datafile,datetime.datetime(2015, 1, 1),datetime.datetime(2016, 1, 1))

        # Get the Strategy
        Get_Trade(StockTicker[i],datafile)
    
    ############# PLOT THE TRADING ###########
    
        Plot_StockTrade(StockTicker[i])
    



#------------------------------------------------------------------------------
# Start program execution.
#
if __name__ == '__main__':
    _main()

