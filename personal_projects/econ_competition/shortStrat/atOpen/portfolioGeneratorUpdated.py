import pandas as pd
import yfinance as yf
import json
from datetime import datetime
import numpy as np

# Update list:
"""
>ftp
>open ftp3.interactivebrokers.com
>shortstock
>get usa.txt (dir for others)

replace , with ;
replace | with ,
"""

# Find candidates
ibkrData = pd.read_csv("ibkr_short.csv")
ibkrData.sort_values(by="FEERATE", ascending=False, inplace=True)
ibkrData = ibkrData.dropna(subset=["FEERATE"])

borrowRates = pd.read_csv("historicborrowupdatedfilled.csv")
borrowRates.set_index("Date", inplace=True)
borrowRates.index = pd.to_datetime(borrowRates.index).date

# Append an empty row to fill with new values
new_row = pd.DataFrame(
    {col: np.nan for col in borrowRates.columns}, index=[datetime.now().date()]
)
borrowRates = pd.concat([borrowRates, new_row])

for ticker in borrowRates.columns:
    borrowRates[ticker][datetime.now().date()] = ibkrData.loc[
        ibkrData["#SYM"] == ticker
    ]["FEERATE"]

# Fill stocks that are unborrowable with their last value
borrowRates = borrowRates.fillna(method="ffill")

# Tickers that werent found in game
blacklist = ["PCF"]

# Blacklist tickers:
for ticker in blacklist:
    borrowRates.drop(ticker, axis=1, inplace=True)
    ibkrData.drop(ibkrData[ibkrData["#SYM"] == ticker].index, axis=0, inplace=True)


# Sort the final row and use for calculations
latest_borrow = (
    borrowRates.iloc[len(borrowRates.index) - 1].copy().sort_values(ascending=False)
)

print(borrowRates)


# Open the holdings file and read the contents
with open("currentHoldings.txt", "r") as file:
    text = file.read()

# Load the contents into a dictionary using json.loads()
currentHoldings = json.loads(text)
print("Current holdings: " + str(currentHoldings))

portfolio = []

# If assets have no shares to borrow, they will not appear on the list
minimumFee = 10000
# Keep tickers that are above minimum percent to reduce transactions
for ticker in currentHoldings:
    if latest_borrow[ticker] > minimumFee:
        portfolio.append(ticker)

minMC = 25000000
minP = 3
targetPortfolioSize = 20
safetyNet = 20


# Change manually to represent buyingPower
buyingPower = 135000

for ticker in latest_borrow.index:

    print(len(portfolio))

    try:
        if "." in ticker or " " in ticker:
            continue
    except:
        continue

    if ticker in portfolio:
        continue

    if len(portfolio) >= safetyNet:
        break

    try:
        tickerData = yf.download(ticker, period="5d")
        if tickerData["Close"][tickerData.index[-1]] > minP:
            stock = yf.Ticker(ticker)
            if stock.fast_info["market_cap"] > minMC:
                portfolio.append(ticker)
    except Exception as e:
        print("Exception: " + str(e))
        continue

    continue

# Find available slots
openSlots = targetPortfolioSize - len(currentHoldings)

newTickersList = []

addedTickers = 0
pos = 0
for ticker in portfolio:
    if addedTickers == openSlots:
        # Remove the remaining tickers that are not part of previous holdings.
        for ticker in portfolio[pos:]:
            if ticker not in currentHoldings:
                portfolio.remove(ticker)
        break
    else:
        if ticker not in currentHoldings:
            newTickersList.append(ticker)
            addedTickers += 1
    pos += 1

# Find what to cover
droppedTickers = [
    item
    for item in currentHoldings
    if item not in set(currentHoldings) & set(portfolio)
]

print("Cover: " + str(droppedTickers))
print("New portfolio: " + str(portfolio))

for ticker in portfolio:
    print(latest_borrow[ticker])

sharesToBuy = {}
for ticker in newTickersList:
    price = yf.download(ticker, period="5d")["Close"][-1]
    sharesToBuy[ticker] = int(buyingPower / openSlots / price)

print("Shares amonuts: " + str(sharesToBuy))

with open("currentHoldings.txt", "w") as f:
    json.dump(portfolio, f)

# borrowRates.to_csv("historicborrowupdatedfilled.csv")
