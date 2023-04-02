import pandas as pd
from datetime import datetime
import yfinance as yf
from matplotlib import pyplot as plt
import numpy as np

# Start date of data and test
date = datetime(2022, 10, 10)

# Access historic borrow rate data, not included in github.
historicalRates = pd.read_csv("historicBorrow.csv")
historicalRates.set_index("Date", inplace=True)
historicalRates.index = pd.to_datetime(historicalRates.index).date

print(historicalRates)

# Get a date index to work with in backtest. The historic rates one included market holidays.
dateIndex = yf.download("AAPL", start=date, end=datetime(2023, 2, 5)).index.date
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
spread = 0.01

minimumMC = 25000000
minPrice = 3

targetPortfolioSize = 10
portfolioLowerBound = 10
# Assets held in portfolio can fall in ranking to the lower bound. To implement this, I scan the ranking up to the lower bound, and check whether the
# assets from the previous portfolio still remain in this list.

date = dateIndex[indexPosition]

# Simulator had 1.5 margin available.
leverage = 1.5

# Scroll through the dates in my date index. Simulate scanning the top stocks that meet criteria. For each day, calculate the change in price of holdings
# going into the next day.
while indexPosition < len(dateIndex) - 1:

    print(date)

    ratesRow = historicalRates.loc[date, :].sort_values(ascending=False, inplace=False)

    portfolio = []

    # Alternative way to minimize trades is to keep a fee minimum, rather than a leaderboard minimum.
    for ticker in previousHoldings:
        if ratesRow[ticker] > 50:
            portfolio.append(ticker)
            feeRate.append(ratesRow[columnNumber])
            assetInfoDictionary[ticker].fees.append(ratesRow[columnNumber])

    columnNumber = 0
    while len(portfolio) < portfolioLowerBound:

        ticker = ratesRow.index[columnNumber]

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
    newTickers = targetPortfolioSize - sameTickers

    # I will keep all the previous holdings that are in this list, and
    # replace the rest with the best new tickers in the portfolio.
    addedTickers = 0
    portfolioIndex = 0
    newTickerNames = []
    for ticker in portfolio:
        if addedTickers == newTickers:
            # Remove the remaining tickers that are not part of previous holdings.
            for ticker in portfolio[portfolioIndex:]:
                if ticker not in previousHoldings:
                    portfolio.remove(ticker)
            break
        else:
            if ticker not in previousHoldings:
                newTickerNames.append(ticker)
                addedTickers += 1
        portfolioIndex += 1

    # Make use of positive correlation between fee and returns by weighing top fee assets more in portfolio. Currently set to 1 / no effect.
    weights = []
    topWeight = 1
    if newTickers == 1:
        weights = [1]
    else:
        step = (2 * topWeight - 2) / (newTickers - 1)
        for n in range(newTickers):
            weights.append(1 / newTickers * (topWeight - step * n))

    droppedTickers = [
        item
        for item in previousHoldings
        if item not in set(previousHoldings) & set(portfolio)
    ]

    # Liquidate dropped tickers. Temporary price data is created to adjust for dividends, but I want to leave a copy of the original data too.
    temporaryPriceData = {}
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

        cash += (
            2 * assetInfoDictionary[ticker].entryPrice
            - temporaryPriceData[ticker]["Close"][date]
        ) * assetInfoDictionary[ticker].shares * (1 - spread / 2) - commissions

        assetInfoDictionary[ticker].contributions[-1] = (
            assetInfoDictionary[ticker].entryPrice
            - assetInfoDictionary[ticker].data["Close"][dateIndex[indexPosition + 1]]
        ) * assetInfoDictionary[ticker].shares - commissions

        assetInfoDictionary[ticker].shares = 0
        assetInfoDictionary[ticker].entryPrice = 0

        assetInfoDictionary[ticker].contributions.append(0)
        assetInfoDictionary[ticker].exitDates.append(date)

    # Calculate the value of the portfolio, seperately calculate intraday and overnight period as well.
    temporaryPriceData = {}
    equity = 0
    nightEquity = 0
    weightNumber = 0

    # If I am in debt, maintain debt until equity turns positive, don't enter any new positions.
    if cash < 0:
        for ticker in newTickerNames:
            portfolio.remove(ticker)

    # Temporary variable for buying power, since cash gets reduced while calculating individual assets
    cashPower = cash
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

        else:
            transactions += 1
            # Add shares and initial entry price
            assetInfoDictionary[ticker].shares = (
                cashPower
                * weights[weightNumber]
                / assetInfoDictionary[ticker].data["Close"][date]
            )

            assetInfoDictionary[ticker].entryPrice = assetInfoDictionary[ticker].data[
                "Close"
            ][date]
            weightNumber += 1

            # Transaction cost included
            cash -= (
                assetInfoDictionary[ticker].shares
                * assetInfoDictionary[ticker].entryPrice
                * (1 + spread / 2)
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
