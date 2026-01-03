import json

from utradeconnect.base import UtradeCommon
from utradeconnect.exception import UtradeGeneralException, UtradeTokenException


class UtradeMarketConnect(UtradeCommon):

    def __init__(self, config, apiKey, secretKey) -> None:
        # initialize the UtradeCommon class
        super().__init__(config=config, apiKey=apiKey, secretKey=secretKey)

    def marketdata_login(self):
        """
        Logs in to the market data service using the provided API key, secret key, and source.

        Returns:
            dict: The response from the API.
        
        Raises:
            UtradeTokenException: If an error occurs while logging in to market data.
        """
        try:
            # Prepare the parameters for the market data login request
            params = {
                "appKey": self.apiKey,
                "secretKey": self.secretKey,
                "source": self.source,
            }

            # Send a POST request to the "market.login" endpoint
            response = self.apiRequest._post("market.login", params)
            
            # Print the response for debugging purposes

            # Check if a "token" is present in the response
            if "token" in response['result']:
                # Set common variables with the token and user ID
                self._set_common_variables(response['result']['token'], response['result']['userID'], False)
            
            # Return the response from the API
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeTokenException("Error while logging in to market data: " + str(e))
    
    def get_config(self):
        """
        Retrieves the market configuration.

        Returns:
            dict: The market configuration response.

        Raises:
            UtradeGeneralException: If an error occurs while retrieving market configuration.
        """
        try:
            # Prepare empty parameters for the request (no additional parameters required)
            params = {}

            # Send a GET request to retrieve market configuration
            response = self.apiRequest._get('market.config', params)

            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving market configuration: " + str(e))
    
    def get_quote(self, instruments, eventCode, publishFormat):
        """
        Retrieves quotes for the specified instruments.

        Args:
            instruments (list): List of instrument codes.
            eventCode (str): Event code for the quote request.
            publishFormat (str): Format in which the quotes should be published.

        Returns:
            dict: Response obtained from the quote request.
        
        Raises:
            UtradeGeneralException: If an error occurs while retrieving quotes.
        """
        try:
            # Prepare the parameters for the quote request
            params = {'instruments': instruments, 'eventCode': eventCode, 'publishFormat': publishFormat}
            
            # Send a POST request to retrieve quotes
            response = self.apiRequest._post('market.instruments.quotes', json.dumps(params))
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving quotes: " + str(e))

    def send_subscription(self, instruments, eventCode):
        """
        Sends a subscription request for the given instruments and event code.

        Args:
            instruments (list): List of instruments to subscribe to.
            eventCode (str): Event code for the subscription.

        Returns:
            dict: Response obtained from the subscription request.

        Raises:
            UtradeGeneralException: If an error occurs while subscribing.
        """
        try:
            # Prepare the parameters for the subscription request
            params = {'instruments': instruments, 'eventCode': eventCode}
            
            # Send a POST request to subscribe to instruments
            response = self.apiRequest._post('market.instruments.subscription', json.dumps(params))
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while subscribing: " + str(e))
    
    def send_unsubscription(self, instruments, eventCode):
        """
        Sends an unsubscription request for the specified instruments and event code.

        Args:
            instruments (list): List of instruments to unsubscribe from.
            eventCode (str): Event code for unsubscription.

        Returns:
            dict: Response obtained from the unsubscription request.

        Raises:
            UtradeGeneralException: If an error occurs while unsubscribing.
        """
        try:
            # Prepare the parameters for unsubscription
            params = {'instruments': instruments, 'eventCode': eventCode}
            
            # Send a PUT request to unsubscribe from instruments
            response = self.apiRequest._put('market.instruments.unsubscription', json.dumps(params))
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while unsubscribing: " + str(e))

    def get_master(self, exchangeSegmentList):
        """
        Retrieves the master data for the given exchange segment list.

        Args:
            exchangeSegmentList (list): A list of exchange segments for which the master data needs to be retrieved.

        Returns:
            dict: The response obtained from the API request to retrieve the master data.

        Raises:
            UtradeGeneralException: If an error occurs while retrieving master data.

        """
        try:
            # Prepare the parameters to retrieve the master data
            params = {"exchangeSegmentList": exchangeSegmentList}
            
            # Send a POST request to get master data
            response = self.apiRequest._post('market.instruments.master', json.dumps(params))
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving master data: " + str(e))

    def get_ohlc(self, exchangeSegment, exchangeInstrumentID, startTime, endTime, compressionValue):
        """
        Retrieves OHLC (Open, High, Low, Close) data for a given instrument within a specified time range.

        Parameters:
        exchangeSegment (str): The exchange segment of the instrument.
        exchangeInstrumentID (str): The exchange instrument ID of the instrument.
        startTime (str): The start time of the data range in the format 'YYYY-MM-DD HH:MM:SS'.
        endTime (str): The end time of the data range in the format 'YYYY-MM-DD HH:MM:SS'.
        compressionValue (int): The compression value for the OHLC data.

        Returns:
        dict: The OHLC data for the specified instrument and time range.

        Raises:
        UtradeGeneralException: If an error occurs while retrieving OHLC data.

        """
        try:
            # Prepare the parameters for OHLC data retrieval
            params = {
                'exchangeSegment': exchangeSegment,
                'exchangeInstrumentID': exchangeInstrumentID,
                'startTime': startTime,
                'endTime': endTime,
                'compressionValue': compressionValue
            }
            
            # Send a GET request to retrieve OHLC data
            response = self.apiRequest._get('market.instruments.ohlc', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            raise UtradeGeneralException("Error while retrieving OHLC data: " + str(e))
            # Handle exceptions and return a description of the error
            return e
    
    def get_series(self, exchangeSegment):
        """
        Retrieves series information for a given exchange segment.

        Args:
            exchangeSegment (str): The exchange segment for which series information is to be retrieved.

        Returns:
            dict: The response obtained from the API request.

        Raises:
            UtradeGeneralException: If there is an error while retrieving series information.
        """
        try:
            # Prepare the parameters to retrieve series information
            params = {'exchangeSegment': exchangeSegment}
            
            # Send a GET request to get series information
            response = self.apiRequest._get('market.instruments.instrument.series', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving series information: " + str(e))

    def get_equity_symbol(self, exchangeSegment, series, symbol):
        """
        Get equity symbol for a given exchange segment, series, and symbol.

        Args:
            exchangeSegment (str): The exchange segment of the equity.
            series (str): The series of the equity.
            symbol (str): The symbol of the equity.

        Returns:
            dict: The response obtained from the API request.

        Raises:
            UtradeGeneralException: If there is an error while retrieving equity symbols.
        """
        try:
            # Prepare the parameters to get equity symbols
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol}
            
            # Send a GET request to get equity symbols
            response = self.apiRequest._get('market.instruments.instrument.equitysymbol', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving equity symbols: " + str(e))

    def get_expiry_date(self, exchangeSegment, series, symbol):
        """
        Get the expiry date information for a given exchange segment, series, and symbol.

        Parameters:
        exchangeSegment (str): The exchange segment.
        series (str): The series.
        symbol (str): The symbol.

        Returns:
        dict: The response obtained from the API.

        Raises:
        UtradeGeneralException: If there is an error while retrieving expiry date information.
        """
        try:
            # Prepare the parameters to get expiry date information
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol}
            
            # Send a GET request to get expiry date information
            response = self.apiRequest._get('market.instruments.instrument.expirydate', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving expiry date information: " + str(e))

    def get_future_symbol(self, exchangeSegment, series, symbol, expiryDate):
        """
        Get future symbol based on the provided parameters.

        Args:
            exchangeSegment (str): The exchange segment of the future symbol.
            series (str): The series of the future symbol.
            symbol (str): The symbol of the future symbol.
            expiryDate (str): The expiry date of the future symbol.

        Returns:
            dict: The response obtained from the API.

        Raises:
            UtradeGeneralException: If there is an error while retrieving future symbols.
        """
        try:
            # Prepare the parameters to get future symbols
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol, 'expiryDate': expiryDate}
            
            # Send a GET request to get future symbols
            response = self.apiRequest._get('market.instruments.instrument.futuresymbol', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving future symbols: " + str(e))
    
    def get_option_symbol(self, exchangeSegment, series, symbol, expiryDate, optionType, strikePrice):
        """
        Get option symbol based on the provided parameters.

        Args:
            exchangeSegment (str): The exchange segment.
            series (str): The series.
            symbol (str): The symbol.
            expiryDate (str): The expiry date.
            optionType (str): The option type.
            strikePrice (float): The strike price.

        Returns:
            dict: The response obtained from the API request.

        Raises:
            UtradeGeneralException: If there is an error while retrieving option symbols.
        """
        try:
            # Prepare the parameters to get option symbols
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol, 'expiryDate': expiryDate,
                    'optionType': optionType, 'strikePrice': strikePrice}
            
            # Send a GET request to get option symbols
            response = self.apiRequest._get('market.instruments.instrument.optionsymbol', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving option symbols: " + str(e))

    def get_option_type(self, exchangeSegment, series, symbol, expiryDate):
        """
        Retrieves the option types for a given instrument.

        Args:
            exchangeSegment (str): The exchange segment of the instrument.
            series (str): The series of the instrument.
            symbol (str): The symbol of the instrument.
            expiryDate (str): The expiry date of the instrument.

        Returns:
            dict: The response obtained from the API request.

        Raises:
            UtradeGeneralException: If there is an error while retrieving option types.
        """
        try:
            # Prepare the parameters to get option types
            params = {'exchangeSegment': exchangeSegment, 'series': series, 'symbol': symbol, 'expiryDate': expiryDate}
            
            # Send a GET request to get option types
            response = self.apiRequest._get('market.instruments.instrument.optiontype', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while retrieving option types: " + str(e))

    def get_index_list(self, exchangeSegment):
        """
        Get the list of indices for a given exchange segment.

        Parameters:
        exchangeSegment (str): The exchange segment for which to retrieve the list of indices.

        Returns:
        dict: The response obtained from the API request.

        Raises:
        UtradeGeneralException: If there is an error while getting the list of indices.
        """
        try:
            # Prepare the parameters to get the list of indices
            params = {'exchangeSegment': exchangeSegment}
            
            # Send a GET request to get the list of indices
            response = self.apiRequest._get('market.instruments.indexlist', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while getting the list of indices: " + str(e))

    def search_by_instrumentid(self, instruments):
        """
        Search for instruments by their ID.

        Args:
            instruments (list): List of instrument IDs to search for.

        Returns:
            dict: Response obtained from the search.

        Raises:
            UtradeGeneralException: If an error occurs while searching by instrument ID.
        """
        try:
            # Prepare the parameters to search by instrument ID
            params = {'source': self.source, 'instruments': instruments}
            
            # Send a POST request to search by instrument ID
            response = self.apiRequest._post('market.search.instrumentsbyid', json.dumps(params))
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while searching by instrument ID: " + str(e))

    def search_by_scriptname(self, searchString):
        """
        Search for instruments by script name.

        Args:
            searchString (str): The script name to search for.

        Returns:
            dict: The response obtained from the search.

        Raises:
            UtradeGeneralException: If an error occurs while searching by script name.
        """
        try:
            # Prepare the parameters to search by script name
            params = {'searchString': searchString}
            
            # Send a GET request to search by script name
            response = self.apiRequest._get('market.search.instrumentsbystring', params)
            
            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeGeneralException("Error while searching by script name: " + str(e))

    def marketdata_logout(self):
        """
        Logs out from the market data.

        Returns:
            dict: The response obtained from the logout request.

        Raises:
            UtradeTokenException: If there is an error while logging out from market data.
        """
        try:
            # Prepare empty parameters for the logout request (no additional parameters required)
            params = {}

            # Send a DELETE request to log out from market data
            response = self.apiRequest._delete('market.logout', params)

            # Return the response obtained
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions and return a description of the error
            raise UtradeTokenException("Error while logging out from market data: " + str(e))

    
    



