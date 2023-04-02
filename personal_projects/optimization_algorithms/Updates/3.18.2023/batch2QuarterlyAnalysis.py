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
import os

# Load list of assets:
with open("../all_assets.txt", "r") as f:
    text = f.read()
    all_assets = list(set(json.loads(text)))

# tickers = all_assets[:500]

analysisYear = 2013
analysisMonth = 1
outSample = True


def dateRotation(year, month):
    if month == 1:
        return [year, month + 3]
    elif month == 4:
        return [year, month + 3]
    elif month == 7:
        return [year, month + 3]
    elif month == 10:
        return [year + 1, 1]


def createData(tickers, dateRange, sampleType, portfolioSize):
    _analysisYear = dateRange[0]
    _analysisMonth = dateRange[1]
    if sampleType == "eval":
        offsetYear, offsetMonth = dateRotation(_analysisYear, _analysisMonth)

        ticker_data = yfinance.download(
            tickers,
            start=datetime.datetime(_analysisYear, _analysisMonth, 1),
            end=datetime.datetime(offsetYear, offsetMonth, 1),
            group_by="ticker",
            actions=True,
        )
    elif sampleType:
        ticker_data = yfinance.download(
            tickers,
            start=datetime.datetime(2010, 1, 1),
            end=datetime.datetime(_analysisYear, _analysisMonth, 1),
            group_by="ticker",
            actions=True,
        )
    else:
        offsetYear, offsetMonth = dateRotation(_analysisYear, _analysisMonth)

        ticker_data = yfinance.download(
            tickers,
            start=datetime.datetime(2010, 1, 1),
            end=datetime.datetime(offsetYear, offsetMonth, 1),
            group_by="ticker",
            actions=True,
        )
    # Create a new data frame and populate it with only the close columns
    ticker_data_close = pd.DataFrame()

    for n in tickers:
        ticker_data_close[n] = ticker_data[(n, "Close")]

    # Since some assets start earlier than others, we need to start at the point when all assets have data
    earliest_date = []
    tickers = []
    # Give it another shuffle for good measure
    for ticker in list(ticker_data_close):
        if len(tickers) >= portfolioSize:
            break
        try:
            if (
                ticker_data_close[ticker].first_valid_index().date()
                == ticker_data.index[0]
            ):
                temp_data = ticker_data_close[ticker].copy()
                temp_data = temp_data.truncate(
                    before=ticker_data_close[ticker].first_valid_index()
                )
                if temp_data.isna().sum() == 0:
                    tickers.append(ticker)
                    earliest_date.append(ticker_data_close[ticker].first_valid_index())
        except Exception as e:
            pass

    ticker_data_close = ticker_data_close.truncate(before=max(earliest_date))
    ticker_data = ticker_data.truncate(before=max(earliest_date))

    # Convert dollar changes to percent changes and drop the first row
    ticker_data_percent = ticker_data_close.pct_change(1)
    ticker_data_percent.drop(ticker_data_percent.index[0], inplace=True)

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

    return ticker_data_percent


