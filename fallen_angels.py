# -----------------------------------------------------------
# Identifies fallen angels stocks worthy of investment
#
# Created: 12/23/2019
# Last Editied: 12/23/2019
# Author: Daniel Alderman
# Email: daniel.alderman@tufts.edu
# -----------------------------------------------------------


# to scrape wikipedia for tickers
import bs4 as bs
import requests

# for getting current date, needed to check stock prices
from datetime import date, timedelta

# for retrieving stock data
# import yfinance as yf
from yahoofinancials import YahooFinancials

# for writing data out to csv file for inspection
import csv

# Class for each individual stock gotten from yahoofinance library
# Functions: Constructor,
# Attributes:
#           -errored: boolean if there was an error retrieving some data
#           -current_price: close price of most recent trading day
#           -current_date: date of current_price in string
#           -month_price: closing price from 28 days ago (wknd adj.)
#           -month_date: date of month_price in string
#           -week_price: closing price from 5 days ago (wknd adj.)
#           -week_date: date of week_price in string
#           -angel_status: boolean if it passess current criteria for an angel
#           -error_message: string with error message if errored is true
#           -ticker: string with ticker of stock info stored in this instance
#
class Stock:

    # method that returns true or false depending on if current price is
    # less than a factor of week and month prices
    def set_angel_status(self):

        # MACRO checking for 20%drop in month or week
        loss_factor = 0.8

        adj_week_price = self.month_price * loss_factor
        adj_month_price = self.week_price * loss_factor

        if (adj_week_price >= self.current_price) or (
            adj_month_price >= self.current_price
        ):
            return True
        else:
            return False

    # method that returns true or false depending on if current price is
    # less than a factor of week and month prices
    def get_extra_info(self, curr_stock):
        temp_data = curr_stock.get_key_statistics_data()
        ticker_symbol = curr_stock.ticker[0]  # for some rzn its list of len 1
        key_data = temp_data[ticker_symbol]
        self.test_pe = curr_stock.get_pe_ratio()
        self.price_book = key_data["priceToBook"]
        income = key_data["netIncomeToCommon"]
        shares = key_data["sharesOutstanding"]
        eps = income / shares
        self.price_earnings = self.current_price / eps

        temp_sheet = curr_stock.get_financial_stmts("quarterly", "balance")
        temp2 = temp_sheet["balanceSheetHistoryQuarterly"]
        temp3 = temp2[ticker_symbol]
        temp4 = temp3[0]
        for key in temp4:
            balance_sheet = temp4[key]
        temp_finance_data = curr_stock.get_financial_data()
        finance_data = temp_finance_data[ticker_symbol]
        self.current_ratio = finance_data["currentRatio"]
        assets = balance_sheet["totalCurrentAssets"]
        debt = finance_data["totalDebt"]
        self.debt_to_assets = assets / debt

    # Description: constructor that makes calls to yahoofinance library to
    #             populate stocks attributes
    # Parameters: curr_stock-yahoofinance object; ticker_symbol-string of ticker
    #
    def __init__(self, curr_stock, ticker_symbol, start_date, end_date):

        try:
            # retrieving dict with all historical price data for this stock
            historical_price_data = curr_stock.get_historical_price_data(
                start_date, end_date, "daily"
            )
        except Exception:
            self.errored = True
            # use error_message to store error message
            self.error_message = "E: getting historical date from object"
            return

        if len(historical_price_data[ticker_symbol]) == 1:
            self.error_message = (
                "E: price data returned 1 field yf page empty",
            )
            self.errored = True
            return
        elif len(historical_price_data[ticker_symbol]["prices"]) == 0:
            self.error_message = "E: no prices returned, yf page empty"
            self.errored = True
            return

        try:
            # getting the prices and associated info from the dict
            stock_prices = historical_price_data[ticker_symbol]["prices"]
        except Exception:
            self.error_message = "E: retrieving prices from array"
            self.errored = True
            return

        closing_prices = []
        closing_dates = []
        for i in range(0, len(stock_prices), 1):
            # extracts only closing price and date from all the objects.
            closing_prices.append(stock_prices[i]["close"])
            closing_dates.append(stock_prices[i]["formatted_date"])

        self.month_price = closing_prices[0]
        self.month_date = closing_dates[0]
        self.week_price = closing_prices[14]
        self.week_date = closing_dates[14]
        self.current_price = closing_prices[19]
        self.current_date = closing_dates[19]
        self.ticker = ticker_symbol
        self.angel_status = self.set_angel_status()
        if self.angel_status == True:
            self.get_extra_info(curr_stock)
        self.errored = False


