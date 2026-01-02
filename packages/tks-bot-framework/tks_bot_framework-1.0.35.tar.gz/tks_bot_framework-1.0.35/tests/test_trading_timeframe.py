import pytest
from botframework.trading_timeframe import TradingTimeFrame 

def test_enum_values():
    # Arrange.
    expected_values = {
        "TICK": "tick",
        "MIN_1": "1",
        "MIN_5": "5",
        "MIN_15": "15",
        "HOUR": "60",
        "HOUR_4": "240",
        "HOUR_6": "360",
        "DAY": "1440",
        "WEEK": "10080",
        "MONTH": "43800",
    }
    # Act and assert.
    for name, value in expected_values.items():
        assert TradingTimeFrame[name].value == value, f"{name} does not match the expected value"

def test_enum_uniqueness():
    # Arrange.
    values = set(item.value for item in TradingTimeFrame)
    # Act and assert.
    assert len(values) == len(TradingTimeFrame)

@pytest.mark.parametrize("member", TradingTimeFrame)
def test_enum_member(member):
    # Arrange, act and assert.
    assert isinstance(member, TradingTimeFrame)