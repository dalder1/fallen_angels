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
# apple_info = apple.get_financial_stmts('annual', 'balance')
test = apple.get_financial_data()
test2 = apple.get_key_statistics_data()
print(test2)
# print(test)
sheet = apple.get_financial_stmts('annual', 'balance')
balance_sheet = sheet["balanceSheetHistory"]
stock_sheet = balance_sheet["ABMD"]
keys = list(stock_sheet[0].keys())
assert len(keys) == 1
key = keys[0]
balanceSheetHistory = (stock_sheet[0])[key]

currentLiabilities = balanceSheetHistory["totalCurrentLiabilities"]
currentAssets = balanceSheetHistory["totalCurrentAssets"]
current_ratio = currentAssets / currentLiabilities
print("\n")
print(current_ratio)
print(balanceSheetHistory["totalAssets"])
# sheet = apple_info["balanceSheetHistory"]
# newSheet = sheet["ABMD"]
# pp = pprint.PrettyPrinter(indent=4)
# keys = list(newSheet[0].keys())
# #print(len(keys))
# assert len(keys) == 1
# key = keys[0]
# history = (newSheet[0])[key]
# pp.pprint(apple_info)

# #pp.pprint(newSheet)


exit()
