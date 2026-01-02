import pytest
from unittest.mock import patch, MagicMock
from botframework.cex_proxy import CEXProxy, get_exchange

@pytest.fixture
def ccxt_exchange_mock():
    """Fixture for creating a mock ccxt exchange."""
    exchange = MagicMock()
    exchange.enableRateLimit = True
    return exchange

def test_get_exchange_supported(ccxt_exchange_mock):
    """Test getting a supported exchange."""
    exchange_name = 'binance'
    with patch.dict('sys.modules', {'ccxt.async_support': MagicMock(binance=MagicMock(return_value=ccxt_exchange_mock))}):
        exchange = get_exchange(exchange_name)
        assert exchange.enableRateLimit == True

def test_get_exchange_unsupported():
    """Test trying to get an unsupported exchange."""
    exchange_name = 'unsupported_exchange'
    with pytest.raises(ValueError) as excinfo:
        get_exchange(exchange_name)
    assert f"Exchange {exchange_name} is not supported by ccxt." in str(excinfo.value)