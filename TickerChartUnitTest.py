from TickerChart import TickerChart

tc = TickerChart()
assert tc.validateTicker('AAPL') == 1
assert tc.validateTicker('GOOOOGLE') == -1
assert tc.validateTicker('GOOGLE') == 0
assert tc.validateTicker(None) == 0
assert tc.validateTicker('')  == 0