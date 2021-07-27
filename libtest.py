import bs4 as bs
import requests
import pprint
import time

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

resp = requests.get(
    "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
)
soup = bs.BeautifulSoup(resp.text, "lxml")
table = soup.find("table", {"class": "wikitable sortable"})
tickers = []
errored_tickers = dict()
# stocks known to error
errored_tickers["BF.B"] = True
errored_tickers["BRK.B"] = True
# isolate each ticker and then add it to list
for row in table.findAll("tr")[1:]:
    ticker = row.findAll("td")[0].text
    ticker = ticker.rstrip("\n")
    # if we already know it errors do not add it to the list of tickers
    if ticker in errored_tickers:
        continue
    tickers.append(ticker)
    if len(tickers) >= 50:
        break
print("doodle")
start2 = time.perf_counter()
for ticker in tickers:
    yf_object = YahooFinancials(ticker)
    yf_object.get_key_statistics_data()
end2 = time.perf_counter()
print("doodle2")
start1 = time.perf_counter()
yf_object = YahooFinancials(tickers)
yf_object.get_key_statistics_data()
end1 = time.perf_counter()

print("multi call was ", (end1-start1), " seconds. Loop on single was ", (end2-start2), " seconds.")

# apple = YahooFinancials('ABMD')
# apple_info = apple.get_financial_stmts('annual', 'balance')
# test = apple.get_financial_data()
# test2 = apple.get_key_statistics_data()
# print(test2)
# # print(test)
# sheet = apple.get_financial_stmts('annual', 'balance')
# balance_sheet = sheet["balanceSheetHistory"]
# stock_sheet = balance_sheet["ABMD"]
# keys = list(stock_sheet[0].keys())
# assert len(keys) == 1
# key = keys[0]
# balanceSheetHistory = (stock_sheet[0])[key]

# currentLiabilities = balanceSheetHistory["totalCurrentLiabilities"]
# currentAssets = balanceSheetHistory["totalCurrentAssets"]
# current_ratio = currentAssets / currentLiabilities
# print("\n")
# print(current_ratio)
# print(balanceSheetHistory["totalAssets"])
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
