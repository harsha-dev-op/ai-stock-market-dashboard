import yfinance as yf
import pandas as pd


def load_tickers(file_path="tickers.txt"):
    with open(file_path, "r") as file:
        tickers = [line.strip() for line in file.readlines()]
    return tickers


def fetch_stock_data(ticker, period="1mo", interval="1d"):
    stock = yf.Ticker(ticker)

    data = stock.history(
        period=period,
        interval=interval
    )

    return data


if __name__ == "__main__":

    tickers = load_tickers()

    for ticker in tickers:

        print(f"\nFetching data for {ticker}...\n")

        data = fetch_stock_data(ticker)

        print(data.tail())