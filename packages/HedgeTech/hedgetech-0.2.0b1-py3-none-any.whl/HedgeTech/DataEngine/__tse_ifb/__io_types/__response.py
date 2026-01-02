# ========================================|======================================== #
#                                      Imports                                      #
# ========================================|======================================== #

from datetime import datetime
from typing import (
    List,
    Union,
    Dict,
    Optional,
    TypedDict,
)

# ========================================|======================================== #
#                                 Class Definitions                                 #
# ========================================|======================================== #

class WebsocketBase_symbolIsin(TypedDict):
    """
    Base structure for websocket messages containing fund or instrument information
    identified by ISIN (International Securities Identification Number).

    This TypedDict defines the common structure of messages received over a websocket
    where each message is linked to a specific ISIN.

    Attributes:
        channel (str): The name of the websocket channel through which the message is sent.
        symbolIsin (str): The ISIN code of the instrument or fund.
        timestamp (str): ISO-formatted timestamp indicating when the message was generated.

    Example:
        >>> message: WebsocketBase_symbolIsin = {
        ...     "channel": "fund_live_updates",
        ...     "symbolIsin": "IR0001234567",
        ...     "timestamp": "2025-11-19T10:30:00Z"
        ... }
        >>> message["symbolIsin"]
        'IR0001234567'
    """
    channel: str
    symbolIsin: str
    timestamp: str


class WebsocketBase_symbolName(TypedDict):
    """
    Base structure for websocket messages containing fund or instrument information
    identified by symbol name.

    This TypedDict defines the common structure of messages received over a websocket
    where each message is linked to a specific symbol name.

    Attributes:
        channel (str): The name of the websocket channel through which the message is sent.
        symbolName (str): The symbol name of the instrument or fund.
        timestamp (str): ISO-formatted timestamp indicating when the message was generated.

    Example:
        >>> message: WebsocketBase_symbolName = {
        ...     "channel": "fund_live_updates",
        ...     "symbolName": "ETF001",
        ...     "timestamp": "2025-11-19T10:30:00Z"
        ... }
        >>> message["symbolName"]
        'ETF001'
    """
    channel: str
    symbolName: str
    timestamp: str
    

class StatusDescription(TypedDict):
    """
    Contains a human-readable description of the server or API status.

    Attributes:
        fa (str): Description in Farsi (Persian) language.
        en (str): Description in English language.

    Example:
        >>> desc: StatusDescription = {
        ...     "fa": "عملیات موفقیت‌آمیز بود",
        ...     "en": "Operation successful"
        ... }
        >>> desc["en"]
        'Operation successful'
    """
    fa: str
    en: str


class Status(TypedDict):
    """
    Represents the status metadata of a server response or websocket message.

    This TypedDict provides information about the success of an operation,
    server timestamp, versioning, author info, description, and status code.

    Attributes:
        State (bool): Indicates whether the operation or request was successful.
        ServerTimeStamp (float): Server timestamp, typically a Unix timestamp.
        Version (str): Version of the API or server sending the message.
        Author (str): Name of the author or owner of the API/server.
        Description (StatusDescription): A human-readable description of the status
                                         in multiple languages.
        StatusCode (int): Numeric status code returned by the server.

    Example:
        >>> status: Status = {
        ...     "State": True,
        ...     "ServerTimeStamp": 1700350200.0,
        ...     "Version": "1.2.3",
        ...     "Author": "HedgeTech",
        ...     "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...     "StatusCode": 200
        ... }
        >>> status["Description"]["en"]
        'Operation successful'
    """
    State: bool
    ServerTimeStamp: float
    Version: str
    Author: str
    Description: StatusDescription
    StatusCode: int

# +--------------------------------------------------------------------------------------+ #


class SecuritiesAndFunds(TypedDict):
    """
    Represents detailed metadata for a security or fund, including trading rules,
    commission rates, limits, and other attributes used in financial operations.

    This TypedDict is typically used in systems that manage ETFs, stocks, or other
    traded instruments, providing all necessary details for order validation,
    display, and transaction execution.

    Attributes:
        symbolIsin (str): International Securities Identification Number (ISIN) of the instrument.
        symbolName (str): Trading symbol of the instrument.
        title (str): Human-readable name or title of the security/fund.

        buyCommission (float): Commission rate applied when buying this security/fund.
        sellCommission (float): Commission rate applied when selling this security/fund.

        minValidBuyVolume (int): Minimum allowable buy volume per order.
        maxValidBuyVolume (int): Maximum allowable buy volume per order.
        minValidSellVolume (int): Minimum allowable sell volume per order.
        maxValidSellVolume (int): Maximum allowable sell volume per order.

        canBuy (bool): Indicates whether buying is currently permitted.
        canSell (bool): Indicates whether selling is currently permitted.

        minAllowedPrice (float): Minimum price allowed for placing an order.
        maxAllowedPrice (float): Maximum price allowed for placing an order.

        is_ETF (bool): Indicates if the security/fund is an Exchange-Traded Fund (ETF).
        baseVolume (float): The base trading volume unit of the instrument.
        minDealablePrice (float): Minimum price at which a deal can be executed.
        minDealableCount (int): Minimum number of units that can be traded per deal.

        owner (str): Name of the instrument owner or issuer.
        hidePrice (int): Flag indicating if the price should be hidden in the interface (0 or 1).
        dataClass (str): Classification of the data, e.g., "Equity", "ETF", etc.

    Example:
        >>> fund: SecuritiesAndFunds = {
        ...     "symbolIsin": "IR0001234567",
        ...     "symbolName": "ETF001",
        ...     "title": "HedgeTech Growth ETF",
        ...     "buyCommission": 0.0015,
        ...     "sellCommission": 0.0015,
        ...     "minValidBuyVolume": 100,
        ...     "maxValidBuyVolume": 10000,
        ...     "minValidSellVolume": 100,
        ...     "maxValidSellVolume": 10000,
        ...     "canBuy": True,
        ...     "canSell": True,
        ...     "minAllowedPrice": 1000.0,
        ...     "maxAllowedPrice": 200000.0,
        ...     "is_ETF": True,
        ...     "baseVolume": 100.0,
        ...     "minDealablePrice": 1000.0,
        ...     "minDealableCount": 100,
        ...     "owner": "HedgeTech",
        ...     "hidePrice": 0,
        ...     "dataClass": "ETF"
        ... }
        >>> fund["symbolName"]
        'ETF001'
        >>> fund["canBuy"]
        True
        >>> fund["minValidBuyVolume"]
        100
    """
    symbolIsin: str
    symbolName: str
    title: str

    buyCommission: float
    sellCommission: float

    minValidBuyVolume: int
    maxValidBuyVolume: int
    minValidSellVolume: int
    maxValidSellVolume: int

    canBuy: bool
    canSell: bool

    minAllowedPrice: float
    maxAllowedPrice: float

    is_ETF: bool
    baseVolume: float
    minDealablePrice: float
    minDealableCount: int

    owner: str
    hidePrice: int
    dataClass: str

# +--------------------------------------------------------------------------------------+ #


