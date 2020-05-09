from datetime import date, timedelta

# for retrieving stock data
# import yfinance as yf
from yahoofinancials import YahooFinancials


def set_angel_status(month_price, week_price, current_price):
    # MACRO checking for 20%drop in month or week
    if (month_price * 0.9 >= current_price) or (
        week_price * 0.9 >= current_price
    ):
        return True
    else:
        return False


# - method that returns the today in datetime object.
# - If weekend returns most recent friday. Also accounts for holidays and
# goes back to most recent open day.
# - Uses: list_holidays.txt which is a .txt file w/ all nyse holidays
# through 2022 in m/d/yyyy format w/ a '*' if it is a half day
def get_today():

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

ticker_symbol = "BRK.B"
curr_stock = YahooFinancials(ticker_symbol)

today = get_today()
lastMonth = today - timedelta(days=28)
start_date = lastMonth.strftime("%Y-%m-%d")
end_date = today.strftime("%Y-%m-%d")

try:
    historical_price_data = curr_stock.get_historical_price_data(
        start_date, end_date, "daily"
    )
except Exception:  # maybe somehow generalize exceptions
    print(ticker_symbol + "new error from getting historical data from object")
    errored = True
    return

if len(historical_price_data[ticker_symbol]) == 1:
    print("found no info, yahoo finance page empty")
    errored = True
    return
elif len(historical_price_data[ticker_symbol]["prices"]) == 0:
    print("found no info, yahoo finance page empty")
    errored = True
    return

try:
    stock_prices = historical_price_data[ticker_symbol]["prices"]
except Exception:
    print(
        ticker_symbol + "new error from retrieving prices from historical data"
    )
    errored = True
    return

# could become function that returns array of size two, month/week price

closing_prices = []
for i in range(0, len(stock_prices), 1):
    # extracts only closing price from all the object w/ dates, etc.
    closing_prices.append(stock_prices[i]["close"])
# if len isn't 5 or 6 then it didn't get a months worth of time
# assert len(closing_prices) == 5 or len(closing_prices) == 6

month_price = closing_prices[0]
week_price = closing_prices[14]
price_dict = curr_stock.get_current_price()
current_price = price_dict[ticker_symbol]
angel_status = set_angel_status()
errored = False
ticker = ticker_symbol
object = curr_stock
