import streamlit as st
import pandas_ta as ta
import pandas as pd
import plotly.graph_objects as go
from streamlit_autorefresh import st_autorefresh

import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "../.."
        )
    )
)
from app.analysis.sentiment import (
    fetch_news,
    analyze_sentiment,
    classify_sentiment
)

from app.data.fetcher import (
    fetch_stock_data,
    load_tickers
)


def calculate_indicators(data):

    data["RSI"] = ta.rsi(
        data["Close"],
        length=14
    )

    if len(data) >= 20:

        data["SMA20"] = (
            data["Close"]
            .rolling(window=20)
            .mean()
        )

    else:

        data["SMA20"] = data["Close"]

    if len(data) >= 50:

        data["SMA50"] = (
            data["Close"]
            .rolling(window=50)
            .mean()
        )

    else:

        data["SMA50"] = data["Close"]

    return data

def calculate_conviction_score(
    rsi,
    sma20,
    sma50,
    sentiment_score
):

    if pd.isna(rsi):

        rsi = 50

    score = 0

    if sma20 > sma50:
        score += 40
    else:
        score -= 40

    if rsi < 30:
        score += 30

    elif rsi > 70:
        score -= 20

    else:
        score += 10

    if sentiment_score > 0.1:
        score += 30

    elif sentiment_score < -0.1:
        score -= 30

    return score


def classify_final_signal(score):

    if score >= 60:
        return "STRONG BUY"

    elif score >= 30:
        return "BUY"

    elif score <= -40:
        return "SELL"

    else:
        return "HOLD"
    
def scan_market(tickers):

    market_results = []

    for ticker in tickers:

        try:

            data = fetch_stock_data(
                ticker,
                period="6mo"
            )

            data = calculate_indicators(data)

            latest_rsi = data["RSI"].iloc[-1]

            if pd.isna(latest_rsi):

                latest_rsi = 50

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

            signal = classify_final_signal(
                conviction_score
            )

            market_results.append({

                "Ticker": ticker,

                "RSI": round(
                    latest_rsi,
                    2
                ),

                "Sentiment": sentiment,

                "Conviction": conviction_score,

                "Signal": signal

            })

        except Exception as e:

            print(
                f"Error scanning {ticker}: {e}"
            )

    return market_results

st.set_page_config(
    page_title="AI Market Intelligence",
    layout="wide"
)
hide_streamlit_style = """
<style>
#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}


</style>
"""

st.markdown(
    hide_streamlit_style,
    unsafe_allow_html=True
)
st_autorefresh(
    interval=30000,
    key="market_refresh"
)

tickers = load_tickers()


st.title("📈 AI Market Intelligence Dashboard")
st.subheader(
    "📊 Top Opportunities Today"
)

market_results = scan_market(
    tickers
)
market_results = sorted(
    market_results,
    key=lambda x: x["Conviction"],
    reverse=True
)
market_results = market_results[:5]
market_df = pd.DataFrame(
    market_results
)

styled_df = market_df.style.map(
    lambda x:
    "color: lime; font-weight: bold"
    if x == "BUY"
    else (
        "color: red; font-weight: bold"
        if x == "SELL"
        else (
            "color: orange; font-weight: bold"
            if x == "HOLD"
            else ""
        )
    ),
    subset=["Signal"]
)

st.dataframe(
    styled_df,
    width="stretch"
)

st.divider()

stock_df = pd.read_csv(
    "stocks.csv"
)

st.sidebar.title(
    "📊 Market Controls"
)
st.sidebar.success(
    "🟢 Market Dashboard Active"
)

selected_stock = st.sidebar.selectbox(
    "Search Stock",
    stock_df["Company"]
)
selected_period = st.sidebar.selectbox(
    "Select Timeframe",
    [
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "5y",
        "max"
    ],
    index=3 
)

chart_type = st.sidebar.selectbox(
    "Chart Type",
    [
        "Candlestick",
        "Line"
    ]
)

selected_ticker = (
    stock_df[
        stock_df["Company"] == selected_stock
    ]["Ticker"].values[0]
)


with st.spinner("Loading market data..."):

    data = fetch_stock_data(
        selected_ticker,
        period=selected_period
    )

    data = calculate_indicators(data)


if data.empty:

    st.error(
        "No stock data found."
    )

    st.stop()

latest_rsi = data["RSI"].iloc[-1]

if pd.isna(latest_rsi):

    latest_rsi = 50

latest_price = data["Close"].iloc[-1]

sma20 = data["SMA20"].iloc[-1]

sma50 = data["SMA50"].iloc[-1]

headlines = fetch_news(selected_ticker)

sentiment_score = analyze_sentiment(headlines)

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

signal = classify_final_signal(
    conviction_score
)
st.header(selected_stock)

tab1, tab2, tab3 = st.tabs(
    [
        "📊 Overview",
        "📰 Sentiment",
        "📈 Technicals"
    ]
)

with tab1:

    col1, col2, col3, col4 = st.columns(4)
    col1.metric(
        "Latest Price",
        f"{latest_price:.2f}"
    )

    col2.metric(
        "RSI",
        f"{latest_rsi:.2f}",
        delta="Bullish" if latest_rsi > 50 else "Bearish"
    )

    if signal == "STRONG BUY":

     signal_display = "🚀 STRONG BUY"

    elif signal == "BUY":

     signal_display = "🟢 BUY"

    elif signal == "SELL":

        signal_display = "🔴 SELL"

    else:

        signal_display = "🟡 HOLD"


    col3.metric(
        "Signal",
        signal_display
    )

    col4.metric(
        "Conviction Score",
        conviction_score
    )
    st.subheader("🤖 AI Signal Explanation")

    reasons = []

    if sma20 > sma50:

        reasons.append(
            "📈 SMA20 is above SMA50 (bullish trend)"
        )

    else:

        reasons.append(
            "📉 SMA20 is below SMA50 (bearish trend)"
        )

    if latest_rsi < 30:

        reasons.append(
            "🟢 RSI indicates oversold conditions"
        )

    elif latest_rsi > 70:

        reasons.append(
            "🔴 RSI indicates overbought conditions"
        )

    else:

        reasons.append(
            "🟡 RSI is in neutral range"
        )

    if sentiment_score > 0.1:

        reasons.append(
            "📰 News sentiment is positive"
        )

    elif sentiment_score < -0.1:

        reasons.append(
            "📰 News sentiment is negative"
        )

    else:

        reasons.append(
            "📰 News sentiment is neutral"
        )

    for reason in reasons:

        st.write(reason)    

with tab2:

    st.subheader("📰 AI News Sentiment")

    st.write(
        f"Overall Sentiment: {sentiment}"
    )

    for headline in headlines:

        st.write(f"- {headline}")

with tab3:

    st.divider()

    fig = go.Figure()

    if chart_type == "Candlestick":

        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data["Open"],
                high=data["High"],
                low=data["Low"],
                close=data["Close"],
                name="Candlestick"
            )
        )

    else:

        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data["Close"],
                mode="lines",
                name="Close Price"
            )
        )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["SMA20"],
            mode="lines",
            name="SMA20"
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data.index,
            y=data["SMA50"],
            mode="lines",
            name="SMA50"
        )
    )

    fig.update_layout(
        title=f"{selected_stock} ({selected_period}) Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