class StockFutures(TypedDict):
    """
    Represents detailed metadata for a stock futures contract, including trading rules,
    margin requirements, underlying assets, commissions, limits, and other attributes
    needed for trading and risk management.

    This TypedDict is typically used in systems that manage futures contracts for equities,
    ETFs, or other underlying instruments, providing all necessary details for order
    validation, execution, and reporting.

    Attributes:
        symbolIsin (str): ISIN code of the futures contract.
        title (str): Human-readable name or title of the futures contract.
        symbolName (str): Trading symbol of the futures contract.

        csize (int): Contract size (number of underlying units per futures contract).
        firstMargin (float): Initial margin required to open a position.
        minimumMargin (float): Minimum maintenance margin required.

        UnderlyingAssets_symbolIsin (str): ISIN of the underlying asset.
        UnderlyingAssets_title (str): Title or name of the underlying asset.
        UnderlyingAssets_symbolName (str): Trading symbol of the underlying asset.
        UnderlyingAssets_is_ETF (bool): Whether the underlying asset is an ETF.

        roundFactor (int): Price rounding factor used for the futures contract.
        ExpirationDate (str): Expiration date of the contract in ISO format (YYYY-MM-DD).
        DaysToExpiration (int): Number of days remaining until the contract expires.

        buyCommission (float): Commission rate applied when buying the contract.
        sellCommission (float): Commission rate applied when selling the contract.

        minValidBuyVolume (int): Minimum valid buy volume per order.
        maxValidBuyVolume (int): Maximum valid buy volume per order.
        minValidSellVolume (int): Minimum valid sell volume per order.
        maxValidSellVolume (int): Maximum valid sell volume per order.

        canBuy (bool): Indicates whether buying is currently allowed.
        canSell (bool): Indicates whether selling is currently allowed.

        minAllowedPrice (float): Minimum price allowed for placing an order.
        maxAllowedPrice (float): Maximum price allowed for placing an order.

        minDealableCount (int): Minimum number of contracts per deal.
        minDealablePrice (float): Minimum price at which a deal can be executed.

        owner (str): Name of the contract owner or issuing entity.

        ExerciseFeePhysical (float): Fee charged for physical settlement of the contract.
        ExerciseFeeCash (float): Fee charged for cash settlement of the contract.
        ExerciseSellTax (float): Tax applied when exercising or selling the contract.

        OpenPositionLimitInstitution (int): Maximum open positions allowed for institutions.
        OpenPositionLimitIndividual (int): Maximum open positions allowed for individuals.
        OpenPositionLimitMarket (int): Maximum open positions allowed for the entire market.

        dataClass (str): Classification of the data, e.g., "Futures", "ETF Futures", etc.

    Example:
        >>> future: StockFutures = {
        ...     "symbolIsin": "IRFUT123456",
        ...     "title": "HedgeTech Equity Futures",
        ...     "symbolName": "FUT001",
        ...     "csize": 100,
        ...     "firstMargin": 5000.0,
        ...     "minimumMargin": 2500.0,
        ...     "UnderlyingAssets_symbolIsin": "IR0001234567",
        ...     "UnderlyingAssets_title": "HedgeTech Growth ETF",
        ...     "UnderlyingAssets_symbolName": "ETF001",
        ...     "UnderlyingAssets_is_ETF": True,
        ...     "roundFactor": 10,
        ...     "ExpirationDate": "2025-12-31",
        ...     "DaysToExpiration": 42,
        ...     "buyCommission": 0.001,
        ...     "sellCommission": 0.001,
        ...     "minValidBuyVolume": 1,
        ...     "maxValidBuyVolume": 100,
        ...     "minValidSellVolume": 1,
        ...     "maxValidSellVolume": 100,
        ...     "canBuy": True,
        ...     "canSell": True,
        ...     "minAllowedPrice": 1000.0,
        ...     "maxAllowedPrice": 200000.0,
        ...     "minDealableCount": 1,
        ...     "minDealablePrice": 1000.0,
        ...     "owner": "HedgeTech",
        ...     "ExerciseFeePhysical": 50.0,
        ...     "ExerciseFeeCash": 25.0,
        ...     "ExerciseSellTax": 5.0,
        ...     "OpenPositionLimitInstitution": 1000,
        ...     "OpenPositionLimitIndividual": 100,
        ...     "OpenPositionLimitMarket": 5000,
        ...     "dataClass": "Futures"
        ... }
        >>> future["symbolName"]
        'FUT001'
        >>> future["UnderlyingAssets_is_ETF"]
        True
        >>> future["DaysToExpiration"]
        42
    """
    symbolIsin: str
    title: str
    symbolName: str

    csize: int
    firstMargin: float
    minimumMargin: float

    UnderlyingAssets_symbolIsin: str
    UnderlyingAssets_title: str
    UnderlyingAssets_symbolName: str
    UnderlyingAssets_is_ETF: bool

    roundFactor: int
    ExpirationDate: str
    DaysToExpiration: int

    buyCommission: float
    sellCommission: float

    minValidBuyVolume: int
    maxValidBuyVolume: int
    minValidSellVolume: int
    maxValidSellVolume: int

    canBuy: bool
    canSell: bool

    minAllowedPrice: float
    maxAllowedPrice: float

    minDealableCount: int
    minDealablePrice: float

    owner: str

    ExerciseFeePhysical: float
    ExerciseFeeCash: float
    ExerciseSellTax: float

    OpenPositionLimitInstitution: int
    OpenPositionLimitIndividual: int
    OpenPositionLimitMarket: int

    dataClass: str

# +--------------------------------------------------------------------------------------+ #


