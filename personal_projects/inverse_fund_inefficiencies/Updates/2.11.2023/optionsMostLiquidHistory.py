import requests
import numpy as np
from matplotlib import pyplot as plt
import yfinance as yf
import pandas as pd

tickers = ["SQQQ", "TQQQ"]

# When requesting data, try both including and excluding the last value. It depends on whether robinhood has published options data for the latest date.
# The correct version will produce a much clearer hedge out of the two.
price_data = {}
for ticker in tickers:
    price_data[ticker] = yf.download(ticker, period="400d")  # [:-1]

# Bearer token can be found by inspecting the robinhood page while logged in and navigating to the network tab. Some of the requests will carry the token in the header.
token = "Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJkY3QiOjE2Njc2MjY1NjAsImRldmljZV9oYXNoIjoiYmIwMzk2MTI2NjAyZjJjZDg1Yjk0ZGRkYjYzZWQ5ZDkiLCJleHAiOjE2NzY5Mjg0MTQsImxldmVsMl9hY2Nlc3MiOmZhbHNlLCJvcHRpb25zIjp0cnVlLCJzY29wZSI6ImludGVybmFsIiwic2VydmljZV9yZWNvcmRzIjpbeyJoYWx0ZWQiOmZhbHNlLCJzZXJ2aWNlIjoibnVtbXVzX3VzIiwic2hhcmRfaWQiOjEsInN0YXRlIjoiYXZhaWxhYmxlIn0seyJoYWx0ZWQiOmZhbHNlLCJzZXJ2aWNlIjoiYnJva2ViYWNrX3VzIiwic2hhcmRfaWQiOjEwLCJzdGF0ZSI6ImF2YWlsYWJsZSJ9XSwidG9rZW4iOiJ6eEJsRnB6SVpmb0U1Ym94bkRYWEQybkg4MnJuZ0wiLCJ1c2VyX2lkIjoiNjU1MmUyNmItYWZlNi00ZjNlLWFmZGMtNDI0MDAyMzBkNmI0IiwidXNlcl9vcmlnaW4iOiJVUyJ9.WM-fmPFV8tnJ8TjBPITMbxESOV7jMl7ht-95Htu1VnmNGBf13QUzu7P9cDU4Y-9hmYInoGhWytcYCTX5k2fXuFLOnqPoza8Na0rgt6qPJ72lRHFDqmSFc8knweCHzreJRAk3eoEXYn2_pM3ZQknL9VBuR5aJRQgGmXvv4fmeIySo03ira8CoH15KEtEih7l9VA6Y1EPhdVBm7F-yZrDzldo9mEfKiWEy1uLfSFoA83kXgCfGwjRapBEjcO-vdQpuQPR-cvNLVBPrMLizjkUYU9etCLQ-RubV6YCf2QPfEkme9IahFWnht0st1_pbSEwXHZ66nq8X6V08kBwDAFLtfg"
request_header = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": token,
}

# Which upcoming expiration should I look at
fridayToAnalyze = 0
# For leveraged assets, here is the multiplier. Asset 2 is an "assetMultiple" of asset 1.
assetMultiple = 1

# Request format may change in the future.
def getOptionData(_asset, _strike, exp_date, _type):

    option_url = (
        "https://api.robinhood.com/options/instruments/"
        + "?state=active"
        + "&type="
        + _type
        + "&chain_symbol="
        + _asset
        + "&strike_price="
        + _strike
    )

    # First find the id of the contract that matches my expiration date.
    response = requests.get(url=option_url, headers=request_header).json()
    option_information = pd.DataFrame(response["results"])

    if exp_date == 0:
        # Instead of passing the whole data frame, find the first friday and pass that row.
        expirationDates = pd.to_datetime(option_information["expiration_date"])
        expirationDates.sort_values(inplace=True)
        friday_dates = expirationDates[expirationDates.dt.dayofweek == 4]
        first_friday = friday_dates.iloc[fridayToAnalyze]

        information = option_information[
            pd.to_datetime(option_information["expiration_date"]) == first_friday
        ]

        price_history = oldestOptions(information)

        print("Oldest Option Price History: " + str(price_history))
    else:
        rows = option_information.loc[option_information["expiration_date"] == exp_date]
        id = list(rows["id"])[0]

        # Then request the price data by id.
        contract_url = (
            "https://api.robinhood.com/marketdata/options/historicals/"
            + id
            + "/?interval=day"
        )
        price_history = requests.get(
            url=contract_url,
            headers=request_header,
        ).json()

        price_history = parseData(price_history, 0)

    return price_history


