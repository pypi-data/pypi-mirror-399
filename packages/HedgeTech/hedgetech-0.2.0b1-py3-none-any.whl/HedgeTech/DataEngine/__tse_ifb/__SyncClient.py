# ========================================|======================================== #
#                                      Imports                                      #
# ========================================|======================================== #

from threading import Event
from websockets.sync.client import connect
from json import loads
from HedgeTech.Auth import AuthSyncClient
from typing import (
    Literal,
    List,
    Union,
    Generator,
)
from .__io_types import (
    Instruments,
    OverviewResponse,
    BestLimitResponse,
    OrderBookResponse,
    AggregateResponse,
    Institutional_vs_IndividualItemResponse,
    ContractInfoResponse,
    FundInfoResponse,
    OHLCVLast1mResponse,
    
    OHLCVResponse,
    CorporateActionResponse,
    
    BestLimit_WS_symbolIsin,
    BestLimit_WS_symbolName,
    OrderBook_WS_symbolIsin,
    OrderBook_WS_symbolName,
    Aggregate_WS_symbolIsin,
    Aggregate_WS_symbolName,
    institutional_vs_individual_WS_symbolIsin,
    institutional_vs_individual_WS_symbolName,
    ContractInfo_WS_symbolIsin,
    ContractInfo_WS_symbolName,
    FundInfo_WS_symbolIsin,
    FundInfo_WS_symbolName,
    OHLCV_WS_symbolIsin,
    OHLCV_WS_symbolName,
)

# ========================================|======================================== #
#                                 Class Definitions                                 #
# ========================================|======================================== #