class StockOptions(TypedDict):
    """
    Represents detailed metadata for a stock options contract, including trading rules,
    commissions, volume limits, underlying assets, exercise fees, position limits, and
    other attributes required for trading and risk management.

    This TypedDict is typically used in systems that handle equity options, providing
    all necessary details for order validation, execution, reporting, and margin calculations.

    Attributes:
        symbolIsin (str): ISIN code of the options contract.
        symbolName (str): Trading symbol of the options contract.
        title (str): Human-readable name or title of the options contract.

        buyCommission (float): Commission rate applied when buying the option.
        sellCommission (float): Commission rate applied when selling the option.

        minValidBuyVolume (int): Minimum valid buy volume per order.
        maxValidBuyVolume (int): Maximum valid buy volume per order.
        minValidSellVolume (int): Minimum valid sell volume per order.
        maxValidSellVolume (int): Maximum valid sell volume per order.

        canBuy (bool): Indicates whether buying is currently allowed.
        canSell (bool): Indicates whether selling is currently allowed.

        minAllowedPrice (float): Minimum price allowed for placing an order.
        maxAllowedPrice (float): Maximum price allowed for placing an order.

        minDealablePrice (float): Minimum price at which a deal can be executed.
        minDealableCount (int): Minimum number of contracts per deal.

        owner (str): Name of the contract owner or issuing entity.

        strikePrice (float): Strike price of the option.
        csize (int): Contract size (number of underlying units per option contract).
        optionType (str): Type of the option, e.g., "Call" or "Put".
        ExpirationDate (str): Expiration date of the option in ISO format (YYYY-MM-DD).
        DaysToExpiration (int): Number of days remaining until expiration.

        UnderlyingAssets_symbolIsin (str): ISIN of the underlying asset.
        UnderlyingAssets_title (str): Title or name of the underlying asset.
        UnderlyingAssets_symbolName (str): Trading symbol of the underlying asset.
        UnderlyingAssets_is_ETF (bool): Indicates whether the underlying asset is an ETF.

        ExerciseFeePhysical (float): Fee for physical settlement of the option.
        ExerciseFeeCash (float): Fee for cash settlement of the option.
        ExerciseSellTax (float): Tax applied when exercising or selling the option.

        OpenPositionLimitInstitution (int): Maximum open positions allowed for institutions.
        OpenPositionLimitIndividual (int): Maximum open positions allowed for individuals.
        OpenPositionLimitMarket (int): Maximum open positions allowed for the entire market.

        dataClass (str): Classification of the data, e.g., "Options", "ETF Options", etc.

    Example:
        >>> option: StockOptions = {
        ...     "symbolIsin": "IROPT123456",
        ...     "symbolName": "OPT001",
        ...     "title": "HedgeTech Call Option",
        ...     "buyCommission": 0.001,
        ...     "sellCommission": 0.001,
        ...     "minValidBuyVolume": 1,
        ...     "maxValidBuyVolume": 50,
        ...     "minValidSellVolume": 1,
        ...     "maxValidSellVolume": 50,
        ...     "canBuy": True,
        ...     "canSell": True,
        ...     "minAllowedPrice": 1000.0,
        ...     "maxAllowedPrice": 200000.0,
        ...     "minDealablePrice": 1000.0,
        ...     "minDealableCount": 1,
        ...     "owner": "HedgeTech",
        ...     "strikePrice": 1200.0,
        ...     "csize": 100,
        ...     "optionType": "Call",
        ...     "ExpirationDate": "2025-12-31",
        ...     "DaysToExpiration": 42,
        ...     "UnderlyingAssets_symbolIsin": "IR0001234567",
        ...     "UnderlyingAssets_title": "HedgeTech Growth ETF",
        ...     "UnderlyingAssets_symbolName": "ETF001",
        ...     "UnderlyingAssets_is_ETF": True,
        ...     "ExerciseFeePhysical": 50.0,
        ...     "ExerciseFeeCash": 25.0,
        ...     "ExerciseSellTax": 5.0,
        ...     "OpenPositionLimitInstitution": 1000,
        ...     "OpenPositionLimitIndividual": 100,
        ...     "OpenPositionLimitMarket": 5000,
        ...     "dataClass": "Options"
        ... }
        >>> option["symbolName"]
        'OPT001'
        >>> option["optionType"]
        'Call'
        >>> option["DaysToExpiration"]
        42
    """
    symbolIsin: str
    symbolName: str
    title: str

    buyCommission: float
    sellCommission: float

    minValidBuyVolume: int
    maxValidBuyVolume: int
    minValidSellVolume: int
    maxValidSellVolume: int

    canBuy: bool
    canSell: bool

    minAllowedPrice: float
    maxAllowedPrice: float

    minDealablePrice: float
    minDealableCount: int

    owner: str

    strikePrice: float
    csize: int
    optionType: str
    ExpirationDate: str
    DaysToExpiration: int

    UnderlyingAssets_symbolIsin: str
    UnderlyingAssets_title: str
    UnderlyingAssets_symbolName: str
    UnderlyingAssets_is_ETF: bool

    ExerciseFeePhysical: float
    ExerciseFeeCash: float
    ExerciseSellTax: float

    OpenPositionLimitInstitution: int
    OpenPositionLimitIndividual: int
    OpenPositionLimitMarket: int

    dataClass: str

# +--------------------------------------------------------------------------------------+ #


class TreasuryBonds(TypedDict):
    """
    Represents detailed metadata for a treasury bond or government-issued debt instrument,
    including trading rules, commissions, limits, settlement, and other attributes needed
    for trading and portfolio management.

    This TypedDict is typically used in financial systems that handle treasury bonds,
    ETFs, or similar instruments, providing all necessary details for order validation,
    execution, reporting, and risk management.

    Attributes:
        symbolIsin (str): ISIN code of the treasury bond.
        symbolName (str): Trading symbol of the bond.
        title (str): Human-readable name or title of the bond.

        buyCommission (float): Commission rate applied when buying the bond.
        sellCommission (float): Commission rate applied when selling the bond.

        minValidBuyVolume (int): Minimum valid buy volume per order.
        maxValidBuyVolume (int): Maximum valid buy volume per order.
        minValidSellVolume (int): Minimum valid sell volume per order.
        maxValidSellVolume (int): Maximum valid sell volume per order.

        canBuy (bool): Indicates whether buying is currently allowed.
        canSell (bool): Indicates whether selling is currently allowed.

        minAllowedPrice (float): Minimum price allowed for placing an order.
        maxAllowedPrice (float): Maximum price allowed for placing an order.

        baseVol (float): Base trading volume unit of the bond.
        minDealablePrice (float): Minimum price at which a deal can be executed.
        minDealableCount (int): Minimum number of bonds per deal.

        owner (str): Name of the bond issuer or owner.
        hidePrice (int): Flag indicating if the price should be hidden in the interface (0 or 1).
        is_ETF (bool): Indicates whether the instrument is an ETF.

        ExpirationDate (str): Expiration date or maturity date of the bond in ISO format (YYYY-MM-DD).
        DaysToExpiration (int): Number of days remaining until expiration or maturity.

        dataClass (str): Classification of the data, e.g., "TreasuryBond", "ETF Bond", etc.

    Example:
        >>> bond: TreasuryBonds = {
        ...     "symbolIsin": "IRTB1234567",
        ...     "symbolName": "TB001",
        ...     "title": "HedgeTech Treasury Bond",
        ...     "buyCommission": 0.001,
        ...     "sellCommission": 0.001,
        ...     "minValidBuyVolume": 1,
        ...     "maxValidBuyVolume": 1000,
        ...     "minValidSellVolume": 1,
        ...     "maxValidSellVolume": 1000,
        ...     "canBuy": True,
        ...     "canSell": True,
        ...     "minAllowedPrice": 1000.0,
        ...     "maxAllowedPrice": 200000.0,
        ...     "baseVol": 1.0,
        ...     "minDealablePrice": 1000.0,
        ...     "minDealableCount": 1,
        ...     "owner": "HedgeTech",
        ...     "hidePrice": 0,
        ...     "is_ETF": False,
        ...     "ExpirationDate": "2030-12-31",
        ...     "DaysToExpiration": 1800,
        ...     "dataClass": "TreasuryBond"
        ... }
        >>> bond["symbolName"]
        'TB001'
        >>> bond["is_ETF"]
        False
        >>> bond["DaysToExpiration"]
        1800
    """
    symbolIsin: str
    symbolName: str
    title: str

    buyCommission: float
    sellCommission: float

    minValidBuyVolume: int
    maxValidBuyVolume: int
    minValidSellVolume: int
    maxValidSellVolume: int

    canBuy: bool
    canSell: bool

    minAllowedPrice: float
    maxAllowedPrice: float

    baseVol: float
    minDealablePrice: float
    minDealableCount: int

    owner: str
    hidePrice: int
    is_ETF: bool

    ExpirationDate: str
    DaysToExpiration: int

    dataClass: str

# +--------------------------------------------------------------------------------------+ #


