from utradeconnect.request import APIRequest
from utradeconnect.exception import UtradeGeneralException

class UtradeCommon:
    def __init__(self, config, apiKey, secretKey) -> None:
            """
            Initialize data common to all UtradeConnect classes.

            Args:
                config (dict): A dictionary containing the configuration parameters.
                    - source (str): The source identifier.
                    - base_url (str, optional): The base URL for API requests. Defaults to None.
                    - disable_ssl (bool, optional): Whether to disable SSL verification. Defaults to False.
                    - debug (bool, optional): Whether to enable debug mode. Defaults to False.
                    - timeout (int, optional): The timeout for API requests in milliseconds. Defaults to 100.
                apiKey (str): The API key for authentication.
                secretKey (str): The secret key for authentication.
            Raises:
                UtradeGeneralException: If there is an error initializing the Utrade Connection.
            """
            try:
                self.token = None
                self.userID = None
                self.isInvestorClient = None
                self.apiKey = apiKey
                self.secretKey = secretKey
                self.source = config['source']
                self.apiRequest = APIRequest(
                    base_url=config.get('base_url',None),
                    disable_ssl=config.get('disable_ssl', False),
                    debug=config.get('debug', False),
                    timeout=config.get('timeout', 100)
                )

            except Exception as e:
                raise UtradeGeneralException("Error initializing Utrade Connection: {}".format(e))

    def _set_common_variables(self, access_token, user_id, is_investor_client):
        """
        Set common variables received after a successful authentication.

        :param access_token: The access token obtained after authentication.
        :param user_id: The user's ID.
        :param is_investor_client: A flag indicating if the user is an investor client.
        """
        self.token = access_token
        self.userID = user_id
        self.isInvestorClient = is_investor_client
        self.apiRequest.token = self.token
