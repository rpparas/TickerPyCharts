from TickerChart import TickerChart
import time

tc = TickerChart()
tc.setDebugMode(True)
delay = 10
# Unit tests for stocks
tc.setSeriesType('S')
tests = {
    'AAPL': 1,
    'GOOOOGLE': 0,
    'GOOGLE': -1,
    None: 0,
    '': 0,
    'AF.PAR': 1,
}

for inp, out in tests.items():
    assert tc.validateTicker(inp) == out
    time.sleep(delay) # Add delay due to rate limit imposed by API

tc.validateTicker('Air France')
assert len(tc.getMatchingTickers()) > 0
time.sleep(delay)

tc.validateTicker('     ABCDEFG     ')
assert len(tc.getMatchingTickers()) == 0
time.sleep(delay)

# # Unit tests for cryptocurrencies
tc.setSeriesType('C')

assert tc.validateTicker('ETH') == 1
assert tc.validateTicker(' xrp  ') == 1
assert tc.validateTicker('btc') == 1
assert tc.validateTicker('808') == 1
assert tc.validateTicker(' dunno ') == -3


# Unit tests for forex rates
tc.setSeriesType('F')
assert tc.validateTicker('USD') == 1
assert tc.validateTicker('Eur') == 1
assert tc.validateTicker('LOL') == -3