class Instruments(TypedDict):
    """
    Represents a complete response containing a list of various financial instruments
    along with the server status metadata.

    This TypedDict is commonly used to fetch or store all instruments data from an API,
    including equities, ETFs, stock futures, stock options, and treasury bonds. Each
    instrument in the `Data` list can be one of several TypedDict types, providing
    a unified structure for heterogeneous financial instruments.

    Attributes:
        Data (List[Union[SecuritiesAndFunds, StockFutures, StockOptions, TreasuryBonds, None]]):
            A list containing individual instrument data. Each item can be:
                - SecuritiesAndFunds: For standard securities and ETFs
                - StockFutures: For futures contracts on equities or ETFs
                - StockOptions: For options contracts
                - TreasuryBonds: For government-issued debt instruments
                - None: In case of missing or unavailable data

        Status (Status): Metadata about the server response, including success state,
            timestamp, version, author, description, and status code.

    Example:
        >>> instruments: Instruments = {
        ...     "Data": [
        ...         {
        ...             "symbolIsin": "IR0001234567",
        ...             "symbolName": "ETF001",
        ...             "title": "HedgeTech Growth ETF",
        ...             "buyCommission": 0.0015,
        ...             "sellCommission": 0.0015,
        ...             "minValidBuyVolume": 100,
        ...             "maxValidBuyVolume": 10000,
        ...             "minValidSellVolume": 100,
        ...             "maxValidSellVolume": 10000,
        ...             "canBuy": True,
        ...             "canSell": True,
        ...             "minAllowedPrice": 1000.0,
        ...             "maxAllowedPrice": 200000.0,
        ...             "is_ETF": True,
        ...             "baseVolume": 100.0,
        ...             "minDealablePrice": 1000.0,
        ...             "minDealableCount": 100,
        ...             "owner": "HedgeTech",
        ...             "hidePrice": 0,
        ...             "dataClass": "ETF"
        ...         },
        ...         {
        ...             "symbolIsin": "IRFUT123456",
        ...             "symbolName": "FUT001",
        ...             "title": "HedgeTech Equity Futures",
        ...             "csize": 100,
        ...             "firstMargin": 5000.0,
        ...             "minimumMargin": 2500.0,
        ...             "UnderlyingAssets_symbolIsin": "IR0001234567",
        ...             "UnderlyingAssets_title": "HedgeTech Growth ETF",
        ...             "UnderlyingAssets_symbolName": "ETF001",
        ...             "UnderlyingAssets_is_ETF": True,
        ...             "roundFactor": 10,
        ...             "ExpirationDate": "2025-12-31",
        ...             "DaysToExpiration": 42,
        ...             "buyCommission": 0.001,
        ...             "sellCommission": 0.001,
        ...             "minValidBuyVolume": 1,
        ...             "maxValidBuyVolume": 100,
        ...             "minValidSellVolume": 1,
        ...             "maxValidSellVolume": 100,
        ...             "canBuy": True,
        ...             "canSell": True,
        ...             "minAllowedPrice": 1000.0,
        ...             "maxAllowedPrice": 200000.0,
        ...             "minDealableCount": 1,
        ...             "minDealablePrice": 1000.0,
        ...             "owner": "HedgeTech",
        ...             "ExerciseFeePhysical": 50.0,
        ...             "ExerciseFeeCash": 25.0,
        ...             "ExerciseSellTax": 5.0,
        ...             "OpenPositionLimitInstitution": 1000,
        ...             "OpenPositionLimitIndividual": 100,
        ...             "OpenPositionLimitMarket": 5000,
        ...             "dataClass": "Futures"
        ...         }
        ...     ],
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> instruments["Data"][0]["symbolName"]
        'ETF001'
        >>> instruments["Status"]["State"]
        True
    """
    Data: List[
        Union[
            SecuritiesAndFunds,
            StockFutures,
            StockOptions,
            TreasuryBonds,
            None
        ]
    ]
    Status: Status
    
# +--------------------------------------------------------------------------------------+ #


class BestLimitItem(TypedDict):
    """
    Represents the best limit order information at a given price level for a financial instrument.

    Attributes:
        buy_order_count (int): Number of active buy orders at this price level.
        buy_quantity (int): Total quantity available for buying at this price level.
        buy_price (int): Price level for buy orders.
        sell_order_count (int): Number of active sell orders at this price level.
        sell_quantity (int): Total quantity available for selling at this price level.
        sell_price (int): Price level for sell orders.

    Example:
        >>> item: BestLimitItem = {
        ...     "buy_order_count": 5,
        ...     "buy_quantity": 1000,
        ...     "buy_price": 12000,
        ...     "sell_order_count": 3,
        ...     "sell_quantity": 800,
        ...     "sell_price": 12100
        ... }
        >>> item["buy_price"]
        12000
    """
    buy_order_count: int
    buy_quantity: int
    buy_price: int
    sell_order_count: int
    sell_quantity: int
    sell_price: int


class BestLimit(TypedDict):
    """
    Represents the aggregated best limit orders for multiple instruments.

    The structure is a nested dictionary where the first key is typically a symbol
    identifier (ISIN or symbolName) and the second key represents the order level or priority.

    Attributes:
        items (Dict[str, Dict[str, BestLimitItem]]): Nested dictionary of BestLimitItem objects.
            - Outer key: Instrument identifier (e.g., ISIN or symbolName)
            - Inner key: Price level or order priority
            - Value: BestLimitItem for that level

    Example:
        >>> best_limit: BestLimit = {
        ...     "ETF001": {
        ...         "1": {
        ...             "buy_order_count": 5,
        ...             "buy_quantity": 1000,
        ...             "buy_price": 12000,
        ...             "sell_order_count": 3,
        ...             "sell_quantity": 800,
        ...             "sell_price": 12100
        ...         }
        ...     }
        ... }
        >>> best_limit["ETF001"]["1"]["sell_quantity"]
        800
    """
    items: Dict[str, Dict[str, BestLimitItem]]


class BestLimitResponse(TypedDict):
    """
    Response structure for best limit orders from a REST API call.

    Attributes:
        Data (BestLimit): Aggregated best limit order data.
        Status (Status): Metadata about the server response, including success state,
                         timestamp, version, author, description, and status code.

    Example:
        >>> response: BestLimitResponse = {
        ...     "Data": best_limit,
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["ETF001"]["1"]["buy_quantity"]
        1000
        >>> response["Status"]["State"]
        True
    """
    Data: BestLimit
    Status: Status


class BestLimit_WS_symbolIsin(WebsocketBase_symbolIsin):
    """
    Websocket message structure for best limit orders identified by ISIN.

    This TypedDict extends `WebsocketBase_symbolIsin` and represents real-time best
    limit order updates for a specific instrument identified by its ISIN.

    Attributes:
        data (Dict[str, BestLimitItem]): Dictionary mapping price levels or order priorities
            to BestLimitItem objects for the instrument.

    Example:
        >>> ws_data: BestLimit_WS_symbolIsin = {
        ...     "channel": "best_limit_updates",
        ...     "symbolIsin": "IR0001234567",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": {
        ...         "1": {
        ...             "buy_order_count": 5,
        ...             "buy_quantity": 1000,
        ...             "buy_price": 12000,
        ...             "sell_order_count": 3,
        ...             "sell_quantity": 800,
        ...             "sell_price": 12100
        ...         },
        ...         "2": {
        ...             "buy_order_count": 4,
        ...             "buy_quantity": 500,
        ...             "buy_price": 11950,
        ...             "sell_order_count": 2,
        ...             "sell_quantity": 600,
        ...             "sell_price": 12150
        ...         }
        ...     }
        ... }
        >>> ws_data["data"]["1"]["sell_price"]
        12100
    """
    data: Dict[str, BestLimitItem]


class BestLimit_WS_symbolName(WebsocketBase_symbolName):
    """
    Websocket message structure for best limit orders identified by symbol name.

    This TypedDict extends `WebsocketBase_symbolName` and represents real-time best
    limit order updates for a specific instrument identified by its trading symbol.

    Attributes:
        data (Dict[str, BestLimitItem]): Dictionary mapping price levels or order priorities
            to BestLimitItem objects for the instrument.

    Example:
        >>> ws_data: BestLimit_WS_symbolName = {
        ...     "channel": "best_limit_updates",
        ...     "symbolName": "ETF001",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": {
        ...         "1": {
        ...             "buy_order_count": 5,
        ...             "buy_quantity": 1000,
        ...             "buy_price": 12000,
        ...             "sell_order_count": 3,
        ...             "sell_quantity": 800,
        ...             "sell_price": 12100
        ...         },
        ...         "2": {
        ...             "buy_order_count": 4,
        ...             "buy_quantity": 500,
        ...             "buy_price": 11950,
        ...             "sell_order_count": 2,
        ...             "sell_quantity": 600,
        ...             "sell_price": 12150
        ...         }
        ...     }
        ... }
        >>> ws_data["data"]["2"]["buy_price"]
        11950
    """
    data: Dict[str, BestLimitItem]

