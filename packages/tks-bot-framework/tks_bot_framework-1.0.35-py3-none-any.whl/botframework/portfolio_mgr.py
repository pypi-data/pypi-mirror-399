from botframework import botframework_utils
from tksessentials import utils
from botframework.trade_mgr import TradeMgr
from famodels.direction import Direction
from botframework.models.position_capacity import PositionCapacity
from argparse import ArgumentError
from cmath import log
from ctypes.wintypes import SHORT
from pickle import NONE
import logging
from datetime import datetime
from typing import List
from pandas import DataFrame
import ast
from fractions import Fraction

logger = logging.getLogger('app')


class PortfolioMgr:
    """Portfolio Manager."""

    def __init__(self) -> None:
        self.algo_cfg = utils.get_app_config()

    def get_position_capacities(self, market: str) -> List[PositionCapacity]:
        """Returns position capacities for the specified base asset (e.g., 'BTC')."""
        loaded_position_capacities = []
        # Load repeated capacities for specific assets.
        position_capacities_of_asset = self.algo_cfg.get("position_capacities_by_asset", [])
        for asset_config in position_capacities_of_asset:
            asset_market = asset_config["market"]  # Keep the market as "BTC-USDT"
            base_market = asset_market.split('-')[0]  # Extract 'BTC' for comparison
            if base_market.lower() == market.lower():  # Match case-insensitively
                market_symbol = asset_config["market_symbol"]
                count = asset_config["count"]
                common_specs = asset_config["common_specs"]
                for i in range(count):
                    pc = PositionCapacity(
                        id=i,
                        market=asset_market,  # Now uses the full "BTC-USDT"
                        market_symbol=market_symbol,
                        direction=common_specs["direction"],
                        position_size_in_percentage=eval(str(common_specs["position_size_in_percentage"])),
                        take_profit=common_specs["take_profit"] if common_specs["take_profit"] != "None" else None,
                        alternative_take_profit=common_specs["alternative_take_profit"] if common_specs["alternative_take_profit"] != "None" else None,
                        stop_loss=common_specs["stop_loss"] if common_specs["stop_loss"] != "None" else None,
                        alternative_stop_loss=common_specs["alternative_stop_loss"] if common_specs["alternative_stop_loss"] != "None" else None
                    )
                    loaded_position_capacities.append(pc)
        # Load individual positions and filter by market.
        individual_positions = self.algo_cfg.get("individual_positions", [])
        for pos_cap in individual_positions:
            pos_data = pos_cap["position_capacity"]
            # Check if the base asset matches the start of pos_data["market"].
            if pos_data["market"].startswith(market):
                pc = PositionCapacity(
                    id=pos_data["id"],
                    market=pos_data["market"],
                    market_symbol=pos_data["market_symbol"],
                    direction=pos_data["direction"],
                    position_size_in_percentage=eval(str(pos_data["position_size_in_percentage"])),
                    take_profit=pos_data["take_profit"] if pos_data["take_profit"] != "None" else None,
                    alternative_take_profit=pos_data["alternative_take_profit"] if pos_data["alternative_take_profit"] != "None" else None,
                    stop_loss=pos_data["stop_loss"] if pos_data["stop_loss"] != "None" else None,
                    alternative_stop_loss=pos_data["alternative_stop_loss"] if pos_data["alternative_stop_loss"] != "None" else None
                )
                loaded_position_capacities.append(pc)

        return loaded_position_capacities

    def get_position_capacity(self, market: str, pos_idx: int) -> PositionCapacity:
        """Expects 'market' as 'BTC."""
        all_position_capacities = self.get_position_capacities(market=market)
        for p_c in all_position_capacities:
            if p_c.id == pos_idx:
                return p_c

    def get_directional_position_capacities(self, market: str, direction: Direction) -> List[PositionCapacity]:
        """Returns the list of PositionCapacities for the specified market and direction (long/short)."""
        allowed_directional_positions: List[PositionCapacity] = []
        position_capacities: List[PositionCapacity] = self.get_position_capacities(market=market)
        for pos in position_capacities:
            if pos.direction == direction.value:
                allowed_directional_positions.append(pos)

        return allowed_directional_positions

    async def get_a_free_position_capacity_for_buys(self, ksqldb_query_url, view_name, direction:Direction) -> PositionCapacity:        
        """This method can only be called if we want to open a position. That is 'side' equals 'buy'; buy-long or buy-short. We always close all positions if 'side' equals 'sell'. 
        So, it returns any free long/short position capacity - or - None if all are occupied. Provide the direction with either long or short."""

        free_directional_position_capacities = await self.get_free_position_capacities_for_buys(ksqldb_query_url, view_name, direction)

        if len(free_directional_position_capacities) > 0:
            logger.info(f"The chosen free position is {free_directional_position_capacities[0].id}.")
            return free_directional_position_capacities[0]
        else:
            return None

    async def get_free_position_capacities_for_buys(self, ksqldb_query_url, view_name, direction: Direction) -> List[PositionCapacity]:
        """Returns all free position capacities for buys."""
        trade_mgr = TradeMgr()
        # Extract market symbol from view_name (e.g., 'BTC' from 'queryable_pull_tks_gatherer_trades_btc').
        market = view_name.split('_')[-1].upper()
        # Validate direction.
        if direction is None:
            raise ArgumentError("Failed to get a free position capacity. The direction is not passed.")
        if direction not in [Direction.LONG, Direction.SHORT]:
            raise ArgumentError(f"Failed to get a free position capacity. The direction passed is not valid: {direction}")
        # Fetch all position capacities of this direction (long/short) for the specific market.
        directional_position_capacities = self.get_directional_position_capacities(market=market, direction=direction)
        logger.info(f"We have {len(directional_position_capacities)} {direction}-position-capacities for {market}.")
        # Fetch active trades for this market, which returns a list of pos_idx integers.
        active_trades = await trade_mgr.get_active_positions(ksqldb_query_url, view_name, direction)
        logger.info(f"Currently there are {len(active_trades)} active trades for {market}.")
        # Determine free directional position capacities by filtering out active trades.
        free_directional_position_capacities = [
            pos_cap for pos_cap in directional_position_capacities
            if pos_cap.id not in active_trades
        ]
        logger.info("The currently available free position capacities (where there is no active trade) are: ")
        for free_trade in free_directional_position_capacities:
            logger.info(free_trade.id)

        return free_directional_position_capacities

    async def get_position_size_in_percentage(self, market: str, direction: Direction) -> float:
        """Returns the position size (in percentage of the total available amount) for a given market (e.g. 'BTC') and direction (long/short)."""
        # Get position capacities for the specified market and direction.
        total_position_capacities = len(self.get_directional_position_capacities(market, direction))
        # If no position capacities found, return 0 to avoid division error.
        if total_position_capacities == 0:
            return 0.0
        
        # Calculate the position size as a percentage of the total available amount.
        position_size_in_percentage = 100 / total_position_capacities
        return position_size_in_percentage

    async def calculate_take_profit_stop_loss(self, close, market: str, direction: Direction, pos_idx: int, atr=None, alternative_profit_loss: bool = None):
        """Calculate take profit and stop loss based on the chosen strategy."""
        # Fetch position capacity parameters for the specified market and position index.
        position_capacity = self.get_position_capacity(market, pos_idx)
        take_profit = position_capacity.take_profit
        stop_loss = position_capacity.stop_loss
        alternative_take_profit = position_capacity.alternative_take_profit
        alternative_stop_loss = position_capacity.alternative_stop_loss
        # Check if take profit and stop loss are calculated by percentage or by ATR.
        if self.algo_cfg["TP_SL_calculation"] == "percentage":
            if direction == Direction.LONG:
                if alternative_profit_loss is None:
                    take_profit_price = close * (1 + take_profit / 100)
                    stop_loss_price = close * (1 - stop_loss / 100)
                else:
                    take_profit_price = close * (1 + alternative_take_profit / 100)
                    stop_loss_price = close * (1 - alternative_stop_loss / 100)
            elif direction == Direction.SHORT:
                if alternative_profit_loss is None:
                    take_profit_price = close * (1 - take_profit / 100)
                    stop_loss_price = close * (1 + stop_loss / 100)
                else:
                    take_profit_price = close * (1 - alternative_take_profit / 100)
                    stop_loss_price = close * (1 + alternative_stop_loss / 100)
        elif self.algo_cfg["TP_SL_calculation"] == "atr" and atr is not None:
            if direction == Direction.LONG:
                if alternative_profit_loss is None:
                    take_profit_price = close + take_profit * atr
                    stop_loss_price = close - stop_loss * atr
                else:
                    take_profit_price = close + alternative_take_profit * atr
                    stop_loss_price = close - alternative_stop_loss * atr
            elif direction == Direction.SHORT:
                if alternative_profit_loss is None:
                    take_profit_price = close - take_profit * atr
                    stop_loss_price = close + stop_loss * atr
                else:
                    take_profit_price = close - alternative_take_profit * atr
                    stop_loss_price = close + alternative_stop_loss * atr

        return take_profit_price, stop_loss_price

    async def check_for_position_closing(self, ksqldb_query_url, topic_name, view_name, pos_idx, close, high, low):
        # Fetch the last entry for the provided pos_idx in the data base.
        # Check wether the take profit or stop loss price was hit during the last interval.
        # Check wether the position closing was already confirmed by freya alpha (and the trade is already marked as 'closed').
        # If not, we mark the trade as 'selling' and wait for the confirmation, then we mark the trade as 'closed'.
        new_status_of_position = 'closed'
        trade_mgr = TradeMgr()
        trade_data = await trade_mgr.get_latest_trade_data_by_pos_idx(ksqldb_query_url, view_name, pos_idx)
        direction = trade_data[8]
        tp = trade_data[9]
        sl = trade_data[10]
        if direction == Direction.LONG and high >= tp:
            logger.info(f"TP for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_name_trade=topic_name, view_name_trade=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        elif direction == Direction.LONG and low <= sl:
            logger.info(f"SL for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_name_trade=topic_name, view_name_trade=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        elif direction == Direction.SHORT and low <= tp:
            logger.info(f"TP for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_name_trade=topic_name, view_name_trade=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        elif direction == Direction.SHORT and high >= sl:
            logger.info(f"SL for position {pos_idx} was reached during the last interval - marking trade in data base as closed.")
            await trade_mgr.create_additional_entry_for_pos_idx(ksqldb_query_url=ksqldb_query_url, topic_name_trade=topic_name, view_name_trade=view_name, pos_idx=pos_idx, new_status_of_position=new_status_of_position, tp_sl_reached=True)
        else:
            logger.info(f"Neither TP nor SL for position {pos_idx} reached during the last interval.")