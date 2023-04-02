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

# Downloading data
tickers = [
    "SPY",
    "QQQ",
    "TLT",
    "GLD",
]

ticker_data = yfinance.download(
    tickers,
    start=datetime.datetime(2000, 1, 1),
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

# Add cash column
ticker_data_percent["Cash"] = np.zeros((len(ticker_data_percent), 1))

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
asset_names = ["SPY", "GLD", "TLT", "QQQ", "Cash"]
length_of_assets = len(asset_names)

covariance_matrix = ticker_data_percent[asset_names].cov()
pprint("Covariance Matrix: ")
# pprint(covariance_matrix)
pprint("---------------")

# Create list of sympy symbols for each weight and our two constraints
equation_variables = []
for ticker_position in range(length_of_assets):
    equation_variables.append(sympy.Symbol("w" + str(ticker_position), real=True))

# Append lambda variables for contraints
equation_variables.append(sympy.Symbol("lambda1", real=True))

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
portfolio_returns_constraint = portfolio_returns_constraint[0][0]
pprint("Portfolio return must meet target: ")
pprint(portfolio_returns_constraint)
pprint("---------------")

lambda1 = equation_variables[length_of_assets]


# Defining and finding the gradient of the lagrangian with both constraints active
lagrangian_function = portfolio_variance - lambda1 * (
    portfolio_returns_constraint - expected_portfolio_returns
)
lagrangian_function = lagrangian_function[0][0]

pprint("The Lagrangian: ")
# pprint(lagrangian_function)
pprint("---------------")

f_numpy = sympy.lambdify(
    equation_variables,
    lagrangian_function,
    "numpy",
)


def objective_function(x):
    return f_numpy(*x)


solutions = []

counter = 0


class outputSolution:
    def __init__(self, solution, output):
        self.solutionVector = solution
        self.output = output


def solve_equation():
    global counter
    guess = list(random.uniform(0, 10000) for a in range(length_of_assets))
    guess.append(0)
    solution = minimize(objective_function, guess).x
    subs = {}
    for variable in range(len(equation_variables) - 1):
        subs[equation_variables[variable]] = solution[variable]

    solutions.append(
        outputSolution(
            solution,
            252 ** 0.5
            * (
                portfolio_returns_constraint.evalf(subs=subs)
                / portfolio_variance.evalf(subs=subs) ** 0.5
            ),
        )
    )
    print(counter)
    counter += 1


with ThreadPoolExecutor(max_workers=100) as executor:
    futures = [executor.submit(solve_equation) for n in range(100)]
    # Wait for all tasks to complete and retrieve their results
    for future in futures:
        future.result()


bestPick = solutions[0]
for solution in solutions:
    if solution.output > bestPick.output:
        bestPick = solution

solution = bestPick.solutionVector
print("Function output: " + str(bestPick.output))

# Strip lambdas from solution
solution = np.array(solution).reshape(-1, 1)[0:length_of_assets]
solution = [float(x[0]) for x in solution]
solution = list(sol / sum(abs(val) for val in solution) for sol in solution)
print(solution)


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
plt.xlabel("Decimal Returns (% * 100)")
plt.ylabel("Date")
plt.show()
