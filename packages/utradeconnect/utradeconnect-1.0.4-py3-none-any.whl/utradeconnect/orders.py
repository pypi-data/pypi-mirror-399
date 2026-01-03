import json

from utradeconnect.base import UtradeCommon
from utradeconnect.exception import UtradeGeneralException, UtradeOrderException, UtradeTokenException


class UtradeOrderConnect(UtradeCommon):
    def __init__(self, config, apiKey, secretKey):
        """
        Initialize the Orders class.

        Args:
            config (dict): The configuration dictionary.
        """
        # initialize the UtradeCommon class
        super().__init__(config=config, apiKey=apiKey, secretKey=secretKey)

    def interactive_login(self, accessToken=None):
        """
        Initiates an interactive login and retrieves a user token.

        Args:
            accessToken (str, optional): Access token for the user. Defaults to None.

        Returns:
            dict: The API response containing the user token.

        Raises:
            UtradeTokenException: If the interactive login fails.
        """
        try:
            # Prepare the parameters for the API request
            params = {
                "appKey": self.apiKey,
                "secretKey": self.secretKey,
                "source": self.source,
            }
            if accessToken:
                params["accessToken"]= accessToken

            # Make a POST request to the "user.login" endpoint
            response = self.apiRequest._post("user.login", params)

            # Check if a "token" is present in the API response
            if "token" in response["result"]:
                # Set common variables based on the response data
                self._set_common_variables(
                    response["result"]["token"],
                    response["result"]["userID"],
                    response["result"]["isInvestorClient"],
                )
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeTokenException("Interactive login failed", 400)
        

    def get_order_book(self, clientID=None):
        """
        Retrieves the order book, which provides the status of orders placed by a user.

        Args:
            clientID (str, optional): The client ID of the user. Required if the user is not an investor client.

        Returns:
            dict: The API response containing the order book.

        Raises:
            UtradeGeneralException: If there is an error while retrieving the order book.
        """
        try:
            # Initialize the request parameters
            params = {}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "order.status" endpoint
            response = self.apiRequest._get("order.status", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get order book failed", 500)

    def place_order(
        self,
        exchangeSegment,
        exchangeInstrumentID,
        productType,
        orderType,
        orderSide,
        timeInForce,
        disclosedQuantity,
        orderQuantity,
        limitPrice,
        stopPrice,
        orderUniqueIdentifier,
        clientID=None,
    ):
        """
        Place an order with the specified parameters.

        Args:
            exchangeSegment (str): The exchange segment of the instrument.
            exchangeInstrumentID (str): The exchange instrument ID.
            productType (str): The product type of the instrument.
            orderType (str): The type of order.
            orderSide (str): The side of the order.
            timeInForce (str): The time in force for the order.
            disclosedQuantity (float): The disclosed quantity for the order.
            orderQuantity (float): The order quantity.
            limitPrice (float): The limit price for the order.
            stopPrice (float): The stop price for the order.
            orderUniqueIdentifier (str): The unique identifier for the order.
            clientID (str, optional): The client ID. Required if the user is not an investor client.

        Returns:
            dict: The API response.

        Raises:
            UtradeOrderException: If the order placement fails.
        """
        try:
            # Prepare the order parameters
            params = {
                "exchangeSegment": exchangeSegment,
                "exchangeInstrumentID": exchangeInstrumentID,
                "productType": productType,
                "orderType": orderType,
                "orderSide": orderSide,
                "timeInForce": timeInForce,
                "disclosedQuantity": disclosedQuantity,
                "orderQuantity": orderQuantity,
                "limitPrice": limitPrice,
                "stopPrice": stopPrice,
                "orderUniqueIdentifier": orderUniqueIdentifier,
            }

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a POST request to the "order.place" endpoint with the order parameters
            response = self.apiRequest._post("order.place", json.dumps(params))

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeOrderException("Place order failed", 500)

    def modify_order(
        self,
        appOrderID,
        modifiedProductType,
        modifiedOrderType,
        modifiedOrderQuantity,
        modifiedDisclosedQuantity,
        modifiedLimitPrice,
        modifiedStopPrice,
        modifiedTimeInForce,
        orderUniqueIdentifier,
        clientID=None,
    ):
        """
        Modify an open order by changing its properties such as order type, quantity, price, and more.

        Args:
            appOrderID (int): The ID of the order to be modified.
            modifiedProductType (str): The modified product type of the order.
            modifiedOrderType (str): The modified order type.
            modifiedOrderQuantity (int): The modified order quantity.
            modifiedDisclosedQuantity (int): The modified disclosed quantity.
            modifiedLimitPrice (float): The modified limit price.
            modifiedStopPrice (float): The modified stop price.
            modifiedTimeInForce (str): The modified time in force.
            orderUniqueIdentifier (str): The unique identifier of the order.
            clientID (str, optional): The client ID. Required if the user is not an investor client.

        Returns:
            dict: The API response.

        Raises:
            UtradeOrderException: If the modification of the order fails.
        """
        try:
            # Ensure appOrderID is an integer
            appOrderID = int(appOrderID)

            # Prepare the parameters for modifying the order
            params = {
                "appOrderID": appOrderID,
                "modifiedProductType": modifiedProductType,
                "modifiedOrderType": modifiedOrderType,
                "modifiedOrderQuantity": modifiedOrderQuantity,
                "modifiedDisclosedQuantity": modifiedDisclosedQuantity,
                "modifiedLimitPrice": modifiedLimitPrice,
                "modifiedStopPrice": modifiedStopPrice,
                "modifiedTimeInForce": modifiedTimeInForce,
                "orderUniqueIdentifier": orderUniqueIdentifier,
            }

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a PUT request to the "order.modify" endpoint with the order modification parameters
            response = self.apiRequest._put("order.modify", json.dumps(params))

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeOrderException("Modify order failed", 500)

    def get_order_history(self, appOrderID, clientID=None):
        """
        Retrieve the order history for a specific order, showing its state changes over time.

        Args:
            appOrderID (str): The ID of the order.
            clientID (str, optional): The ID of the client. Defaults to None.

        Returns:
            dict: The API response containing the order history.

        Raises:
            UtradeOrderException: If the request to get order history fails.
        """
        try:
            # Prepare the parameters for the request
            params = {"appOrderID": appOrderID}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "order.history" endpoint with the specified parameters
            response = self.apiRequest._get("order.history", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeOrderException("Get order history failed", 500)
        

    def cancel_order(self, appOrderID, orderUniqueIdentifier, clientID=None):
        """
        Cancel an open order.

        Args:
            appOrderID (int): The ID of the order to be cancelled.
            orderUniqueIdentifier (str): The unique identifier of the order.
            clientID (str, optional): The ID of the client. Defaults to None.

        Returns:
            dict: The API response.

        Raises:
            UtradeOrderException: If the cancellation of the order fails.
        """
        try:
            # Prepare the parameters for cancelling the order
            params = {
                "appOrderID": int(appOrderID),
                "orderUniqueIdentifier": orderUniqueIdentifier,
            }

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a DELETE request to the "order.cancel" endpoint with the specified parameters
            response = self.apiRequest._delete("order.cancel", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeOrderException("Cancel order failed", 500)

    def get_profile(self, clientID=None):
        """
        Retrieves the user's profile information using their session token.

        Args:
            clientID (str, optional): The client ID of the user. Required if the user is not an investor client.

        Returns:
            dict: The API response containing the user's profile information.

        Raises:
            UtradeGeneralException: If the request to retrieve the profile fails.
        """
        try:
            # Initialize the request parameters
            params = {}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "user.profile" endpoint with the specified parameters
            response = self.apiRequest._get("user.profile", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get profile failed", 500)

    def get_balance(self, clientID=None):
        """Get balance information related to limits on equities, derivatives, upfront margin, available exposure,
        and other RMS-related balances available to the user.

        This API call provides balance-related information based on the user's privileges and client type.
        """
        if self.isInvestorClient:
            try:
                # Initialize the request parameters
                params = {}

                # If the user is not an investor client, specify the clientID in the request
                if not self.isInvestorClient:
                    params["clientID"] = clientID

                # Make a GET request to the "user.balance" endpoint with the specified parameters
                response = self.apiRequest._get("user.balance", params)

                # Return the API response
                return response
            except (Exception, UtradeTokenException) as e:
                raise UtradeGeneralException("Get balance failed", 500)
        else:
            # Notify that balance API is available for retail API users only
            print(
                "Balance: Balance API available for retail API users only, dealers can watch the same on dealer terminal"
            )

    def get_trade(self, clientID=None):
        """Retrieve the trade book, which contains a list of all trades executed on a particular day that were placed by the user.

        The trade book displays both filled and partially filled orders.

        Args:
            clientID (str, optional): The client ID of the user. Defaults to None.

        Returns:
            dict: The API response containing the trade book.

        Raises:
            UtradeGeneralException: If the request to retrieve the trade book fails.
        """
        try:
            # Initialize the request parameters
            params = {}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "trades" endpoint with the specified parameters
            response = self.apiRequest._get("trades", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get trade failed", 500)

    def get_holding(self, clientID=None):
        """Retrieve long-term holdings with the broker using the Holdings API.

        This API call provides information about the user's holdings, allowing them to check their long-term investments.
        """
        try:
            # Initialize the request parameters
            params = {}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "portfolio.holdings" endpoint with the specified parameters
            response = self.apiRequest._get("portfolio.holdings", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get holding failed", 500)

    def get_position_daywise(self, clientID=None):
        """
        Retrieve positions by day, which is a snapshot of the buying and selling activity for a particular day.

        The positions API provides insight into the user's daily trading activities.

        :param clientID: (optional) The client ID for which to retrieve positions. Required if the user is not an investor client.
        :type clientID: str
        :return: The API response containing the positions by day.
        :rtype: dict
        :raises UtradeGeneralException: If the request to retrieve positions fails.
        """
        try:
            # Initialize the request parameters, specifying 'DayWise' for dayOrNet
            params = {"dayOrNet": "DayWise"}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "portfolio.positions" endpoint with the specified parameters
            response = self.apiRequest._get("portfolio.positions", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get position daywise failed", 500)

    def get_position_netwise(self, clientID=None):
        # The positions API positions by net. Net is the actual, current net position portfolio
        try:
            # Initialize the request parameters, specifying 'NetWise' for dayOrNet
            params = {"dayOrNet": "NetWise"}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "portfolio.positions" endpoint with the specified parameters
            response = self.apiRequest._get("portfolio.positions", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get position netwise failed", 500)

    def get_dealerposition_netwise(self, clientID=None):
        """Retrieve dealer positions by net, which represents the current net position portfolio.

        The positions API provides information about the dealer's net positions.
        """
        try:
            # Initialize the request parameters, specifying 'NetWise' for dayOrNet
            params = {"dayOrNet": "NetWise"}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "portfolio.dealerpositions" endpoint with the specified parameters
            response = self.apiRequest._get("portfolio.dealerpositions", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get dealer position netwise failed", 500)

    def get_dealerposition_daywise(self, clientID=None):
        """Retrieve dealer positions by day, which is a snapshot of the buying and selling activity for a particular day.

        The positions API provides information about the dealer's daily trading activities.
        """
        try:
            # Initialize the request parameters, specifying 'DayWise' for dayOrNet
            params = {"dayOrNet": "DayWise"}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "portfolio.dealerpositions" endpoint with the specified parameters
            response = self.apiRequest._get("portfolio.dealerpositions", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get dealer position daywise failed", 500)

    def get_dealer_orderbook(self, clientID=None):
        """Request the order book, which provides the states of all the orders placed by a user, including dealer orders."""
        try:
            # Initialize the request parameters
            params = {}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "order.dealer.status" endpoint with the specified parameters
            response = self.apiRequest._get("order.dealer.status", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get dealer order book failed", 500)

    def get_dealer_tradebook(self, clientID=None):
        """Retrieve the dealer trade book, which contains a list of all trades executed on a particular day that were placed by the user.

        The trade book displays both filled and partially filled orders.
        """
        try:
            # Initialize the request parameters
            params = {}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a GET request to the "dealer.trades" endpoint with the specified parameters
            response = self.apiRequest._get("dealer.trades", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Get dealer trade book failed", 500)

    def convert_position(
        self,
        exchangeSegment,
        exchangeInstrumentID,
        targetQty,
        isDayWise,
        oldProductType,
        newProductType,
        clientID=None,
    ):
        """
        Convert open positions from NRML intra-day to Short term MIS or vice versa, provided sufficient margin/funds exist.

        Args:
            exchangeSegment (int): The exchange segment of the instrument.
            exchangeInstrumentID (int): The exchange instrument ID.
            targetQty (int): The target quantity to convert.
            isDayWise (bool): Flag indicating whether the conversion is day-wise or not.
            oldProductType (str): The old product type of the position.
            newProductType (str): The new product type to convert the position to.
            clientID (str, optional): The client ID. Required only if the user is not an investor client.

        Returns:
            dict: The API response.

        Raises:
            UtradeGeneralException: If the conversion fails.
        """
        try:
            # Prepare the parameters for converting the position
            params = {
                "exchangeSegment": exchangeSegment,
                "exchangeInstrumentID": exchangeInstrumentID,
                "targetQty": targetQty,
                "isDayWise": isDayWise,
                "oldProductType": oldProductType,
                "newProductType": newProductType,
            }

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a PUT request to the "portfolio.positions.convert" endpoint with the conversion parameters
            response = self.apiRequest._put(
                "portfolio.positions.convert", json.dumps(params)
            )

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeGeneralException("Convert position failed", 500)
        
    def cancelall_order(self, exchangeSegment, exchangeInstrumentID):
        """Cancel all open orders of the user by providing the exchange segment and exchange instrument ID.

        This API allows the user to cancel all open orders associated with a specific exchange segment and instrument.

        Args:
            exchangeSegment (str): The exchange segment of the orders to be cancelled.
            exchangeInstrumentID (str): The exchange instrument ID of the orders to be cancelled.

        Returns:
            dict: The API response containing the result of the cancellation request.

        Raises:
            UtradeOrderException: If the cancellation request fails.

        """
        try:
            # Prepare the parameters for cancelling all open orders
            params = {
                "exchangeSegment": exchangeSegment,
                "exchangeInstrumentID": exchangeInstrumentID,
            }

            # If the user is not an investor client, specify the clientID as the userID
            if not self.isInvestorClient:
                params["clientID"] = self.userID

            # Make a POST request to the "order.cancelall" endpoint with the specified parameters
            response = self.apiRequest._post("order.cancelall", json.dumps(params))

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeOrderException("Cancel all order failed", 500)

    def interactive_logout(self, clientID=None):
        """
        Invalidate the session token and destroy the API session, requiring the user to go through the login flow again.

        This API call logs out the user, effectively terminating their current session. To continue using the API, the user
        must log in again and extract a new session token from the login response.

        :param clientID: (optional) The client ID of the user. Required if the user is not an investor client.
        :type clientID: str

        :return: The API response.
        :rtype: dict

        :raises UtradeTokenException: If interactive logout fails.
        """
        try:
            # Initialize the request parameters
            params = {}

            # If the user is not an investor client, specify the clientID in the request
            if not self.isInvestorClient:
                params["clientID"] = clientID

            # Make a DELETE request to the "user.logout" endpoint with the specified parameters
            response = self.apiRequest._delete("user.logout", params)

            # Return the API response
            return response
        except (Exception, UtradeTokenException) as e:
            # Handle exceptions gracefully and return an error description
            raise UtradeTokenException("Interactive logout failed", 500)
