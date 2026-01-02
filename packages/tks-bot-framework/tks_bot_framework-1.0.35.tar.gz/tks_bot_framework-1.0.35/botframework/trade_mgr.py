from botframework import botframework_utils
from botframework.market_mgr import MarketMgr
from famodels.direction import Direction
from famodels.trade import StatusOfTrade
from fasignalprovider.side import Side
from tksessentials import utils
from tksessentials import database
from datetime import datetime, timezone
import logging
import json
import time

logger = logging.getLogger('app')


class TradeMgr:

    def __init__(self):
        pass

    async def create_first_entry_for_pos_idx(self, kafka_producer_manager, topic_name_trade, pos_idx, provider_trade_id, provider_signal_id, status_of_position:StatusOfTrade, price, is_hot_signal:bool, market, data_source, direction:Direction, tp, sl, position_size_in_percentage, percentage_of_position, timestamp=None):
        if timestamp is None:
            timestamp = time.time() * 1000
        trade_data = {
            "pos_idx_str": str(pos_idx),
            "time_of_data_entry": str(timestamp),
            "pos_idx": pos_idx,
            "provider_trade_id": provider_trade_id,
            "status_of_position": status_of_position,
            "is_hot_signal": is_hot_signal,
            "market": market,
            "data_source": data_source,
            "direction": direction,
            "tp": tp,
            "sl": sl,
            "tp_sl_reached": False,
            "position_size_in_percentage": position_size_in_percentage,
            "time_of_position_opening": str(timestamp),
            "time_of_position_closing": None,
            "buy_orders": json.dumps({
                "buy_order_1": {
                    "timestamp": timestamp,
                    "provider_signal_id": provider_signal_id,
                    "percentage_of_position": percentage_of_position,
                    "buy_price": price
                }
            }),
            "sell_orders": json.dumps({})
        }
        # Use KafkaProducerManager to produce the message
        try:
            await kafka_producer_manager.produce_message(
                topic_name=topic_name_trade,
                key=str(pos_idx),
                value=trade_data
            )
            logger.info(f'Position index data produced to Kafka for provider_trade_id {provider_trade_id} and pos_idx {pos_idx}. Status: "new."')
        except Exception as e:
            logger.error(f"Failed to produce first entry for pos_idx {pos_idx}: {e}")
            raise
    
    async def create_additional_entry_for_pos_idx(self, kafka_producer_manager, ksqldb_query_url, topic_name_trade, view_name_trade, pos_idx, new_status_of_position: StatusOfTrade = None, price = None, provider_signal_id = None, percentage_of_position = None, timestamp = None, buy_order_id = None, sell_order_id = None, new_buy_order = False, new_sell_order = False, tp_sl_reached=False):
        if timestamp is None:
            timestamp = time.time() * 1000
        trade_data = await self.get_latest_trade_data_by_pos_idx(ksqldb_query_url, view_name_trade, pos_idx)
        # Unpack the list into variables
        (data_pos_idx_str, data_time_of_data_entry, data_pos_idx, data_provider_trade_id, data_status_of_position, data_is_hot_signal,
        data_market, data_data_source, data_direction, data_tp, data_sl, data_tp_sl_reached, data_position_size_in_percentage,
        data_time_of_position_opening, data_time_of_position_closing, data_buy_orders_json, data_sell_orders_json) = trade_data
        # Parse the JSON strings into dictionaries
        buy_orders = json.loads(data_buy_orders_json)
        sell_orders = json.loads(data_sell_orders_json)
        # Update variables if necessary.
        if tp_sl_reached:
            new_tp_sl_reached = tp_sl_reached
        else:
            new_tp_sl_reached = data_tp_sl_reached
        new_time_of_data_entry = str(timestamp)
        if new_status_of_position:
            new_status_of_position = new_status_of_position
        else:
            new_status_of_position = data_status_of_position
        if new_status_of_position == StatusOfTrade.CLOSED:
            new_time_of_position_closing = timestamp
        else:
            new_time_of_position_closing = data_time_of_position_closing
        # Add new buy order if new_buy_order is True.
        if new_buy_order:
            new_buy_order_id = f"buy_order_{len(buy_orders) + 1}"
            buy_orders[new_buy_order_id] = {
                "timestamp": timestamp,
                "provider_signal_id": provider_signal_id,
                "percentage_of_position": percentage_of_position,
                "buy_price": price
            }
        # Add new sell order if new_sell_order is True
        if new_sell_order:
            new_sell_order_id = f"sell_order_{len(sell_orders) + 1}"
            sell_orders[new_sell_order_id] = {
                "timestamp": timestamp,
                "provider_signal_id": provider_signal_id,
                "percentage_of_position": percentage_of_position,
                "sell_price": price
            }
        new_trade_data = {
            "pos_idx_str": str(pos_idx),
            "time_of_data_entry": new_time_of_data_entry,
            "pos_idx": pos_idx,
            "provider_trade_id": data_provider_trade_id,
            "status_of_position": new_status_of_position,
            "is_hot_signal": data_is_hot_signal,
            "market": data_market,
            "data_source": data_data_source,
            "direction": data_direction,
            "tp": data_tp,
            "sl": data_sl,
            "tp_sl_reached": new_tp_sl_reached,
            "position_size_in_percentage": data_position_size_in_percentage,
            "time_of_position_opening": data_time_of_position_opening,
            "time_of_position_closing": new_time_of_position_closing,
            "buy_orders": json.dumps(buy_orders),
            "sell_orders": json.dumps(sell_orders)
        }
        # Use KafkaProducerManager to produce the message.
        try:
            await kafka_producer_manager.produce_message(
                topic_name=topic_name_trade,
                key=str(pos_idx),
                value=new_trade_data
            )
            logger.info(f"Position index data updated for pos_idx {pos_idx}.")
        except Exception as e:
            logger.error(f"Failed to produce additional entry for pos_idx {pos_idx}: {e}")
            raise

    async def process_updates_from_freya_alpha(self):
        pass
    
    async def get_active_positions(self, ksqldb_query_url, view_name, direction: Direction = None):
        # Run a single query to pull all positions for this asset in one go.
        market_symbol = view_name.split('_')[-1].upper()
        try:
            results = await botframework_utils.execute_pull_query(
                ksqldb_query_url=ksqldb_query_url,
                view_name=view_name,
                select_columns='*',
                where_clause="1=1",  # No specific filter to fetch all records
                offset_reset="earliest"
            )
            logger.debug(f"Fetched all records for {view_name}: {results}")
            # If no records are fetched, log and return an empty list.
            if not results:
                logger.info(f"No records found for {market_symbol} in {view_name}. Returning an empty list.")
                return []
            occupied_positions = []
            # Filter results to find active positions based on status_of_position.
            for record in results:
                # Ensure the record has the expected structure
                if len(record) > 8:  # Safeguard for index-based access
                    pos_idx = record[2]
                    status_of_position = record[4]
                    direction_of_position = record[8]
                    # Append pos_idx to occupied_positions if the status is not 'CLOSED'.
                    if status_of_position != StatusOfTrade.CLOSED.value:
                        if direction is None or direction_of_position == direction.value:
                            occupied_positions.append(pos_idx)
                else:
                    logger.warning(f"Unexpected record format in {view_name}: {record}")
            logger.info(f"Occupied positions for {market_symbol}: {occupied_positions}")
            return occupied_positions

        except Exception as e:
            logger.error(f"Failed to fetch or process positions for {view_name}: {e}")
            return []

    async def get_latest_trade_data_by_pos_idx(self, ksqldb_query_url, view_name, pos_idx):
        # Execute pull query to get all messages for the given pos_idx
        results = await botframework_utils.execute_pull_query(
            ksqldb_query_url=ksqldb_query_url,
            view_name=view_name,
            select_columns='*',
            where_clause=f"POS_IDX = {pos_idx}",
            offset_reset="earliest"
        )
        if results:
            # Sort the results by time_of_data_entry in descending order
            sorted_results = sorted(results, key=lambda x: x[0], reverse=True)  # Assuming the first element is the timestamp
            latest_message = sorted_results[0]  # The latest message for the given pos_idx
            return latest_message  # Return all the data in the message

        return None  # Return None if no results found
    
    async def get_latest_trade_data_by_provider_trade_id(self, ksqldb_query_url, view_name, provider_trade_id):
        # Execute pull query to get all messages for the given provider_trade_id.
        results = await botframework_utils.execute_pull_query(
            ksqldb_query_url=ksqldb_query_url,
            view_name=view_name,
            select_columns='*',
            where_clause=f"PROVIDER_TRADE_ID = '{provider_trade_id}'",
            offset_reset="earliest"
        )
        if results:
            # Sort the results by time_of_data_entry in descending order
            sorted_results = sorted(results, key=lambda x: x[0], reverse=True)  # Assuming the first element is the timestamp
            latest_message = sorted_results[0]  # The latest message for the given pos_idx
            return latest_message  # Return all the data in the message

        return None  # Return None if no results found

    async def update_status_of_trade(self, ksqldb_query_url, view_name, provider_trade_id, topic_name, status_of_position:StatusOfTrade):
        timestamp = time.time() * 1000
        new_time_of_data_entry = str(timestamp)
        active_trade = await self.get_latest_trade_data_by_provider_trade_id(ksqldb_query_url, view_name, provider_trade_id)
        if not active_trade:
            logger.info(f"No active trade found for provider_trade_id {provider_trade_id}")
        # Unpack the list into variables
        (data_pos_idx_str, data_time_of_data_entry, data_pos_idx, data_provider_trade_id, data_status_of_position, data_is_hot_signal,
        data_market, data_data_source, data_direction, data_tp, data_sl, data_tp_sl_reached, data_position_size_in_percentage,
        data_time_of_position_opening, data_time_of_position_closing, data_buy_orders_json, data_sell_orders_json) = active_trade
        # Parse the JSON strings into dictionaries
        buy_orders = json.loads(data_buy_orders_json)
        sell_orders = json.loads(data_sell_orders_json)
        new_trade_data = {
            "pos_idx_str": data_pos_idx_str,
            "time_of_data_entry": new_time_of_data_entry,
            "pos_idx": data_pos_idx,
            "provider_trade_id": data_provider_trade_id,
            "status_of_position": status_of_position,
            "is_hot_signal": data_is_hot_signal,
            "market": data_market,
            "data_source": data_data_source,
            "direction": data_direction,
            "tp": data_tp,
            "sl": data_sl,
            "tp_sl_reached": data_tp_sl_reached,
            "position_size_in_percentage": data_position_size_in_percentage,
            "time_of_position_opening": data_time_of_position_opening,
            "time_of_position_closing": data_time_of_position_closing,
            "buy_orders": json.dumps(buy_orders),
            "sell_orders": json.dumps(sell_orders)
        }
        # Produce the updated trade_data to Kafka
        await database.produce_message(topic_name=topic_name, key=str(data_pos_idx), value=new_trade_data)
        logger.info(f"Data updated for provider_trade_id {provider_trade_id}. New status of position: {status_of_position}")

    async def get_realized_and_unrealized_profit_and_loss_of_position(self, ksqldb_query_url, view_name, pos_idx: int, market, exchange=None) -> tuple:
        """Return the realized and unrealized profit without considering the commissions (buy/sell)."""
        # Get the latest active trade data by position index
        active_trade = await self.get_latest_trade_data_by_pos_idx(ksqldb_query_url, view_name, pos_idx)
        if not active_trade:
            logger.info(f"No active trade found for pos_idx {pos_idx}")
            return 0, 0, 0, 0
        # Unpack the list into variables
        (data_pos_idx_str, data_time_of_data_entry, data_pos_idx, data_provider_trade_id, data_status_of_position, data_is_hot_signal,
        data_market, data_data_source, data_direction, data_tp, data_sl, data_tp_sl_reached, data_position_size_in_percentage,
        data_time_of_position_opening, data_time_of_position_closing, data_buy_orders_json, data_sell_orders_json) = active_trade
        # Get the current price of the market
        current_price = await MarketMgr().get_last_price(market, exchange)
        # Extract buy orders from the active trade
        buy_orders = json.loads(data_buy_orders_json)
        # Extract sell orders from the active trade
        sell_orders = json.loads(data_sell_orders_json)
        # Calculate the total percentage of positions in buy and sell orders
        total_buy_percentage = sum(buy_order['percentage_of_position'] for buy_order in buy_orders.values())
        total_sell_percentage = sum(sell_order['percentage_of_position'] for sell_order in sell_orders.values())
        unrealized_profit_and_loss = 0
        realized_profit_and_loss = 0

        # If there are only buy orders and no sell orders
        if total_sell_percentage == 0:
            for buy_order in buy_orders.values():
                buy_price = buy_order['buy_price']
                percentage_of_position = buy_order['percentage_of_position']
                unrealized_profit_and_loss += (current_price - buy_price) / buy_price * percentage_of_position

        # If there are both buy and sell orders and the total sell percentage is less than 100%
        elif 0 < total_sell_percentage < 100 and total_buy_percentage > total_sell_percentage:
            hypothetical_unrealized_profit = 0
            # Calculate hypothetical unrealized profit
            for buy_order in buy_orders.values():
                buy_price = buy_order['buy_price']
                percentage_of_position = buy_order['percentage_of_position']
                hypothetical_unrealized_profit += (current_price - buy_price) / buy_price * percentage_of_position
            # Calculate average entry price
            average_entry_price = current_price / ((100 + hypothetical_unrealized_profit) / 100)
            # Calculate realized profit and loss
            for sell_order in sell_orders.values():
                sell_price = sell_order['sell_price']
                percentage_of_position = sell_order['percentage_of_position']
                realized_profit_and_loss += (sell_price - average_entry_price) / average_entry_price * percentage_of_position
            # Calculate open percentage of position
            open_percentage_of_position = total_buy_percentage - total_sell_percentage
            # Calculate unrealized profit
            unrealized_profit_and_loss = (current_price - average_entry_price) / average_entry_price * open_percentage_of_position
        
        # If total sell percentage is equal to total buy percentage
        elif total_sell_percentage > 0 and total_buy_percentage == total_sell_percentage:
            hypothetical_unrealized_profit = 0
            # Calculate hypothetical unrealized profit
            for buy_order in buy_orders.values():
                buy_price = buy_order['buy_price']
                percentage_of_position = buy_order['percentage_of_position']
                hypothetical_unrealized_profit += (current_price - buy_price) / buy_price * percentage_of_position
            # Calculate average entry price
            average_entry_price = current_price / ((100 + hypothetical_unrealized_profit) / 100)
            # Calculate realized profit and loss
            for sell_order in sell_orders.values():
                sell_price = sell_order['sell_price']
                percentage_of_position = sell_order['percentage_of_position']
                realized_profit_and_loss += (sell_price - average_entry_price) / average_entry_price * percentage_of_position
        logger.info(f"Position with pos_idx {pos_idx}: Realized PnL: {realized_profit_and_loss} Unrealized PnL: {unrealized_profit_and_loss} Total buy percentage: {total_buy_percentage} Total sell percentage: {total_sell_percentage}")

        return realized_profit_and_loss, unrealized_profit_and_loss, total_buy_percentage, total_sell_percentage