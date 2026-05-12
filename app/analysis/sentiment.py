import feedparser

from textblob import TextBlob


def fetch_news(ticker):

    rss_url = (
        f"https://news.google.com/rss/search?q={ticker}+stock"
    )

    feed = feedparser.parse(rss_url)

    headlines = []

    for entry in feed.entries[:5]:

        headlines.append(entry.title)

    return headlines


def analyze_sentiment(headlines):

    sentiment_scores = []

    for headline in headlines:

        analysis = TextBlob(headline)

        polarity = analysis.sentiment.polarity

        sentiment_scores.append(polarity)

    average_score = (
        sum(sentiment_scores)
        / len(sentiment_scores)
    )

    return average_score


def classify_sentiment(score):

    if score > 0.1:
        return "Positive"

    elif score < -0.1:
        return "Negative"

    else:
        return "Neutral"


if __name__ == "__main__":

    ticker = "RELIANCE.NS"

    headlines = fetch_news(ticker)

    print("\nLatest Headlines:\n")

    for headline in headlines:
        print("-", headline)

    sentiment_score = analyze_sentiment(headlines)

    sentiment = classify_sentiment(sentiment_score)

    print(f"\nSentiment Score: {sentiment_score:.2f}")

    print(f"Overall Sentiment: {sentiment}")