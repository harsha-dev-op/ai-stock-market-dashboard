import pandas as pd

from app.data.fetcher import (
    fetch_stock_data,
    load_tickers
)


def calculate_moving_averages(data):

    data["SMA20"] = (
        data["Close"]
        .rolling(window=20)
        .mean()
    )

    data["SMA50"] = (
        data["Close"]
        .rolling(window=50)
        .mean()
    )

    return data


def analyze_trend(data):

    latest_sma20 = data["SMA20"].iloc[-1]
    latest_sma50 = data["SMA50"].iloc[-1]

    if latest_sma20 > latest_sma50:
        return "Bullish Trend"

    elif latest_sma20 < latest_sma50:
        return "Bearish Trend"

    else:
        return "Neutral Trend"


if __name__ == "__main__":

    tickers = load_tickers()

    for ticker in tickers:

        print(f"\nAnalyzing {ticker}...\n")

        data = fetch_stock_data(
            ticker,
            period="3mo"
        )

        data = calculate_moving_averages(data)

        trend = analyze_trend(data)

        latest_sma20 = data["SMA20"].iloc[-1]
        latest_sma50 = data["SMA50"].iloc[-1]

        print(f"SMA20: {latest_sma20:.2f}")
        print(f"SMA50: {latest_sma50:.2f}")
        print(f"Trend: {trend}")