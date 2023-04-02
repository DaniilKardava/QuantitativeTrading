import pandas as pd
import yfinance as yf
import json

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
data = pd.read_csv("ibkr_short.csv")
data.sort_values(by="FEERATE", ascending=False, inplace=True)
data = data.dropna(subset=["FEERATE"])

print(data)

# Open the holdings file and read the contents
with open("currentHoldings.txt", "r") as file:
    text = file.read()

# Load the contents into a dictionary using json.loads()
currentHoldings = json.loads(text)
print("Current holdings: " + str(currentHoldings))

portfolio = []

minimumFee = 100
# Keep tickers that are above minimum percent to reduce transactions
for ticker in currentHoldings:
    if data.loc[data["#SYM"] == ticker]["FEERATE"] > 100:
        portfolio.append(ticker)

minMC = 50000000
minP = 3
targetPortfolioSize = 10
safetyNet = 10


# Change manually to represent buyingPower
buyingPower = 150000

for ticker in data["#SYM"]:

    print(len(portfolio))

    if "." in ticker or " " in ticker:
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

sharesToBuy = {}
for ticker in newTickersList:
    price = yf.download(ticker, period="5d")["Close"][-1]
    sharesToBuy[ticker] = int(buyingPower / openSlots / price)

print("Shares amonuts: " + str(sharesToBuy))

with open("currentHoldings.txt", "w") as f:
    json.dump(portfolio, f)
