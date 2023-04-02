import yfinance
import datetime
import pandas as pd
import numpy as np
import sympy
from sympy import pprint
from matplotlib import pyplot as plt
import random
from concurrent.futures import ThreadPoolExecutor
from scipy.optimize import minimize
import statistics
import json
from scipy import stats


# Load list of assets:
with open("all_assets.txt", "r") as f:
    text = f.read()
    all_assets = list(set(json.loads(text)))

# tickers = all_assets[:500]
tickers = [
    "CRL",
    "CRI",
    "CCK",
    "PKG",
    "VLY",
    "WSM",
    "FORM",
    "WWD",
    "ABG",
    "PLXS",
    "SPTN",
    "MANH",
    "EBS",
    "SEIC",
]
tickers.append("SPY")

ticker_data = yfinance.download(
    tickers,
    start=datetime.datetime(2021, 1, 1),
    end=datetime.datetime(2022, 1, 1),
    group_by="ticker",
    actions=True,
)
print(ticker_data)

# Create a new data frame and populate it with only the close columns
ticker_data_close = pd.DataFrame()

for n in tickers:
    ticker_data_close[n] = ticker_data[(n, "Close")]


# Since some assets start earlier than others, we need to start at the point when all assets have data
portfolioSize = 20
earliest_date = []
tickers = []
# Give it another shuffle for good measure
for ticker in list(ticker_data_close):
    if len(tickers) >= portfolioSize:
        break
    try:
        if ticker_data_close[ticker].first_valid_index().date() == ticker_data.index[0]:
            temp_data = ticker_data_close[ticker].copy()
            temp_data = temp_data.truncate(
                before=ticker_data_close[ticker].first_valid_index()
            )
            if temp_data.isna().sum() == 0:
                tickers.append(ticker)
                earliest_date.append(ticker_data_close[ticker].first_valid_index())
    except Exception as e:
        pass

print(tickers)

ticker_data_close = ticker_data_close.truncate(before=max(earliest_date))
ticker_data = ticker_data.truncate(before=max(earliest_date))

# Convert dollar changes to percent changes and drop the first row
ticker_data_percent = ticker_data_close.pct_change(1)
ticker_data_percent.drop(ticker_data_percent.index[0], inplace=True)

print(ticker_data_percent["SPY"])
# Add cash column
ticker_data_percent["Cash"] = np.zeros((len(ticker_data_percent), 1))
if "SPY" in tickers:
    tickerCopy = tickers.copy()
else:
    tickerCopy = tickers.copy() + ["SPY"]

# Add dividends
for ticker in tickerCopy:
    dividend_history = ticker_data[(ticker, "Dividends")]
    if len(dividend_history) == 0:
        continue
    dividend_history = dividend_history.reindex_like(ticker_data_percent).fillna(0)
    ticker_data_percent[ticker] = ticker_data_percent[
        ticker
    ] + dividend_history / np.array(ticker_data[(ticker, "Close")][:-1])

# ---------------------- #

# The sympy math starts here

# Subset of ticker list, in case you want to exclude some tickers from the main list.
asset_names = tickers + ["Cash"]
length_of_assets = len(asset_names)

covariance_matrix = ticker_data_percent[asset_names].cov()
pprint("Covariance Matrix: ")
# pprint(covariance_matrix)
pprint("---------------")

# Create list of sympy symbols for each weight and our two constraints
equation_variables = []
for ticker_position in range(length_of_assets):
    equation_variables.append(sympy.Symbol("w" + str(ticker_position), real=True))


# Isolate the variables representing the asset weights
asset_weights = []
for n in range(0, length_of_assets):
    asset_weights.append(equation_variables[n])

# Reshape the matrix to be vertical. -1 indicates that the rows should be whatever value fits as long as the columns is 1.
asset_weights = np.array(asset_weights).reshape(-1, 1)

# I'm building asset weight constraint into the main function
# Copy the weights into new list while Im altering the original
weights_copy = asset_weights.copy()
for position in range(len(weights_copy)):
    asset_weights[position] = weights_copy[position] / sum(abs(weights_copy))

asset_weights_T = np.transpose(asset_weights)


