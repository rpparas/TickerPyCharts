from TickerChart import TickerChart

tc = TickerChart()
tc.setDebugMode(True)

# Unit tests for stocks
tc.setSeriesType('S')
assert tc.validateTicker('AAPL') == 1
assert tc.validateTicker('GOOOOGLE') == 0
assert tc.validateTicker('GOOGLE') == -1
assert tc.validateTicker(None) == 0
assert tc.validateTicker('')  == 0
assert tc.validateTicker('AF.PAR') == 1

tc.validateTicker('Air France')
assert len(tc.getMatchingTickers()) > 0

tc.validateTicker('     ABCDEFG     ')
assert len(tc.getMatchingTickers()) == 0


# Unit tests for cryptocurrencies
tc.setSeriesType('C')
assert tc.validateTicker('ETH') == 1
assert tc.validateTicker(' xrp  ') == 1
assert tc.validateTicker('btc') == 1
assert tc.validateTicker('808       ') == 1
assert tc.validateTicker(' dunno ') == -3


# Unit tests for forex rates
tc.setSeriesType('F')
assert tc.validateTicker('USD') == 1
assert tc.validateTicker('Eur') == 1
assert tc.validateTicker('LOL') == -3


