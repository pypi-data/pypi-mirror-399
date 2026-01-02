import pytest
import uuid
from datetime import datetime, timezone
from fasignalprovider.trading_signal import TradingSignal
from fasignalprovider.side import Side
from fasignalprovider.order_type import OrderType
from famodels.direction import Direction

def test_trading_signal_validation():
    provider_signal_id = str(uuid.uuid4())
    provider_trade_id = str(uuid.uuid4())
    provider_id = 'tks'
    strategy_id = 'tks-atomic-test'
    is_hot_signal = True
    market = 'BTC-USDT'
    data_source = 'Binance'
    direction = Direction.LONG
    side = Side.BUY
    order_type = OrderType.LIMIT_ORDER
    price = 65000
    tp = 66000
    sl = 64000
    position_size_in_percentage = 33.3
    date_of_creation = int(datetime.now(timezone.utc).timestamp() * 1000)

    # Create the TradingSignal instance
    trading_signal = TradingSignal(
        provider_signal_id=provider_signal_id,
        provider_trade_id=provider_trade_id,
        provider_id=provider_id,
        strategy_id=strategy_id,
        is_hot_signal=is_hot_signal,
        market=market,
        data_source=data_source,
        direction=direction,
        side=side,
        order_type=order_type,
        price=price,
        tp=tp,
        sl=sl,
        position_size_in_percentage=position_size_in_percentage,
        date_of_creation=date_of_creation
    )

    assert trading_signal.provider_signal_id == provider_signal_id
    assert trading_signal.provider_trade_id == provider_trade_id
    assert trading_signal.provider_id == provider_id
    assert trading_signal.strategy_id == strategy_id
    assert trading_signal.is_hot_signal == is_hot_signal
    assert trading_signal.market == market
    assert trading_signal.data_source == data_source
    assert trading_signal.direction == direction
    assert trading_signal.side == side
    assert trading_signal.order_type == order_type
    assert trading_signal.price == price
    assert trading_signal.tp == tp
    assert trading_signal.sl == sl
    assert trading_signal.position_size_in_percentage == position_size_in_percentage
    assert trading_signal.date_of_creation == date_of_creation
