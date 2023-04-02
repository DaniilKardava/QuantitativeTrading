import yfinance
import datetime
import pandas as pd
import numpy as np
import sympy
from sympy import pprint
from matplotlib import pyplot as plt
import statistics
import json
from scipy.stats import ttest_ind
from scipy.stats import mannwhitneyu
from scipy.stats import levene

# Downloading data
tickers = ["SPY", "QQQ", "TLT", "GLD"]

ticker_data = yfinance.download(
    tickers,
    start=datetime.datetime(2019, 1, 1),
    end=datetime.datetime(2024, 1, 1),
    group_by="ticker",
)


# Create a new data frame and populate it with only the close columns
ticker_data_close = pd.DataFrame()

for n in tickers:
    ticker_data_close[n] = ticker_data[(n, "Close")]


# Since some assets start earlier than others, we need to start at the point when all assets have data
earliest_date = []
for n in list(ticker_data_close):
    earliest_date.append(ticker_data_close[n].first_valid_index())

ticker_data_close = ticker_data_close.truncate(before=max(earliest_date))
ticker_data = ticker_data.truncate(before=max(earliest_date))

# Convert dollar changes to percent changes and drop the first row
ticker_data_percent = ticker_data_close.pct_change(1)
ticker_data_percent.drop(ticker_data_percent.index[0], inplace=True)

# Add dividends
for ticker in tickers:
    asset = yfinance.Ticker(ticker)
    dividend_history = asset.dividends

    if len(dividend_history) == 0:
        continue
    dividend_history = dividend_history.reindex_like(ticker_data_percent).fillna(0)

    # Note, division is arranged so that the percent is calculated relative to the close prior to ex-date, since that is how overnight losses
    # due to sell-offs are calculated as well.
    ticker_data_percent[ticker] = ticker_data_percent[
        ticker
    ] + dividend_history / np.array(ticker_data[(ticker, "Close")][:-1])


# ---------------------- #

# The sympy math starts here

# Subset of ticker list, in case you want to exclude some tickers from the main list.
asset_names = ["SPY", "QQQ", "TLT", "GLD"]
length_of_assets = len(asset_names)

covariance_matrix = ticker_data_percent[asset_names].cov()
pprint("Covariance Matrix: ")
pprint(covariance_matrix)
pprint("---------------")

# Create list of sympy symbols for each weight and our two constraints
equation_variables = []
for ticker_position in range(length_of_assets):
    equation_variables.append(sympy.Symbol("w" + str(ticker_position), real=True))

# Append lambda variables for contraints
equation_variables.append(sympy.Symbol("lambda1", real=True))
equation_variables.append(sympy.Symbol("lambda2", real=True))

# Isolate the variables representing the asset weights
asset_weights = []
for n in range(0, length_of_assets):
    asset_weights.append(equation_variables[n])

# Reshape the matrix to be vertical. -1 indicates that the rows should be whatever value fits as long as the columns is 1.
asset_weights = np.array(asset_weights).reshape(-1, 1)
asset_weights_T = np.transpose(asset_weights)


# Portfolio variance function, main function to minimize
portfolio_variance = asset_weights_T @ covariance_matrix @ asset_weights
portfolio_variance = portfolio_variance[0][0]  # Strip outer brackets

pprint("Variance function: ")
pprint(portfolio_variance)
pprint("---------------")

# Constraint 1: Sum of the absolute weights must equal 1.
ones_vector = np.ones((1, asset_weights.shape[0]))
weight_sum_constraint = ones_vector @ abs(asset_weights)
pprint("Sum of weights must equal 1 constraint: ")
pprint(weight_sum_constraint)
pprint("---------------")

# Calculate an array of corresponding average daily returns based off of the columns of the data table.
expected_portfolio_returns = np.array(
    ticker_data_percent.mean(axis=0)[asset_names]
).reshape(-1, 1)
pprint("Expected Returns: " + str(expected_portfolio_returns))
pprint("---------------")

target_portfolio_returns = (
    ticker_data_percent.mean(axis=0)["SPY"] * 1
)  # Set target return
pprint("Target Return: " + str(target_portfolio_returns))
pprint("---------------")

