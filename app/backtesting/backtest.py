import pandas as pd
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


def generate_signals(data):

    signals = []

    for i in range(len(data)):

        rsi = data["RSI"].iloc[i]
        sma20 = data["SMA20"].iloc[i]
        sma50 = data["SMA50"].iloc[i]

        if sma20 > sma50 and rsi < 70:
            signals.append(1)

        elif sma20 < sma50 and rsi < 40:
            signals.append(-1)

        else:
            signals.append(0)

    data["Signal"] = signals

    return data


def backtest_strategy(data):

    data["Market Return"] = (
        data["Close"]
        .pct_change()
    )

    data["Strategy Return"] = (
        data["Market Return"]
        * data["Signal"].shift(1)
    )

    cumulative_return = (
        (1 + data["Strategy Return"])
        .cumprod()
    )

    final_return = (
        cumulative_return.iloc[-1] - 1
    ) * 100

    return final_return


if __name__ == "__main__":

    tickers = load_tickers()

    for ticker in tickers:

        print(f"\nBacktesting {ticker}...\n")

        data = fetch_stock_data(
            ticker,
            period="6mo"
        )

        data = calculate_indicators(data)

        data = generate_signals(data)

        final_return = backtest_strategy(data)

        print(f"Strategy Return: {final_return:.2f}%")