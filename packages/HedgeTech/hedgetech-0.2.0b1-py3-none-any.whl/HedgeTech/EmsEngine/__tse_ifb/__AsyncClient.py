# ========================================|======================================== #
#                                      Imports                                      #
# ========================================|======================================== #

from typing import (
    Literal,
)
from .__io_types import (
    HexUUID,
    OrderStatus,
)
from HedgeTech.Auth import AuthAsyncClient
from PIL.Image import open as image_open
from PIL.ImageFile import ImageFile
from io import BytesIO

# ========================================|======================================== #
#                                 Class Definitions                                 #
# ========================================|======================================== #
class Order:
    
    def __init__(
        self,
        *,
        order_uuid : HexUUID,
        AuthASyncClient : AuthAsyncClient,
        Order_ValidityType : Literal[
            'DAY',
            'GTC', # Good Till Cancelled
            'GTD', # Good Till Date
            'FAK', # Fill And Kill
            'FOK', # Fill Or Kill
        ] = 'DAY',
        ValidityDate : int = 0,
        SymbolNameOrIsin : str,
        Price : int,
        Volume :int,
    ):
        
        self.__AuthASyncClient = AuthASyncClient
        self.__order_uuid : HexUUID = order_uuid
        self.ValidityType : str = Order_ValidityType
        self.ValidityDate : int = ValidityDate
        self.SymbolNameOrIsin : str = SymbolNameOrIsin
        self.Price : int = Price 
        self.Volume : int = Volume
        self.is_deleted : bool = False
        

    # +--------------------------------------------------------------------------------------+ #
    
    async def Edit(
        self,
        *,
        Order_ValidityType : Literal[
            'DAY',
            'GTC', # Good Till Cancelled
            'GTD', # Good Till Date
            'FAK', # Fill And Kill
            'FOK', # Fill Or Kill
        ] = 'DAY',
        ValidityDate : int = 0,
        Price : int,
        Volume :int,
    )-> None:
        
        Edit_response = await self.__AuthASyncClient.httpx_Client.patch(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/order/edit',
            data={
                'order_uuid' : self.__order_uuid,
                'Order_ValidityType' : Order_ValidityType,
                'ValidityDate' : ValidityDate,
                'Price' : Price,
                'Volume' : Volume
            }
        )
        
        
        match Edit_response.status_code:
            
            case 200:
                
                Edit_response = Edit_response.json()
                
                self.__order_uuid = Edit_response['Data']['order_uuid']
                self.ValidityType = Edit_response['Data']['order_validity_type']
                self.ValidityDate = ValidityDate
                self.Price = Edit_response['Data']['order_price']
                self.Volume = Edit_response['Data']['order_volume']
                
            case 400:
                
                raise ValueError(Edit_response.json()['detail']['Status']['Description']['en'])
                
            case _ :
                
                raise ValueError(Edit_response.text)
            
    # +--------------------------------------------------------------------------------------+ #
    @property
    async def Status(self)-> OrderStatus:
        
        status_respnse = await self.__AuthASyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/order/status',
            params={'order_uuid' : self.__order_uuid}
        )
        
        match status_respnse.status_code :
            
            case 200:
                
                return status_respnse.json()['Data']
                
            case 400:
                
                raise ValueError(status_respnse.json()['detail']['Status']['Description']['en'])

            case _ :
                
                raise ValueError(status_respnse.text)
            
    # +--------------------------------------------------------------------------------------+ #
    
    @property
    async def order_is_valid(self)-> bool:
        
        status = await self.Status
        
        if (status['Price'] == self.Price) and (
            status['Volume'] == self.Volume
        ) and (status['ValidityType'] == self.ValidityType) and status['OrderInQueue']:
            
            return True
        
        else : return False
    
    # +--------------------------------------------------------------------------------------+ #
    
    @property
    async def Delete(self)-> bool :
        
        Delete_respnse =  await self.__AuthASyncClient.httpx_Client.delete(
            url= 'https://core.hedgetech.ir/ems-engine/tse-ifb/order/delete',
            params={'order_uuid' : self.__order_uuid}
        )
        

        match Delete_respnse.status_code :
            
            case 200:
                
                self.is_deleted = True
                
            case 400:
                
                raise ValueError(Delete_respnse.json()['detail']['Status']['Description']['en'])
        
            case _ :
                
                raise ValueError(Delete_respnse.text)
    

