import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import sys
import json, urllib.request

class TickerChart:
    def __init__(self):
        self.ticker = ''
        self.converted = ''
        self.name = 'Not Available'
        self.df = None
        self.seriesType = 'S'
        self.currency = 'USD'
        self.matchingTickers = []
        self.start = ''
        self.end = ''
        self.apiKey = 'JQKUZMZK74N9U4KY'
        self.shouldOutputToConsole = True

    def setTickers(ticker, converted = ''):
        self.ticker = ticker
        self.converted = converted

    def setSeriesType(seriesType):
        self.seriesType = seriesType

    def enableConsoleOutput(shouldOutputToConsole):
        self.shouldOutputToConsole = shouldOutputToConsole


    def identifyType(self):
        if len(sys.argv) >= 2 and sys.argv[1].strip().upper() in ['S', 'F', 'C']:
            self.seriesType = sys.argv[1].strip().upper()
            return

        self.seriesType = self.askForSeriesType()

    def identifyTickers(self):
        if self.shouldOutputToConsole:
            print('Please wait while we validate your inputs.')

        if len(sys.argv) >= 3 and self.seriesType in ['S', 'C']:
            self.ticker = sys.argv[2]
            if self.validateTicker(self.ticker) == 1:
                return

        if len(sys.argv) >= 4 and self.seriesType in ['F']:
            if len(sys.argv) >= 3:
                self.ticker = sys.argv[2].strip().upper()
                if self.validateTicker(self.ticker) == 1:
                    if len(sys.argv) >= 4:
                        self.converted = sys.argv[3].strip().upper()
                        if self.validateTicker(self.converted) == 1:
                            return
                        elif self.validateTicker(self.converted) == -2:
                            print('Your second ticker is the same as the first one.')
                            self.ticker = ''
                            self.converted = ''
                        elif self.validateTicker(self.converted) == -3:
                            print('Your second ticker doesn\'t look like a physical currency.')
                            self.converted = self.askForTickerSymbol(f'{self.seriesType}2')
                            return

                elif self.validateTicker(self.ticker) == -3:
                    print('Your first ticker doesn\'t look like physical currency.')

        self.ticker = self.askForTickerSymbol(self.seriesType)
        if self.seriesType in ['F']:
            self.converted = self.askForTickerSymbol(f'{self.seriesType}2')


    def askForSeriesType(self):
        while True:
            prompt = 'Enter [S] for Stocks, [F] for Foreign Exchange Rates, [C] for Cryptocurrency Prices: '
            try:
                seriesType = input(prompt).strip().upper()
            except KeyboardInterrupt:
                self.displayStatus(-1)

            if seriesType in ['S', 'F', 'C']:
                return seriesType

    def askForTickerSymbol(self, key):
        label = {
            'S': 'Ticker symbol for stock (e.g. GOOGL)',
            'F': 'Physical currency you\'re converting FROM (e.g. USD)',
            'F2': 'Physical currency you\'re converting TO (e.g. EUR)',
            'C': 'Ticker for digital currency (e.g. ETH)',
        }

        try:
            if key == 'S' and len(self.getMatchingTickers()) > 0:
                print(f'We can\'t an exact match for that ticker.\nPerhaps you meant: {self.getMatchingTickers()}')
            ticker = input(f'  Enter a {label[key]}: ').strip().upper()
        except KeyboardInterrupt:
            self.displayStatus(-1)

        if ticker in self.getMatchingTickers():
            tickerStatus = 1
        else:
            self.matchingTickers = []
            tickerStatus = self.validateTicker(ticker)


        if tickerStatus == 1:
            return ticker
        elif tickerStatus == -2:
            print('Your second ticker is the same as the first one. Please enter a different one.')
        else:
            print('Your input doesn\'t appear to be a valid ticker.')
            if key == 'S' and len(self.getMatchingTickers()) > 0:
                print(f'We can\'t an exact match for that ticker.\nPerhaps you meant: {self.getMatchingTickers()}')

        return self.askForTickerSymbol(key)


    # Returns 1 if ticker is an exact match (correct)
    # Returns 0 if there are no matching tickers
    # Returns -1 if there are ticker suggestions
    # Returns -2 if first and second tickers are duplicates (forex)
    # Returns -3 if currency doesn't match expected forex/crypto input

    def validateTicker(self, ticker):
        if ticker is None or ticker.strip() == '':
            return 0

        ticker = ticker.strip().upper()
        ticker = urllib.parse.quote(ticker)
        if self.seriesType == 'S': # make sure that the ticker corresponds to a valid stock:
            requestUrl = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={ticker}&apikey=' + self.apiKey
            # print(requestUrl)
            contents = urllib.request.urlopen(requestUrl).read()
            output = json.loads(contents)
            df = pd.DataFrame(output['bestMatches'])

            if df.empty:
                requestUrl = self.getRequestUrl(self.seriesType, 'timeseries')
                df = pd.read_csv(requestUrl)
                return 0 if df.empty else 1

            firstMatch = df['1. symbol'].iloc[0]
            if firstMatch == ticker:
                self.name = df['2. name'].iloc[0]
                self.df = df
                return 1
            else:
                self.df = df
                return -1

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
        if len(self.matchingTickers) > 0:
            return self.matchingTickers

        try:
            self.matchingTickers = list(self.df['1. symbol'])
            return self.matchingTickers
        except AttributeError:
            return []
        except TypeError:
            return []

    def getRequestUrl(self, key, epName):
        apiUrl = 'https://www.alphavantage.co/query?function='
        commonParam = f'&symbol={self.ticker}&datatype=csv&apikey=' + self.apiKey

        endpoints = {}
        if self.seriesType in ['S']:
            # daily opening, high, low and closing prices for a stock ticker
            endpoints['timeseries'] = 'TIME_SERIES_DAILY'

            # 50-day moving average of prices at closing:
            endpoints['sma50'] = 'SMA&interval=daily&time_period=50&series_type=close'

            # 200-day moving average of prices at closing
            endpoints['sma200'] = 'SMA&interval=daily&time_period=200&series_type=close'

        elif self.seriesType in ['F']:
            endpoints['timeseries'] = f'FX_DAILY&from_symbol={self.ticker}&to_symbol={self.converted}'

            # internally-computed 50-day MA since this isn't available from API
        elif self.seriesType in ['C']:
            endpoints['timeseries'] = 'DIGITAL_CURRENCY_DAILY&market=USD'

        requestUrl = ''
        if key == 'S':
            requestUrl = apiUrl + endpoints[epName] + commonParam
        return requestUrl

    # This function assumes that ticker has already been verified as valid, otherwise, we need to add error-checking
    def requestData(self):
        if self.shouldOutputToConsole:
            print("Requesting data from server (this may take a while) ...")

        endpoints = ['timeseries', 'sma50', 'sma200']
        data = {}

        for epName in endpoints:
            if self.shouldOutputToConsole:
                print(f'  Downloading {epName} ... ')
                requestUrl = self.getRequestUrl(self.seriesType, epName)
                try:
                    data[epName] = pd.read_csv(requestUrl)
                    xAxis = 'timestamp' if epName == 'timeseries' else 'time'
                    data[epName] = data[epName].sort_values(by=xAxis)
                except KeyboardInterrupt:
                    self.displayStatus(-1)
                except KeyError:
                    print('We\'re sorry but our data source doesn\'t support these inputs or you may have exceeded the rate limits.')
                    return

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
            smas = {'sma50': 50, 'sma200': 200}
        if self.seriesType == 'F':
            smas = {'sma50': 50}


        print(f'  Organizing & cleaning up data ... ')
        if self.seriesType == 'S':
            data['sma50'] = data['sma50'][data['sma50'].time > self.start]
            data['sma200'] = data['sma200'][data['sma200'].time > self.start]
        else:
            for sma, days in smas.items():
                if sma not in endpoints:
                    data[sma] = pd.DataFrame({
                            'time': list(data['timeseries']['timestamp']),
                            'SMA': list(data['timeseries']['close'].rolling(window = days).mean())
                        })


        return data


    def plotChart(self, data):
        if self.seriesType in ['S', 'C']:
            print(f'Preparing graphing library to plot chart for {self.name} (${self.ticker}) ...')
        else:
            print(f'Preparing graphing library to plot chart for {self.ticker} to {self.converted} ...')

        seriesLabels = {
            'S': 'Stock Prices',
            'F': 'Forex Exchange Rate',
            'C': 'Cryptocurrency Spot Prices',
        }
        candlestick = go.Ohlc(x = data['timeseries']['timestamp'],
                        open = data['timeseries']['open'],
                        high = data['timeseries']['high'],
                        low = data['timeseries']['low'],
                        close = data['timeseries']['close'],
                        name = seriesLabels[self.seriesType]
                    )
        chartData = [candlestick]

        if 'sma50' in data:
            sma50 = go.Scatter(x = data['sma50']['time'],
                            y = data['sma50']['SMA'],
                            name = '50-day MA',
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
            sma200 = go.Scatter(x = data['sma200']['time'],
                            y = data['sma200']['SMA'],
                            name ='200-day MA',
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

        fig = go.Figure(data = chartData, layout = self.getLayoutParams())
        py.plot(fig, filename = self.generateFilename())


    def generateFilename(self):
        path = f'outputs/ticker-chart-{self.ticker}'
        if self.converted != '':
            path += f'-{self.converted}'
        path += '.html'
        return path


    def getLayoutParams(self):
        titles = {
            'S': f' Time Series for {self.ticker}<br>Stock Name: {self.name}',
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
                font = dict(family="Verdana", size=25)
            ),
            xaxis=go.layout.XAxis(
                title=go.layout.xaxis.Title(
                    text=f'Period',
                    font = dict(
                        family='Verdana',
                        size=18,
                        color='#7f7f7f'
                    )
                )
            ),
            yaxis=go.layout.YAxis(
                title=go.layout.yaxis.Title(
                    text=yAxisLabel,
                    font = dict(
                        family='Verdana',
                        size=18,
                        color='#7f7f7f'
                    )
                )
            )
        )
        return layout

    def displayStatus(self, code):
        if code == -1:
            print('\nProgram terminated by user.')
            exit()


    def main():
        from TickerChart import TickerChart

        tc = TickerChart()
        tc.identifyType()
        tc.identifyTickers()
        data = tc.requestData()
        if data:
            tc.plotChart(data)

    if __name__== "__main__":
        main()