savedSolutions = {}
while analysisYear <= 2022:
    print(analysisYear)
    tickers = ["CAR", "CMG", "EFX", "GRMN", "FIS", "LULU", "MNST", "PHM", "TRIP", "WDC"]
    tickers.append("SPY")

    ticker_data_percent = createData(
        tickers, (analysisYear, analysisMonth), outSample, 10
    )

    # ---------------------- #

    # The sympy math starts here

    # Subset of ticker list, in case you want to exclude some tickers from the main list.
    asset_names = tickers + ["Cash"]
    length_of_assets = len(asset_names)

    covariance_matrix = ticker_data_percent[asset_names].cov()
    # pprint("Covariance Matrix: ")
    # pprint(covariance_matrix)
    # pprint("---------------")

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

    # pprint("Variance function: ")
    # pprint(portfolio_variance)
    # pprint("---------------")

    # Calculate an array of corresponding average daily returns based off of the columns of the data table.
    expected_asset_returns = np.array(
        ticker_data_percent.mean(axis=0)[asset_names]
    ).reshape(-1, 1)
    # pprint("Expected Returns: " + str(expected_asset_returns))
    # pprint("---------------")

    target_portfolio_returns = (
        ticker_data_percent.mean(axis=0)["SPY"] * 0.5
    )  # Set target return
    # pprint("Target Return: " + str(target_portfolio_returns))
    # pprint("---------------")

    # Constraint 1: The sum of each weight multiplied with its corresponding return must equal our target return
    portfolio_returns_constraint = asset_weights_T @ expected_asset_returns
    portfolio_returns_constraint = portfolio_returns_constraint[0][0]
    # pprint("Portfolio return must meet target: ")
    # pprint(portfolio_returns_constraint)
    # pprint("---------------")

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

    # Append solution to my amazing list
    try:
        savedSolutions[(analysisYear, analysisMonth)].append(solution)
    except:
        savedSolutions[(analysisYear, analysisMonth)] = [solution]

    if not outSample:
        analysisYear, analysisMonth = dateRotation(analysisYear, analysisMonth)
    outSample = not outSample

globalInSample = []
globalOutSample = []
globalEqualSample = []


def loadStratified():
    with open("../quarterlySharpeDevs/stratifiedInSharpes.txt", "r") as f:
        stratifiedInSharpes = json.load(f)
        stratifiedInSharpes = {
            tuple(map(int, k.strip("()").split(", "))): v
            for k, v in stratifiedInSharpes.items()
        }
    with open("../quarterlySharpeDevs/stratifiedOutSharpes.txt", "r") as f:
        stratifiedOutSharpes = json.load(f)
        stratifiedOutSharpes = {
            tuple(map(int, k.strip("()").split(", "))): v
            for k, v in stratifiedOutSharpes.items()
        }
    with open("../quarterlySharpeDevs/stratifiedEqualSharpes.txt", "r") as f:
        stratifiedEqualSharpes = json.load(f)
        stratifiedEqualSharpes = {
            tuple(map(int, k.strip("()").split(", "))): v
            for k, v in stratifiedEqualSharpes.items()
        }

    return stratifiedInSharpes, stratifiedOutSharpes, stratifiedEqualSharpes


# Stratified list. Make sure to delete when resetting.
if os.path.isfile("../quarterlySharpeDevs/stratifiedEqualSharpes.txt"):
    stratifiedInSharpes, stratifiedOutSharpes, stratifiedEqualSharpes = loadStratified()
else:
    # Create the necessary files, assuming if one is missing, they all are.
    stratifiedDictionary = {}
    for dateRange in list(savedSolutions.keys()):
        stratifiedDictionary[dateRange] = []
    stratifiedDictionary = json.dumps(
        {str(k): v for k, v in stratifiedDictionary.items()}
    )
    with open("../quarterlySharpeDevs/stratifiedEqualSharpes.txt", "w") as f:
        f.write(stratifiedDictionary)
    with open("../quarterlySharpeDevs/stratifiedInSharpes.txt", "w") as f:
        f.write(stratifiedDictionary)
    with open("../quarterlySharpeDevs/stratifiedOutSharpes.txt", "w") as f:
        f.write(stratifiedDictionary)

    stratifiedInSharpes, stratifiedOutSharpes, stratifiedEqualSharpes = loadStratified()


