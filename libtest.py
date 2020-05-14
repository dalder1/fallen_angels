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


tickers = "AAPL"

yf_object = YahooFinancials(tickers)


temp_sheet = yf_object.get_financial_stmts("quarterly", "balance")
temp2 = temp_sheet["balanceSheetHistoryQuarterly"]
temp3 = temp2[tickers]

pp = pprint.PrettyPrinter(indent=1)
pp.pprint(temp3)


exit()
