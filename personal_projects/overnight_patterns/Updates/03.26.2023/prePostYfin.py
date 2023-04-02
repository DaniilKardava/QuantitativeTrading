import yfinance as yf
from datetime import datetime
from matplotlib import pyplot as plt
import mplfinance as mpf
import numpy as np
import pandas as pd
from datetime import timedelta


asset = "WKEY"
startDate = datetime(2023, 2, 28)


def minuteGrab():

    start = startDate
    minData = pd.DataFrame()

    for n in range(4):
        df = yf.download(
            asset,
            interval="1m",
            start=start,
            end=start + timedelta(days=7),
            prepost=True,
        )
        if n != 3:
            df = df[:-1]
        minData = minData.append(df)

        start = start + timedelta(days=7)

    return minData


intraData = minuteGrab()
intraData.index = intraData.index.tz_localize(None)
intraData.to_csv("dataAnalysis.csv")

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

dailyData = yf.download(asset, start=startDate)

# Calculate night returns
nightChange = np.array(dailyData["Open"][1:]) / np.array(dailyData["Close"][:-1])
dailyData = dailyData[1:]
dailyData["nightChange"] = nightChange

plt.plot(dailyData.index, np.cumprod(dailyData["nightChange"]), label="Extended Hours")
plt.plot(dailyData.index, np.cumprod(prePostChange), label="Post-Pre Jump")
plt.legend()
plt.title("How much of extended move occurs during pre-post jump?")
plt.show()


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