# +--------------------------------------------------------------------------------------+ #


class OrderItem(TypedDict):
    """
    Represents a single order entry in the order book.

    Attributes:
        price (float): Price level of the order.
        quantity (int): Total quantity available at this price level.
        count (int): Number of orders at this price level.

    Example:
        >>> order: OrderItem = {
        ...     "price": 12000.0,
        ...     "quantity": 500,
        ...     "count": 3
        ... }
        >>> order["price"]
        12000.0
    """
    price: float
    quantity: int
    count: int


class OrderBook(TypedDict):
    """
    Represents the full order book for a single financial instrument.

    Attributes:
        Buy (List[OrderItem]): List of buy orders, usually sorted by descending price.
        Sell (List[OrderItem]): List of sell orders, usually sorted by ascending price.

    Example:
        >>> book: OrderBook = {
        ...     "Buy": [{"price": 12000.0, "quantity": 500, "count": 3}],
        ...     "Sell": [{"price": 12100.0, "quantity": 400, "count": 2}]
        ... }
        >>> book["Sell"][0]["quantity"]
        400
    """
    Buy: List[OrderItem]
    Sell: List[OrderItem]


class OrderBookResponse(TypedDict):
    """
    Response structure for order book data from a REST API call.

    Attributes:
        Data (Dict[str, OrderBook]): Dictionary mapping instrument identifiers (ISIN or symbolName)
                                     to their respective order book.
        Status (Status): Metadata about the server response, including success state,
                         timestamp, version, author, description, and status code.

    Example:
        >>> response: OrderBookResponse = {
        ...     "Data": {
        ...         "IR0001234567": {
        ...             "Buy": [{"price": 12000.0, "quantity": 500, "count": 3}],
        ...             "Sell": [{"price": 12100.0, "quantity": 400, "count": 2}]
        ...         }
        ...     },
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["IR0001234567"]["Buy"][0]["price"]
        12000.0
        >>> response["Status"]["State"]
        True
    """
    Data: Dict[str, OrderBook]
    Status: Status


class OrderBook_WS_symbolIsin(WebsocketBase_symbolIsin):
    """
    Websocket message structure for order book updates identified by ISIN.

    Attributes:
        data (OrderBook): Real-time order book for the specified instrument.

    Example:
        >>> ws_data: OrderBook_WS_symbolIsin = {
        ...     "channel": "order_book_updates",
        ...     "symbolIsin": "IR0001234567",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": {
        ...         "Buy": [{"price": 12000.0, "quantity": 500, "count": 3}],
        ...         "Sell": [{"price": 12100.0, "quantity": 400, "count": 2}]
        ...     }
        ... }
        >>> ws_data["data"]["Buy"][0]["price"]
        12000.0
    """
    data: OrderBook


class OrderBook_WS_symbolName(WebsocketBase_symbolName):
    """
    Websocket message structure for order book updates identified by symbol name.

    Attributes:
        data (OrderBook): Real-time order book for the specified instrument.

    Example:
        >>> ws_data: OrderBook_WS_symbolName = {
        ...     "channel": "order_book_updates",
        ...     "symbolName": "ETF001",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": {
        ...         "Buy": [{"price": 12000.0, "quantity": 500, "count": 3}],
        ...         "Sell": [{"price": 12100.0, "quantity": 400, "count": 2}]
        ...     }
        ... }
        >>> ws_data["data"]["Sell"][0]["quantity"]
        400
    """
    data: OrderBook
    
# +--------------------------------------------------------------------------------------+ #



class Aggregate(TypedDict):
    """
    Represents aggregated market data for a single financial instrument over a given period.

    This includes trade statistics, volume, value, and price information.

    Attributes:
        date (str): Date of the aggregation in ISO format (YYYY-MM-DD).
        time (str): Time of the aggregation in HH:MM:SS format.
        trade_count (int): Number of trades executed during this period.
        total_volume (int): Total traded volume.
        total_value (int): Total traded value (sum of price * quantity).
        closing_price (float): Closing price at the end of the period.
        last_price (float): Last traded price.
        low_price (float): Lowest price during the period.
        high_price (float): Highest price during the period.
        open_price (float): Opening price at the start of the period.
        previous_close (float): Closing price from the previous trading period.

    Example:
        >>> agg: Aggregate = {
        ...     "date": "2025-11-19",
        ...     "time": "10:30:00",
        ...     "trade_count": 120,
        ...     "total_volume": 5000,
        ...     "total_value": 60000000,
        ...     "closing_price": 12000.0,
        ...     "last_price": 12100.0,
        ...     "low_price": 11950.0,
        ...     "high_price": 12150.0,
        ...     "open_price": 12050.0,
        ...     "previous_close": 11980.0
        ... }
        >>> agg["closing_price"]
        12000.0
    """
    date: str
    time: str
    trade_count: int
    total_volume: int
    total_value: int
    closing_price: float
    last_price: float
    low_price: float
    high_price: float
    open_price: float
    previous_close: float


class AggregateResponse(TypedDict):
    """
    Response structure for aggregated market data from a REST API call.

    Attributes:
        Data (Dict[str, Aggregate]): Dictionary mapping instrument identifiers (ISIN or symbolName)
                                     to their corresponding aggregated data.
        Status (Status): Metadata about the server response, including success state,
                         timestamp, version, author, description, and status code.

    Example:
        >>> response: AggregateResponse = {
        ...     "Data": {
        ...         "IR0001234567": agg
        ...     },
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["IR0001234567"]["last_price"]
        12100.0
        >>> response["Status"]["State"]
        True
    """
    Data: Dict[str, Aggregate]
    Status: Status


class Aggregate_WS_symbolIsin(WebsocketBase_symbolIsin):
    """
    Websocket message structure for aggregated market data identified by ISIN.

    Attributes:
        data (Aggregate): Real-time aggregated data for the specified instrument.

    Example:
        >>> ws_data: Aggregate_WS_symbolIsin = {
        ...     "channel": "aggregate_updates",
        ...     "symbolIsin": "IR0001234567",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": agg
        ... }
        >>> ws_data["data"]["high_price"]
        12150.0
    """
    data: Aggregate


class Aggregate_WS_symbolName(WebsocketBase_symbolName):
    """
    Websocket message structure for aggregated market data identified by symbol name.

    Attributes:
        data (Aggregate): Real-time aggregated data for the specified instrument.

    Example:
        >>> ws_data: Aggregate_WS_symbolName = {
        ...     "channel": "aggregate_updates",
        ...     "symbolName": "ETF001",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": agg
        ... }
        >>> ws_data["data"]["total_volume"]
        5000
    """
    data: Aggregate
    
# +--------------------------------------------------------------------------------------+ #


