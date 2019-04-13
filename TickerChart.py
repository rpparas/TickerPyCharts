import plotly.offline as py
import plotly.graph_objs as go
import pandas as pd
import json
from pandas.io.json import json_normalize

apiKey = 'JQKUZMZK74N9U4KY'
apiUrl = 'https://www.alphavantage.co/query?function='
params = '&symbol=MSFT&datatype=csv&apikey=' + apiKey
timeseries = apiUrl + 'TIME_SERIES_DAILY' + params

df = pd.read_csv(timeseries)
df.sort_values(by=['timestamp']) # sort entries by date (from oldest to newest)


trace = go.Ohlc(x=df['timestamp'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close'])
data = [trace]
py.plot(data, filename='simple_candlestick.html')
