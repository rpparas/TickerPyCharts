import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd

def requestData():
    apiKey = 'JQKUZMZK74N9U4KY'
    apiUrl = 'https://www.alphavantage.co/query?function='
    commonParam = '&symbol=MSFT&datatype=csv&apikey=' + apiKey
    endpoints = {
        # daily opening, high, low and closing prices for a ticker
        'timeseries': {'fxn': 'TIME_SERIES_DAILY', 'x-axis': 'timestamp'},
        # 50-day moving average of prices at closing:
        'sma50': {'fxn': 'SMA&interval=daily&time_period=50&series_type=close', 'x-axis': 'time'},
    }

    data = {}
    for name, epParams in endpoints.items():
        requestUrl = apiUrl + epParams['fxn'] + commonParam
        data[name] = pd.read_csv(requestUrl)
        data[name].sort_values(by=[epParams['x-axis']])

    return data


def plotChart(data):
    candlestick = go.Ohlc(x=data['timeseries']['timestamp'],
                    open=data['timeseries']['open'],
                    high=data['timeseries']['high'],
                    low=data['timeseries']['low'],
                    close=data['timeseries']['close'])
    sma50 = go.Scatter(x=data['sma50']['time'],
                    y=data['sma50']['SMA'])

    data = [candlestick, sma50]
    py.plot(data, filename='simple_candlestick.html')


data = requestData()
plotChart(data)