def oldestOptions(_option_information):
    oldestDates = {}
    for expiration in _option_information["expiration_date"]:
        rows = _option_information.loc[
            _option_information["expiration_date"] == expiration
        ]
        id = list(rows["id"])[0]

        # Then request the price data by id.
        contract_url = (
            "https://api.robinhood.com/marketdata/options/historicals/"
            + id
            + "/?interval=day"
        )
        price_history = requests.get(
            url=contract_url,
            headers=request_header,
        ).json()
        data = parseData(price_history, 0)

        # Filter chart to remove flat period preceding data. Really distance myself.
        # I've also had assets that NEVER break, so if that happens I want to make sure they aren't contenders
        broke = False
        for indexPosition in range(1, len(data.index)):
            if (
                data["close_price"][data.index[indexPosition]]
                != data["close_price"][data.index[indexPosition - 1]]
            ):
                data = data.truncate(before=data.index[indexPosition + 2])
                broke = True
                break

        if not broke:
            continue
        else:
            oldestDates[expiration] = [data.index[0], data]

    # Convert the dictionary to a list of tuples
    sorted_list = sorted(oldestDates.items(), key=lambda x: x[1][0])

    # Convert the list back to a dictionary
    sorted_dict = dict(sorted_list)

    print("Expiration: " + list(sorted_dict.keys())[0])
    return sorted_dict[list(sorted_dict.keys())[0]][1]


def parseData(_hist, _startDate):
    price_data = pd.DataFrame(_hist["data_points"])

    price_data.set_index("begins_at", inplace=True)
    price_data.index = pd.to_datetime(price_data.index)

    if _startDate != 0:
        price_data = price_data[price_data.index.get_loc(_startDate) :]
    price_data["close_price"] = price_data["close_price"].astype(float)

    return price_data


def calcAndPlot(_ticker, _strike, _exp, _start_analysis):
    call_data = getOptionData(_ticker, _strike, _exp, "call")
    call_data = call_data.truncate(before=_start_analysis)
    call_changes = np.diff(np.array(call_data["close_price"]))

    put_data = getOptionData(_ticker, _strike, _exp, "put")
    put_data = put_data.truncate(before=_start_analysis)
    put_changes = np.diff(np.array(put_data["close_price"]))

    # When it comes to price changes, account for dividends.
    tickerInfo = yf.Ticker(_ticker)
    dividends = tickerInfo.dividends
    dividends = dividends.truncate(before=price_data[_ticker].index[0])
    temporaryPriceData = price_data[_ticker]["Close"].copy()

    for date in dividends.index:
        temporaryPriceData.loc[date:] = temporaryPriceData.loc[date:] + dividends[date]

    ticker_price_changes = np.diff(
        np.array(temporaryPriceData[-(len(put_changes) + 1) :])
    )

    # Plot synthetic long position on top of long stock position
    plt.plot(
        put_data.index[1:],
        np.cumsum(call_changes - put_changes),
        label=_ticker + " Options",
    )
    plt.plot(
        put_data.index[1:], np.cumsum(ticker_price_changes), label=_ticker + " Shares"
    )

    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Dollar Change")
    plt.show()

    plt.plot(
        put_data.index[1:],
        np.cumsum((call_changes - put_changes) - ticker_price_changes),
        label="Options - " + _ticker,
    )
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Dollar Change")
    plt.show()

    graph_x_axis = put_data.index
    return call_changes, put_changes, ticker_price_changes, graph_x_axis


