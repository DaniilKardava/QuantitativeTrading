import pandas as pd
from datetime import datetime
import yfinance as yf
from matplotlib import pyplot as plt
import numpy as np

"""
Instructions:
Historic borrow rates correspond to end of day snapshots. For each day, put together a list of candidates 
and send transactions in after hours to be executed at open next day, avoiding all spreads in simulation.
Cash wise, I don't know what I have when I submit orders to close and open new positions. Therefore,
I will delay opening new positions until old positions have been closed and cash has been received. 
"""


# Start date of data and test
date = datetime(2022, 10, 6)

# Access historic borrow rate data, not included in github.
historicalRates = pd.read_csv("historicBorrowUpdatedFilled.csv")
historicalRates.set_index("Unnamed: 0", inplace=True)
historicalRates.index.name = "Date"

historicalRates.index = pd.to_datetime(historicalRates.index).date

print(historicalRates)


# It 10x I didn't want it to mess with the graph...
blacklist = ["MSGM"]

for ticker in blacklist:
    try:
        historicalRates.drop(ticker, axis=1, inplace=True)
    except:
        continue


# Get a date index to work with in backtest. The historic rates one included market holidays.
dateIndex = yf.download("AAPL", start=date, end=datetime(2023, 3, 10)).index.date
indexPosition = 0

cash = 100000
equity = 0

# List for saving borrow rates of assets in portfolio.
feeRate = []

# Separate lists for saving graph data
performanceIndex = [dateIndex[indexPosition]]
performance = [100000]
overnightPerformance = [100000]
intraPerformance = [100000]

transactions = 0

previousHoldings = []
quedTransactions = []

assetInfoDictionary = {}


class assetInfo:
    def __init__(self, ticker, data):
        self.ticker = ticker
        self.data = data

    def setDiv(self, dividends):
        self.dividends = dividends

    def setMC(self, marketCap):
        self.marketCap = marketCap

    def setShares(self, shares):
        self.shares = shares

    def setEntryPrice(self, entryPrice):
        self.entryPrice = entryPrice

    def setEntryDates(self, dates):
        self.entryDates = dates

    def setExitDates(self, dates):
        self.exitDates = dates

    def setContribution(self, contributions):
        self.contributions = contributions

    def setFees(self, fees):
        self.fees = fees


# Commissions and two way spread
commissions = 5
spread = 0.00

minimumMC = 25000000
minPrice = 3

targetPortfolioSize = 20
portfolioLowerBound = 20
# Assets held in portfolio can fall in ranking to the lower bound. To implement this, I scan the ranking up to the lower bound, and check whether the
# assets from the previous portfolio still remain in this list.

date = dateIndex[indexPosition]

# Simulator had 1.5 margin available.
leverage = 1.5

# When to transact settings
atOpen = True

# Liquidate positions
def liquidatePosition(droppedTickers):
    temporaryPriceData = {}
    global transactions
    global cash
    global assetInfoDictionary

    for ticker in droppedTickers:

        transactions += 1
        temporaryPriceData[ticker] = (
            assetInfoDictionary[ticker].data[["Close", "Open"]].copy()
        )

        # Add dividends
        assetInfoDictionary[ticker].dividends = assetInfoDictionary[
            ticker
        ].dividends.truncate(before=(date))

        for index in assetInfoDictionary[ticker].dividends.index:
            temporaryPriceData[ticker]["Close"].loc[index:] = (
                temporaryPriceData[ticker]["Close"].loc[index:]
                + assetInfoDictionary[ticker].dividends[index]
            )
            temporaryPriceData[ticker]["Open"].loc[index:] = (
                temporaryPriceData[ticker]["Open"].loc[index:]
                + assetInfoDictionary[ticker].dividends[index]
            )

        # Transact at open of the next day.
        cash += (
            2 * assetInfoDictionary[ticker].entryPrice
            - temporaryPriceData[ticker]["Open"][dateIndex[indexPosition + 1]]
        ) * assetInfoDictionary[ticker].shares * (1 - spread / 2) - commissions

        assetInfoDictionary[ticker].contributions[-1] = (
            assetInfoDictionary[ticker].entryPrice
            - assetInfoDictionary[ticker].data["Open"][dateIndex[indexPosition + 1]]
        ) * assetInfoDictionary[ticker].shares - commissions

        assetInfoDictionary[ticker].shares = 0
        assetInfoDictionary[ticker].entryPrice = 0

        assetInfoDictionary[ticker].contributions.append(0)
        assetInfoDictionary[ticker].exitDates.append(date)


