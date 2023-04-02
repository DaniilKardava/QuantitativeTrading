import yfinance as yf
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from datetime import timedelta

asset1 = "QQQ"
asset2 = "SQQQ"

# Asset 2 is n times leveraged relative to asset 1
scale = 3


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


def night_gaps(asset):
    intra_data = pd.read_csv(f"barchartData/{asset}.csv")

    intra_data.set_index("Date", inplace=True)
    intra_data.index = pd.to_datetime(intra_data.index)

    # Artificially create rows for comparison
    for date in sorted(set(intra_data.index.date)):
        target_time = datetime.combine(date, datetime.min.time()) + timedelta(
            hours=19, minutes=59
        )
        if target_time not in intra_data.index:
            prev_row = intra_data.loc[intra_data.index.date == date].iloc[-1]
            new_row = prev_row.copy()
            new_row.name = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=19, minutes=59
            )

            intra_data = intra_data.append(new_row)

        target_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=4)
        if target_time not in intra_data.index:
            prev_row = intra_data.loc[intra_data.index.date == date].iloc[
                0
            ]  # get the last row of the current date
            new_row = prev_row.copy()
            new_row.name = datetime.combine(date, datetime.min.time()) + timedelta(
                hours=4
            )
            intra_data = intra_data.append(new_row)

    intra_data = intra_data.sort_index()

    # Calculate pre post gap
    hour = intra_data.index.hour
    minute = intra_data.index.minute

    pre_post_change = np.array(
        intra_data[(hour == 4) & (minute == 0)]["Open"][1:]
    ) / np.array(intra_data[(hour == 19) & (minute == 59)]["Close"][:-1])

    start_date = intra_data.index[0].date()
    end_date = intra_data.index[-1].date() + timedelta(days=1)
    daily_data = yf.download(asset, start=start_date, end=end_date)

    # Calculate night returns
    night_change = np.array(daily_data["Open"][1:]) / np.array(daily_data["Close"][:-1])

    # After calculating total night, pre-post gap, calculate pre and post seperately
    pre_change = np.array(daily_data["Open"]) / np.array(
        intra_data[(hour == 4) & (minute == 0)]["Open"]
    )
    post_change = np.array(
        intra_data[(hour == 19) & (minute == 59)]["Close"]
    ) / np.array(daily_data["Close"])

    # Trim to match the other lists, which have dropped the first val due to looking backward
    pre_change = pre_change[1:]
    post_change = post_change[1:]

    post_close_data = intra_data[(hour == 19) & (minute == 59)]["Close"]
    night_change, pre_post_change = dividend_calculator(
        asset, daily_data, night_change, pre_post_change, post_close_data
    )

    # Trim to match the other lists, which have dropped the first val due to looking backward
    daily_data = daily_data[1:]

    return (
        night_change - 1,
        pre_post_change - 1,
        pre_change - 1,
        post_change - 1,
        daily_data.index,
    )


night1, prePost1, pre1, post1, first_chart_index = night_gaps(asset1)
night2, prePost2, pre2, post2, second_chart_index = night_gaps(asset2)

# Create equal size:
chartIndex = first_chart_index.intersection(second_chart_index)

# Cut first index:
bottom_cut = (first_chart_index < chartIndex[0]).sum()
top_cut = (first_chart_index > chartIndex[-1]).sum()

night1 = night1[bottom_cut:]
prePost1 = prePost1[bottom_cut:]
pre1 = pre1[bottom_cut:]
post1 = post1[bottom_cut:]
if top_cut != 0:
    night1 = night1[:-top_cut]
    prePost1 = prePost1[:-top_cut]
    pre1 = pre1[:-top_cut]
    post1 = post1[:-top_cut]


# Cut second index:
bottom_cut = (second_chart_index < chartIndex[0]).sum()
top_cut = (second_chart_index > chartIndex[-1]).sum()

night2 = night2[bottom_cut:]
prePost2 = prePost2[bottom_cut:]
pre2 = pre2[bottom_cut:]
post2 = post2[bottom_cut:]
if top_cut != 0:
    night2 = night2[:-top_cut]
    prePost2 = prePost2[:-top_cut]
    pre2 = pre2[:-top_cut]
    post2 = post2[:-top_cut]

night1 *= scale
prePost1 *= scale
pre1 *= scale
post1 *= scale

nightPortfolio = night1 + night2 + 1
prePostPortfolio = prePost1 + prePost2 + 1
prePortfolio = pre1 + pre2 + 1
postPortfolio = post1 + post2 + 1

plt.yscale("log")
plt.plot(chartIndex, np.cumprod(nightPortfolio), label="Extended Hours")
plt.plot(chartIndex, np.cumprod(prePostPortfolio), label="Post-Pre Jump")
plt.plot(chartIndex, np.cumprod(prePortfolio), label="Pre Market Returns")
plt.plot(chartIndex, np.cumprod(postPortfolio), label="Post Market Returns")

plt.legend()
plt.title(
    asset1 + " , " + asset2 + ": How much of extended move occurs during pre-post jump?"
)
plt.show()

"""
my_style = mpf.make_mpf_style(base_mpf_style="charles", rc={"font.size": 8})

# plot the chart with volume bars
mpf.plot(
    intra_data,
    type="candle",
    volume=True,
    style=my_style,
    title="Stock Price",
    ylabel="Price ($)",
    ylabel_lower="Volume",
)
"""
