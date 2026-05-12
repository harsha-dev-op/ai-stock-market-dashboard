import pandas_ta as ta

from app.data.fetcher import (
    fetch_stock_data,
    load_tickers
)

from app.analysis.sentiment import (
    fetch_news,
    analyze_sentiment,
    classify_sentiment
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


def calculate_conviction_score(
    rsi,
    sma20,
    sma50,
    sentiment_score
):

    score = 0

    # Trend Analysis
    if sma20 > sma50:
        score += 40
    else:
        score -= 40

    # RSI Analysis
    if rsi < 30:
        score += 30

    elif rsi > 70:
        score -= 20

    else:
        score += 10

    # Sentiment Analysis
    if sentiment_score > 0.1:
        score += 30

    elif sentiment_score < -0.1:
        score -= 30

    return score


def classify_signal(score):

    if score >= 60:
        return "STRONG BUY"

    elif score >= 30:
        return "BUY"

    elif score <= -40:
        return "SELL"

    else:
        return "HOLD"


if __name__ == "__main__":

    tickers = load_tickers()

    for ticker in tickers:

        print(f"\nAnalyzing {ticker}...\n")

        data = fetch_stock_data(
            ticker,
            period="6mo"
        )

        data = calculate_indicators(data)

        latest_rsi = data["RSI"].iloc[-1]

        sma20 = data["SMA20"].iloc[-1]

        sma50 = data["SMA50"].iloc[-1]

        headlines = fetch_news(ticker)

        sentiment_score = (
            analyze_sentiment(headlines)
        )

        sentiment = classify_sentiment(
            sentiment_score
        )

        conviction_score = (
            calculate_conviction_score(
                latest_rsi,
                sma20,
                sma50,
                sentiment_score
            )
        )

        signal = classify_signal(
            conviction_score
        )

        print(f"RSI: {latest_rsi:.2f}")

        print(
            f"Trend: "
            f"{'Bullish' if sma20 > sma50 else 'Bearish'}"
        )

        print(f"Sentiment: {sentiment}")

        print(
            f"Conviction Score: "
            f"{conviction_score}"
        )

        print(f"Final Signal: {signal}")