# ================================================================================= #

class EmsEngine_TseIfb_ASyncClient:
    
    def __init__(
        self,
        AuthASyncClient : AuthAsyncClient,
    ):
        
        
        self.__AuthASyncClient = AuthASyncClient
        
        self.Customer_FullName : str | None = None
        self.Customer_TSEBourseCode : str | None = None
        self.oms_session : str | None = None
        
    # +--------------------------------------------------------------------------------------+ #
    
    
    async def Get_Captcha(
        self,
        OMS : Literal[
            'Omex | Parsian',
            'Sahra | Karamad',
        ]
    )-> ImageFile:
        
        Captcha = await self.__AuthASyncClient.httpx_Client.get(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/oms/login',
            params={'oms' : OMS }
        )
        
        if Captcha.status_code == 200: return image_open(BytesIO(Captcha.content))
        
        else : raise ValueError(Captcha.json()['detail']['Status']['Description']['en'])
    
    
    # +--------------------------------------------------------------------------------------+ #
    
    async def oms_login(
        self,
        username: str,
        password: str,
        captcha_value: str,
    ) -> None :

        response = await self.__AuthASyncClient.httpx_Client.post(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/oms/login',
            data={
                'username' : username,
                'Password' : password,
                'Captcha_Value' : captcha_value
            },
        )
        
        match response.status_code :
            
            case 200 :
                
                data = response.json()

                self.Customer_FullName = data['Data']['Customer_FullName']
                self.Customer_TSEBourseCode = data['Data']['Customer_TSEBourseCode']
                self.oms_session = data['Data']['oms_session']

                return None
                
            case 400 :
                
                raise ValueError(response.json()['detail']['Status']['Description']['en'])

            case _ :
                
                raise ValueError(response.text)
            
    # +--------------------------------------------------------------------------------------+ #
    
    
    async def Buy_by_Name(
        self,
        *,
        Order_ValidityType : Literal[
            'DAY',
            'GTC', # Good Till Cancelled
            'GTD', # Good Till Date
            'FAK', # Fill And Kill
            'FOK', # Fill Or Kill
        ] = 'DAY',
        ValidityDate : int = 0,
        symbolName : str,
        Price : int,
        Volume :int,
    )-> Order:
        
        order_response = await self.__AuthASyncClient.httpx_Client.post(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/order/new/buy/name',
            data={
                'oms_session' : self.oms_session,
                'Order_ValidityType' : Order_ValidityType,
                'ValidityDate' : ValidityDate,
                'symbolName' : symbolName,
                'Price' : Price,
                'Volume' : Volume
            }
        )
        
        match order_response.status_code:
            
            
            case 200:
                
                order_response = order_response.json()
                
                return Order(
                    order_uuid=order_response['Data']['order_uuid'],
                    AuthSyncClient=self.__AuthASyncClient,
                    Order_ValidityType=Order_ValidityType,
                    ValidityDate=ValidityDate,
                    SymbolNameOrIsin = symbolName,
                    Price=Price,
                    Volume=Volume
                )
                
            case 400:
                
                raise ValueError(order_response.json()['detail']['Status']['Description']['en'])
                
            case _ :
                
                raise ValueError(order_response.text)
                        

    # +--------------------------------------------------------------------------------------+ #
    
    
    async def Sell_by_Name(
        self,
        *,
        Order_ValidityType : Literal[
            'DAY',
            'GTC', # Good Till Cancelled
            'GTD', # Good Till Date
            'FAK', # Fill And Kill
            'FOK', # Fill Or Kill
        ] = 'DAY',
        ValidityDate : int = 0,
        symbolName : str,
        Price : int,
        Volume :int,
    )-> Order:
        
        order_response = await self.__AuthASyncClient.httpx_Client.post(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/order/new/sell/name',
            data={
                'oms_session' : self.oms_session,
                'Order_ValidityType' : Order_ValidityType,
                'ValidityDate' : ValidityDate,
                'symbolName' : symbolName,
                'Price' : Price,
                'Volume' : Volume
            }
        )
        
        match order_response.status_code:
            
            
            case 200:
                
                order_response = order_response.json()
                
                return Order(
                    order_uuid=order_response['Data']['order_uuid'],
                    AuthSyncClient=self.__AuthASyncClient,
                    Order_ValidityType=Order_ValidityType,
                    ValidityDate=ValidityDate,
                    SymbolNameOrIsin = symbolName,
                    Price=Price,
                    Volume=Volume
                )
                
            case 400:
                
                raise ValueError(order_response.json()['detail']['Status']['Description']['en'])
                
            case _ :
                
                raise ValueError(order_response.text)
        
    # +--------------------------------------------------------------------------------------+ #

    async def Buy_by_isin(
        self,
        *,
        Order_ValidityType : Literal[
            'DAY',
            'GTC', # Good Till Cancelled
            'GTD', # Good Till Date
            'FAK', # Fill And Kill
            'FOK', # Fill Or Kill
        ] = 'DAY',
        ValidityDate : int = 0,
        symbolIsin : str,
        Price : int,
        Volume :int,
    )-> Order:
        
        order_response = await self.__AuthASyncClient.httpx_Client.post(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/order/new/buy/isin',
            data={
                'oms_session' : self.oms_session,
                'Order_ValidityType' : Order_ValidityType,
                'ValidityDate' : ValidityDate,
                'symbolIsin' : symbolIsin,
                'Price' : Price,
                'Volume' : Volume
            }
        )
        
        match order_response.status_code:
            
            
            case 200:
                
                order_response = order_response.json()
                
                return Order(
                    order_uuid=order_response['Data']['order_uuid'],
                    AuthSyncClient=self.__AuthASyncClient,
                    Order_ValidityType=Order_ValidityType,
                    ValidityDate=ValidityDate,
                    SymbolNameOrIsin = symbolIsin,
                    Price=Price,
                    Volume=Volume
                )
                
            case 400:
                
                raise ValueError(order_response.json()['detail']['Status']['Description']['en'])
                
            case _ :
                
                raise ValueError(order_response.text)
        
        
    # +--------------------------------------------------------------------------------------+ #
    
    async def Sell_by_isin(
        self,
        *,
        Order_ValidityType : Literal[
            'DAY',
            'GTC', # Good Till Cancelled
            'GTD', # Good Till Date
            'FAK', # Fill And Kill
            'FOK', # Fill Or Kill
        ] = 'DAY',
        ValidityDate : int = 0,
        symbolIsin : str,
        Price : int,
        Volume :int,
    )-> Order:
        
        order_response = await self.__AuthASyncClient.httpx_Client.post(
            url='https://core.hedgetech.ir/ems-engine/tse-ifb/order/new/sell/isin',
            data={
                'oms_session' : self.oms_session,
                'Order_ValidityType' : Order_ValidityType,
                'ValidityDate' : ValidityDate,
                'symbolIsin' : symbolIsin,
                'Price' : Price,
                'Volume' : Volume
            }
        )
        
        match order_response.status_code:
            
            
            case 200:
                
                order_response = order_response.json()
                
                return Order(
                    order_uuid=order_response['Data']['order_uuid'],
                    AuthSyncClient=self.__AuthASyncClient,
                    Order_ValidityType=Order_ValidityType,
                    ValidityDate=ValidityDate,
                    SymbolNameOrIsin = symbolIsin,
                    Price=Price,
                    Volume=Volume
                )
                
            case 400:
                
                raise ValueError(order_response.json()['detail']['Status']['Description']['en'])
                
            case _ :
                
                raise ValueError(order_response.text)
        
    # +--------------------------------------------------------------------------------------+ #
            