# Constraint 2: The sum of each weight multiplied with its corresponding return must equal our target return
portfolio_returns_constraint = asset_weights_T @ expected_portfolio_returns
pprint("Portfolio return must meet target: ")
pprint(portfolio_returns_constraint)
pprint("---------------")

lambda1 = equation_variables[length_of_assets]
lambda2 = equation_variables[length_of_assets + 1]


# Defining and finding the gradient of the lagrangian with both constraints active
lagrangian_function = (
    portfolio_variance
    - lambda1 * (weight_sum_constraint - 1)
    - lambda2 * (portfolio_returns_constraint - expected_portfolio_returns)
)
lagrangian_function = lagrangian_function[0][0]

pprint("The Lagrangian: ")
pprint(lagrangian_function)
pprint("---------------")


system_of_equations = []

# Calculate partial derivatives wrt to all weights and lambdas
for variable in equation_variables[:-2]:

    partial_derivative = sympy.diff(lagrangian_function, variable)

    # Equation solver fails to parse sign(x) representation of derivative of abs(x), therefore replace all sign(x) with x/(abs(x))
    derivative_of_abs = variable / abs(variable)
    partial_derivative = partial_derivative.replace(
        sympy.sign(variable), derivative_of_abs
    )
    system_of_equations.append(partial_derivative)

system_of_equations.append(sympy.diff(lagrangian_function, lambda1))
system_of_equations.append(sympy.diff(lagrangian_function, lambda2))

pprint("System of Equations: ")
pprint(system_of_equations)
pprint("---------------")

# Initial guess for all weights
initial_guess_vector = []
for n in range(length_of_assets):
    initial_guess_vector.append(1 / length_of_assets)

# Initial guess for all lambdas
initial_guess_vector.append(0.5)
initial_guess_vector.append(0.5)


solution = sympy.nsolve(
    system_of_equations, equation_variables, initial_guess_vector, verify=False
)

# Strip lambdas from solution
solution = np.array(solution).reshape(-1, 1)[0:length_of_assets]
solution = [float(x[0]) for x in solution]
print(solution)


solution = [
    0.019439008066687906,
    0.3338958269558381,
    0.48067822062742405,
    0.16598694435004996,
]

backtest = pd.concat(
    [ticker_data_percent, ticker_data_percent[asset_names] @ solution], axis=1
)
backtest.rename({0: "Optimal_Portfolio"}, axis=1, inplace=True)

# Plot SPY returns
plt.plot(backtest.index, (backtest["SPY"] + 1).cumprod() - 1, label="SPY")

# Plot Optimal Portfolio returns
plt.plot(
    backtest.index,
    (backtest["Optimal_Portfolio"] + 1).cumprod() - 1,
    label="Optimal Portfolio",
)

plt.legend()
plt.ylabel("Decimal Returns (% * 100)")
plt.xlabel("Date")
plt.show()


print(backtest)

populateTrainData = False

# Subsamples of size n to capture overall volatility. Second is overall portfolio volatility as time passes
trainingPortfolioVolatility = []
trainingRunningPortfolioVolatility = []
allTimeReturns = []
runningVolatilityIndex = []

if not populateTrainData:
    with open("portfolioVolatility.txt", "r") as file:
        text = file.read()
    trainingPortfolioVolatility = json.loads(text)

    with open("runningPortfolioVolatility.txt", "r") as file:
        text = file.read()
    trainingRunningPortfolioVolatility = json.loads(text)[1]
    runningVolatilityIndex = list(
        datetime.datetime.fromisoformat(date) for date in json.loads(text)[0]
    )

    with open("allTimeReturns.txt", "r") as file:
        text = file.read()
    allTimeReturns = json.loads(text)

testPortfolioVolatility = []
testRunningPortfolioVolatility = []

spyVolatility = []

