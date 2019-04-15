# TickerPyCharts
A mini-project showing how to plot equity, currency and other ticker symbols using Python charting libraries from data supplied by third-party APIs. The program lets the user select the type of instrument (stock, digital or physical currency) and ticker symbol for that instrument. The program outputs a chart showing time series for the stock's price, forex between 2 currencies, or a digital currency's value in USD.

![Screenshot of Candlestick Chart with Moving Averages](https://res.cloudinary.com/mpyr-com/image/upload/v1555210942/screenshot-stock-chart_c0bpms.png)

# Features:
1. Program accepts ticker input(s) from user via command line or during execution.
2. Program asks user if he/she wants to enter a stock, physical or digital currency.
3. Program checks whether ticker symbols are valid for the selection in #1, or whether they're duplicate (USD to USD).
4. For stock tickers, the program provides suggestions whenever user's input isn't an exact match.
5. For stock tickers, the program plots the data in a candlestick chart with 50-day and 200-day SMA overlays.
6. The program accepts tickers for stocks domicled overseas, e.g. Air France where one of its tickers is AF.PAR
7. For currencies, the program computes simple moving average internally with Pandas dataframe since these aren't available from the API.

# Installation and Usage:
1. Install Python 3.7 on your computer. Please refer to this guide: https://realpython.com/installing-python/
2. For Mac users: Open Terminal and type: `pip install plotly` or `pip3 install plotly`
3. The program allows you to enter inputs 2 ways: as parameters on the command line or via user prompts
4. To provide inputs during program execution, simply type: `python TickerCharts.py` The program will show additional prompts.
5. To input a stock ticker on the command line, type: 
   `python TickerCharts.py S GOOGL`  # first parameter (S) indicates stock followed by ticker symbol.
6. To input physical (forex) currencies for conversion on the command line, type: 
   `python TickerCharts.py F GBP CNY` # first parameter (F) followed by 2 currencies to convert
7. To input a digital currency for conversion on the command line, type: 
   `python TickerCharts.py C XRP` # first parameter (C) followed by cryptocurrency ticker

# Troubleshooting:
1. If you encounter SSL errors like *SSL: CERTIFICATE_VERIFY_FAILED*, please attempt to fix it by following this guide: https://stackoverflow.com/questions/41328451/ssl-module-in-python-is-not-available-when-installing-package-with-pip3
2. If you're trying to run the program inside Sublime, you'll likely be unable to do so due to Sublime's restrictions in accessing STDIN. To get around this, please run the program via command line.
3. To cancel or terminate the program, press `Ctrl C` on Windows or Mac.

# Future (Nice-to-have) Features:
1. Build REST API with MVT architecture using Flask
2. Create gateway for GET operations to retrieve ticker data (timeseries, SMA, etc)
3. Build frontend UI for inputs and validation using Vue.js
4. Use frontend charting library using D3.js or HighCharts which interfaces with backend API

# Links:
- API data source: Alpha Advantage | https://www.alphavantage.co/documentation/
- Plotting library: Plotly | https://plot.ly/python/candlestick-charts/
- Python version: 3.7 | https://www.python.org/downloads/
