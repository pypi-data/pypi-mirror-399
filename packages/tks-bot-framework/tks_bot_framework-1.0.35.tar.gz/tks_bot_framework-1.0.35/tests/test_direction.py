from famodels.direction import Direction

def test_buy_value():        
    assert Direction.LONG.value == "long"
def test_sell_value():        
    assert Direction.SHORT.value == "short"
