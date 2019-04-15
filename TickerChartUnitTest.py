from TickerChart import TickerChart

tc = TickerChart()
tc.setDebugMode(True)
tc.setSeriesType('S')

assert tc.validateTicker('AAPL') == 1
assert tc.validateTicker('GOOOOGLE') == 0
assert tc.validateTicker('GOOGLE') == -1
assert tc.validateTicker(None) == 0
assert tc.validateTicker('')  == 0
assert tc.validateTicker('AF.PAR') == 1