# Compare a portfolio composed of asset 1 and asset 2 options.
# Specify the contract detials in the function arguments below: ticker, strike, exp, start of analysis.
# Data is only available for active contracts.

# First get the optimal expiration date to maximize amount of data. The following logic is horrible, I'm sorry future me.
# I pass a 0 to indicate that the expiration dates should be found by looking for the option with the longest history.
# Then the data is processed and the earliest date for the best expiration date history is found.
# Then I can either choose to pass a custom or this best mutual start date as beginAnalysis.
# Passing 0 into calcAndPlot does the same thing as above, alternatively I can choose to pass custom start dates and expiration dates.

firstStrike = int(price_data[tickers[0]]["Close"][price_data[tickers[0]].index[-1]])

secondStrike = int(price_data[tickers[1]]["Close"][price_data[tickers[1]].index[-1]])


while True:
    try:
        firstAssetData = getOptionData(tickers[0], str(firstStrike), 0, "call")
        break
    except Exception as e:
        print("Exception: " + str(e) + "; incrementing strike")
        firstStrike += 1

while True:
    try:
        secondAssetData = getOptionData(tickers[1], str(secondStrike), 0, "call")
        break
    except Exception as e:
        print("Exception: " + str(e) + "; incrementing strike")
        secondStrike += 1


beginAnalysis = max(firstAssetData.index[0], secondAssetData.index[0])

# Get first asset data
(
    first_asset_call_changes,
    first_asset_put_changes,
    first_asset_price_changes,
    graph_x_axis,
) = calcAndPlot(tickers[0], str(firstStrike), 0, beginAnalysis)

# Get second asset data
(
    second_asset_call_changes,
    second_asset_put_changes,
    second_asset_price_changes,
    graph_x_axis,
) = calcAndPlot(tickers[1], str(secondStrike), 0, beginAnalysis)

# Calculate the multiples of asset 1 and asset 2 to artificially hedge the two assets.


second_asset_multiple = list(
    price_data[tickers[0]]["Close"] / price_data[tickers[1]]["Close"] / assetMultiple
)


adjusted_second_asset_price_changes = np.multiply(
    second_asset_price_changes,
    second_asset_multiple[-(len(second_asset_price_changes) + 1) : -1],
)


# The graphs below are my best attempt to analyze the option prices. Don't take the returns at face value, rather pay attention to the trend. Fees are not included.


# The dollar returns graphed below will represent the theoretical returns of a single share in asset 1 and x number of shares in asset 2, whose value
# equals the share value of asset 1, rebalanced daily.

plt.plot(
    graph_x_axis[1:],
    np.cumsum(-1 * (first_asset_price_changes + adjusted_second_asset_price_changes)),
)
plt.title("Short Stock in " + tickers[0] + " and " + tickers[1])
plt.xlabel("Date")
plt.ylabel("Dollar Change")
plt.show()

adjusted_second_asset_option_changes = np.multiply(
    second_asset_call_changes - second_asset_put_changes,
    second_asset_multiple[-(len(second_asset_price_changes) + 1) : -1],
)

# The dollar returns graphed below will represent the theoretical returns of a single synthetic long/short position in asset 1 and x number
# of synthetic long/short positions in asset 2, whose value equals the share value controlled by asset 1, rebalanced daily. This assumes
# fractional contracts, but in reality would require shares for hedging.

plt.plot(
    graph_x_axis[1:],
    np.cumsum(
        -1
        * (
            adjusted_second_asset_option_changes
            + first_asset_call_changes
            - first_asset_put_changes
        )
    ),
)
plt.title("Synthetic Short in " + tickers[0] + " and " + tickers[1])
plt.xlabel("Date")
plt.ylabel("Dollar Change (/100)")
plt.show()
