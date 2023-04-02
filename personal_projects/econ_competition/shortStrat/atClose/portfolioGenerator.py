import pandas as pd
import yfinance as yf
import json

# Update present day borrow data list:
"""
open cmd:
>ftp
>open ftp3.interactivebrokers.com
>username: shortstock
>No password just hit enter
>get usa.txt (dir for others)
replace , with ;
replace | with ,
"""

# Load the data saved using the method above
data = pd.read_csv("ibkr_short.csv")
data.sort_values(by="FEERATE", ascending=False, inplace=True)
data = data.dropna(subset=["FEERATE"])

print(data)

# Open the current holdings file
with open("currentHoldings.txt", "r") as file:
    text = file.read()

# Load the contents into a dictionary using json.loads()
currentHoldings = json.loads(text)
print(currentHoldings)


portfolio = []
minMC = 50000000
minP = 3
targetPortfolioSize = 20

# How far assets can fall outside of the top 20 range before getting replaced. 
safetyNet = 30

# Current buying power
buyingPower = 150000

for ticker in data["#SYM"]:

    print(len(portfolio))

    if "." in ticker or " " in ticker:
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

# Find overlapping tickers
sameTickers = len(set(currentHoldings) & set(portfolio))
newTickers = targetPortfolioSize - sameTickers

newTickersList = []

# Strip down the top 30 to meet the target portfolio size. If some assets were dropped, keep the best new ones. 
addedTickers = 0
pos = 0
for ticker in portfolio:
    if addedTickers == newTickers:
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

print(portfolio)

# Never actually used this script, realized it doesnt reflect buying power rising after dropping some assets. 
sharesToBuy = {}
for ticker in newTickersList:
    price = yf.download(ticker, period="5d")["Close"][-1]
    sharesToBuy[ticker] = int(buyingPower / newTickers / price)

print(sharesToBuy)

with open("currentHoldings.txt", "w") as f:
    json.dump(portfolio, f)
