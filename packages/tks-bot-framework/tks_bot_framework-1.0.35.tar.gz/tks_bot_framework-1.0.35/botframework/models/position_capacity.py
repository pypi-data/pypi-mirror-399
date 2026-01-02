from typing import List, Set, Optional
from famodels.direction import Direction
from sqlmodel import Field, SQLModel

class PositionCapacity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)             
    direction: Direction # long, short   
    position_size_in_percentage: float     
    take_profit: float = None
    alternative_take_profit: float = None
    stop_loss: float = None
    alternative_stop_loss: float = None
    market: str
    market_symbol: str

    def __getitem__(self, key):
        return self.__dict__[key]   