class institutional_vs_individual(TypedDict):
    """
    Represents the breakdown of buy and sell activity between individual and institutional traders
    for a specific financial instrument.

    Attributes:
        buy_count_individual (int): Number of buy orders placed by individual traders.
        buy_volume_individual (int): Total volume bought by individual traders.
        buy_count_institution (int): Number of buy orders placed by institutional traders.
        buy_volume_institution (int): Total volume bought by institutional traders.
        sell_count_individual (int): Number of sell orders placed by individual traders.
        sell_volume_individual (int): Total volume sold by individual traders.
        sell_count_institution (int): Number of sell orders placed by institutional traders.
        sell_volume_institution (int): Total volume sold by institutional traders.

    Example:
        >>> trades: institutional_vs_individual = {
        ...     "buy_count_individual": 120,
        ...     "buy_volume_individual": 5000,
        ...     "buy_count_institution": 45,
        ...     "buy_volume_institution": 10000,
        ...     "sell_count_individual": 100,
        ...     "sell_volume_individual": 4000,
        ...     "sell_count_institution": 50,
        ...     "sell_volume_institution": 9000
        ... }
        >>> trades["buy_volume_institution"]
        10000
    """
    buy_count_individual: int
    buy_volume_individual: int
    buy_count_institution: int
    buy_volume_institution: int
    sell_count_individual: int
    sell_volume_individual: int
    sell_count_institution: int
    sell_volume_institution: int


class Institutional_vs_IndividualItemResponse(TypedDict):
    """
    Response structure for institutional vs individual trading data from a REST API call.

    Attributes:
        Data (Dict[str, institutional_vs_individual]): Dictionary mapping instrument identifiers
            (ISIN or symbolName) to their corresponding buy/sell breakdown.
        Status (Status): Metadata about the server response, including success state,
                         timestamp, version, author, description, and status code.

    Example:
        >>> response: Institutional_vs_IndividualItemResponse = {
        ...     "Data": {"IR0001234567": trades},
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["IR0001234567"]["sell_volume_individual"]
        4000
        >>> response["Status"]["State"]
        True
    """
    Data: Dict[str, institutional_vs_individual]
    Status: Status


class institutional_vs_individual_WS_symbolIsin(WebsocketBase_symbolIsin):
    """
    Websocket message structure for institutional vs individual trading data identified by ISIN.

    Attributes:
        data (institutional_vs_individual): Real-time breakdown of buy/sell activity for
            individual and institutional traders.

    Example:
        >>> ws_data: institutional_vs_individual_WS_symbolIsin = {
        ...     "channel": "inst_vs_ind_updates",
        ...     "symbolIsin": "IR0001234567",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": trades
        ... }
        >>> ws_data["data"]["buy_count_individual"]
        120
    """
    data: institutional_vs_individual


class institutional_vs_individual_WS_symbolName(WebsocketBase_symbolName):
    """
    Websocket message structure for institutional vs individual trading data identified by symbol name.

    Attributes:
        data (institutional_vs_individual): Real-time breakdown of buy/sell activity for
            individual and institutional traders.

    Example:
        >>> ws_data: institutional_vs_individual_WS_symbolName = {
        ...     "channel": "inst_vs_ind_updates",
        ...     "symbolName": "ETF001",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": trades
        ... }
        >>> ws_data["data"]["sell_count_institution"]
        50
    """
    data: institutional_vs_individual
    
# +--------------------------------------------------------------------------------------+ #


class ContractInfo(TypedDict):
    """
    Represents key contract information for derivatives, including open interest and margin requirements.

    Attributes:
        open_interest (int): Total number of outstanding contracts that have not been settled.
        initial_margin (int): Margin required to open a new position.
        required_margin (int): Margin required to maintain an existing position.

    Example:
        >>> contract: ContractInfo = {
        ...     "open_interest": 1200,
        ...     "initial_margin": 5000,
        ...     "required_margin": 4500
        ... }
        >>> contract["open_interest"]
        1200
    """
    open_interest: int
    initial_margin: int
    required_margin: int


class ContractInfoResponse(TypedDict):
    """
    Response structure for contract information from a REST API call.

    Attributes:
        Data (Dict[str, ContractInfo]): Dictionary mapping instrument identifiers (ISIN or symbolName)
                                        to their corresponding contract information.
        Status (Status): Metadata about the server response, including success state,
                         timestamp, version, author, description, and status code.

    Example:
        >>> response: ContractInfoResponse = {
        ...     "Data": {"IRFUT123456": contract},
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["IRFUT123456"]["initial_margin"]
        5000
        >>> response["Status"]["State"]
        True
    """
    Data: Dict[str, ContractInfo]
    Status: Status


class ContractInfo_WS_symbolIsin(WebsocketBase_symbolIsin):
    """
    Websocket message structure for contract information updates identified by ISIN.

    Attributes:
        data (ContractInfo): Real-time contract information for the specified instrument.

    Example:
        >>> ws_data: ContractInfo_WS_symbolIsin = {
        ...     "channel": "contract_info_updates",
        ...     "symbolIsin": "IRFUT123456",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": contract
        ... }
        >>> ws_data["data"]["required_margin"]
        4500
    """
    data: ContractInfo


class ContractInfo_WS_symbolName(WebsocketBase_symbolName):
    """
    Websocket message structure for contract information updates identified by symbol name.

    Attributes:
        data (ContractInfo): Real-time contract information for the specified instrument.

    Example:
        >>> ws_data: ContractInfo_WS_symbolName = {
        ...     "channel": "contract_info_updates",
        ...     "symbolName": "FUT001",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": contract
        ... }
        >>> ws_data["data"]["open_interest"]
        1200
    """
    data: ContractInfo

# +--------------------------------------------------------------------------------------+ #
    

class FundInfo(TypedDict):
    """
    Represents key information about a fund, including its net asset value, total units, 
    market capitalization, and the timestamp of the data.

    Attributes:
        nav (float): Net Asset Value of the fund per unit.
        units (int): Total number of fund units outstanding.
        marketCap (int): Total market capitalization of the fund.
        as_of (datetime): Timestamp indicating when the data was recorded.

    Example:
        >>> fund: FundInfo = {
        ...     "nav": 12500.0,
        ...     "units": 100000,
        ...     "marketCap": 1250000000,
        ...     "as_of": datetime(2025, 11, 19, 10, 30)
        ... }
        >>> fund["nav"]
        12500.0
    """
    nav: float
    units: int
    marketCap: int
    as_of: datetime


class FundInfoResponse(TypedDict):
    """
    Response structure for fund information from a REST API call.

    Attributes:
        Data (Dict[str, FundInfo]): Dictionary mapping fund identifiers (ISIN or symbolName)
                                    to their corresponding FundInfo.
        Status (Status): Metadata about the server response, including success state,
                         timestamp, version, author, description, and status code.

    Example:
        >>> response: FundInfoResponse = {
        ...     "Data": {"IRFND123456": fund},
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["IRFND123456"]["marketCap"]
        1250000000
        >>> response["Status"]["State"]
        True
    """
    Data: Dict[str, FundInfo]
    Status: Status


class FundInfo_WS_symbolIsin(WebsocketBase_symbolIsin):
    """
    Websocket message structure for fund information updates identified by ISIN.

    Attributes:
        data (FundInfo): Real-time fund information for the specified fund.

    Example:
        >>> ws_data: FundInfo_WS_symbolIsin = {
        ...     "channel": "fund_info_updates",
        ...     "symbolIsin": "IRFND123456",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": fund
        ... }
        >>> ws_data["data"]["units"]
        100000
    """
    data: FundInfo


class FundInfo_WS_symbolName(WebsocketBase_symbolName):
    """
    Websocket message structure for fund information updates identified by symbol name.

    Attributes:
        data (FundInfo): Real-time fund information for the specified fund.

    Example:
        >>> ws_data: FundInfo_WS_symbolName = {
        ...     "channel": "fund_info_updates",
        ...     "symbolName": "FND001",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": fund
        ... }
        >>> ws_data["data"]["nav"]
        12500.0
    """
    data: FundInfo
    
# +--------------------------------------------------------------------------------------+ #


