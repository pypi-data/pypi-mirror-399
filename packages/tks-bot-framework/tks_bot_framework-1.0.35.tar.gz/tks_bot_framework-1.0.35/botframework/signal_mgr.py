from tksessentials import utils
from tksessentials import database
from botframework.trade_mgr import TradeMgr
from botframework import botframework_utils
from fasignalprovider.trading_signal import TradingSignal
from fasignalprovider.order_type import OrderType
from fasignalprovider.side import Side
from famodels.direction import Direction
from famodels.trade import StatusOfTrade
from datetime import datetime, timezone
import asyncio
import socket
import logging
import uuid
import json
import time

logger = logging.getLogger('app')

class SignalMgr:

    def __init__(self):
        pass

    async def produce_signal_to_kafka(self, kafka_producer_manager, ksqldb_query_url, topic_name_signal, market, data_source, direction:Direction, side:Side, order_type:OrderType, price, tp, sl, position_size_in_percentage, percentage_of_position, topic_name_trade=None, view_name_trade=None, provider_trade_id=None, pos_idx=None, status_of_position:StatusOfTrade=None):
        # Create the TradingSignal.
        provider_signal_id = str(uuid.uuid4())
        if provider_trade_id:
            position_size_in_percentage = percentage_of_position
        else:
            provider_trade_id = str(uuid.uuid4())
        app_cfg = utils.get_app_config()
        provider_id = app_cfg['provider_id']
        strategy_id = app_cfg['application']
        is_hot_signal = app_cfg['is_hot']
        timestamp = time.time() * 1000
        trading_signal = TradingSignal(
            provider_signal_id = provider_signal_id,
            provider_trade_id = provider_trade_id,
            provider_id = provider_id,
            strategy_id = strategy_id,
            is_hot_signal = is_hot_signal,
            market = market,
            data_source = data_source, 
            direction = direction,
            side = side,  
            order_type = order_type,
            price = price, 
            tp = tp,
            sl = sl,
            position_size_in_percentage = position_size_in_percentage, 
            date_of_creation = int(timestamp)  
        )
        logger.info(f"Created TradingSignal: {trading_signal}")
        # # Produce the TradingSignal to kafka.
        try:
            await kafka_producer_manager.produce_message(
                topic_name=topic_name_signal,
                key=provider_signal_id,
                value=trading_signal.__dict__,
            )
            logger.info(f"Produced signal to Kafka topic {topic_name_signal}")
        except Exception as e:
            logger.error(f"Exception during produce_signal_to_kafka: {e}")
            raise
        # Potentially store event in data base.
        trade_mgr = TradeMgr()
        if topic_name_trade:
            if status_of_position==StatusOfTrade.NEW:
                await trade_mgr.create_first_entry_for_pos_idx(kafka_producer_manager, topic_name_trade=topic_name_trade, pos_idx=pos_idx, provider_trade_id=provider_trade_id, provider_signal_id=provider_signal_id, status_of_position=status_of_position, price=price, is_hot_signal=is_hot_signal, market=market, data_source=data_source, direction=direction, tp=tp, sl=sl, position_size_in_percentage=position_size_in_percentage, percentage_of_position=percentage_of_position, timestamp=timestamp)
            else:
                if side == Side.BUY:
                    await trade_mgr.create_additional_entry_for_pos_idx(kafka_producer_manager, ksqldb_query_url=ksqldb_query_url, topic_name_trade=topic_name_trade, view_name_trade=view_name_trade, pos_idx=pos_idx, new_status_of_position=status_of_position, price=price, provider_signal_id=provider_signal_id, percentage_of_position=percentage_of_position, timestamp=timestamp, new_buy_order=True)
                else:
                    await trade_mgr.create_additional_entry_for_pos_idx(kafka_producer_manager, ksqldb_query_url=ksqldb_query_url, topic_name_trade=topic_name_trade, view_name_trade=view_name_trade, pos_idx=pos_idx, new_status_of_position=status_of_position, price=price, provider_signal_id=provider_signal_id, percentage_of_position=percentage_of_position, timestamp=timestamp, new_sell_order=True)
        return timestamp, provider_trade_id, provider_signal_id