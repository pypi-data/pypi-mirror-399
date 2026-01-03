import configparser
import os

import socketio


class OrderSocket_io(socketio.Client):

    def __init__(self, token, userID, base_url=None, broadcast_mode = "FULL", reconnection=True, reconnection_attempts=0, reconnection_delay=1,
                 reconnection_delay_max=50000, randomization_factor=0.5, logger=False, binary=False, json=None,
                 **kwargs):
        """
        Initializes the OrderSocket object.

        Args:
            token (str): The authentication token.
            userID (str): The user ID.
            reconnection (bool, optional): Whether to enable reconnection. Defaults to True.
            reconnection_attempts (int, optional): The number of reconnection attempts. Defaults to 0.
            reconnection_delay (int, optional): The delay between reconnection attempts in seconds. Defaults to 1.
            reconnection_delay_max (int, optional): The maximum delay between reconnection attempts in milliseconds. Defaults to 50000.
            randomization_factor (float, optional): The randomization factor for reconnection delay. Defaults to 0.5.
            logger (bool, optional): Whether to enable logging. Defaults to False.
            binary (bool, optional): Whether to use binary mode. Defaults to False.
            json (object, optional): The JSON object. Defaults to None.
            **kwargs: Additional keyword arguments.

        """
        self.sid = socketio.Client(logger=True, engineio_logger=True)
        self.eventlistener = self.sid
        self.sid.on('connect', self.on_connect)
        self.sid.on('message', self.on_message)
        self.sid.on('joined', self.on_joined)
        self.sid.on('error', self.on_error)
        self.sid.on('order', self.on_order)
        self.sid.on('trade', self.on_trade)
        self.sid.on('position', self.on_position)
        self.sid.on('tradeConversion', self.on_tradeconversion)
        self.sid.on('logout', self.on_messagelogout)
        self.sid.on('disconnect', self.on_disconnect)

        self.userID = userID
        self.token = token

        """Get root url from config file"""
        currDirMain = os.getcwd()
        configParser = configparser.RawConfigParser()
        configFilePath = os.path.join(currDirMain, 'config.ini')
        configParser.read(configFilePath)
        self.port = base_url if base_url else configParser.get('root_url', 'root').strip()

        port = f'{self.port}/?token='

        self.connection_url = port + self.token + '&userID=' + self.userID

    def connect(self, headers={}, transports='websocket', namespaces=None, socketio_path='/socket.io',
                verify=False):
        """
        Connects to the socket.

        Args:
            headers (dict): Additional headers to be sent with the connection request.
            transports (str): The transport mechanism to be used for the connection. Default is 'websocket'.
            namespaces (list): List of namespaces to connect to. Default is None.
            socketio_path (str): The path to the socket.io server. Default is '/socket.io'.
            verify (bool): Whether to verify the SSL certificate. Default is False.
        """
        url = self.connection_url

        """Connected to the socket."""
        self.sid.connect(url, headers, transports, namespaces, socketio_path)
        self.sid.wait()
        print('COnnect ************')
        """Disconnect from the socket."""

    def on_connect(self):
        """Connect from the socket"""
        """
        This method is called when the socket connection is established.
        This method can be overridden to perform any action on successful connection.
        """
        print('Interactive socket connected successfully!')

    def on_message(self):
        """On message from socket"""
        print('I received a message!')

    def on_joined(self, data):
        """On socket joined"""
        print('Interactive socket joined successfully!' + data)

    def on_error(self, data):
        """On receiving error from socket"""
        print('Interactive socket error!' + data)

    def on_order(self, data):
        """On receiving order placed data from socket"""
        print("Order placed!" + data)

    def on_trade(self, data):
        """On receiving trade data from socket"""
        print("Trade Received!" + data)

    def on_position(self, data):
        """On receiving position data from socket"""
        print("Position Retrieved!" + data)

    def on_tradeconversion(self, data):
        """On receiving trade conversion data from socket"""
        print("Trade Conversion Received!" + data)

    def on_messagelogout(self, data):
        """On receiving user logout message"""
        print("User logged out!" + data)

    def on_disconnect(self, data):
        """On receiving disconnection from socket"""
        print('Interactive Socket disconnected!')

    def get_emitter(self):
        """For getting event listener"""
        return self.eventlistener
