# This test will work again once the mock response from Freya Alpha is removed.

# import pytest
# from unittest.mock import patch, AsyncMock, MagicMock
# from botframework.signal_mgr import Signal_Mgr
# from fasignalprovider.side import Side
# from fasignalprovider.order_type import OrderType
# from famodels.direction import Direction
# from famodels.trade import StatusOfTrade
# import botframework.botframework_utils as botframework_utils
# from fasignalprovider.trading_signal import TradingSignal
# import time
# import uuid

# @pytest.mark.asyncio
# @patch('tksessentials.database.produce_message', new_callable=AsyncMock)
# @patch('botframework.signal_mgr.utils.get_app_config')
# @patch('botframework.signal_mgr.TradeMgr')
# @patch('fasignalprovider.trading_signal.TradingSignal', autospec=True)
# async def test_produce_signal_to_kafka(MockTradingSignal, MockTradeMgr, mock_get_app_config, mock_kafka_send_message):
#     # Arrange
#     mock_get_app_config.return_value = {
#         'provider_id': 'test_provider_id',
#         'application': 'test_strategy_id',
#         'is_hot': True
#     }
#     mock_trade_mgr_instance = MockTradeMgr.return_value
#     mock_trade_mgr_instance.create_first_entry_for_pos_idx = AsyncMock()
#     mock_trade_mgr_instance.create_additional_entry_for_pos_idx = AsyncMock()

#     signal_mgr_instance = Signal_Mgr()

#     ksqldb_query_url = 'http://ksql.test'
#     topic_name_signal = 'signal_topic'
#     topic_name_trade = 'trade_topic'
#     market = 'test_market'
#     data_source = 'test_source'
#     direction = Direction.LONG
#     side = Side.BUY
#     order_type = OrderType.MARKET_ORDER
#     price = 100.0
#     tp = 110.0
#     sl = 90.0
#     position_size_in_percentage = 10
#     percentage_of_position = 50
#     provider_trade_id = 'test_trade_id'
#     pos_idx = 1
#     status_of_position = StatusOfTrade.NEW
#     # Mock time to ensure consistent timestamp
#     timestamp = time.time() * 1000

#     # Act
#     with patch('time.time', return_value=timestamp / 1000):
#         timestamp, returned_provider_trade_id, provider_signal_id = await signal_mgr_instance.produce_signal_to_kafka(
#             ksqldb_query_url, topic_name_signal, market, data_source, direction, side, order_type, price, tp, sl,
#             position_size_in_percentage, percentage_of_position, topic_name_trade, view_name_trade='trade_view',
#             provider_trade_id=provider_trade_id, pos_idx=pos_idx, status_of_position=status_of_position
#         )

#     # Create the expected TradingSignal instance manually
#     expected_trading_signal = TradingSignal(
#         provider_signal_id=provider_signal_id,
#         provider_trade_id=provider_trade_id,
#         provider_id='test_provider_id',
#         strategy_id='test_strategy_id',
#         is_hot_signal=True,
#         market=market,
#         data_source=data_source,
#         direction=direction,
#         side=side,
#         order_type=order_type,
#         price=price,
#         tp=tp,
#         sl=sl,
#         position_size_in_percentage=percentage_of_position,
#         date_of_creation=int(timestamp)
#     )

#     # Assert
#     assert provider_signal_id is not None
#     assert returned_provider_trade_id == provider_trade_id
#     mock_kafka_send_message.assert_called_once_with(
#         topic_name=topic_name_signal,
#         key=provider_signal_id,
#         value=expected_trading_signal
#     )
#     mock_trade_mgr_instance.create_first_entry_for_pos_idx.assert_called_once()