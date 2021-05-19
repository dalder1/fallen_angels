import bs4 as bs
import requests
import pprint

# for getting current date, needed to check stock prices
from datetime import date, timedelta

# for retrieving stock data
# import yfinance as yf
from yahoofinancials import YahooFinancials

# for writing data out to csv file for inspection
import csv


tickers = [
    ["AAPL"],
    ["V"],
    ["MMM"],
    ["GE"],
    ["TSLA"],
    ["ABT"],
]
"""
tickers.append("AAPL")
tickers.append("V")
tickers.append("MMM")
tickers.append("GE")
tickers.append("TSLA")
tickers.append("ABT")
tickers.append("MRK")
"""

apple = YahooFinancials('ABMD')
apple_info = apple.get_key_statistics_data()
print(type(apple_info))
for (key) in apple_info:
    print(key)
    print(apple_info[key])

exit()