# Try to filter out stocks like XPON, rallying for a while
stoppedOut = []

# Scroll through the dates in my date index. Simulate scanning the top stocks that meet criteria. For each day, calculate the change in price of holdings
# going into the next day.
while indexPosition < len(dateIndex) - 2:

    print(date)

    ratesRow = historicalRates.loc[date, :].sort_values(ascending=False, inplace=False)

    portfolio = []

    def checkStop(ticker):
        for stoppedTicker in stoppedOut:
            if ticker == stoppedTicker[0]:
                return False
        return True

    # Alternative way to minimize trades is to keep a fee minimum, rather than a leaderboard minimum.
    for ticker in previousHoldings:
        if ratesRow[ticker] > 10000 and checkStop(ticker):
            portfolio.append(ticker)
            feeRate.append(ratesRow[columnNumber])
            assetInfoDictionary[ticker].fees.append(ratesRow[columnNumber])

    columnNumber = 0
    while len(portfolio) < portfolioLowerBound:

        ticker = ratesRow.index[columnNumber]

        def checkStoppedTicker(ticker):
            global stoppedOut
            for stoppedTicker in stoppedOut:
                if ticker == stoppedTicker[0]:
                    if stoppedTicker[1] > 30:
                        stoppedOut.remove(stoppedTicker)
                        return False
                    else:
                        stoppedTicker[1] += 1
                        return True
            return False

        if checkStoppedTicker(ticker):
            columnNumber += 1
            continue

        if "." in ticker or " " in ticker:
            columnNumber += 1
            continue

        if ticker in portfolio:
            columnNumber += 1
            continue

        # Try referencing previously downloaded data
        try:

            # No need to check conditions if I already own the asset
            if ticker in previousHoldings:
                portfolio.append(ticker)
                feeRate.append(ratesRow[columnNumber])
                assetInfoDictionary[ticker].fees.append(ratesRow[columnNumber])
                columnNumber += 1
                continue

            if assetInfoDictionary[ticker].data["Close"][date] > minPrice:
                if assetInfoDictionary[ticker].marketCap > minimumMC:
                    portfolio.append(ticker)
                    feeRate.append(ratesRow[columnNumber])
                    assetInfoDictionary[ticker].fees.append(ratesRow[columnNumber])
        except:
            try:
                assetInfoDictionary[ticker] = assetInfo(
                    ticker,
                    yf.download(ticker, period="1y"),
                )
                assetInfoDictionary[ticker].data.index = assetInfoDictionary[
                    ticker
                ].data.index.date

                if assetInfoDictionary[ticker].data["Close"][date] > minPrice:
                    stock = yf.Ticker(ticker)
                    assetInfoDictionary[ticker].setMC(stock.fast_info["market_cap"])
                    assetInfoDictionary[ticker].setDiv(stock.dividends)

                    # Change index of dividends
                    assetInfoDictionary[ticker].dividends.index = assetInfoDictionary[
                        ticker
                    ].dividends.index.date

                    if assetInfoDictionary[ticker].marketCap > minimumMC:

                        # Add variable for shares and entry price
                        assetInfoDictionary[ticker].setShares(0)
                        assetInfoDictionary[ticker].setEntryPrice(0)

                        # Add variables for entry/exit/contribution. Contribution will be seperate for each trade.
                        assetInfoDictionary[ticker].setEntryDates([])
                        assetInfoDictionary[ticker].setExitDates([])
                        assetInfoDictionary[ticker].setContribution([0])

                        # Append list for fee for asset
                        assetInfoDictionary[ticker].setFees([])

                        portfolio.append(ticker)
                        feeRate.append(ratesRow[columnNumber])

                        assetInfoDictionary[ticker].fees.append(ratesRow[columnNumber])

            except Exception as e:
                historicalRates.drop(ticker, axis=1, inplace=True)
                assetInfoDictionary.pop(ticker)
                print("Exception: " + str(e))

        columnNumber += 1

    sameTickers = len(set(previousHoldings) & set(portfolio))

    if not atOpen:
        openSlots = targetPortfolioSize - sameTickers
    else:
        # If I transact at the open price of the next day, openslots will not be determined by the number of assets ready to be replaced today,
        # but rather the number of empty slots that already exist with cash on hand as a result.
        openSlots = targetPortfolioSize - len(previousHoldings)

    # I will keep all the previous holdings that are in this list, and
    # replace the rest with the best new tickers in the portfolio.
    addedTickers = 0
    portfolioIndex = 0
    newTickers = []

    for ticker in portfolio:
        if addedTickers == openSlots:
            # Remove the remaining tickers that are not part of previous holdings.
            for ticker in portfolio[portfolioIndex:]:
                if ticker not in previousHoldings:
                    portfolio.remove(ticker)
            break
        else:
            if ticker not in previousHoldings:
                newTickers.append(ticker)
                addedTickers += 1
        portfolioIndex += 1

    # Make use of positive correlation between fee and returns by weighing top fee assets more in portfolio. Currently set to 1 / no effect.
    weights = []
    topWeight = 1
    if len(newTickers) == 1:
        weights = [1]
    else:
        step = (2 * topWeight - 2) / (len(newTickers) - 1)
        for n in range(len(newTickers)):
            weights.append(1 / len(newTickers) * (topWeight - step * n))

    droppedTickers = [
        item
        for item in previousHoldings
        if item not in set(previousHoldings) & set(portfolio)
    ]

    print(droppedTickers)
    print(newTickers)
    # Determine when transactions happen. If at open next day, then check for the cash on hand before liquidating positions, since those proceeds would
    # be delayed.

    if atOpen:
        # If I am in debt, maintain debt until cash turns positive, don't enter any new positions.
        if cash < 0:
            for ticker in newTickers:
                portfolio.remove(ticker)

        # Temporary variable for buying power, since cash gets reduced while calculating individual assets
        cashPower = cash

    # Liquidate dropped tickers.
    liquidatePosition(droppedTickers)

    # Calculate the value of the portfolio, seperately calculate intraday and overnight period as well.
    temporaryPriceData = {}
    equity = 0
    nightEquity = 0
    weightNumber = 0

    if not atOpen:
        # If I am in debt, maintain debt until cash turns positive, don't enter any new positions.
        if cash < 0:
            for ticker in newTickers:
                portfolio.remove(ticker)

        # Temporary variable for buying power, since cash gets reduced while calculating individual assets
        cashPower = cash

    # Try to filter out stocks like XPON, rallying hard for a while.
    for ticker in portfolio:

        temporaryPriceData[ticker] = (
            assetInfoDictionary[ticker].data[["Close", "Open"]].copy()
        )

        # Add dividends
        assetInfoDictionary[ticker].dividends = assetInfoDictionary[
            ticker
        ].dividends.truncate(before=(date))

        for index in assetInfoDictionary[ticker].dividends.index:
            temporaryPriceData[ticker]["Close"].loc[index:] = (
                temporaryPriceData[ticker]["Close"].loc[index:]
                + assetInfoDictionary[ticker].dividends[index]
            )
            temporaryPriceData[ticker]["Open"].loc[index:] = (
                temporaryPriceData[ticker]["Open"].loc[index:]
                + assetInfoDictionary[ticker].dividends[index]
            )

        if ticker in previousHoldings:
            equity += (
                2 * assetInfoDictionary[ticker].entryPrice
                - temporaryPriceData[ticker]["Close"][dateIndex[indexPosition + 1]]
            ) * assetInfoDictionary[ticker].shares

            nightEquity += (
                2 * assetInfoDictionary[ticker].entryPrice
                - temporaryPriceData[ticker]["Open"][dateIndex[indexPosition + 1]]
            ) * assetInfoDictionary[ticker].shares

            # Stop loss. Allow again after n days
            if (
                temporaryPriceData[ticker]["Close"][dateIndex[indexPosition + 1]]
                > 1.3 * assetInfoDictionary[ticker].entryPrice
            ):
                stoppedOut.append([ticker, 0])

        else:
            transactions += 1
            # Add shares and initial entry price
            assetInfoDictionary[ticker].shares = (
                cashPower
                * weights[weightNumber]
                / assetInfoDictionary[ticker].data["Open"][dateIndex[indexPosition + 1]]
            )

            # Filled below quoted price
            assetInfoDictionary[ticker].entryPrice = assetInfoDictionary[ticker].data[
                "Open"
            ][dateIndex[indexPosition + 1]] * (1 - spread / 2)
            weightNumber += 1

            # Transaction cost included
            cash -= (
                assetInfoDictionary[ticker].shares
                * assetInfoDictionary[ticker].entryPrice
                + commissions
            )
            equity += (
                2 * assetInfoDictionary[ticker].entryPrice
                - temporaryPriceData[ticker]["Close"][dateIndex[indexPosition + 1]]
            ) * assetInfoDictionary[ticker].shares

            nightEquity += (
                2 * assetInfoDictionary[ticker].entryPrice
                - temporaryPriceData[ticker]["Open"][dateIndex[indexPosition + 1]]
            ) * assetInfoDictionary[ticker].shares

            assetInfoDictionary[ticker].entryDates.append(date)

    # Save the change in equity at the close of next day
    indexPosition += 1
    previousHoldings = portfolio

    # The performance calcualted should be associated with tomorrow, since the returns are forward looking.
    date = dateIndex[indexPosition]
    performanceIndex.append(date)
    performance.append(equity + cash)
    overnightPerformance.append(nightEquity + cash)
    intraPerformance.append(equity - nightEquity + cash)

