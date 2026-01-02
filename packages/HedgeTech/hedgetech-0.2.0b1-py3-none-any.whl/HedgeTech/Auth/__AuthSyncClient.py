# ========================================|======================================== #
#                                      Imports                                      #
# ========================================|======================================== #

from httpx import (
    Client ,
    Timeout ,
)
from jwt import decode

# ========================================|======================================== #
#                                 Class Definitions                                 #
# ========================================|======================================== #


class AuthSyncClient:
    """
    Synchronous client for interacting with the HedgeTech API using JWT-based authentication.

    This class provides a high-level interface to authenticate users, manage JWT tokens, 
    and make authorized HTTP requests using an `httpx.Client`.

    Attributes:
        httpx_Client (Client): An instance of `httpx.Client` configured with authentication headers.
        token (dict[str, str]): Dictionary containing authentication tokens, typically including 'Authorization'.

    Example:
        >>> client = AuthSyncClient.login(
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
        httpx_Client:Client,
        token:dict[str,str],
    ):
        """
        Initialize the AuthSyncClient with an existing httpx.Client and authentication token.

        Args:
            httpx_Client (Client): Preconfigured Client for making authorized requests.
            token (dict[str, str]): Dictionary containing authentication tokens.
        """  
        
        self.httpx_Client : Client = httpx_Client
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
    def login(
        cls,
        *,
        UserName_or_Email : str,
        Password : str
    )-> "AuthSyncClient":
        
        """
        Authenticate a user synchronously and return an instance of `AuthSyncClient`.

        This method performs the login request to the HedgeTech API, retrieves JWT tokens,
        and configures an `httpx.Client` with authentication headers and cookies.

        Args:
            UserName_or_Email (str): The username or email of the user.
            Password (str): The user's password.

        Returns:
            AuthSyncClient: An initialized client ready to make authorized requests.

        Raises:
            ValueError: If the login attempt fails (e.g., wrong credentials).

        Example:
            >>> client = AuthSyncClient.login(
            ...     UserName_or_Email="user@example.com",
            ...     Password="secure_password"
            ... )
            >>> client.token['Authorization'][:10]
            'eyJ0eXAiOi'
        """
        
        httpx_Client = Client(verify=True ,http1=False ,http2=True)
        
        
        login_res = httpx_Client.post(
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
                        
            httpx_Client = Client(
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
                token = login_res.json()
            )
        
        else :
            
            raise ValueError(login_res.json().get('detail'))