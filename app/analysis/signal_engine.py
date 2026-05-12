import pandas_ta as ta

from app.data.fetcher import (
    fetch_stock_data,
    load_tickers
)


def calculate_indicators(data):

    data["RSI"] = ta.rsi(
        data["Close"],
        length=14
    )

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


def generate_signal(data):

    latest_rsi = data["RSI"].iloc[-1]
    sma20 = data["SMA20"].iloc[-1]
    sma50 = data["SMA50"].iloc[-1]

    if sma20 > sma50 and latest_rsi < 70:
        return "BUY"

    elif sma20 < sma50 and latest_rsi < 40:
        return "SELL"

    else:
        return "HOLD"


if __name__ == "__main__":

    tickers = load_tickers()

    for ticker in tickers:

        print(f"\nAnalyzing {ticker}...\n")

        data = fetch_stock_data(
            ticker,
            period="3mo"
        )

        data = calculate_indicators(data)

        latest_rsi = data["RSI"].iloc[-1]

        signal = generate_signal(data)

        print(f"RSI: {latest_rsi:.2f}")
        print(f"Signal: {signal}")