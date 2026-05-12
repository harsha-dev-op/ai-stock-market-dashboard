import yfinance as yf

stock = yf.Ticker("RELIANCE.NS")

data = stock.history(period="5d")

print(data)