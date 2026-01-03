import configparser
import json
from urllib.parse import urljoin
import requests
from utradeconnect.exception import UtradeDataException, UtradeTokenException
from utradeconnect.apiConfig import get_all_routes


class ConfigReader:
    def __init__(self):
        """
        Initializes the ConfigReader object by reading the provided config file path.
        """
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

    def get_user_source(self):
        """
        Retrieves the 'source' value from the [user] section of the config file.

        Returns:
            str: The 'source' value.
        """
        return self.config.get('user', 'source')

    def is_ssl_disabled(self):
        """
        Checks if SSL is disabled.

        Returns:
            bool: True if SSL is disabled, False otherwise.
        """
        return self.config.getboolean('SSL', 'disable_ssl')

    def get_root_url(self):
        """
        Retrieves the 'root' value from the [root_url] section of the config file.

        Returns:
            str: The 'root' value.
        """
        return self.config.get('root_url', 'root')

    def get_broadcast_mode(self):
        """
        Retrieves the 'broadcastMode' value from the [root_url] section of the config file.

        Returns:
            str: The 'broadcastMode' value.
        """
        return self.config.get('root_url', 'broadcastMode')


class APIRequest:
    """
    Represents an API request.

    Args:
        base_url (str, optional): The base URL for the API. Defaults to None.
        token (str, optional): The authorization token. Defaults to None.
        disable_ssl (bool, optional): Whether to disable SSL verification. Defaults to False.
        debug (bool, optional): Whether to enable debug mode. Defaults to False.
        timeout (int, optional): The timeout for the request. Defaults to 100.
    """

    def __init__(self, base_url=None, token=None, disable_ssl=False, debug=False, timeout=100):
        # Initialize the APIRequest with the configuration from the file
        config_reader = ConfigReader()
        self.root = base_url if base_url is not None else config_reader.get_root_url()
        self.token = token
        self.disable_ssl = disable_ssl if disable_ssl is not None else config_reader.is_ssl_disabled()
        self.debug = debug
        self.reqsession = requests
        self.timeout = timeout
        self._routes = get_all_routes()
        # disable requests SSL warning
        requests.packages.urllib3.disable_warnings()

    def _get(self, route, params=None):
        """
        Alias for sending a GET request.

        Args:
            route (str): The route to send the GET request to.
            params (dict, optional): The parameters to include in the GET request.

        Returns:
            The response from the GET request.
        """
        return self._request(route, "GET", params)

    def _post(self, route, params=None):
        """
        Alias for sending a POST request.

        Args:
            route (str): The route to send the request to.
            params (dict, optional): The parameters to include in the request. Defaults to None.

        Returns:
            The response from the POST request.
        """
        return self._request(route, "POST", params)

    def _put(self, route, params=None):
        """
        Alias for sending a PUT request.

        Args:
            route (str): The route for the PUT request.
            params (dict, optional): The parameters to be sent with the request. Defaults to None.

        Returns:
            The response from the PUT request.
        """
        return self._request(route, "PUT", params)

    def _delete(self, route, params=None):
        """
        Alias for sending a DELETE request.

        Args:
            route (str): The route for the DELETE request.
            params (dict, optional): The parameters to be included in the request.

        Returns:
            The response from the DELETE request.
        """
        return self._request(route, "DELETE", params)

    def _request(self, route, method, parameters=None):
        """Make an HTTP request.

        Args:
            route (str): The route for the request.
            method (str): The HTTP method for the request.
            parameters (dict, optional): The parameters for the request. Defaults to None.

        Returns:
            dict: The response data from the server.

        Raises:
            UtradeDataException: If the server response cannot be parsed as JSON or has an unknown content type.
            UtradeTokenException: If the server response contains an error and the status code is 400.
        """
        params = parameters if parameters else {}

        # Form a restful URL
        uri = self._routes[route].format(params)  
        url = urljoin(self.root, uri)
        headers = {}

        if self.token:
            # Set authorization header
            headers.update({'Content-Type': 'application/json', 'Authorization': self.token})

        try:
            r = self.reqsession.request(method,
                                        url,
                                        data=params if method in ["POST", "PUT"] else None,
                                        params=params if method in ["GET", "DELETE"] else None,
                                        headers=headers,
                                        verify=not self.disable_ssl, timeout=self.timeout)

        except Exception as e:
            raise e

        # Validate the content type.
        if "json" in r.headers["content-type"]:
            try:
                data = json.loads(r.content.decode("utf8"))
            except ValueError:
                raise UtradeDataException("Couldn't parse the JSON response received from the server: {content}".format(
                    content=r.content))
            print(data)
            # Handle API errors
            if data.get("error"):
                if r.status_code == 400 :
                    raise UtradeTokenException(data)

            return data
        else:
            raise UtradeDataException("Unknown Content-Type ({content_type}) with response: ({content})".format(
                content_type=r.headers["content-type"],
                content=r.content))