for dateRange in list(savedSolutions.keys()):
    tickers = ["CAR", "CMG", "EFX", "GRMN", "FIS", "LULU", "MNST", "PHM", "TRIP", "WDC"]
    tickers.append("SPY")

    ticker_data_percent = createData(tickers, dateRange, "eval", 10)

    outOfSample = savedSolutions[dateRange][0]
    backtestOut = pd.concat(
        [ticker_data_percent, ticker_data_percent[asset_names] @ outOfSample], axis=1
    )
    backtestOut.rename({0: "Optimal_Portfolio"}, axis=1, inplace=True)

    inSample = savedSolutions[dateRange][1]
    backtestIn = pd.concat(
        [ticker_data_percent, ticker_data_percent[asset_names] @ inSample], axis=1
    )
    backtestIn.rename({0: "Optimal_Portfolio"}, axis=1, inplace=True)

    # Create an equal weights portfolio for comparison, excluding cash
    equal_weights = [1 / (length_of_assets - 1) for n in range(length_of_assets - 1)]
    equal_weights.append(0)

    # Concat the equal weights portfolio
    backtestIn = pd.concat(
        [backtestIn, ticker_data_percent[asset_names] @ equal_weights], axis=1
    )
    backtestIn.rename({0: "Equal_Weights"}, axis=1, inplace=True)

    inData = (
        252 ** 0.5
        * statistics.mean(backtestIn["Optimal_Portfolio"][:])
        / statistics.pstdev(backtestIn["Optimal_Portfolio"][:])
    )
    outData = (
        252 ** 0.5
        * statistics.mean(backtestOut["Optimal_Portfolio"][:])
        / statistics.pstdev(backtestOut["Optimal_Portfolio"][:])
    )
    equalData = (
        252 ** 0.5
        * statistics.mean(backtestIn["Equal_Weights"][:])
        / statistics.pstdev(backtestIn["Equal_Weights"][:])
    )

    globalInSample.append(inData)

    globalOutSample.append(outData)

    globalEqualSample.append(equalData)

    # Stratified data sets:
    stratifiedEqualSharpes[dateRange].append(equalData)
    stratifiedInSharpes[dateRange].append(inData)
    stratifiedOutSharpes[dateRange].append(outData)


# Load historic sharpes
with open("../quarterlySharpeDevs/inSharpes.txt", "r") as f:
    savedInSharpes = json.load(f)
with open("../quarterlySharpeDevs/outSharpes.txt", "r") as f:
    savedOutSharpes = json.load(f)
with open("../quarterlySharpeDevs/equalSharpes.txt", "r") as f:
    savedEqualSharpes = json.load(f)

globalInSample.extend(savedInSharpes)
globalOutSample.extend(savedOutSharpes)
globalEqualSample.extend(savedEqualSharpes)


sharpeDiffs = np.array(globalInSample) - np.array(globalOutSample)
print("--------- Output Begins -------------")
print("Data points: " + str(len(sharpeDiffs)))
print("--------- In vs Out ---------")
print("In - Out Sharpe diff means: " + str(statistics.mean(sharpeDiffs)))
print("In - Out Sharpe diff std dev: " + str(statistics.pstdev(sharpeDiffs)))
plt.hist(sharpeDiffs, bins=30)
plt.title("In-Out Sharpe")
plt.show()

# Save historic sharpes
with open("../quarterlySharpeDevs/inSharpes.txt", "w") as f:
    json.dump(globalInSample, f)

with open("../quarterlySharpeDevs/outSharpes.txt", "w") as f:
    json.dump(globalOutSample, f)

with open("../quarterlySharpeDevs/equalSharpes.txt", "w") as f:
    json.dump(globalEqualSample, f)


# Run paired test on the sharpe differences. Test if in sample is greater than out of sample
p_value = stats.ttest_rel(
    globalInSample,
    globalOutSample,
    alternative="greater",
)[1]
print("Paired test in-out, in greater than out p_value: " + str(p_value))


# Correlate the initial sharpe to the difference in sharpes
print("---------- In Sample Outperformance vs Out Sample Outperformace ----------")
plt.scatter(np.array(globalInSample) - np.array(globalEqualSample), sharpeDiffs)
plt.title("In sample outperformance vs out sample outperformance")
slope, intercept, r_value, p_value, std_err = stats.linregress(
    np.array(globalInSample) - np.array(globalEqualSample), sharpeDiffs
)
x_vals = np.array(
    [
        min(np.array(globalInSample) - np.array(globalEqualSample)),
        max(np.array(globalInSample) - np.array(globalEqualSample)),
    ]
)
y_vals = intercept + slope * x_vals
plt.plot(x_vals, y_vals, color="r")
plt.show()

