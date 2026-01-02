# ========================================|======================================== #
#                                      Imports                                      #
# ========================================|======================================== #

from typing import (
    NewType,
    TypedDict,
    Literal,
)

# ========================================|======================================== #
#                                 Class Definitions                                 #
# ========================================|======================================== #

HexUUID = NewType("HexUUID", str)

# +--------------------------------------------------------------------------------------+ #

class OrderStatus(TypedDict):
    
    order_uuid : HexUUID
    OrderInQueue : bool
    Price : int
    Volume : int
    RemainedVolume : int
    ExecutedVolume : int
    OrderSide : Literal['Buy','Sell']
    ValidityType : Literal['DAY','GTC','GTD']
    ValidityDate : int