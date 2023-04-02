import yfinance as yf
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta

asset = "SPXU"
intraData = pd.read_csv(f"barchartData/{asset}.csv")

intraData.set_index("Date", inplace=True)
intraData.index = pd.to_datetime(intraData.index)


def dividend_calculator(
    asset, daily_data, night_change, pre_post_change, post_close_data
):
    ticker_object = yf.Ticker(asset)
    dividend_table = ticker_object.dividends
    dividend_table.index = dividend_table.index.tz_localize(None)
    dividend_table = dividend_table.truncate(before=daily_data.index[1])
    for ex_date in dividend_table.index:
        index = daily_data.index.get_loc(ex_date)
        night_change[index - 1] += (
            dividend_table[ex_date] / daily_data["Close"][daily_data.index[index - 1]]
        )
        pre_post_change[index - 1] += (
            dividend_table[ex_date] / post_close_data[index - 1]
        )
    return night_change, pre_post_change


# Artificially create rows for comparison
for date in sorted(set(intraData.index.date)):
    targetTime = datetime.combine(date, datetime.min.time()) + timedelta(
        hours=19, minutes=59
    )
    if targetTime not in intraData.index:
        prev_row = intraData.loc[intraData.index.date == date].iloc[-1]
        new_row = prev_row.copy()
        new_row.name = datetime.combine(date, datetime.min.time()) + timedelta(
            hours=19, minutes=59
        )

        intraData = intraData.append(new_row)

    targetTime = datetime.combine(date, datetime.min.time()) + timedelta(hours=4)
    if targetTime not in intraData.index:
        prev_row = intraData.loc[intraData.index.date == date].iloc[
            0
        ]  # get the last row of the current date
        new_row = prev_row.copy()
        new_row.name = datetime.combine(date, datetime.min.time()) + timedelta(hours=4)
        intraData = intraData.append(new_row)

intraData = intraData.sort_index()

# Calculate pre post gap
hour = intraData.index.hour
minute = intraData.index.minute

prePostChange = np.array(intraData[(hour == 4) & (minute == 0)]["Open"][1:]) / np.array(
    intraData[(hour == 19) & (minute == 59)]["Close"][:-1]
)

# Daily calculations
startDate = intraData.index[0].date()
endDate = intraData.index[-1].date() + timedelta(days=1)
dailyData = yf.download(asset, start=startDate, end=endDate)

# Calculate night returns
nightChange = np.array(dailyData["Open"][1:]) / np.array(dailyData["Close"][:-1])

# After calculating total night, pre-post gap, calculate pre and post seperately
preChange = np.array(dailyData["Open"]) / np.array(
    intraData[(hour == 4) & (minute == 0)]["Open"]
)
postChange = np.array(intraData[(hour == 19) & (minute == 59)]["Close"]) / np.array(
    dailyData["Close"]
)

# Trim lists to account for first available overnight calculation
preChange = preChange[1:]
postChange = postChange[1:]

postCloseData = intraData[(hour == 19) & (minute == 59)]["Close"]

nightChange, prePostChange = dividend_calculator(
    asset, dailyData, nightChange, prePostChange, postCloseData
)

dailyData = dailyData[1:]

# Set original value to share price
# nightChange[0] = dailyData["Open"][0]
# prePostChange[0] = dailyData["Open"][0]

plt.yscale("log")

plt.plot(dailyData.index, np.cumprod(nightChange), label="Extended Hours")
plt.plot(dailyData.index, np.cumprod(prePostChange), label="Post-Pre Jump")
plt.plot(dailyData.index, np.cumprod(preChange), label="Pre-Market")
plt.plot(dailyData.index, np.cumprod(postChange), label="Post-Market")

plt.legend()
plt.title(asset + ": How much of extended move occurs during pre-post jump?")
plt.show()

"""
my_style = mpf.make_mpf_style(base_mpf_style="charles", rc={"font.size": 8})

# plot the chart with volume bars
mpf.plot(
    intraData,
    type="candle",
    volume=True,
    style=my_style,
    title="Stock Price",
    ylabel="Price ($)",
    ylabel_lower="Volume",
)
"""
