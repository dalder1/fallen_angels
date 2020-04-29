# -----------------------------------------------------------
# Identifies fallen angels stocks worthy of investment
#
# Created: 12/23/2019
# Last Editied: 12/23/2019
# Author: Daniel Alderman
# email daniel.alderman@tufts.edu
# -----------------------------------------------------------

# ------------------------------------------------------------
# MACRO checking for 20%drop in month or week
# ------------------------------------------------------------

# to scrape wikipedia for tickers
import bs4 as bs
import requests

# for getting current date, needed to check stock prices
from datetime import date, timedelta

# for retrieving stock data
# import yfinance as yf
from yahoofinancials import YahooFinancials

# Class for each individual stock gotten from yahoofinance library
# Functions: Constructor,
# Attributes:
#           -errored: boolean if there was an error retrieving some data
#           -current_price: current price as float unrounded
#           -month_price: from mon 4 wks ago not counting current wk(exc. Fri)
#           -week_price: from mon 1 wk ago not counting current wk(exc.Fri)
#           -angel status: boolean if it passess current criteria for an angel
#
class Stock:

    # method that returns true or false depending on if week and month
    # prices work
    def set_angel_status(self):
        # MACRO checking for 20%drop in month or week
        if (self.month_price * 0.9 >= self.current_price) or (
            self.week_price * 0.9 >= self.current_price
        ):
            return True
        else:
            return False

    # - method that returns the today in datetime object.
    # - If weekend returns most recent friday. Also accounts for holidays and
    # goes back to most recent open day.
    # - Uses: list_holidays.txt which is a .txt file w/ all nyse holidays
    # through 2022 in m/d/yyyy format w/ a '*' if it is a half day
    def get_today(self):

        today = date.today()
        if today.strftime("%y") > "21":
            print("WARNING, NYSE holidays no longer accounted for after 2021")

        holidays = dict()
        earlyday = dict()
        with open("list_holidays.txt") as openFile:
            for line in openFile:
                curr_date = openFile.readline()
                curr_date = curr_date.rstrip("\n")
                if curr_date[len(curr_date) - 1] == "*":
                    curr_date = curr_date[:-1]
                    earlyday[curr_date] = True
                else:
                    holidays[curr_date] = True

        today_str = today.strftime("%m/%e/%Y").lstrip("0").replace(" ", "")
        if today_str in holidays:
            today = today - timedelta(days=1)

        if today.strftime("%w") > "5":
            days_off = today.weekday() - 4
            today = today - timedelta(days=days_off)

        # deal with if in current open market. perhaps calls already account.
        return today

    # Description: constructor that makes calls from yahoofinance object to
    #             populate stocks attributes.
    # Parameters: curr_stock-yahoofinance object; ticker_symbol-string of ticker
    #
    def __init__(self, curr_stock, ticker_symbol):

        today = self.get_today()
        lastMonth = today - timedelta(days=28)
        start_date = lastMonth.strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")

        try:
            historical_price_data = curr_stock.get_historical_price_data(
                start_date, end_date, "daily"
            )
        except Exception:  # maybe somehow generalize exceptions
            print(
                ticker_symbol
                + "new error from getting historical data from object"
            )
            self.errored = True
            return

        if len(historical_price_data[ticker_symbol]) == 1:
            print("found no info, yahoo finance page empty")
            self.errored = True
            return
        elif len(historical_price_data[ticker_symbol]["prices"]) == 0:
            print("found no info, yahoo finance page empty")
            self.errored = True
            return

        try:
            stock_prices = historical_price_data[ticker_symbol]["prices"]
        except Exception:
            print(
                ticker_symbol
                + "new error from retrieving prices from historical data"
            )
            self.errored = True
            return

        # could become function that returns array of size two, month/week price

        closing_prices = []
        for i in range(0, len(stock_prices), 1):
            # extracts only closing price from all the object w/ dates, etc.
            closing_prices.append(stock_prices[i]["close"])
        # if len isn't 5 or 6 then it didn't get a months worth of time
        # assert len(closing_prices) == 5 or len(closing_prices) == 6

        self.month_price = closing_prices[0]
        self.week_price = closing_prices[14]
        price_dict = curr_stock.get_current_price()
        self.current_price = price_dict[ticker_symbol]
        self.angel_status = self.set_angel_status()
        self.errored = False
        self.ticker = ticker_symbol
        self.object = curr_stock

    # Function called to get more info after we know it's an angel
    # def_get_advanced_info


# method that scrapes tickers of every s%p 500 stock and adds them to a list
# this method is based off a script described by sentdex in a youtube tutorial
# Return:  list of strings
#
def sp500_tickers():
    # opening wikipedia article to be scraped
    resp = requests.get(
        "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    )
    soup = bs.BeautifulSoup(resp.text, "lxml")
    table = soup.find("table", {"class": "wikitable sortable"})
    tickers = []
    # isolate each ticker and then add it to list
    for row in table.findAll("tr")[1:]:
        ticker = row.findAll("td")[0].text
        tickers.append(ticker)
    return tickers


# method that makes api call to tiingo to retrieve price close for
# for today and one month ago today. Returns an object that contains
# these prices and the ticker name, as well as the entire json file
def retrieve_stock_info(ticker_name, errored_tickers):

    # stock object we will return
    curr_stock = None
    # call to library to get object
    try:
        yf_object = YahooFinancials(ticker_name)
    except Exception:
        print(ticker_name + "new error from getting object from library")
        return None

    curr_stock = Stock(yf_object, ticker_name)

    if curr_stock.errored == True:
        return None
    return curr_stock


#
#
# Main Function
#
#

# fills tickers list with every stock symbol in s&p 500
tickers = sp500_tickers()
# stores all stocks that we could not find pull yfinance data for
errored_tickers = []
# stores all stocks we find that match our criteria for a 'fallen angel'.
angels = []

for i in range(len(tickers)):  # for limit with requests
    temp_symbol = tickers[i].rstrip("\n")
    curr_stock = retrieve_stock_info(temp_symbol, errored_tickers)
    print("got number " + str(i) + " " + temp_symbol)
    # if returned None then the function errored at a certain try block
    if curr_stock == None:
        errored_tickers.append(temp_symbol)
        continue
    # add it to our list of angels
    elif curr_stock.angel_status == True:
        angels.append(curr_stock)

print("\n These are the angels:")
for stock in angels:
    print(stock.ticker)
