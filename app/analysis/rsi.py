import pandas_ta as ta

from app.data.fetcher import (
    fetch_stock_data,
    load_tickers
)


def calculate_rsi(data, length=14):

    data["RSI"] = ta.rsi(
        data["Close"],
        length=length
    )

    return data


if __name__ == "__main__":

    tickers = load_tickers()

    for ticker in tickers:

        print(f"\nAnalyzing {ticker}...\n")

        data = fetch_stock_data(ticker)

        data = calculate_rsi(data)

        latest_rsi = data["RSI"].iloc[-1]

        print(f"Latest RSI: {latest_rsi:.2f}")

        if latest_rsi < 30:
            print("Possible Oversold Condition")

        elif latest_rsi > 70:
            print("Possible Overbought Condition")

        else:
            print("Neutral Momentum")