class OHLCV_live(TypedDict):
    """
    Represents live OHLCV (Open, High, Low, Close, Volume) data for a financial instrument.

    Attributes:
        open (float): Opening price of the instrument for the current interval.
        high (float): Highest price reached during the interval.
        low (float): Lowest price reached during the interval.
        close (float): Last traded price (closing price) during the interval.
        volume (int): Total traded volume during the interval.

    Example:
        >>> ohlcv: OHLCV_live = {
        ...     "open": 12000.0,
        ...     "high": 12150.0,
        ...     "low": 11950.0,
        ...     "close": 12100.0,
        ...     "volume": 5000
        ... }
        >>> ohlcv["high"]
        12150.0
    """
    open: float
    high: float
    low: float
    close: float
    volume: int


class OHLCVLast1mResponse(TypedDict):
    """
    Response structure for the latest 1-minute OHLCV data from a REST API call.

    Attributes:
        Data (Dict[str, OHLCV_live]): Dictionary mapping instrument identifiers (ISIN or symbolName)
                                      to their corresponding OHLCV_live data.
        Status (Status): Metadata about the server response, including success state,
                         timestamp, version, author, description, and status code.

    Example:
        >>> response: OHLCVLast1mResponse = {
        ...     "Data": {"IR0001234567": ohlcv},
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["IR0001234567"]["volume"]
        5000
        >>> response["Status"]["State"]
        True
    """
    Data: Dict[str, OHLCV_live]
    Status: Status


class OHLCV_WS_symbolIsin(WebsocketBase_symbolIsin):
    """
    Websocket message structure for live OHLCV updates identified by ISIN.

    Attributes:
        data (OHLCV_live): Real-time OHLCV data for the specified instrument.

    Example:
        >>> ws_data: OHLCV_WS_symbolIsin = {
        ...     "channel": "ohlcv_updates",
        ...     "symbolIsin": "IR0001234567",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": ohlcv
        ... }
        >>> ws_data["data"]["close"]
        12100.0
    """
    data: OHLCV_live


class OHLCV_WS_symbolName(WebsocketBase_symbolName):
    """
    Websocket message structure for live OHLCV updates identified by symbol name.

    Attributes:
        data (OHLCV_live): Real-time OHLCV data for the specified instrument.

    Example:
        >>> ws_data: OHLCV_WS_symbolName = {
        ...     "channel": "ohlcv_updates",
        ...     "symbolName": "ETF001",
        ...     "timestamp": "2025-11-19T10:30:00Z",
        ...     "data": ohlcv
        ... }
        >>> ws_data["data"]["low"]
        11950.0
    """
    data: OHLCV_live
    

# +--------------------------------------------------------------------------------------+ #


class OverviewSecuritiesAndFunds(SecuritiesAndFunds):
    """
    Overview of a security or fund instrument including best limit orders, aggregated market data,
    trading breakdown by individual vs institutional investors, fund info, and contract info.

    Inherits from `SecuritiesAndFunds` and extends it with additional real-time and aggregated metrics.

    Attributes:
        BestLimit (Dict[str, BestLimitItem]): Best limit orders for this instrument by price level.
        Aggregate (Aggregate): Aggregated trading statistics for this instrument.
        institutional_vs_individual (institutional_vs_individual): Buy/sell activity breakdown 
            between individual and institutional traders.
        FundInfo (FundInfo): Net asset value, total units, and market capitalization.
        ContractInfo (ContractInfo): Derivatives contract data (if applicable).

    Example:
        >>> overview: OverviewSecuritiesAndFunds = {
        ...     "symbolIsin": "IR0001234567",
        ...     "symbolName": "ETF001",
        ...     "title": "Example ETF",
        ...     "buyCommission": 0.001,
        ...     "sellCommission": 0.001,
        ...     "minValidBuyVolume": 1,
        ...     "maxValidBuyVolume": 1000,
        ...     "minValidSellVolume": 1,
        ...     "maxValidSellVolume": 1000,
        ...     "canBuy": True,
        ...     "canSell": True,
        ...     "minAllowedPrice": 10000,
        ...     "maxAllowedPrice": 20000,
        ...     "is_ETF": True,
        ...     "baseVolume": 1,
        ...     "minDealablePrice": 10000,
        ...     "minDealableCount": 1,
        ...     "owner": "Market",
        ...     "hidePrice": 0,
        ...     "dataClass": "SecuritiesAndFunds",
        ...     "BestLimit": {"1": {"buy_order_count": 5, "buy_quantity": 1000, "buy_price": 12000, "sell_order_count": 3, "sell_quantity": 800, "sell_price": 12100}},
        ...     "Aggregate": {"date": "2025-11-19", "time": "10:30:00", "trade_count": 120, "total_volume": 5000, "total_value": 60000000, "closing_price": 12000.0, "last_price": 12100.0, "low_price": 11950.0, "high_price": 12150.0, "open_price": 12050.0, "previous_close": 11980.0},
        ...     "institutional_vs_individual": {"buy_count_individual": 120, "buy_volume_individual": 5000, "buy_count_institution": 45, "buy_volume_institution": 10000, "sell_count_individual": 100, "sell_volume_individual": 4000, "sell_count_institution": 50, "sell_volume_institution": 9000},
        ...     "FundInfo": {"nav": 12500.0, "units": 100000, "marketCap": 1250000000, "as_of": datetime(2025,11,19,10,30)},
        ...     "ContractInfo": {"open_interest": 1200, "initial_margin": 5000, "required_margin": 4500}
        ... }
        >>> overview["BestLimit"]["1"]["buy_price"]
        12000
        >>> overview["Aggregate"]["high_price"]
        12150
        >>> overview["FundInfo"]["nav"]
        12500.0
    """
    BestLimit: Dict[str, BestLimitItem]
    Aggregate: Aggregate
    institutional_vs_individual: institutional_vs_individual
    FundInfo: FundInfo
    ContractInfo: ContractInfo


class OverviewTreasuryBonds(TreasuryBonds):
    """
    Overview of a treasury bond instrument including best limit orders, aggregated market data,
    trading breakdown, fund info, and contract info.

    Inherits from `TreasuryBonds` and extends it with additional metrics.

    Attributes:
        BestLimit (Dict[str, BestLimitItem])
        Aggregate (Aggregate)
        institutional_vs_individual (institutional_vs_individual)
        FundInfo (FundInfo)
        ContractInfo (ContractInfo)
    """
    BestLimit: Dict[str, BestLimitItem]
    Aggregate: Aggregate
    institutional_vs_individual: institutional_vs_individual
    FundInfo: FundInfo
    ContractInfo: ContractInfo


class OverviewStockOptions(StockOptions):
    """
    Overview of a stock option instrument including best limit orders, aggregated market data,
    trading breakdown, fund info, and contract info.

    Inherits from `StockOptions` and extends it with additional metrics.

    Attributes:
        BestLimit (Dict[str, BestLimitItem])
        Aggregate (Aggregate)
        institutional_vs_individual (institutional_vs_individual)
        FundInfo (FundInfo)
        ContractInfo (ContractInfo)
    """
    BestLimit: Dict[str, BestLimitItem]
    Aggregate: Aggregate
    institutional_vs_individual: institutional_vs_individual
    FundInfo: FundInfo
    ContractInfo: ContractInfo


