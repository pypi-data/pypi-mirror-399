import pytest
from fasignalprovider.side import Side

def test_buy_value():        
    assert Side.BUY.value == "buy"
def test_sell_value():        
    assert Side.SELL.value == "sell"