# Portfolio variance function, main function to minimize
portfolio_variance = asset_weights_T @ covariance_matrix @ asset_weights
portfolio_variance = portfolio_variance[0][0]  # Strip outer brackets

pprint("Variance function: ")
# pprint(portfolio_variance)
pprint("---------------")

# Calculate an array of corresponding average daily returns based off of the columns of the data table.
expected_asset_returns = np.array(
    ticker_data_percent.mean(axis=0)[asset_names]
).reshape(-1, 1)
pprint("Expected Returns: " + str(expected_asset_returns))
pprint("---------------")

target_portfolio_returns = (
    ticker_data_percent.mean(axis=0)["SPY"] * 0.5
)  # Set target return
pprint("Target Return: " + str(target_portfolio_returns))
pprint("---------------")


# Constraint 1: The sum of each weight multiplied with its corresponding return must equal our target return
portfolio_returns_constraint = asset_weights_T @ expected_asset_returns
portfolio_returns_constraint = portfolio_returns_constraint[0][0]
pprint("Portfolio return must meet target: ")
# pprint(portfolio_returns_constraint)
pprint("---------------")


returnTarget = sympy.lambdify(
    equation_variables,
    portfolio_returns_constraint,
    "numpy",
)

# Inequality, violations are negative
def returnsConstraint(x):
    return returnTarget(*x) - target_portfolio_returns


constraints = [
    {"type": "ineq", "fun": returnsConstraint},
]

# Maximize by minimizing the negative
sharpe_function = (
    -1 * 252 ** 0.5 * portfolio_returns_constraint / portfolio_variance ** 0.5
)

objectiveFunction = sympy.lambdify(
    equation_variables,
    sharpe_function,
    "numpy",
)


def objective(x):
    return objectiveFunction(*x)


solutions = []

counter = 0


class outputSolution:
    def __init__(
        self,
        solution,
        returns,
        volatility,
    ):
        self.solutionVector = solution
        self.volatility = volatility
        self.returns = returns
        self.sharpe = self.returns / self.volatility


def solve_equation():
    global counter
    guess = list(random.uniform(0, 10000) for a in range(length_of_assets))
    solution = minimize(objective, guess, constraints=constraints).x
    subs = {}
    for variable in range(len(equation_variables)):
        subs[equation_variables[variable]] = solution[variable]

    solutions.append(
        outputSolution(
            solution,
            portfolio_returns_constraint.evalf(subs=subs) * 252,
            portfolio_variance.evalf(subs=subs) ** 0.5 * 252 ** 0.5,
        )
    )
    print(counter)
    counter += 1


with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(solve_equation) for n in range(100)]
    # Wait for all tasks to complete and retrieve their results
    for future in futures:
        future.result()

# Don't forget to switch the inequality depending on sorting metric
bestPick = solutions[0]
for solution in solutions:
    if solution.sharpe > bestPick.sharpe:
        bestPick = solution

solution = bestPick.solutionVector
# Convert to percentages
solution = list(sol / sum(abs(val) for val in solution) for sol in solution)
print("Solution for comparison: " + str(solution))

subs = {}
for variable in range(len(equation_variables)):
    subs[equation_variables[variable]] = solution[variable]
bestPick.returns = portfolio_returns_constraint.evalf(subs=subs) * 252
bestPick.volatility = portfolio_variance.evalf(subs=subs) ** 0.5 * 252 ** 0.5
bestPick.sharpe = bestPick.returns / bestPick.volatility

print(
    "Portfolio returns: "
    + str(bestPick.returns)
    + " vs Benchmark: "
    + str(ticker_data_percent.mean(axis=0)["SPY"] * 252)
)
print(
    "Portfolio volatility: "
    + str(bestPick.volatility)
    + " vs Benchmark: "
    + str(statistics.pstdev(ticker_data_percent["SPY"]) * 252 ** 0.5)
)
print(
    "Portfolio sharpe: "
    + str(bestPick.sharpe)
    + " vs Benchmark: "
    + str(
        ticker_data_percent.mean(axis=0)["SPY"]
        * 252
        / (statistics.pstdev(ticker_data_percent["SPY"]) * 252 ** 0.5)
    )
)