# method that makes api call to tiingo to retrieve price close for
# for today and one month ago today. Returns an object that contains
# these prices and the ticker name, as well as the entire json file
def retrieve_stock_info(ticker_name, errored_tickers, start_date, end_date):

    # stock object we will return
    curr_stock = None

    try:

        # call to library to get object
        yf_object = YahooFinancials(ticker_name)
    except Exception:
        print(ticker_name + "new error from getting object from library")
        return None

    curr_stock = Stock(yf_object, ticker_name, start_date, end_date)
    assert curr_stock != None
    return curr_stock


# - method that returns the most reecent open market day in datetime object.
# - If weekend returns most recent friday. Also accounts for holidays and
# goes back to most recent open day.
# - Uses: list_holidays.txt which is a .txt file w/ all nyse holidays
# through 2022 in m/d/yyyy format w/ a '*' if it is a half day
def get_today():

    today = date.today()
    if today.strftime("%y") > "21":
        print("WARNING, NYSE holidays no longer accounted for after 2021")

    # creating hash tables to store all nyse holidays
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


# method that scrapes tickers of every s%p 500 stock and adds them to a list
# this method is based off a script described by sentdex in a youtube tutorial
# Return:  list of strings
#
def sp500_tickers(errored_tickers):
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
        ticker = ticker.rstrip("\n")
        # if we already know it errors do not add it to the list of tickers
        if ticker in errored_tickers:
            continue
        tickers.append(ticker)
    return tickers


#
#
# Main Function
#
#


# stores all stocks that we could not find pull yfinance data for
errored_tickers = dict()
# stocks known to error
errored_tickers["BF.B"] = True
errored_tickers["BRK.B"] = True

# fills tickers list with every stock symbol in s&p 500
tickers = sp500_tickers(errored_tickers)
# stores all stocks that we could not find pull yfinance data for

# stores all stocks we find that match our criteria for a 'fallen angel'.
angels = []

# filename for data analysis
filename = "stock-stats.csv"
# header for columns in csv sheet
headers = [
    "Stock Name",
    "Month Price",
    "Month Date",
    "Week Price",
    "Week Date",
    "Current Price",
    "Current Date",
    "Current Date",
    "Angel Status",
    "P/E Ratio",
    "Price to Book",
    "Current Ratio",
    "Debt to Current Assets",
]
# list to store all lists of each stock data
rows = []

today = get_today()
start_date = (today - timedelta(days=28)).strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

for i in range(len(tickers)):  # for limit with requests
    temp_symbol = tickers[i]
    curr_stock = retrieve_stock_info(
        temp_symbol, errored_tickers, start_date, end_date
    )
    if i % 50 == 0:
        print(str(i / 5) + "% done")
    # if returned None then the function errored at a certain try block
    if curr_stock.errored == True:
        errored_tickers[temp_symbol] = True
        curr_row = [temp_symbol, "ERRORED", curr_stock.error_message]
        rows.append(curr_row)
        continue

    curr_row = [
        curr_stock.ticker,
        curr_stock.month_price,
        curr_stock.month_date,
        curr_stock.week_price,
        curr_stock.week_date,
        curr_stock.current_price,
        curr_stock.current_date,
        curr_stock.angel_status,
    ]

    if curr_stock.angel_status == True:
        angels.append(curr_stock)
        curr_row.append(curr_stock.price_earnings)
        curr_row.append(curr_stock.price_book)
        curr_row.append(curr_stock.current_ratio)
        curr_row.append(curr_stock.debt_to_assets)

    rows.append(curr_row)

print("\n These were not tracked due to ERRORS:")
for key in errored_tickers:
    print(key)

print("\n These are the angels:")
for stock in angels:
    print(stock.ticker)

with open(filename, "w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(headers)
    csvwriter.writerows(rows)
