import requests
import json
from requests import exceptions
from requests.exceptions import HTTPError
from requests import ConnectTimeout, HTTPError, Timeout, ConnectionError

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
                Here we have declared all the exception and responses
    If there is any exception occurred we have this code to convey the messages
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


class UtradeException(Exception):
    """
    Base exception class representing a Utrade client exception.

    Every specific Utrade client exception is a subclass of this
    and exposes two instance variables `.code` (HTTP error code)
    and `.message` (error text).
    """

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(UtradeException, self).__init__(message)
        self.code = code
        self.message = message


class UtradeGeneralException(UtradeException):
    """An unclassified, general error. Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(UtradeGeneralException, self).__init__(message, code)


class UtradeTokenException(UtradeException):
    """Represents all token and authentication related errors. Default code is 400."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(UtradeTokenException, self).__init__(message, code)


class UtradePermissionException(UtradeException):
    """Represents permission denied exceptions for certain calls. Default code is 400."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(UtradePermissionException, self).__init__(message, code)


class UtradeOrderException(UtradeException):
    """Represents all order placement and manipulation errors. Default code is 500."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(UtradeOrderException, self).__init__(message, code)


class UtradeInputException(UtradeException):
    """Represents user input errors such as missing and invalid parameters. Default code is 400."""

    def __init__(self, message, code=400):
        """Initialize the exception."""
        super(UtradeInputException, self).__init__(message, code)


class UtradeDataException(UtradeException):
    """Represents a bad response from the backend Order Management System (OMS). Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(UtradeDataException, self).__init__(message, code)


class UtradeNetworkException(UtradeException):
    """Represents a network issue between Utrade and the backend Order Management System (OMS). Default code is 500."""

    def __init__(self, message, code=500):
        """Initialize the exception."""
        super(UtradeNetworkException, self).__init__(message, code)
