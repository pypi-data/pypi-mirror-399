# ========================================|======================================== #
#                                      Imports                                      #
# ========================================|======================================== #

from httpx import (
    AsyncClient ,
    Timeout ,
)
from jwt import decode

# ========================================|======================================== #
#                                 Class Definitions                                 #
# ========================================|======================================== #

class AuthAsyncClient:
    """
    Asynchronous client for interacting with the HedgeTech API using JWT-based authentication.

    This class provides a high-level interface to authenticate users, manage JWT tokens, 
    and make authorized HTTP requests using an `httpx.AsyncClient`.

    Attributes:
        httpx_Client (AsyncClient): An instance of `httpx.AsyncClient` configured with authentication headers.
        token (dict[str, str]): Dictionary containing authentication tokens, typically including 'Authorization'.

    Example:
        >>> client = await AuthAsyncClient.login(
        ...     UserName_or_Email="user@example.com",
        ...     Password="secure_password"
        ... )
        >>> client.token['Authorization'][:10]
        'eyJ0eXAiOi'
        >>> client.Permissions  # Decoded JWT payload
        {'sub': 'user_id', 'exp': 1700350200, ...}
    """
    
    def __init__(
        self,
        *,
        httpx_Client:AsyncClient,
        token:dict[str,str],
    ):
        """
        Initialize the AuthAsyncClient with an existing httpx.AsyncClient and authentication token.

        Args:
            httpx_Client (AsyncClient): Preconfigured AsyncClient for making authorized requests.
            token (dict[str, str]): Dictionary containing authentication tokens.
        """
        
        self.httpx_Client : AsyncClient = httpx_Client
        self.token : dict[str,str] = token
        
        self.UpdatePermission
    
    
    @property
    def UpdatePermission(self)-> None:
        
        """
        Decodes the JWT 'Authorization' token to extract user permissions.

        Raises:
            ValueError: If the JWT cannot be decoded.
        """
        
        try : 
        
            self.Permissions = decode(
                jwt=self.token['Authorization'].encode(),
                algorithms='HS256',
                options={"verify_signature": False},
            )
            
        except Exception as e:
            
            raise ValueError(e)
            
        
    @classmethod
    async def login(
        cls,
        *,
        UserName_or_Email : str,
        Password : str
    )-> "AuthAsyncClient":
        
        """
        Authenticate a user and return an instance of `AuthAsyncClient`.

        This method performs the login request to the HedgeTech API, retrieves JWT tokens,
        and configures an `httpx.AsyncClient` with authentication headers and cookies.

        Args:
            UserName_or_Email (str): The username or email of the user.
            Password (str): The user's password.

        Returns:
            AuthAsyncClient: An initialized client ready to make authorized requests.

        Raises:
            ValueError: If the login attempt fails (e.g., wrong credentials).

        Example:
            >>> client = await AuthAsyncClient.login(
            ...     UserName_or_Email="user@example.com",
            ...     Password="secure_password"
            ... )
            >>> client.token['Authorization'][:10]
            'eyJ0eXAiOi'
        """
        
        httpx_Client = AsyncClient(verify=True ,http1=False ,http2=True)
        
        login_res = await httpx_Client.post(
            url='https://core.hedgetech.ir/auth/user/token/issue',
            data={
                'UserName_or_Email' : UserName_or_Email,
                'Password' : Password
            }
        )
        
        if login_res.status_code == 201:
            
            token = login_res.json()
            headers = {'origin'  : 'https://core.hedgetech.ir'}
            headers.update(token)
            
            httpx_Client = AsyncClient(
                verify=True ,
                http1=False ,
                http2=True ,
                headers=headers,
                cookies=httpx_Client.cookies,
                timeout=Timeout(
                    connect=.5,
                    read=1,
                    write=1,
                    pool=.5,
                ),
            )
            
            return cls(
                httpx_Client = httpx_Client,
                token = token
            )
        
        else :
            
            raise ValueError(login_res.json().get('detail'))