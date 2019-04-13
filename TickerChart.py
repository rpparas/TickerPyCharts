import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import sys

def getTicker():
    if len(sys.argv) == 2:
        ticker = sys.argv[1]
    else:
        ticker = requestUserInput()

    print("Please hold on while while we look that up ...")
    tickerStatus = isTickerValid(ticker)
    while tickerStatus != 1:
        print('Your entry doesn\'t appear to be a valid ticker.')
        if tickerStatus == -1:
            suggestions = suggestMatchingTickers(ticker)
            if len(suggestions) > 0:
                print(f'Here are some suggestions: {suggestions}')
        ticker = requestUserInput()
        print("Please hold on while while we look that up ...")
        tickerStatus = isTickerValid(ticker)

    return ticker


def requestUserInput():
    ticker = input("Enter a Ticker symbol: ")
    return ticker

# returns 1 if ticker is an exact match, 0 if there are no matching tickers, -1 if there are ticker suggestions
def isTickerValid(ticker):
    apiKey = 'JQKUZMZK74N9U4KY'
    requestUrl = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey=' + apiKey
    df = pd.read_json(requestUrl)
    if df.empty:
        return -1
    firstMatch = df['bestMatches'].iloc[0]['1. symbol']
    return 1 if firstMatch == ticker else 0

def suggestMatchingTickers(df):
    apiKey = 'JQKUZMZK74N9U4KY'
    requestUrl = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey=' + apiKey
    df = pd.read_json(requestUrl)
    if df.empty:
        return None
    return list(df['bestMatches']['1. symbol'])


# This function assumes that ticker has already been verified as valid, otherwise, we need to add error-checking
def requestData(ticker):
    apiKey = 'JQKUZMZK74N9U4KY'
    apiUrl = 'https://www.alphavantage.co/query?function='
    commonParam = f'&symbol={ticker}&datatype=csv&apikey=' + apiKey
    endpoints = {
        # daily opening, high, low and closing prices for a ticker
        'timeseries': {'fxn': 'TIME_SERIES_DAILY', 'x-axis': 'timestamp'},
        # 50-day moving average of prices at closing:
        'sma50': {'fxn': 'SMA&interval=daily&time_period=50&series_type=close', 'x-axis': 'time'},
        # 200-day moving average of prices at closing
        'sma200': {'fxn': 'SMA&interval=daily&time_period=200&series_type=close', 'x-axis': 'time'},
    }

    data = {}
    for name, epParams in endpoints.items():
        requestUrl = apiUrl + epParams['fxn'] + commonParam
        data[name] = pd.read_csv(requestUrl)
        data[name] = data[name].sort_values(by=[epParams['x-axis']])

    oldestDataPoint = data['timeseries'].iloc[0]['timestamp']
    data['sma50'] = data['sma50'][data['sma50'].time > oldestDataPoint]
    data['sma200'] = data['sma200'][data['sma200'].time > oldestDataPoint]

    return data


def plotChart(data):
    print("Preparing graphing library to plot chart ...")
    candlestick = go.Ohlc(x=data['timeseries']['timestamp'],
                    open=data['timeseries']['open'],
                    high=data['timeseries']['high'],
                    low=data['timeseries']['low'],
                    close=data['timeseries']['close'])
    sma50 = go.Scatter(x=data['sma50']['time'],
                    y=data['sma50']['SMA'])
    sma200 = go.Scatter(x=data['sma200']['time'],
                    y=data['sma200']['SMA'])

    data = [candlestick, sma50, sma200]
    py.plot(data, filename='ticker-chart.html')

ticker = getTicker()
data = requestData(ticker)
plotChart(data)