print("Positive slope indicates a higher outperformance carries on to out of sample")
print("LOBF Slope: " + str(slope))
print("Constant: " + str(intercept))

print("--------- Equal vs Out of Sample ------------")
plt.scatter(globalEqualSample, globalOutSample)
plt.title("Equal sharpe vs out of sample sharpes")
plt.show()

slope, intercept, r_value, p_value, std_err = stats.linregress(
    globalEqualSample, globalOutSample
)

null_hypothesis = 1
t_value = (slope - null_hypothesis) / std_err
p_value = 1 - stats.t.cdf(t_value, len(globalEqualSample) - 2)

print("LOBF Slope: " + str(slope))
print("P-value slope greater than 1: " + str(p_value))

print("-------- Out of sample vs Equal Sample -----------")
# Measure distribution of difference between out sample and equal weights.
sharpeDiffs = np.array(globalOutSample) - np.array(globalEqualSample)
print("Out-Equal Sharpe diff means: " + str(statistics.mean(sharpeDiffs)))
print("Out-Equal Sharpe diff std dev: " + str(statistics.pstdev(sharpeDiffs)))
plt.hist(sharpeDiffs, bins=30)
plt.title("Out-Equal Sharpe")
plt.show()


# Run paired test on the sharpe differences. Test if out of sample is greater than equal sample
p_value = stats.ttest_rel(
    globalOutSample,
    globalEqualSample,
    alternative="greater",
)[1]
print("Paired test out-equal, in greater than out p_value: " + str(p_value))

print("----------- Train Length vs Outperformance -----------")
# Analyse stratified sharpes
means = []
for dateRange in list(stratifiedEqualSharpes.keys()):
    # print("Date range test: " + dateRange)
    #
    # print("Sharpe diff means: " + str(statistics.mean(sharpeDiffs)))
    # print("Sharpe diff std dev: " + str(statistics.pstdev(sharpeDiffs)))

    sharpeDiffs = np.array(stratifiedInSharpes[dateRange]) - np.array(
        stratifiedEqualSharpes[dateRange]
    )
    means.append(statistics.mean(sharpeDiffs))

plt.scatter(np.arange(len(list(stratifiedEqualSharpes.keys()))), means)
plt.title("Mean Difference vs Train Range")
plt.show()

slope, intercept, r_value, p_value, std_err = stats.linregress(
    np.arange(0, len(list(stratifiedEqualSharpes.keys()))), means
)
print("Train length and difference slope: " + str(slope))
print("Train length and difference slope p-value: " + str(p_value))

# Explain to my why the out sample outperformance is negative? Look at in sample outperformance
sharpeDiffs = np.array(globalInSample) - np.array(globalEqualSample)
print("--------- In vs Equal ---------")
print("In - Equal Sharpe diff means: " + str(statistics.mean(sharpeDiffs)))
print("In - Equal Sharpe diff std dev: " + str(statistics.pstdev(sharpeDiffs)))
plt.hist(sharpeDiffs, bins=30)
plt.title("In-Equal Sharpe")
plt.show()

# Save historic stratified sharpes
with open("../quarterlySharpeDevs/stratifiedEqualSharpes.txt", "w") as f:
    stratifiedEqualSharpes = json.dumps(
        {str(k): v for k, v in stratifiedEqualSharpes.items()}
    )
    f.write(stratifiedEqualSharpes)

with open("../quarterlySharpeDevs/stratifiedInSharpes.txt", "w") as f:
    stratifiedInSharpes = json.dumps(
        {str(k): v for k, v in stratifiedInSharpes.items()}
    )
    f.write(stratifiedInSharpes)

with open("../quarterlySharpeDevs/stratifiedOutSharpes.txt", "w") as f:
    stratifiedOutSharpes = json.dumps(
        {str(k): v for k, v in stratifiedOutSharpes.items()}
    )
    f.write(stratifiedOutSharpes)
