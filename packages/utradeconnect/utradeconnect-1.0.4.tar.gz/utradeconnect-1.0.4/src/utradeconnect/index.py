from utradeconnect.market import UtradeMarketConnect
from utradeconnect.orders import UtradeOrderConnect


class UtradeConnect(UtradeMarketConnect, UtradeOrderConnect):
    """
    UtradeConnect class represents a connection to the Utrade API.

    Args:
        apiKey (str): The API key for authentication.
        secretKey (str): The secret key for authentication.
        source (str): The source identifier for the connection.

    Attributes:
        apiKey (str): The API key for authentication.
        secretKey (str): The secret key for authentication.
        source (str): The source identifier for the connection.
        root (str): The root URL for the connection to the Utrade API, defaults to production environment.
        debug (bool): A boolean flag indicating if debug mode is enabled, defaults to False.
        timeout (int): The timeout for the connection, defaults to 100.
        pool (int): The connection pool size.
        disable_ssl (bool): A boolean flag indicating if SSL is disabled, defaults to False.
        market_data_api_key (str): optional, The API key for authentication for the market data connection, defaults to apiKey.
        market_data_api_secret (str): optional, The secret key for authentication for the market data connection, defaults to secretKey.
    """

    def __init__(
            self,
            apiKey,
            secretKey, 
            source,
            root=None,
            debug=False,
            timeout=None,
            pool=None,
            disable_ssl=False,
            market_data_api_key=None,
            market_data_api_secret=None,
            ):
        config = {
            "source": source,
            "base_url": root[:-1] if root and root.endswith('/') else root,
            "debug": debug,
            "timeout": timeout, 
            "pool": pool, 
            "disable_ssl": disable_ssl
            }
        # initialize the UtradeMarketConnect and UtradeOrderConnect classes
        if not market_data_api_key:
            market_data_api_key = apiKey
        if not market_data_api_secret:
            market_data_api_secret = secretKey
        UtradeMarketConnect.__init__(self, config, apiKey=market_data_api_key, secretKey=market_data_api_secret)
        UtradeOrderConnect.__init__(self, config,apiKey=apiKey, secretKey=secretKey)
    
