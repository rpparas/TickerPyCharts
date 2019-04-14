# TickerPyCharts
A mini-project showing how to plot equity, currency and other ticker symbols using Python charting libraries from data supplied by third-party APIs. The program lets the user select the type of instrument (stock, digital or physical currency) and ticker symbol for that instrument. The program outputs a chart showing time series for the stock's price, forex between 2 currencies, or a digital currency's value in USD.

![Screenshot of Candlestick Chart with Moving Averages](https://res.cloudinary.com/mpyr-com/image/upload/v1555210942/screenshot-stock-chart_c0bpms.png)

# Features:
1. Program asks user if he/she wants to enter a stock, physical or digital currency.
2. Program accepts ticker input/s from user via command line or during execution.
3. Program checks whether ticker symbols are valid for the selection in #1, or they're duplicate (USD to USD).
4. For stock symbols, the program plots the data in a candlestick chart with 50-day and 200-day SMA overlays.
5. For foreign currencies, the program plots the data in a candlestick chart but without SMAs since these are not available from the API.
6. For digital currencies, the program plots the data in a timeseries.

# Installation and Usage:
1. Install Python 3.7 on your computer. Please refer to this guide: https://realpython.com/installing-python/
2. For Mac users: Open Terminal and type: `pip install plotly` or `pip3 install plotly`
3. To run and supply the input during program execution, simply type: `python TickerCharts.py`
4. To run and supply stock ticker on the command line, type: 
   `python TickerCharts.py S GOOGL` # first parameter 'S' indicates stock followed by ticker symbol.
5. To run and supply physical (forex) currencies for conversion on the command line, type: 
   `python TickerCharts.py F GBP CNY` # first parameter 'F' followed by 2 currencies to convert
6. To run and supply digital for conversion on the command line, type: 
   `python TickerCharts.py C XRP` # first parameter 'C' followed by cryptocurrency ticker

# Troubleshooting:
1. If you encounter SSL errors like ** SSL: CERTIFICATE_VERIFY_FAILED **, please attempt to fix it by following this guide: https://stackoverflow.com/questions/41328451/ssl-module-in-python-is-not-available-when-installing-package-with-pip3
2. If you're trying to run the program inside Sublime, you'll likely be unable to do so due to Sublime's restrictions in accessing STDIN. To get around this, please run the program via command line.
3. To cancel or terminate the program, press `Ctrl C` on Windows or Mac.

# Links:
- API data source: Alpha Advantage | https://www.alphavantage.co/documentation/
- Plotting library: Plotly | https://plot.ly/python/candlestick-charts/
- Python version: 3.7 | https://www.python.org/downloads/