class DataEngine_TseIfb_SyncClient:
    
    """
    Synchronous client for interacting with the TSE-IFB (Iranian Securities Exchange) Data Engine API.

    This class provides high-level synchronous methods to retrieve live and historical market data,
    order book information, best-limit quotes, OHLCV data, fund info, corporate actions, and other
    trading-related data. It leverages an authenticated `AuthSyncClient` for authorized access.

    All methods return TypedDict objects defined in the module, providing structured data
    including:
        - Instruments, SecuritiesAndFunds, StockOptions, StockFutures, TreasuryBonds
        - BestLimit, OrderBook, Aggregate, Institutional_vs_Individual
        - ContractInfo, FundInfo, OHLCV (live and historical)
        - CorporateActions

    Attributes:
        __AuthSyncClient (AuthSyncClient): An instance of `AuthSyncClient` used to perform
            authorized synchronous HTTP requests and WebSocket connections.

    Examples:
        >>> auth_client = AuthSyncClient.login(
        ...     UserName_or_Email="user@example.com",
        ...     Password="secure_password"
        ... )
        >>> data_client = DataEngine_TseIfb_SyncClient(AuthSyncClient=auth_client)
        >>> instruments = data_client.instruments_static_info_by_name(["فملی", "خودرو"])
        >>> print(instruments["Data"]["فملی"]["symbolName"])
        >>> for update in data_client.websocket_by_name(
        ...     channels=["best-limit", "order-book"],
        ...     symbol_names=["فملی"]
        ... ):
        ...     print(update)

    Notes:
        - All network requests are synchronous and return after the server responds.
        - WebSocket methods yield streaming updates and should be used with `for` loops.
        - Exceptions (ValueError) are raised when the API returns an error or request fails.
    """
    
    def __init__(
        self,
        AuthSyncClient : AuthSyncClient,
    ):
        """
        Initialize the DataEngine_TseIfb_SyncClient with an authenticated sync client.

        Args:
            AuthSyncClient (AuthSyncClient): An instance of `AuthSyncClient` used for
                making authorized synchronous requests to the TSE-IFB data engine.
        """
        
        self.__AuthSyncClient = AuthSyncClient
        
    
    # +--------------------------------------------------------------------------------------+ #
    
    def search_instruments(
        self,
        *,
        market : Literal[
            "SecuritiesAndFunds",
            "TreasuryBonds",
            "StockOptions",
            "StockFutures",  
        ],
        Search_char : str,
    )-> Instruments:
        
        """
        Search for instruments in a specific market by name, title, or partial text (synchronous).

        Args:
            market (Literal["SecuritiesAndFunds", "TreasuryBonds", "StockOptions", "StockFutures"]):
                Determines which market group to search in.
                Each market corresponds to a specific instrument class category.
            
            Search_char (str):
                Text to search for. Can be part of the symbol name, title,
                or any searchable field related to the instrument.

        Returns:
            Instruments:
                A dictionary containing:
                    - Data: A list of matched instruments. Each item is one of:
                        * SecuritiesAndFunds
                        * TreasuryBonds
                        * StockOptions
                        * StockFutures
                        * None (when no match exists)
                    - Status: Status information returned by the API.

        Raises:
            ValueError:
                Raised when API response is not successful or contains an error message
                in the field ``detail``.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> result = client.search_instruments(
            ...     market="SecuritiesAndFunds",
            ...     Search_char="فولاد"
            ... )
            >>> print(result["Data"][0]["symbolName"])
        """
        
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/static/data/instruments/search',
            params={
                'market' : market,
                'Search_char' : Search_char
            } 
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    def instruments_static_info_by_name(self,symbol_names : List[str])-> Instruments:
        """
        Retrieve static instrument information based on a list of symbol names (synchronous).

        This endpoint returns complete static metadata for each provided symbol name,
        including instrument type, commissions, trading permissions, price limits,
        and additional attributes depending on the instrument class.

        Args:
            symbol_names (List[str]):
                A list of instrument symbol names to query.
                Each item must be an exact symbol name as recognized by TSE/IFB.

        Returns:
            Instruments:
                A dictionary containing:
                    - Data: A mapping of symbol_name → Instrument info.
                      Instrument info is one of:
                        * SecuritiesAndFunds
                        * TreasuryBonds
                        * StockOptions
                        * StockFutures
                        * None (if symbol not found)
                    - Status: General API status information.

        Raises:
            ValueError:
                Raised if the API request fails or returns an error message inside ``detail``.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> result = client.instruments_static_info_by_name(
            ...     ["فملی", "خودرو"]
            ... )
            >>> print(result["Data"]["فملی"]["symbolIsin"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/static/data/instruments/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    def instruments_static_info_by_isin(self,symbol_isins : List[str])-> Instruments:
        """
        Get static information for multiple instruments using their ISIN codes (synchronous).

        Args:
            symbol_isins (List[str]):
                A list of instrument ISIN codes. Each ISIN must be a valid symbol
                registered in TSE/IFB. The request supports multiple ISIN values.

        Returns:
            Instruments:
                A dictionary containing:
                    - Data: A list of instruments matching the provided ISINs.
                            Each item can be SecuritiesAndFunds, TreasuryBonds,
                            StockOptions, StockFutures, or None if not found.
                    - Status: Status information returned by the API.

        Raises:
            ValueError:
                Raised when the API response indicates failure or contains an
                error message in the response payload.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> result = client.instruments_static_info_by_isin([
            ...     "IRO1XYZ12345",
            ...     "IRO1ABC98765"
            ... ])
            >>> print(result["Data"][0]["symbolName"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/static/data/instruments/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_overview_by_name(self,symbol_names : List[str])-> OverviewResponse:
        """
        Retrieve the **live aggregated market overview** for a list of symbol names (synchronous).

        This endpoint provides a full real-time snapshot for each symbol, combining multiple
        live data sources—best limits, aggregate prices, institutional vs individual flow,
        fund information, and contract details—into a unified structure for each instrument.

        Args:
            symbol_names (List[str]):
                A list of symbol names whose live overview data should be fetched.
                Each name must match the exact trading symbol (e.g., "فملی", "خودرو").

        Returns:
            OverviewResponse:
                A dictionary structured as:
                    - **Data**: Mapping of symbol_name → overview object.  
                      Each overview object is one of:
                        * OverviewSecuritiesAndFunds  
                        * OverviewTreasuryBonds  
                        * OverviewStockOptions  
                        * OverviewStockFuturess  
                        * None (if symbol not found)
                      
                      Each overview entry includes:
                        - BestLimit: Real-time order-book best limits  
                        - Aggregate: Live OHLC/volume summary  
                        - institutional_vs_individual: Buy/sell breakdown  
                        - FundInfo: NAV + fund statistics  
                        - ContractInfo: Margin & open interest (if applicable)

                    - **Status**: Standard API status and metadata.

        Raises:
            ValueError:
                If the request fails or if an error is returned by the API in the `detail` field.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> overview = client.live_overview_by_name(["فملی", "شستا"])
            >>> print(overview["Data"]["فملی"]["Aggregate"]["closing_price"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/overview/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_overview_by_isin(self,symbol_isins : List[str])-> OverviewResponse:
        """
        Retrieve the **live aggregated market overview** for instruments using their ISIN codes (synchronous).

        This endpoint provides a comprehensive real-time snapshot for each requested instrument,
        combining multiple live data streams—best limits, aggregate OHLCV, institutional vs
        individual flow, fund information, and contract details—into one unified response object.

        Args:
            symbol_isins (List[str]):
                A list of instrument ISIN codes (e.g., "IRO1XYZ12345").
                Each ISIN must reference a valid tradable instrument in the TSE/IFB markets.

        Returns:
            OverviewResponse:
                A dictionary containing:
                    - **Data**: Mapping of ISIN → overview object.
                      Each overview object is one of:
                        * OverviewSecuritiesAndFunds
                        * OverviewTreasuryBonds
                        * OverviewStockOptions
                        * OverviewStockFuturess
                        * None (if the ISIN is not found)

                      Each overview contains:
                        - BestLimit: Current best bid/ask levels  
                        - Aggregate: Latest intraday market summary  
                        - institutional_vs_individual: Buy/sell breakdown  
                        - FundInfo: NAV and fund-related metrics (if applicable)  
                        - ContractInfo: Margins & open interest (if applicable)

                    - **Status**: API status information and metadata.

        Raises:
            ValueError:
                Raised when the API returns a failure response or an error description
                in the `detail` field of the payload.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> result = client.live_overview_by_isin([
            ...     "IRO1XYZ12345",
            ...     "IRO1ABC98765"
            ... ])
            >>> print(result["Data"]["IRO1XYZ12345"]["BestLimit"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/overview/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_best_limit_by_name(self,symbol_names : List[str])-> BestLimitResponse:
        """
        Retrieve **real-time best-limit (best bid/ask)** data for a list of instruments using their symbol names (synchronous).

        This endpoint returns the top-of-the-book order data, including:
        - Best bid price, quantity, and order count
        - Best ask price, quantity, and order count

        Args:
            symbol_names (List[str]):
                A list of trading symbol names (e.g., ["فملی", "خودرو"]).
                Each name must exactly match the market symbol.

        Returns:
            BestLimitResponse:
                An object containing:
                    - **Data**:  
                      Mapping of symbol_name → BestLimitItem  
                      Each BestLimitItem includes:  
                        * buy_order_count  
                        * buy_quantity  
                        * buy_price  
                        * sell_order_count  
                        * sell_quantity  
                        * sell_price  
                    - **Status**: Standard API status object.

        Raises:
            ValueError:
                If the request fails or if the API returns an error message in the `detail` field.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> bl = client.live_best_limit_by_name(["فملی"])
            >>> print(bl["Data"]["فملی"]["buy_price"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/best-limit/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_best_limit_by_isin(self,symbol_isins : List[str])-> BestLimitResponse:
        """
        Retrieve **real-time best-limit (best bid/ask)** data for a list of instruments using their ISIN codes (synchronous).

        This endpoint returns the top-of-book order metrics for each ISIN instrument.

        Args:
            symbol_isins (List[str]):
                A list of instrument ISIN codes (e.g., ["IRO1XYZ12345"]).

        Returns:
            BestLimitResponse:
                An object containing:
                    - **Data**:  
                      Mapping of symbol_isin → BestLimitItem  
                      Each BestLimitItem includes:  
                        * buy_order_count  
                        * buy_quantity  
                        * buy_price  
                        * sell_order_count  
                        * sell_quantity  
                        * sell_price  
                    - **Status**: API status metadata.

        Raises:
            ValueError:
                If the request fails or the server returns an error in the `detail` field.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> bl = client.live_best_limit_by_isin(["IRO1XYZ12345"])
            >>> print(bl["Data"]["IRO1XYZ12345"]["sell_quantity"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/best-limit/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_order_book_by_name(self,symbol_names : List[str])-> OrderBookResponse:
        """
        Fetch live order book data for instruments by symbol names (synchronous).

        Args:
            symbol_names (List[str]): List of instrument symbol names (e.g., ["فملی", "شپنا"]).

        Returns:
            OrderBookResponse: TypedDict with structure:
                {
                    "Data": {
                        "<symbol_name>": {
                            "Buy": List[OrderItem],
                            "Sell": List[OrderItem]
                        },
                        ...
                    },
                    "Status": Status
                }

                Each OrderItem contains:
                    - price (float)
                    - quantity (int)
                    - count (int)

                Status is a standard API status object.

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ob = client.live_order_book_by_name(["فملی"])
            >>> print(ob["Data"]["فملی"]["Buy"][0]["price"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/order-book/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_order_book_by_isin(self,symbol_isins : List[str])-> OrderBookResponse:
        """
        Fetch live order book data for instruments by ISIN codes (synchronous).

        Args:
            symbol_isins (List[str]): List of instrument ISIN codes (e.g., ["IRO1FOLD0001", "IRO1PASN0001"]).

        Returns:
            OrderBookResponse: TypedDict with structure:
                {
                    "Data": {
                        "<ISIN>": {
                            "Buy": List[OrderItem],
                            "Sell": List[OrderItem]
                        },
                        ...
                    },
                    "Status": Status
                }

                Each OrderItem contains:
                    - price (float)
                    - quantity (int)
                    - count (int)

                Status is a standard API status object.

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ob = client.live_order_book_by_isin(["IRO1FOLD0001"])
            >>> print(ob["Data"]["IRO1FOLD0001"]["Buy"][0]["price"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/order-book/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_aggregate_by_name(self,symbol_names : List[str])-> AggregateResponse:
        """
        Fetch live aggregate (OHLCV) data for instruments by symbol names (synchronous).

        Args:
            symbol_names (List[str]): List of instrument symbol names (for example, ["فملی", "شپنا"]).

        Returns:
            AggregateResponse: TypedDict with structure:
                {
                    "Data": {
                        "<symbol_name>": {
                            "date": str,
                            "time": str,
                            "trade_count": int,
                            "total_volume": int,
                            "total_value": int,
                            "closing_price": float,
                            "last_price": float,
                            "low_price": float,
                            "high_price": float,
                            "open_price": float,
                            "previous_close": float
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> agg = client.live_aggregate_by_name(["فملی"])
            >>> print(agg["Data"]["فملی"]["closing_price"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/aggregate/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_aggregate_by_isin(self,symbol_isins : List[str])-> AggregateResponse:
        """
        Fetch live aggregate (OHLCV) data for instruments by ISIN codes (synchronous).

        Args:
            symbol_isins (List[str]): List of instrument ISIN codes (for example, ["IRO1FOLD0001", "IRO1PASN0001"]).

        Returns:
            AggregateResponse: TypedDict with structure:
                {
                    "Data": {
                        "<ISIN>": {
                            "date": str,
                            "time": str,
                            "trade_count": int,
                            "total_volume": int,
                            "total_value": int,
                            "closing_price": float,
                            "last_price": float,
                            "low_price": float,
                            "high_price": float,
                            "open_price": float,
                            "previous_close": float
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> agg = client.live_aggregate_by_isin(["IRO1FOLD0001"])
            >>> print(agg["Data"]["IRO1FOLD0001"]["closing_price"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/aggregate/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_institutional_vs_individual_by_name(self,symbol_names : List[str])-> Institutional_vs_IndividualItemResponse:
        """
        Fetch real-time buy/sell statistics for institutional vs individual investors by symbol names (synchronous).

        Args:
            symbol_names (List[str]): List of instrument symbol names (for example, ["فملی", "شپنا"]).

        Returns:
            Institutional_vs_IndividualItemResponse: TypedDict with structure:
                {
                    "Data": {
                        "<symbol_name>": {
                            "buy_count_individual": int,
                            "buy_volume_individual": int,
                            "buy_count_institution": int,
                            "buy_volume_institution": int,
                            "sell_count_individual": int,
                            "sell_volume_individual": int,
                            "sell_count_institution": int,
                            "sell_volume_institution": int
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> stats = client.live_institutional_vs_individual_by_name(["فملی"])
            >>> print(stats["Data"]["فملی"]["buy_volume_institution"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/institutional-vs-individual/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_institutional_vs_individual_by_isin(self,symbol_isins : List[str])-> Institutional_vs_IndividualItemResponse:
        """
        Fetch real-time buy/sell statistics for institutional vs individual investors by ISIN codes (synchronous).

        Args:
            symbol_isins (List[str]): List of instrument ISIN codes (for example, ["IRO1FOLD0001", "IRO1PASN0001"]).

        Returns:
            Institutional_vs_IndividualItemResponse: TypedDict with structure:
                {
                    "Data": {
                        "<ISIN>": {
                            "buy_count_individual": int,
                            "buy_volume_individual": int,
                            "buy_count_institution": int,
                            "buy_volume_institution": int,
                            "sell_count_individual": int,
                            "sell_volume_individual": int,
                            "sell_count_institution": int,
                            "sell_volume_institution": int
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> stats = client.live_institutional_vs_individual_by_isin(["IRO1FOLD0001"])
            >>> print(stats["Data"]["IRO1FOLD0001"]["buy_volume_institution"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/institutional-vs-individual/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_contract_info_by_name(self,symbol_names : List[str])-> ContractInfoResponse:
        """
        Fetch real-time contract information (margins and open interest) for instruments by symbol names (synchronous).

        Args:
            symbol_names (List[str]): List of instrument symbol names (for example, ["فملی", "شپنا"]).

        Returns:
            ContractInfoResponse: TypedDict with structure:
                {
                    "Data": {
                        "<symbol_name>": {
                            "open_interest": int,
                            "initial_margin": int,
                            "required_margin": int
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ci = client.live_contract_info_by_name(["فملی"])
            >>> print(ci["Data"]["فملی"]["required_margin"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/contract-info/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_contract_info_by_isin(self,symbol_isins : List[str])-> ContractInfoResponse:
        """
        Fetch real-time contract information (margins and open interest) for instruments by ISIN codes (synchronous).

        Args:
            symbol_isins (List[str]): List of instrument ISIN codes (for example, ["IRO1FOLD0001", "IRO1PASN0001"]).

        Returns:
            ContractInfoResponse: TypedDict with structure:
                {
                    "Data": {
                        "<ISIN>": {
                            "open_interest": int,
                            "initial_margin": int,
                            "required_margin": int
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ci = client.live_contract_info_by_isin(["IRO1FOLD0001"])
            >>> print(ci["Data"]["IRO1FOLD0001"]["required_margin"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/contract-info/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_fund_info_by_name(self,symbol_names : List[str])-> FundInfoResponse:
        """
        Fetch real-time fund information for a list of instruments by symbol names (synchronous).

        Args:
            symbol_names (List[str]): List of instrument symbol names (for example, ["صندوق_مثالی1", "صندوق_مثالی2"]).

        Returns:
            FundInfoResponse: TypedDict with structure:
                {
                    "Data": {
                        "<symbol_name>": {
                            "nav": float,
                            "units": int,
                            "marketCap": int,
                            "as_of": datetime
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> fund_info = client.live_fund_info_by_name(["صندوق_مثالی1"])
            >>> print(fund_info["Data"]["صندوق_مثالی1"]["nav"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/fund-info/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_fund_info_by_isin(self,symbol_isins : List[str])-> FundInfoResponse:
        """
        Fetch real-time fund information for a list of instruments by ISIN codes (synchronous).

        Args:
            symbol_isins (List[str]): List of instrument ISIN codes (for example, ["IRO1FUND0001", "IRO1FUND0002"]).

        Returns:
            FundInfoResponse: TypedDict with structure:
                {
                    "Data": {
                        "<ISIN>": {
                            "nav": float,
                            "units": int,
                            "marketCap": int,
                            "as_of": datetime
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> fund_info = client.live_fund_info_by_isin(["IRO1FUND0001"])
            >>> print(fund_info["Data"]["IRO1FUND0001"]["nav"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/fund-info/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def live_ohlcv_last1m_by_name(self,symbol_names : List[str])-> OHLCVLast1mResponse:
        """
        Retrieve the last 1-minute OHLCV (Open, High, Low, Close, Volume) data for a list of instruments by symbol names (synchronous).

        Args:
            symbol_names (List[str]): List of trading symbol names (for example, ["فملی", "خودرو"]).

        Returns:
            OHLCVLast1mResponse: TypedDict with structure:
                {
                    "Data": {
                        "<symbol_name>": {
                            "open": float,
                            "high": float,
                            "low": float,
                            "close": float,
                            "volume": int
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ohlcv = client.live_ohlcv_last1m_by_name(["فملی"])
            >>> print(ohlcv["Data"]["فملی"]["close"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/ohlcv-last-1m/symbol/name',
            params=[('symbol_names', name) for name in symbol_names]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def live_ohlcv_last1m_by_isin(self,symbol_isins : List[str])-> OHLCVLast1mResponse:
        """
        Retrieve the last 1-minute OHLCV (Open, High, Low, Close, Volume) data for a list of instruments by ISIN codes (synchronous).

        Args:
            symbol_isins (List[str]): List of instrument ISIN codes (for example, ["IRO1FOLD0001", "IRO1PASN0001"]).

        Returns:
            OHLCVLast1mResponse: TypedDict with structure:
                {
                    "Data": {
                        "<ISIN>": {
                            "open": float,
                            "high": float,
                            "low": float,
                            "close": float,
                            "volume": int
                        },
                        ...
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ohlcv = client.live_ohlcv_last1m_by_isin(["IRO1FOLD0001"])
            >>> print(ohlcv["Data"]["IRO1FOLD0001"]["close"])
        """
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/live/data/instruments/ohlcv-last-1m/symbol/isin',
            params=[('symbol_isins', isin) for isin in symbol_isins]
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def historical_ohlcv_by_name(
        self,
        *,
        symbol_name : str,
        start_timestamp : int,
        end_timestamp : int,
        AdjustedPrice : bool,
        Resolution : Literal["1m","5m","15m","30m","1h","D","W","M",]
    )-> OHLCVResponse:
        
        """
        Fetch historical OHLCV (Open, High, Low, Close, Volume) data for a given instrument by symbol name (synchronous).

        Args:
            symbol_name (str): Trading symbol name (e.g., "فملی").
            start_timestamp (int): Unix timestamp for the start of the requested period.
            end_timestamp (int): Unix timestamp for the end of the requested period.
            AdjustedPrice (bool): Whether to return adjusted prices (True) or raw prices (False).
            Resolution (Literal): Data resolution. Options:
                - "1m", "5m", "15m", "30m", "1h" for intraday  
                - "D" for daily  
                - "W" for weekly  
                - "M" for monthly  

        Returns:
            OHLCVResponse: TypedDict with structure:
                {
                    "Data": {
                        "Date_timestamp": List[int],
                        "Open": List[float|int],
                        "High": List[float|int],
                        "Low": List[float|int],
                        "Close": List[float|int],
                        "Volume": List[int],
                        "symbolName": str,
                        "symbolIsin": str
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ohlcv = client.historical_ohlcv_by_name(
            ...     symbol_name="فملی",
            ...     start_timestamp=1690000000,
            ...     end_timestamp=1690100000,
            ...     AdjustedPrice=True,
            ...     Resolution="1h"
            ... )
            >>> print(ohlcv["Data"]["Close"])
        """
        
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/historical/data/instruments/ohlcv/symbol/name',
            params={
                'symbolName' : symbol_name,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
                'AdjustedPrice' : AdjustedPrice,
                'Resolution' : Resolution,
            }
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def historical_ohlcv_by_isin(
        self,
        *,
        symbol_isin : str,
        start_timestamp : int,
        end_timestamp : int,
        AdjustedPrice : bool,
        Resolution : Literal["1m","5m","15m","30m","1h","D","W","M",]
    )-> OHLCVResponse:
        """
        Fetch historical OHLCV (Open, High, Low, Close, Volume) data for a given instrument by ISIN code (synchronous).

        Args:
            symbol_isin (str): Instrument ISIN code (e.g., "IRO1FOLD0001").
            start_timestamp (int): Unix timestamp for the start of the requested period.
            end_timestamp (int): Unix timestamp for the end of the requested period.
            AdjustedPrice (bool): Whether to return adjusted prices (True) or raw prices (False).
            Resolution (Literal): Data resolution. Options:
                - "1m", "5m", "15m", "30m", "1h" for intraday  
                - "D" for daily  
                - "W" for weekly  
                - "M" for monthly  

        Returns:
            OHLCVResponse: TypedDict with structure:
                {
                    "Data": {
                        "Date_timestamp": List[int],
                        "Open": List[float|int],
                        "High": List[float|int],
                        "Low": List[float|int],
                        "Close": List[float|int],
                        "Volume": List[int],
                        "symbolName": str,
                        "symbolIsin": str
                    },
                    "Status": Status
                }

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> ohlcv = client.historical_ohlcv_by_isin(
            ...     symbol_isin="IRO1FOLD0001",
            ...     start_timestamp=1690000000,
            ...     end_timestamp=1690100000,
            ...     AdjustedPrice=True,
            ...     Resolution="1h"
            ... )
            >>> print(ohlcv["Data"]["Close"])
        """
        
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/historical/data/instruments/ohlcv/symbol/isin',
            params={
                'isin' : symbol_isin,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
                'AdjustedPrice' : AdjustedPrice,
                'Resolution' : Resolution,
            }
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
        
    def historical_corporateactions_by_name(
        self,
        *,
        symbol_name : str,
        start_timestamp : int,
        end_timestamp : int,
    )-> CorporateActionResponse:
        """
        Fetch historical corporate actions (dividends and capital increases) for a given instrument by symbol name (synchronous).

        Args:
            symbol_name (str): Trading symbol name (e.g., "فملی").
            start_timestamp (int): Unix timestamp marking the start of the requested period.
            end_timestamp (int): Unix timestamp marking the end of the requested period.

        Returns:
            CorporateActionResponse: TypedDict with structure:
                {
                    "Data": List[Union[DividendAction, CapitalIncreaseAction, None]],
                    "Status": Status
                }
            Each item in Data includes fields such as:
                - Date_timestamp: int
                - corporateAction: str
                - symbolName: str
                - symbolIsin: str
                - سود_تقسیم_شده (optional for DividendAction)
                - سرمایه_قبلی, سرمایه_جدید, درصد_افزایش (optional for CapitalIncreaseAction)
                - تاریخ: str

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> actions = client.historical_corporateactions_by_name(
            ...     symbol_name="فملی",
            ...     start_timestamp=1690000000,
            ...     end_timestamp=1690100000
            ... )
            >>> print(actions["Data"][0]["corporateAction"])
        """
        
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/historical/data/instruments/corporateactions/symbol/name',
            params={
                'symbolName' : symbol_name,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
            }
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    def historical_corporateactions_by_isin(
        self,
        *,
        symbol_isin : str,
        start_timestamp : int,
        end_timestamp : int,
    )-> CorporateActionResponse:
        
        """
        Fetch historical corporate actions (dividends and capital increases) for a given instrument by ISIN code (synchronous).

        Args:
            symbol_isin (str): Instrument ISIN code (e.g., "IRO1FOLD0001").
            start_timestamp (int): Unix timestamp marking the start of the requested period.
            end_timestamp (int): Unix timestamp marking the end of the requested period.

        Returns:
            CorporateActionResponse: TypedDict with structure:
                {
                    "Data": List[Union[DividendAction, CapitalIncreaseAction, None]],
                    "Status": Status
                }
            Each item in Data includes fields such as:
                - Date_timestamp: int
                - corporateAction: str
                - symbolName: str
                - symbolIsin: str
                - سود_تقسیم_شده (optional for DividendAction)
                - سرمایه_قبلی, سرمایه_جدید, درصد_افزایش (optional for CapitalIncreaseAction)
                - تاریخ: str

        Raises:
            ValueError: If the HTTP request fails or the API returns an error.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> actions = client.historical_corporateactions_by_isin(
            ...     symbol_isin="IRO1FOLD0001",
            ...     start_timestamp=1690000000,
            ...     end_timestamp=1690100000
            ... )
            >>> print(actions["Data"][0]["corporateAction"])
        """
        
        data = self.__AuthSyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/data-engine/tse-ifb/historical/data/instruments/corporateactions/symbol/isin',
            params={
                'isin' : symbol_isin,
                'start_timestamp' : start_timestamp,
                'end_timestamp' : end_timestamp,
            }
        )
        
        if data.is_success :
            
            return data.json()
        
        else :
            
            raise ValueError(data.json().get('detail'))
        
    # +--------------------------------------------------------------------------------------+ #
    
    def websocket_by_name(
        self,
        channels: List[
            Literal[
                'best-limit',
                'order-book',
                'ohlcv-last-1m',
                'aggregate',
                'institutional-vs-individual',
                'contract-info',
                'fund-info',
            ]
        ],
        symbol_names: List[str],
        event: Event | None = None,
    )-> Generator[
        Union[
            BestLimit_WS_symbolName,
            OrderBook_WS_symbolName,
            Aggregate_WS_symbolName,
            institutional_vs_individual_WS_symbolName,
            ContractInfo_WS_symbolName,
            FundInfo_WS_symbolName,
            OHLCV_WS_symbolName,
        ],
        None,
        None
    ]:
        
        """
        WebSocket streaming is not available in the synchronous version.

        The synchronous client does not support real-time WebSocket subscriptions.
        Although the method signature exists to maintain interface compatibility,
        it cannot provide live updates like the asynchronous client.

        Args:
            channels (List[str]):
                List of channels to subscribe to. Possible values are:
                    - 'best-limit'
                    - 'order-book'
                    - 'ohlcv-last-1m'
                    - 'aggregate'
                    - 'institutional-vs-individual'
                    - 'contract-info'
                    - 'fund-info'
            symbol_names (List[str]):
                List of trading symbol names to receive updates for (e.g., ["فملی", "خودرو"]).
            event (Event | None, optional):
                Optional event object to mimic the async interface. 
                It has no effect in the synchronous client.

        Returns:
            Generator:
                This generator does not yield any data in the synchronous client.
                Use `DataEngine_TseIfb_AsyncClient.websocket_by_name` for streaming data.

        Raises:
            NotImplementedError:
                Always raised to indicate that real-time WebSocket streaming
                is not supported in the synchronous version.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> for update in client.websocket_by_name(
            ...     channels=["best-limit", "order-book"],
            ...     symbol_names=["فملی"]
            ... ):
            ...     print(update)  # This will not run; method is not implemented
        """
        
        if event is None :
            event = Event()
            event.set()
        
        with connect(
            uri=(
                f"wss://core.hedgetech.ir/data-engine/tse-ifb/live/data/websocket/symbol/name?"
                + "&".join(f"channels={c}" for c in channels)
                + "&" + "&".join(f"symbol_names={s}" for s in symbol_names)
            ),
            additional_headers=self.__AuthSyncClient.token
        ) as ws:
                        
            while event.is_set():
                
                try : 
                    yield loads(ws.recv())
                except : 
                    ws.close()
                    break
    
    
    # +--------------------------------------------------------------------------------------+ #
    
    def websocket_by_isin(
        self,
        channels: List[
            Literal[
                'best-limit',
                'order-book',
                'ohlcv-last-1m',
                'aggregate',
                'institutional-vs-individual',
                'contract-info',
                'fund-info',
            ]
        ],
        symbol_isins: List[str],
        event: Event | None = None,
    )-> Generator[
        Union[
            BestLimit_WS_symbolIsin,
            OrderBook_WS_symbolIsin,
            Aggregate_WS_symbolIsin,
            institutional_vs_individual_WS_symbolIsin,
            ContractInfo_WS_symbolIsin,
            FundInfo_WS_symbolIsin,
            OHLCV_WS_symbolIsin,
        ],
        None,
        None
    ]:
        """
        WebSocket streaming is not available in the synchronous version.

        The synchronous client does not support real-time WebSocket subscriptions
        by ISIN codes. This method exists to maintain interface consistency with
        the asynchronous client but does not yield any live updates.

        Args:
            channels (List[str]):
                List of channels to subscribe to. Possible values are:
                    - 'best-limit'
                    - 'order-book'
                    - 'ohlcv-last-1m'
                    - 'aggregate'
                    - 'institutional-vs-individual'
                    - 'contract-info'
                    - 'fund-info'
            symbol_isins (List[str]):
                List of instrument ISIN codes to receive updates for 
                (e.g., ["IR1234567890", "IR0987654321"]).
            event (Event | None, optional):
                Optional event object to mimic the async interface. 
                It has no effect in the synchronous client.

        Returns:
            Generator:
                This generator does not yield any data in the synchronous client.
                Use `DataEngine_TseIfb_AsyncClient.websocket_by_isin` for real-time streaming.

        Raises:
            NotImplementedError:
                Always raised to indicate that WebSocket streaming is not supported
                in the synchronous client.

        Example:
            >>> client = DataEngine_TseIfb_SyncClient(auth_client)
            >>> for update in client.websocket_by_isin(
            ...     channels=["best-limit", "order-book"],
            ...     symbol_isins=["IR1234567890"]
            ... ):
            ...     print(update)  # This will not run; method is not implemented
        """

        if event is None :
            event = Event()
            event.set()
        
        with connect(
            uri=(
                f"wss://core.hedgetech.ir/data-engine/tse-ifb/live/data/websocket/symbol/isin?"
                + "&".join(f"channels={c}" for c in channels)
                + "&" + "&".join(f"symbol_isins={s}" for s in symbol_isins)
            ),
            additional_headers=self.__AuthSyncClient.token
        ) as ws:
            
            while event.is_set():
                
                try : 
                    yield loads(ws.recv())
                except : 
                    ws.close()
                    break