measurementPeriod = 5
for subsample in range(1, int(len(backtest.index) / measurementPeriod)):
    try:
        testPortfolioVolatility.append(
            statistics.pstdev(
                backtest["Optimal_Portfolio"][
                    measurementPeriod * (subsample - 1) : measurementPeriod * subsample
                ]
            )
        )
        spyVolatility.append(
            statistics.pstdev(
                backtest["SPY"][
                    measurementPeriod * (subsample - 1) : measurementPeriod * subsample
                ]
            )
        )
    except:
        continue

    if populateTrainData:
        trainingRunningPortfolioVolatility.append(
            statistics.pstdev(
                backtest["Optimal_Portfolio"][0 : measurementPeriod * subsample]
            )
        )
        runningVolatilityIndex.append(backtest.index[subsample * measurementPeriod])
    else:
        trainingRunningPortfolioVolatility.append(
            statistics.pstdev(
                allTimeReturns
                + list(backtest["Optimal_Portfolio"][0 : measurementPeriod * subsample])
            )
        )
        runningVolatilityIndex.append(backtest.index[subsample * measurementPeriod])

if not populateTrainData:
    trainingPortfolioVolatility = testPortfolioVolatility
    
fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

ax1.hist(testPortfolioVolatility, bins=100)
ax1.set_title("OoS volatility sample")
print("OOS")
print("AVG: " + str(statistics.mean(testPortfolioVolatility)))
print("DEV: " + str(statistics.pstdev(testPortfolioVolatility)))

if not populateTrainData:
    ax2.hist(trainingPortfolioVolatility, bins=100)
    ax2.set_title("Training volatility sample")
    print("Trained")
    print("AVG: " + str(statistics.mean(trainingPortfolioVolatility)))
    print("DEV: " + str(statistics.pstdev(trainingPortfolioVolatility)))

ax3.hist(spyVolatility, bins=100)
ax3.set_title("SPY volatility sample")
print("SPY")
print("AVG: " + str(statistics.mean(spyVolatility)))
print("DEV: " + str(statistics.pstdev(spyVolatility)))

plt.show()

# Plot the dynamic portfolio volatiltiy as time passes
# Generate an index for graphing
plt.plot(
    runningVolatilityIndex,
    trainingRunningPortfolioVolatility,
)
plt.title("Portfolio Volatility: TRAIN VS OOS")
plt.axvline(datetime.datetime(2019, 1, 1), label="OOS")
plt.legend()
plt.show()

# Plot the difference in volatility test pvalues as a function of time from oos start
if not populateTrainData:
    pvalues = []
    for sample in range(10, len(testPortfolioVolatility)):
        t_statistic, p_value = ttest_ind(
            testPortfolioVolatility[:sample],
            trainingPortfolioVolatility,
            equal_var=False,
            alternative="greater",
        )
        pvalues.append(p_value)

    plt.plot(runningVolatilityIndex[-(len(pvalues)) :], pvalues)
    plt.title("PVALUES: TRAIN VS OOS")
    plt.show()

# Tests to compare volatility of training set to volatility of testing set
if not populateTrainData:
    print("WELSCH")
    t_statistic, p_value = ttest_ind(
        testPortfolioVolatility,
        trainingPortfolioVolatility,
        equal_var=False,
        alternative="greater",
    )

    print(p_value)

    print("mannwhitneyu, normality not met")
    u_statistic, p_value = mannwhitneyu(
        testPortfolioVolatility, trainingPortfolioVolatility, alternative="greater"
    )

    print(p_value)

    print("LEVENES")
    t_statistic, p_value = levene(
        testPortfolioVolatility,
        trainingPortfolioVolatility,
    )
    print(p_value)

if populateTrainData:
    with open("portfolioVolatility.txt", "w") as f:
        json.dump(testPortfolioVolatility, f)

    runningVolatilityIndex = list(index.isoformat() for index in runningVolatilityIndex)
    with open("runningPortfolioVolatility.txt", "w") as f:
        json.dump([runningVolatilityIndex, trainingRunningPortfolioVolatility], f)

    with open("allTimeReturns.txt", "w") as f:
        json.dump(
            list(backtest["Optimal_Portfolio"][0 : measurementPeriod * subsample]), f
        )