class OverviewStockFuturess(StockFutures):
    """
    Overview of a stock futures instrument including best limit orders, aggregated market data,
    trading breakdown, fund info, and contract info.

    Inherits from `StockFutures` and extends it with additional metrics.

    Attributes:
        BestLimit (Dict[str, BestLimitItem])
        Aggregate (Aggregate)
        institutional_vs_individual (institutional_vs_individual)
        FundInfo (FundInfo)
        ContractInfo (ContractInfo)
    """
    BestLimit: Dict[str, BestLimitItem]
    Aggregate: Aggregate
    institutional_vs_individual: institutional_vs_individual
    FundInfo: FundInfo
    ContractInfo: ContractInfo


class OverviewResponse:
    """
    Response structure for the comprehensive overview of multiple financial instruments.

    Attributes:
        Data (Dict[str, Optional[Union[OverviewSecuritiesAndFunds, OverviewTreasuryBonds, 
               OverviewStockOptions, OverviewStockFuturess]]]): Dictionary mapping instrument 
               identifiers (ISIN or symbolName) to their corresponding overview data. 
               Some entries may be None if data is unavailable.
        Status (Status): Metadata about the server response, including success state, timestamp,
                         version, author, description, and status code.

    Example:
        >>> overview_response: OverviewResponse = {
        ...     "Data": {"IR0001234567": overview},
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> overview_response["Data"]["IR0001234567"]["BestLimit"]["1"]["sell_price"]
        12100
        >>> overview_response["Status"]["State"]
        True
    """
    Data : Dict[
        str,Optional[
            Union[
                OverviewSecuritiesAndFunds,
                OverviewTreasuryBonds,
                OverviewStockOptions,
                OverviewStockFuturess
            ]
        ]
    ]
    Status: Status
    
# +--------------------------------------------------------------------------------------+ #
 

class OHLCV_historical(TypedDict):
    """
    Represents historical OHLCV (Open, High, Low, Close, Volume) data for a financial instrument
    over multiple timestamps.

    Attributes:
        Date_timestamp (List[int]): List of timestamps (in UNIX epoch format) for each OHLCV record.
        Open (List[Union[float, int]]): Opening prices corresponding to each timestamp.
        High (List[Union[float, int]]): Highest prices for each timestamp.
        Low (List[Union[float, int]]): Lowest prices for each timestamp.
        Close (List[Union[float, int]]): Closing prices for each timestamp.
        Volume (List[int]): Traded volume for each timestamp.
        symbolName (str): Symbol name of the instrument.
        symbolIsin (str): ISIN identifier of the instrument.

    Example:
        >>> ohlcv_hist: OHLCV_historical = {
        ...     "Date_timestamp": [1700000000, 1700000600],
        ...     "Open": [12000.0, 12100.0],
        ...     "High": [12150.0, 12200.0],
        ...     "Low": [11950.0, 12050.0],
        ...     "Close": [12100.0, 12150.0],
        ...     "Volume": [5000, 6000],
        ...     "symbolName": "ETF001",
        ...     "symbolIsin": "IR0001234567"
        ... }
        >>> ohlcv_hist["Close"][1]
        12150.0
        >>> ohlcv_hist["Volume"][0]
        5000
    """
    Date_timestamp: List[int]
    Open: List[Union[float, int]]
    High: List[Union[float, int]]
    Low: List[Union[float, int]]
    Close: List[Union[float, int]]
    Volume: List[int]
    symbolName: str
    symbolIsin: str



class OHLCVResponse(TypedDict):
    """
    Response structure for historical OHLCV data from a REST API call.

    Attributes:
        Data (OHLCV_historical): Historical OHLCV data for the specified instrument.
        Status (Status): Metadata about the server response, including success state, timestamp,
                         version, author, description, and status code.

    Example:
        >>> response: OHLCVResponse = {
        ...     "Data": ohlcv_hist,
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"]["symbolName"]
        'ETF001'
        >>> response["Data"]["High"][0]
        12150.0
        >>> response["Status"]["State"]
        True
    """
    Data: OHLCV_historical
    Status: Status

# +--------------------------------------------------------------------------------------+ #

class DividendAction(TypedDict):
    """
    Represents a dividend distribution action for a financial instrument.

    Attributes:
        Date_timestamp (int): Timestamp of the dividend action in UNIX epoch format.
        corporateAction (str): Type of corporate action (e.g., "Dividend").
        symbolName (str): Symbol name of the instrument.
        symbolIsin (str): ISIN identifier of the instrument.
        سود_تقسیم_شده (Optional[str]): Distributed dividend amount (may be None if not available).
        تاریخ (str): Human-readable date of the dividend action.

    Example:
        >>> dividend: DividendAction = {
        ...     "Date_timestamp": 1700350200,
        ...     "corporateAction": "Dividend",
        ...     "symbolName": "ETF001",
        ...     "symbolIsin": "IR0001234567",
        ...     "سود_تقسیم_شده": "1500",
        ...     "تاریخ": "2025-11-19"
        ... }
        >>> dividend["سود_تقسیم_شده"]
        '1500'
    """
    Date_timestamp: int
    corporateAction: str
    symbolName: str
    symbolIsin: str
    سود_تقسیم_شده: Optional[str]
    تاریخ: str


class CapitalIncreaseAction(TypedDict):
    """
    Represents a capital increase action for a financial instrument.

    Attributes:
        Date_timestamp (int): Timestamp of the capital increase action in UNIX epoch format.
        corporateAction (str): Type of corporate action (e.g., "Capital Increase").
        symbolName (str): Symbol name of the instrument.
        symbolIsin (str): ISIN identifier of the instrument.
        سرمایه_قبلی (Optional[str]): Previous capital amount (may be None if not available).
        سرمایه_جدید (Optional[str]): New capital amount after increase (may be None if not available).
        درصد_افزایش (Optional[str]): Percentage of capital increase (may be None if not available).
        تاریخ (str): Human-readable date of the capital increase action.

    Example:
        >>> capital_inc: CapitalIncreaseAction = {
        ...     "Date_timestamp": 1700350200,
        ...     "corporateAction": "Capital Increase",
        ...     "symbolName": "ETF002",
        ...     "symbolIsin": "IR0009876543",
        ...     "سرمایه_قبلی": "1000000",
        ...     "سرمایه_جدید": "1200000",
        ...     "درصد_افزایش": "20%",
        ...     "تاریخ": "2025-11-19"
        ... }
        >>> capital_inc["درصد_افزایش"]
        '20%'
    """
    Date_timestamp: int
    corporateAction: str
    symbolName: str
    symbolIsin: str
    سرمایه_قبلی: Optional[str]
    سرمایه_جدید: Optional[str]
    درصد_افزایش: Optional[str]
    تاریخ: str



class CorporateActionResponse(TypedDict):
    """
    Response structure for corporate actions (dividends and capital increases) from a REST API call.

    Attributes:
        Data (List[Union[DividendAction, CapitalIncreaseAction, None]]): List of corporate action records.
            Each item may represent a dividend action, a capital increase action, or None if unavailable.
        Status (Status): Metadata about the server response, including success state, timestamp,
                         version, author, description, and status code.

    Example:
        >>> response: CorporateActionResponse = {
        ...     "Data": [dividend, capital_inc, None],
        ...     "Status": {
        ...         "State": True,
        ...         "ServerTimeStamp": 1700350200.0,
        ...         "Version": "1.2.3",
        ...         "Author": "HedgeTech",
        ...         "Description": {"fa": "عملیات موفقیت‌آمیز بود", "en": "Operation successful"},
        ...         "StatusCode": 200
        ...     }
        ... }
        >>> response["Data"][0]["سود_تقسیم_شده"]
        '1500'
        >>> response["Data"][1]["سرمایه_جدید"]
        '1200000'
        >>> response["Status"]["State"]
        True
    """
    Data: List[Union[DividendAction, CapitalIncreaseAction, None]]
    Status: Status