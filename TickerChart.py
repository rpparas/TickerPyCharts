import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import sys

class TickerChart:
    def __init__(self):
        self.ticker = ''
        self.converted = ''
        self.name = ''
        self.df = None
        self.matchingTickers = []
        self.seriesType = 'S'
        self.currency = 'USD'
        self.start = ''
        self.end = ''
        self.apiKey = 'JQKUZMZK74N9U4KY'


    def identifyType(self):
        if len(sys.argv) >= 3:
            self.seriesType = sys.argv[1]
        else:
            self.seriesType = self.askForSeriesType()

    def identifyTickers(self):
        if sys.argv[2] and self.seriesType in ['S', 'C']:
            self.ticker = sys.argv[2]
            if self.isTickerValid(self.ticker):
                return

        elif sys.argv[2] and sys.argv[3] and self.seriesType in ['F']:
            self.ticker = sys.argv[2]
            self.converted = sys.argv[3]
            if self.isTickerValid(self.ticker) and self.isTickerValid(self.converted):
                return

        self.ticker = self.askForTickerSymbol(self.seriesType)
        if self.seriesType in ['F']:
            self.converted = self.askForTickerSymbol(f'{self.seriesType}2')


    def askForSeriesType(self):
        while True:
            seriesType = input("Enter [S] for Stocks, [F] for Foreign Exchange Rates, [C] for Cryptocurrency Prices: ").strip().upper()
            if seriesType in ['S', 'F', 'C']:
                return seriesType

    def askForTickerSymbol(self, key):
        label = {
            'S': 'Ticker symbol (e.g.  GOOGL)',
            'F': 'Physical or Digital currency you\'re converting FROM (e.g. USD)',
            'F2': 'Physical or Digital currency you\'re converting TO (e.g. BTC)',
            'C': 'Ticker for digital currency (e.g. ETH)',
        }

        ticker = input(f"Enter a {label[key]}: ")
        tickerStatus = self.isTickerValid(ticker)
        if tickerStatus == 1:
            return ticker
        else:
            print('Your input doesn\'t appear to be a valid ticker.')
            if tickerStatus == -1 and len(self.getMatchingTickers()) > 0:
                print(f'Here are some suggestions: {suggestions}')

            return self.askForTickerSymbol(key)

    # returns 1 if ticker is an exact match, 0 if there are no matching tickers, -1 if there are ticker suggestions
    def isTickerValid(self, ticker):
        print("Please hold on while we look that up ...")

        ticker = ticker.strip().upper()
        if self.seriesType == "S": # make sure that the ticker corresponds to a valid stock:
            requestUrl = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey=' + self.apiKey
            df = pd.read_json(requestUrl)
            if df.empty:
                return -1
            firstMatch = df['bestMatches'].iloc[0]['1. symbol']
            if firstMatch == ticker:
                self.name = df['bestMatches'].iloc[0]['2. name']
                self.df = df
                return 1
            else:
                return 0

        else: # handle all physical and digital currencies by checking against the lists we have
            df = pd.read_csv('resources/digital_currency_list.csv')
            if any(df['currency code'] == ticker):
                self.seriesType = 'C'
                return 1

            df = pd.read_csv('resources/physical_currency_list.csv')
            if any(df['currency code'] == ticker):
                self.seriesType = 'F'
                return 1

            return 0


    def getMatchingTickers(self):
        if self.df and self.df.empty:
            return []
        else:
            self.matchingTickers = list(self.df['bestMatches']['1. symbol'])
            return self.matchingTickers

    # This function assumes that ticker has already been verified as valid, otherwise, we need to add error-checking
    def requestData(self):
        print("Requesting data from server (this may take a while) ...")

        apiUrl = 'https://www.alphavantage.co/query?function='
        commonParam = f'&symbol={self.ticker}&datatype=csv&apikey=' + self.apiKey

        endpoints = {}
        if self.seriesType in ['S']:
            # daily opening, high, low and closing prices for a stock ticker
            endpoints['timeseries'] = {'fxn': f'TIME_SERIES_DAILY', 'x-axis': 'timestamp'}

            # 50-day moving average of prices at closing:
            endpoints['sma50'] = {'fxn': 'SMA&interval=daily&time_period=50&series_type=close', 'x-axis': 'time'}

            # 200-day moving average of prices at closing
            endpoints['sma200'] = {'fxn': 'SMA&interval=daily&time_period=200&series_type=close', 'x-axis': 'time'}

        elif self.seriesType in ['F']:
            endpoints['timeseries'] = {'fxn': f'FX_DAILY&from_symbol={self.ticker}&to_symbol={self.converted}', 'x-axis': 'timestamp'}
        elif self.seriesType in ['C']:
            endpoints['timeseries'] = {'fxn': 'DIGITAL_CURRENCY_DAILY&market=USD', 'x-axis': 'timestamp'}

        data = {}
        for name, epParams in endpoints.items():
            print(f'  Downloading {name} ... ')
            requestUrl = apiUrl + epParams['fxn'] + commonParam
            print(requestUrl)
            data[name] = pd.read_csv(requestUrl)
            data[name] = data[name].sort_values(by=[epParams['x-axis']])

        self.start = data['timeseries'].iloc[0]['timestamp']
        self.end = data['timeseries'].iloc[-1]['timestamp']

        print(f'  Cleaning up data ... ')
        if 'sma50' in endpoints:
            data['sma50'] = data['sma50'][data['sma50'].time > self.start]
        if 'sma200' in endpoints:
            data['sma200'] = data['sma200'][data['sma200'].time > self.start]

        return data


    def plotChart(self, data):
        print(f'Preparing graphing library to plot chart for {self.ticker} ...')
        seriesLabels = {
            'S': 'Stock Prices',
            'F': 'Forex Exchange Rate',
            'C': 'Cryptocurrency Spot Prices',
        }
        candlestick = go.Ohlc(x=data['timeseries']['timestamp'],
                        open=data['timeseries']['open'],
                        high=data['timeseries']['high'],
                        low=data['timeseries']['low'],
                        close=data['timeseries']['close'],
                        name=seriesLabels[self.seriesType]
                    )
        data = [candlestick]

        if 'sma50' in data:
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
            data.append(sma50)

        if 'sma200' in data:
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
            data.append(sma200)

        fig = go.Figure(data=data, layout=self.getLayoutParams())
        py.plot(fig, filename='ticker-chart.html')

    def getLayoutParams(self):
        titles = {
            'S': f' Time Series for {self.ticker}<br>{self.name}',
            'F': f' {self.ticker} to {self.converted} Exchange Rate',
            'C': f' {self.ticker} Cryptocurrency Spot Prices',
        }
        if self.seriesType in ['S', 'C']:
            yAxisLabel = self.currency
        else:
            yAxisLabel = f'{self.ticker} to {self.converted}'

        layout = go.Layout(
            title=go.layout.Title(
                text=titles[self.seriesType],
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
                    text=yAxisLabel,
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
tc.identifyType()
tc.identifyTickers()
data = tc.requestData()
tc.plotChart(data)