import yfinance as yf
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd

stocks = ["SPY", "SH"]

stocks_data = yf.download(stocks, start=datetime(2010, 1, 1), group_by="ticker")

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

# Alter the percent change of overnight returns to reflect dividend payments.
dividend_as_percent = {}
for ticker in stocks:
    asset_object = yf.Ticker(ticker)
    dividend_table = asset_object.dividends
    dividend_table.index = dividend_table.index.date

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

# Scale  the returns of my funds when comparing leveraged instruments. The benchmark should be scaled by n/n+1 where n is the leverage factor
# of the second asset. The second asset should be scaled by 1/n+1. Check github Updates folder for explanation.
benchmark_scale = 1 / 2
target_scale = 1 / 2

stocks_data[(stocks[0], "Close Percent")] = (
    stocks_data[(stocks[0], "Close Percent")] * benchmark_scale
)
stocks_data[(stocks[1], "Close Percent")] = (
    stocks_data[(stocks[1], "Close Percent")] * target_scale
)

stocks_data[(stocks[0], "Intra Percent")] = (
    stocks_data[(stocks[0], "Intra Percent")] * benchmark_scale
)
stocks_data[(stocks[1], "Intra Percent")] = (
    stocks_data[(stocks[1], "Intra Percent")] * target_scale
)

stocks_data[(stocks[0], "Overnight Percent")] = (
    stocks_data[(stocks[0], "Overnight Percent")] * benchmark_scale
)
stocks_data[(stocks[1], "Overnight Percent")] = (
    stocks_data[(stocks[1], "Overnight Percent")] * target_scale
)

# Plot image of total hedging period
plt.plot(
    stocks_data.index,
    np.cumprod(
        stocks_data[(stocks[0], "Close Percent")]
        + stocks_data[(stocks[1], "Close Percent")]
        + 1
    )
    - 1,
)
plt.title("Total Hedge")
plt.xlabel("Date")
plt.ylabel("Decimal Returns (%/100)")
plt.show()


# Bottom overnight, top intraday
fig, (top_plot, bottom_plot) = plt.subplots(2, 1, sharex=True)

bottom_plot.plot(
    stocks_data.index,
    np.cumprod(
        stocks_data[(stocks[0], "Overnight Percent")]
        + stocks_data[(stocks[1], "Overnight Percent")]
        + 1
    )
    - 1,
    label="Overnight Portfolio",
)


# Plot the federal funds rate
top_plot.plot(
    stocks_data.index,
    np.cumprod(
        stocks_data[(stocks[0], "Intra Percent")]
        + stocks_data[(stocks[1], "Intra Percent")]
        + 1
    )
    - 1,
    label="Intraday Hedge",
)


top_plot.legend()
top_plot.set_title("Intraday Portfolio Returns")
top_plot.set_xlabel("Date")
top_plot.set_ylabel("Decimal Returns (%/100)")

bottom_plot.legend()
bottom_plot.set_title("Overnight Portfolio Returns")
bottom_plot.set_xlabel("Date")
bottom_plot.set_ylabel("Decimal Returns (%/100)")

plt.show()
