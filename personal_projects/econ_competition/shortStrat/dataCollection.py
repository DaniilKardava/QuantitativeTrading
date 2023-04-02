import concurrent.futures
import pandas as pd
import stocksera

# Load list of ticker
tickerList = ["SPY"]

client = stocksera.Client(api_key="YOURKEY")

# Concat incoming data to this dataframe
allData = pd.DataFrame(index=pd.DatetimeIndex([], name="Date"))


counter = 0


def process_ticker(ticker):
    global counter
    try:
        print(counter)
        counter += 1
        short_data = client.borrowed_shares(ticker=ticker)

        df = pd.DataFrame(short_data)

        df["date_updated"] = pd.to_datetime(df["date_updated"])
        
        # Convert intraday index to end of day values
        newT = df.groupby(df["date_updated"].dt.date).first()
        newT.drop("date_updated", axis=1, inplace=True)
        newT.index.rename("Date", inplace=True)
      
        # Format 
        newT.drop("available", axis=1, inplace=True)
        newT.drop("ticker", axis=1, inplace=True)
        newT.rename({"fee": ticker}, inplace=True, axis=1)

        return newT
    except Exception as e:
        print(e)
        return None


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(process_ticker, ticker) for ticker in tickerList
    ]
    for future in concurrent.futures.as_completed(futures):
        result = future.result()
        if result is not None:
            allData = pd.concat([allData, result], axis=1)

# I ran this script concurrently in multiple tabs and saved each run to its own csv file. I combined them all afterwards. 
allData.to_csv("borrowData.csv")