# Convert to percentages
solution = list(sol / sum(abs(val) for val in solution) for sol in solution)


outOfSample = [
    0.14436427783326014,
    0.09850445996372259,
    0.0878430302395238,
    0.10918593085648028,
    0.022497926127541406,
    0.05870454713922701,
    0.0031526346192993163,
    0.031153867116401696,
    0.161030489403944,
    0.10649745199853401,
    0.1770653847020658,
]
backtestOut = pd.concat(
    [ticker_data_percent, ticker_data_percent[asset_names] @ outOfSample], axis=1
)
backtestOut.rename({0: "Optimal_Portfolio"}, axis=1, inplace=True)


inSample = [
    0.16503366407971015,
    0.03291690063957646,
    0.019629546286106813,
    0.13026787497526424,
    0.026003153381071058,
    0.2125009489116254,
    0.01860951258874688,
    0.15913668620755408,
    0.08251028721310584,
    0.05580246877088856,
    0.09758895694635047,
]
backtestIn = pd.concat(
    [ticker_data_percent, ticker_data_percent[asset_names] @ inSample], axis=1
)
backtestIn.rename({0: "Optimal_Portfolio"}, axis=1, inplace=True)


# pretty_weights = {k: v for k, v in zip(asset_names, solution)}
# print(pretty_weights)

# Create an equal weights portfolio for comparison, excluding cash
equal_weights = [1 / (length_of_assets - 1) for n in range(length_of_assets - 1)]
equal_weights.append(0)

# Concat the equal weights portfolio
backtestIn = pd.concat(
    [backtestIn, ticker_data_percent[asset_names] @ equal_weights], axis=1
)
backtestIn.rename({0: "Equal_Weights"}, axis=1, inplace=True)


# Plot SPY returns
plt.plot(backtestIn.index, (ticker_data_percent["SPY"] + 1).cumprod() - 1, label="SPY")

# Plot In Sample
plt.plot(
    backtestIn.index,
    (backtestIn["Optimal_Portfolio"] + 1).cumprod() - 1,
    label="In Sample Portfolio",
)

# Plot out of sample
plt.plot(
    backtestOut.index,
    (backtestOut["Optimal_Portfolio"] + 1).cumprod() - 1,
    label="Out of Sample Portfolio",
)

# Plot equal weights portfolio
plt.plot(
    backtestIn.index,
    (backtestIn["Equal_Weights"] + 1).cumprod() - 1,
    label="Equal Weights",
)


plt.legend()
plt.xlabel("Decimal Returns (% * 100)")
plt.ylabel("Date")
plt.show()

# Calculate pvalues and trailing sharpe ratios:
trailingSharpeIn = []
trailingSharpeOut = []

pvalues = []
# Start with 1 to prevent 0 std dev in denominator
for index in range(1, len(backtestIn.index)):
    # Scale down my sharpes for in sample to set a more realistic comparison
    trailingSharpeIn.append(
        0.9
        * statistics.mean(backtestIn["Optimal_Portfolio"][0 : index + 1])
        / statistics.pstdev(backtestIn["Optimal_Portfolio"][0 : index + 1])
    )

    trailingSharpeOut.append(
        statistics.mean(backtestOut["Optimal_Portfolio"][0 : index + 1])
        / statistics.pstdev(backtestOut["Optimal_Portfolio"][0 : index + 1])
    )

    # Append paired t-test pvalues as a function of time from training end
    if len(trailingSharpeIn) >= 100:
        pvalues.append(
            stats.ttest_rel(
                trailingSharpeIn,
                np.array(trailingSharpeOut),
                alternative="greater",
            )[1]
        )

# Scale my sharpes to annual values
trailingSharpeIn = np.array(trailingSharpeIn) * 252 ** 0.5
trailingSharpeOut = np.array(trailingSharpeOut) * 252 ** 0.5

# Plot sharpes
plt.plot(backtestIn.index[1:], trailingSharpeIn, label="In sample sharpe")
plt.plot(backtestIn.index[1:], trailingSharpeOut, label="Out of sample sharpe")
plt.legend()
plt.show()

# Plot the p-values
plt.plot(backtestIn.index[100:], pvalues)
plt.title("Paired tests significance")
plt.show()
