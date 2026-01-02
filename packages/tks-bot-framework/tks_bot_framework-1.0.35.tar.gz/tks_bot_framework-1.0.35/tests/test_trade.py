import pytest
from famodels.trade import StatusOfTrade

def test_buy_value():        
    assert StatusOfTrade.NEW.value == "new"
def test_sell_value():        
    assert StatusOfTrade.CLOSED.value == "closed"
