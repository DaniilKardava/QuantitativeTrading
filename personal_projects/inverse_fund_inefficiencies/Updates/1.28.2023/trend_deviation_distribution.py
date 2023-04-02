import yfinance as yf
import numpy as np
from datetime import datetime
from matplotlib import pyplot as plt
import pandas as pd
from scipy.ndimage import gaussian_filter1d
import statistics
from scipy.stats import f_oneway

stocks = ["SPY", "SH"]

# To get a more accurate anova test, consider specifying start time past 2008
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


# Compare the deviations from the general trend

real_price_growth = list(
    np.cumprod(
        stocks_data[(stocks[0], "Close Percent")]
        + stocks_data[(stocks[1], "Close Percent")]
        + 1
    )
    - 1,
)

nav_growth = list(
    np.cumprod(
        stocks_data[(stocks[0], "Close Percent")] + stocks_data["Close NAV Percent"] + 1
    )
    - 1,
)

# Smooth the returns
smoothed_real_price_growth = gaussian_filter1d(np.array(real_price_growth), sigma=10)
smoothed_nav_growth = gaussian_filter1d(np.array(nav_growth), sigma=10)

# Graph the smoothed returns on top of raw returns
plt.plot(stocks_data.index, smoothed_real_price_growth, label="smoothed")
plt.plot(stocks_data.index, real_price_growth, label="real data")

plt.title("Smoothed vs Real")
plt.xlabel("Date")
plt.ylabel("Portfolio Return")
plt.legend()
plt.show()

smooth_diff_real_price = np.array(real_price_growth) - np.array(
    smoothed_real_price_growth
)

smooth_diff_nav = np.array(nav_growth) - np.array(smoothed_nav_growth)

# Plot a histogram of the differences between the general trend and day to day
plt.hist(smooth_diff_real_price, bins=300)
plt.title("Distribution of Price - Avg Trend")
plt.ylabel("Occurances")
plt.xlabel("Percent Deviation")
plt.show()
print(
    "Average difference between real price and trend: "
    + str(statistics.mean(smooth_diff_real_price))
)
print(
    "Average standard deviation of differences: "
    + str(statistics.pstdev(smooth_diff_real_price))
)

plt.hist(smooth_diff_nav, bins=300)
plt.title("Distribution of NAV - Avg Trend")
plt.xlabel("Percent Deviation")
plt.ylabel("Occurances")

plt.show()
print(
    "Average difference between NAV price and trend: "
    + str(statistics.mean(smooth_diff_nav))
)
print(
    "Average standard deviation of differences: "
    + str(statistics.pstdev(smooth_diff_nav))
)

# Now seperate by weekdays
weekday_diff_real = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
}
weekday_diff_nav = {
    0: [],
    1: [],
    2: [],
    3: [],
    4: [],
}

position = 0
for index in stocks_data.index:
    weekday_diff_real[index.weekday()].append(smooth_diff_real_price[position])
    weekday_diff_nav[index.weekday()].append(smooth_diff_nav[position])
    position += 1

# Plot difference distribution for actual prices by weekday
print("Real prices:")
fig, weekday_plots = plt.subplots(2, 3)
fig.suptitle("Real Prices - Avg Trend by Weekday")
for weekday in range(5):
    print(
        "Weekday: "
        + str(weekday)
        + " mean: "
        + str(statistics.mean(weekday_diff_real[weekday]))
    )
    print(
        "Weekday: "
        + str(weekday)
        + " std: "
        + str(statistics.pstdev(weekday_diff_real[weekday]))
    )
    weekday_plots[weekday // 3, weekday % 3].hist(weekday_diff_real[weekday], bins=100)
    weekday_plots[weekday // 3, weekday % 3].set_title("Weekday: " + str(weekday))
plt.show()

# Run an anova test on the weekday distributions
f_statistic, p_value = f_oneway(*weekday_diff_real.values())
print("Real prices weekday anova p_value: " + str(p_value))


print("NAV prices:")
# Plot difference distribution for NAV by weekday
fig, weekday_plots = plt.subplots(2, 3)
fig.suptitle("NAV Prices - Avg Trend by Weekday")
for weekday in range(5):
    print(
        "Weekday: "
        + str(weekday)
        + " mean: "
        + str(statistics.mean(weekday_diff_nav[weekday]))
    )
    print(
        "Weekday: "
        + str(weekday)
        + " std: "
        + str(statistics.pstdev(weekday_diff_nav[weekday]))
    )
    weekday_plots[weekday // 3, weekday % 3].hist(weekday_diff_nav[weekday], bins=100)
    weekday_plots[weekday // 3, weekday % 3].set_title("Weekday: " + str(weekday))
plt.show()

# Run an anova test on the weekday distributions
f_statistic, p_value = f_oneway(*weekday_diff_nav.values())
print("NAV prices weekday anova p_value: " + str(p_value))
