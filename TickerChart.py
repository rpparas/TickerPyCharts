import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import sys

class TickerChart:
    def __init__(self):
        self.ticker = ''
        self.name = ''
        self.df = None
        self.matchingTickers = []
        self.seriesType = 'Stock Prices'
        self.currency = 'USD'
        self.start = ''
        self.end = ''
        self.apiKey = 'JQKUZMZK74N9U4KY'


    def getTicker(self):
        if len(sys.argv) == 3:
            seriesType = sys.argv[1]
            ticker = sys.argv[2]
        else:
            # TO-DO: ask for ticker type first (stock, forex, crypto)
            ticker = self.requestUserInput()

        tickerStatus = self.isTickerValid(ticker)
        while tickerStatus != 1:
            print('Your input doesn\'t appear to be a valid ticker.')
            if tickerStatus == -1 and len(self.getMatchingTickers()) > 0:
                print(f'Here are some suggestions: {suggestions}')

            ticker = self.requestUserInput()
            tickerStatus = self.isTickerValid(ticker)

        return ticker


    def requestUserInput(self):
        return input("Enter a Ticker symbol: ")

    # returns 1 if ticker is an exact match, 0 if there are no matching tickers, -1 if there are ticker suggestions
    def isTickerValid(self, ticker):
        print("Please hold on while we look that up ...")

        ticker = ticker.strip().upper()
        requestUrl = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey=' + self.apiKey
        df = pd.read_json(requestUrl)
        if df.empty:
            return -1
        firstMatch = df['bestMatches'].iloc[0]['1. symbol']
        if firstMatch == ticker:
            self.ticker = ticker
            self.name = df['bestMatches'].iloc[0]['2. name']
            self.df = df
            return 1
        else:
            return 0

    def getMatchingTickers(self):
        if self.df and self.df.empty:
            return []
        else:
            self.matchingTickers = list(self.df['bestMatches']['1. symbol'])
            return self.matchingTickers

    # This function assumes that ticker has already been verified as valid, otherwise, we need to add error-checking
    def requestData(self, ticker):
        print("Requesting data from server (this may take a while) ...")
        apiUrl = 'https://www.alphavantage.co/query?function='
        commonParam = f'&symbol={ticker}&datatype=csv&apikey=' + self.apiKey
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
            print(f'  Downloading {name} ... ')
            requestUrl = apiUrl + epParams['fxn'] + commonParam
            data[name] = pd.read_csv(requestUrl)
            data[name] = data[name].sort_values(by=[epParams['x-axis']])

        self.start = data['timeseries'].iloc[0]['timestamp']
        self.end = data['timeseries'].iloc[-1]['timestamp']
        data['sma50'] = data['sma50'][data['sma50'].time > self.start]
        data['sma200'] = data['sma200'][data['sma200'].time > self.start]

        return data


    def plotChart(self, data):
        print(f'Preparing graphing library to plot chart for {self.ticker} ...')
        candlestick = go.Ohlc(x=data['timeseries']['timestamp'],
                        open=data['timeseries']['open'],
                        high=data['timeseries']['high'],
                        low=data['timeseries']['low'],
                        close=data['timeseries']['close'],
                        name=self.seriesType)
        sma50 = go.Scatter(x=data['sma50']['time'],
                        y=data['sma50']['SMA'],
                        name='50-day MA',
                        marker = dict(
                                size = 10,
                                color = 'rgba(128, 0, 0, .9)',
                                line = dict(
                                    width = 2,
                                    color = 'rgb(128, 0, 0)',
                                )
                            )
                        )
        sma200 = go.Scatter(x=data['sma200']['time'],
                        y=data['sma200']['SMA'],
                        name='200-day MA',
                        marker = dict(
                                size = 10,
                                color = 'rgba(0, 0, 255, .8)',
                                line = dict(
                                    width = 2,
                                    color = 'rgb(0, 0, 255)'
                                )
                            )
                        )

        data = [candlestick, sma50, sma200]
        fig = go.Figure(data=data, layout=self.getLayoutParams())
        py.plot(fig, filename='ticker-chart.html')

    def getLayoutParams(self):
        layout = go.Layout(
            title=go.layout.Title(
                text=f' Time Series for {self.ticker}<br>{self.name}',
                xref='paper',
                font=dict(family="Verdana", size=25)
            ),
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text=f'Period',
                    font=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                )
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text=self.currency,
                    font=dict(
                        family='Courier New, monospace',
                        size=18,
                        color='#7f7f7f'
                    )
                )
            )
        )
        return layout


tc = TickerChart()
ticker = tc.getTicker()
data = tc.requestData(ticker)
tc.plotChart(data)