import numpy as np
import pandas as pd
import statistics
import yfinance as yf

# Any data that contains a list of market wide tickers.
data = pd.read_csv("ibkr_short.csv")
data = data.dropna(subset=["FEERATE"])

print(data)

# Load the CSV file in chunks of 1000 rows at a time
chunks = pd.read_csv(
    "marketWideHistory.csv",
    header=[0, 1],
    low_memory=False,
    dtype="float64",
    parse_dates=[0],
    index_col=0,
    chunksize=1000,
)

tickerData = pd.DataFrame()
chunkNumber = 1
# Iterate over the chunks and process them as needed
for chunk in chunks:
    print("Chunk number: " + str(chunkNumber))
    chunkNumber += 1
    tickerData = pd.concat([tickerData, chunk])

# Date range subset
tickerData = tickerData[-300:]
print(tickerData)

tickers = set(tickerData.columns.get_level_values(level=0))


rankedReturns = {}
rankedStdev = {}
counter = 0
for ticker in tickers:

    if counter % 100 == 0:
        print(counter)
    counter += 1
    
    # Not counting dividends, too lazy. 
    # Remove all nans
    try:
        assetData = tickerData[[(ticker, "Close"), (ticker, "Open")]].copy()
        assetData = assetData.droplevel(0, axis=1)

        first_valid_index = assetData["Open"].first_valid_index()
        assetData = assetData.loc[first_valid_index:]

        overnightReturns = list(
            np.array(assetData["Open"])[1:] / np.array(assetData["Close"])[:-1]
        )

        if not np.isnan(statistics.mean(overnightReturns)):
            rankedStdev[ticker] = statistics.pstdev(overnightReturns)
            # Im removing all values that represent sudden jumps, not helpful and fucks with my data.
            overnightReturns = [x for x in overnightReturns if abs(1 - x) < 0.2]
            rankedReturns[ticker] = statistics.mean(overnightReturns)

    except:
        continue


# Sort dicitoinary
rankedReturns = dict(sorted(rankedReturns.items(), key=lambda x: x[1]))
lowest = list(rankedReturns.keys())[:200]
highest = list(rankedReturns.keys())[-200:]

# Volatility filter lowest
stdRanking = {}
for ticker in lowest:
    stdRanking[ticker] = rankedStdev[ticker]

# Lowest returns ranked in order of lowest to highest volatility
stdRanking = dict(sorted(stdRanking.items(), key=lambda x: x[1]))

filteredTickers = []
for ticker in list(stdRanking.keys()):
    try:
        if tickerData[(ticker, "Close")][tickerData.index[-1]] > 3:
            if yf.Ticker(ticker).fast_info["market_cap"] > 25000000:
                filteredTickers.append(ticker)
    except:
        continue

print("Lowest: " + str(filteredTickers))

# Volatility filter highest
stdRanking = {}
for ticker in highest:
    stdRanking[ticker] = rankedStdev[ticker]

# Lowest returns ranked in order of lowest to highest volatility
stdRanking = dict(sorted(stdRanking.items(), key=lambda x: x[1]))

filteredTickers = []
for ticker in list(stdRanking.keys()):
    try:
        if tickerData[(ticker, "Close")][tickerData.index[-1]] > 3:
            if yf.Ticker(ticker).fast_info["market_cap"] > 25000000:
                filteredTickers.append(ticker)
    except:
        continue


print("Highest: " + str(filteredTickers))