# Values are finalized when I close a position. At the end of the simulation, call to close all positions
liquidatePosition(previousHoldings)

print("Average Borrow Rate: " + str(sum(feeRate) / len(feeRate)))
plt.hist(feeRate, bins=100)
plt.title("Fee Rate Distribution")
plt.show()

# Remove the unused tickers.
attribute = "contributions"
assetData = {
    k: v
    for k, v in assetInfoDictionary.items()
    if hasattr(v, attribute) and sum(getattr(v, attribute)) != 0
}

# Organize by contribution
assetData = dict(sorted(assetData.items(), key=lambda x: sum(x[1].contributions)))

print("Least to greatest contribution: " + str(list(assetData.keys())))
print("Total transactions: " + str(transactions))

# Calculate leveraged portfolio:
levPortfolio = np.diff(performance) * leverage
levPortfolio = np.insert(levPortfolio, 0, 100000)
levPortfolio = np.cumsum(levPortfolio)

plt.plot(performanceIndex, performance, label="Total")
plt.plot(performanceIndex, levPortfolio, label="Lev Total")
plt.plot(performanceIndex, overnightPerformance, label="Night")
plt.plot(performanceIndex, intraPerformance, label="Day")
plt.legend()
plt.show()


# Analyze the correlation between fee rate and return.
returns = []
avgRate = []
for ticker in list(assetData.keys()):
    returns.append(sum(assetData[ticker].contributions))
    avgRate.append(sum(assetData[ticker].fees) / len(assetData[ticker].fees))

print("Return and fee correlations")
print(np.corrcoef(avgRate, returns))
plt.scatter(avgRate, returns)
plt.title("Return and fee rate correlations")
plt.show()
