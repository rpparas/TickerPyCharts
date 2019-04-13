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
        if len(sys.argv) >= 3 and sys.argv[1].strip().upper() in ['S', 'F', 'C']:
            self.seriesType = sys.argv[1].strip().upper()
            return

        self.seriesType = self.askForSeriesType()

    def identifyTickers(self):
        if len(sys.argv) >= 3 and sys.argv[2] and self.seriesType in ['S', 'C']:
            self.ticker = sys.argv[2]
            if self.validateTicker(self.ticker) == 1:
                return

        elif len(sys.argv) >= 4 and sys.argv[2] and sys.argv[3] and self.seriesType in ['F']:
            self.ticker = sys.argv[2]
            self.converted = sys.argv[3]

            if self.validateTicker(self.ticker) == -2:
                print('Your second ticker is the same as the first one.')
                self.ticker = ''
                self.converted = ''
            elif self.validateTicker(self.ticker) == -3:
                print('Your first ticker is not considered a physical currency.')
            elif self.validateTicker(self.converted) == -3:
                print('Your second ticker is not considered a physical currency.')
            elif self.validateTicker(self.ticker) == 1:
                if self.validateTicker(self.converted) == 1:
                    return
                elif self.validateTicker(self.converted) == -2:

                    self.converted = self.askForTickerSymbol(f'{self.seriesType}2')

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

        ticker = input(f"Enter a {label[key]}: ").strip().upper()
        tickerStatus = self.validateTicker(ticker)
        if tickerStatus == 1:
            return ticker
        elif tickerStatus == -2:
            print('Your second ticker is the same as the first one. Please enter a different one.')
        else:
            print('Your input doesn\'t appear to be a valid ticker.')
            if len(self.getMatchingTickers()) > 0:
                print(f'Here are some suggestions: {suggestions}')

        return self.askForTickerSymbol(key)

    # returns 1 if ticker is an exact match, 0 if there are no matching tickers, -1 if there are ticker suggestions
    def validateTicker(self, ticker):
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
            if self.ticker == self.converted and self.converted != '':
                return -2

            if self.seriesType == 'C':
                df = pd.read_csv('resources/digital_currency_list.csv')
                if any(df['currency code'] == ticker):
                    self.name = df.loc[df['currency code'] == ticker, 'currency name'].iloc[0]
                    return 1
                else:
                    return -3

            if self.seriesType == 'F':
                df = pd.read_csv('resources/physical_currency_list.csv')
                if any(df['currency code'] == ticker):
                    return 1
                else:
                    return -3

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
            # print(requestUrl)
            data[name] = pd.read_csv(requestUrl)
            data[name] = data[name].sort_values(by=[epParams['x-axis']])

        self.start = data['timeseries'].iloc[0]['timestamp']
        self.end = data['timeseries'].iloc[-1]['timestamp']


        # rename column names to make them consistent
        if self.seriesType == 'C':
            data['timeseries'] = data['timeseries'].rename(columns = {"open (USD)": "open",
                                                                            "high (USD)": "high",
                                                                            "low (USD)": "low",
                                                                            "close (USD)": "close"
                                                                        }
                                                                    )

        print(f'  Cleaning up data ... ')
        if 'sma50' in endpoints:
            data['sma50'] = data['sma50'][data['sma50'].time > self.start]
        if 'sma200' in endpoints:
            data['sma200'] = data['sma200'][data['sma200'].time > self.start]

        return data


    def plotChart(self, data):
        if self.seriesType in ['S', 'C']:
            print(f'Preparing graphing library to plot chart for {self.ticker} ...')
        else:
            print(f'Preparing graphing library to plot chart for {self.ticker} to {self.converted} ...')

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
        chartData = [candlestick]

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
            chartData.append(sma50)

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
            chartData.append(sma200)

        fig = go.Figure(data=chartData, layout=self.getLayoutParams())
        py.plot(fig, filename='ticker-chart.html')

    def getLayoutParams(self):
        titles = {
            'S': f' Time Series for {self.ticker}<br>{self.name}',
            'F': f' {self.ticker} to {self.converted} Exchange Rate',
            'C': f' {self.ticker} Cryptocurrency Spot Prices<br>{self.name} in USD (default)',
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