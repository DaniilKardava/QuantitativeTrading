import yfinance as yf
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd


stocks = ["SPY", "SH"]

stocks_data = yf.download(stocks, start=datetime(2000, 1, 1), group_by="ticker")

# Trim data to begin at newest asset
earliest_dates = []
for ticker in stocks:
    if stocks_data[ticker].first_valid_index() != None:
        earliest_dates.append(stocks_data[ticker].first_valid_index())
    else:
        stocks_data = stocks_data.drop(ticker, 1)
        stocks.drop(ticker)

stocks_data = stocks_data.truncate(before=max(earliest_dates))

# Calculate the intraday percent change for both assets
stocks_data[(stocks[0], "Intra Percent")] = (
    stocks_data[(stocks[0], "Close")] / stocks_data[(stocks[0], "Open")]
) - 1

stocks_data[(stocks[1], "Intra Percent")] = (
    stocks_data[(stocks[1], "Close")] / stocks_data[(stocks[1], "Open")]
) - 1

# Calculate the overnight percent change for both assets. An overnight return value corresponds to the period preceding the date index
first_asset_overnight_return = (
    np.array(stocks_data[(stocks[0], "Open")][1:])
    / np.array(stocks_data[(stocks[0], "Close")][:-1])
    - 1
)

second_asset_overnight_return = (
    np.array(stocks_data[(stocks[1], "Open")][1:])
    / np.array(stocks_data[(stocks[1], "Close")][:-1])
    - 1
)

# Calculate close to close percent difference
stocks_data[(stocks[0], "Close Percent")] = stocks_data[
    (stocks[0], "Close")
].pct_change()

stocks_data[(stocks[1], "Close Percent")] = stocks_data[
    (stocks[1], "Close")
].pct_change()

# Add the overnight returns change to the main table
stocks_data = stocks_data[1:]
stocks_data[(stocks[0], "Overnight Percent")] = first_asset_overnight_return
stocks_data[(stocks[1], "Overnight Percent")] = second_asset_overnight_return

# Add NAV close column for SH
nav_data = pd.read_csv("sh_nav.csv")

nav_data["Date"] = pd.to_datetime(nav_data["Date"])
nav_data.index = nav_data["Date"]
nav_data.drop("Date", axis=1, inplace=True)

# Convert value column from string to numeric and flip table
nav_data["Value"] = nav_data["Value"].apply(lambda x: float(x.strip("%")) / 100)
nav_data = nav_data.iloc[::-1]


# Adjust prices where my data starts
close_nav = []
for index in stocks_data.index:
    try:
        close_nav.append(
            stocks_data[(stocks[1], "Close")][index] / (1 + nav_data["Value"][index])
        )
    except Exception as e:
        close_nav.append(stocks_data[(stocks[1], "Close")][index])

stocks_data["Close NAV"] = close_nav

# Calculate close to close nav change
stocks_data["Close NAV Percent"] = stocks_data["Close NAV"].pct_change()
stocks_data = stocks_data[1:]

# Alter the percent change of overnight returns to reflect dividend payments.
dividend_as_percent = {}
for ticker in stocks:
    asset_object = yf.Ticker(ticker)
    dividend_table = asset_object.dividends
    if len(dividend_table) == 0:
        continue
    dividend_table = dividend_table.reindex_like(stocks_data).fillna(0)

    # Note, division is arranged so that the percent is calculated relative to the close prior to ex-date, since sell-offs are calculated
    # as well. Note also that np.array is used to avoid dividing along index. The data is sliced so that for every index, a previous index
    # containing a close also exists. This will require removal of the first row of the main table in the future to concat the data.

    dividend_as_percent[ticker] = dividend_table[1:] / np.array(
        stocks_data[(ticker, "Close")][:-1]
    )

# Remove first row of main table to create equal indeces
stocks_data = stocks_data[1:]

# Add dividends to main table
for ticker in stocks:
    stocks_data[(ticker, "Overnight Percent")] += dividend_as_percent[ticker]
    stocks_data[(ticker, "Close Percent")] += dividend_as_percent[ticker]
    if ticker == stocks[1]:
        stocks_data["Close NAV Percent"] += dividend_as_percent[ticker]

# Compare portfolio hedge of using actual prices and NAV prices
plt.plot(
    stocks_data.index,
    np.cumprod(
        stocks_data[(stocks[0], "Close Percent")]
        + stocks_data[(stocks[1], "Close Percent")]
        + 1
    )
    - 1,
    label="Actual Price Portfolio",
)
plt.plot(
    stocks_data.index,
    np.cumprod(
        stocks_data[(stocks[0], "Close Percent")] + stocks_data["Close NAV Percent"] + 1
    )
    - 1,
    label="NAV Portfolio",
)

plt.legend()
plt.title("Total Hedge")
plt.xlabel("Date")
plt.ylabel("Decimal Returns (%/100)")
plt.show()

# Analyze close to close returns by weekday

# Store the corresponding weekdays returns for both assets and the index. 0 corresponds to Monday
weekday_close_returns = {
    0: [[], [], [], []],
    1: [[], [], [], []],
    2: [[], [], [], []],
    3: [[], [], [], []],
    4: [[], [], [], []],
}

for index in stocks_data.index:
    weekday_close_returns[index.weekday()][0].append(
        stocks_data[(stocks[0], "Close Percent")][index]
    )
    weekday_close_returns[index.weekday()][1].append(
        stocks_data[(stocks[1], "Close Percent")][index]
    )
    weekday_close_returns[index.weekday()][2].append(
        stocks_data["Close NAV Percent"][index]
    )
    weekday_close_returns[index.weekday()][3].append(index)

# For each weekday, graph the return of the portfolio calculated using real asset prices and NAV
for weekday in range(5):
    plt.yscale("log")
    plt.plot(
        weekday_close_returns[weekday][3],
        np.cumprod(
            np.array(weekday_close_returns[weekday][0])
            + np.array(weekday_close_returns[weekday][1])
            + 1
        ),
        label="Actual Price Portfolio",
    )
    plt.plot(
        weekday_close_returns[weekday][3],
        np.cumprod(
            np.array(weekday_close_returns[weekday][0])
            + np.array(weekday_close_returns[weekday][2])
            + 1
        ),
        label="NAV Portfolio",
    )
    plt.title("Weekday number: " + str(weekday))
    plt.xlabel("Date")
    plt.ylabel("Decimal Returns (%/100)")
    plt.legend(fontsize="large")
    plt.show()
