import yfinance as yf
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
from scipy.ndimage import gaussian_filter1d


stocks = ["SPY", "SH"]

stocks_data = yf.download(stocks, start=datetime(2000, 1, 1), group_by="ticker")

# Standardize datetime to date
stocks_data.index = stocks_data.index.date

# Trim data to begin at newest asset
earliest_dates = []
for ticker in stocks:
    if stocks_data[ticker].first_valid_index() != None:
        earliest_dates.append(stocks_data[ticker].first_valid_index())
    else:
        stocks_data = stocks_data.drop(ticker, 1)
        stocks.drop(ticker)

stocks_data = stocks_data.truncate(before=max(earliest_dates))

# Calculate close to close percent difference
stocks_data[(stocks[0], "Close Percent")] = stocks_data[
    (stocks[0], "Close")
].pct_change()

stocks_data[(stocks[1], "Close Percent")] = stocks_data[
    (stocks[1], "Close")
].pct_change()

stocks_data = stocks_data[1:]

# Add dividend payments.
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
    stocks_data[(ticker, "Close Percent")] += dividend_as_percent[ticker]

# Plot federal funds rate and portfolio performance
fig, (top_plot, bottom_plot) = plt.subplots(2, 1, sharex=True)

top_plot.plot(
    stocks_data.index,
    np.cumprod(
        stocks_data[(stocks[0], "Close Percent")]
        + stocks_data[(stocks[1], "Close Percent")]
        + 1
    )
    - 1,
    label="Actual Price Portfolio",
)


# Plot the federal funds rate
ff_rate = pd.read_csv("ff_rates.csv")
ff_rate.set_index("DATE", inplace=True)
ff_rate.index = pd.to_datetime(ff_rate.index)
ff_rate = ff_rate.truncate(before=stocks_data.index[0])

bottom_plot.plot(ff_rate.index, ff_rate["DFF"], label="FF Rate")


top_plot.legend()
top_plot.set_title("Portfolio Returns")
top_plot.set_xlabel("Date")
top_plot.set_ylabel("Decimal Returns (%/100)")

bottom_plot.legend()
bottom_plot.set_title("Federal Funds Rate")
bottom_plot.set_xlabel("Date")
bottom_plot.set_ylabel("Annual Rate")

plt.show()


# Correlate interest rates and portfolio growth

# Federal funds data does not get updated, remove all stock data after final rates value
stocks_data = stocks_data.truncate(after=ff_rate.index[-1])

portfolio_change = (
    stocks_data[(stocks[0], "Close Percent")]
    + stocks_data[(stocks[1], "Close Percent")]
)

# Unable to detect trends for raw data, need to smooth.
portfolio_change = gaussian_filter1d(np.array(portfolio_change), sigma=10)

# FF rate table has all days, make indeces match with portfolio:
ff_rate = ff_rate.reindex(index=stocks_data.index)

# Round ff rate to nearest n decimal to smooth
ff_rate["DFF"] = ff_rate["DFF"].round(3)

# Line of best fit
coefficients = np.polyfit(ff_rate["DFF"], portfolio_change, 1)
polynomial = np.poly1d(coefficients)
print("Line of best fit: " + str(polynomial))
print("X-intercept: " + str(polynomial.roots))

plt.plot(ff_rate["DFF"], polynomial(ff_rate["DFF"]), label="LSRL")

plt.scatter(ff_rate["DFF"], portfolio_change)

plt.legend()
plt.xlabel("FF Rate")
plt.ylabel("Portfolio Change %")
plt.title("Interest Rate Effect on Portfolio Growth")

print("Correlation coef: " + str(np.corrcoef(ff_rate["DFF"], portfolio_change)))
plt.show()
