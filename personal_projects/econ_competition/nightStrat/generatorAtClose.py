import yfinance as yf
import json

tickers = {
    "FKWL": "Short",
    "FG": "Short",
    "ABCM": "Short",
    "MBC": "Short",
    "FERG": "Short",
}


# Load asset deets. Asset deets contains shares owned in dictionary format above. 
with open("assetDeets.txt", "r") as file:
    text = file.read()

# Load shares data
assetDeets = json.loads(text)

tickerPrices = yf.download(list(tickers.keys()), group_by="ticker")

positionValue = 0
for ticker in list(tickers.keys()):
    # If short overnight, then long intraday
    if tickers[ticker] == "Short":
        positionValue += (
            assetDeets[ticker] * tickerPrices[(ticker, "Close")][tickerPrices.index[-1]]
        )
    else:
        # Entry value at open
        positionValue += assetDeets[ticker] * (
            2 * tickerPrices[(ticker, "Open")][tickerPrices.index[:-1][-1]]
            - tickerPrices[(ticker, "Close")][tickerPrices.index[-1]]
        )

cash = 0
totalBuyingPower = positionValue + cash
perAsset = totalBuyingPower / 5

targetShares = {}
sendTransaction = {}
for ticker in list(tickers.keys()):
    if tickers[ticker] == "Short":
        sendTransaction[ticker] = "SELL " + str(
            int(perAsset / tickerPrices[(ticker, "Close")][tickerPrices.index[-1]])
            + assetDeets[ticker]
        )
        targetShares[ticker] = int(
            perAsset / tickerPrices[(ticker, "Close")][tickerPrices.index[-1]]
        )

    else:
        sendTransaction[ticker] = "BUY " + str(
            int(perAsset / tickerPrices[(ticker, "Close")][tickerPrices.index[-1]])
            + assetDeets[ticker]
        )
        targetShares[ticker] = int(
            perAsset / tickerPrices[(ticker, "Close")][tickerPrices.index[-1]]
        )


print("Target shares: " + str(targetShares))
print("Send Transaction: " + str(sendTransaction))


with open("assetDeets.txt", "w") as f:
    json.dump(targetShares, f)

