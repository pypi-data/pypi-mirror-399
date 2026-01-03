import configparser
import os
from datetime import datetime

import socketio


class MDSocket_io(socketio.Client):
    """A Socket.IO client.
    This class implements a fully compliant Socket.IO web client with support
    for websocket and long-polling transports.
    :param reconnection: 'True'. if the client should automatically attempt to
                         reconnect to the server after an interruption, or
                         'False' to not reconnect. The default is 'True'.
    :param reconnection_attempts: How many reconnection attempts to issue
                                  before giving up, or 0 for infinity attempts.
                                  The default is 0.
    :param reconnection_delay: How long to wait in seconds before the first
                               reconnection attempt. Each successive attempt
                               doubles this delay.
    :param reconnection_delay_max: The maximum delay between reconnection
                                   attempts.
    :param randomization_factor: Randomization amount for each delay between
                                 reconnection attempts. The default is 0.5,
                                 which means that each delay is randomly
                                 adjusted by +/- 50%.
    :param logger: To enable logging set to 'True' or pass a logger object to
                   use. To disable logging set to 'False'. The default is
                   'False'.
    :param binary: 'True' to support binary payloads, 'False' to treat all
                   payloads as text. On Python 2, if this is set to 'True',
                   'unicode' values are treated as text, and 'str' and
                   'bytes' values are treated as binary.  This option has no
                   effect on Python 3, where text and binary payloads are
                   always automatically discovered.
    :param json: An alternative json module to use for encoding and decoding
                 packets. Custom json modules must have 'dumps' and 'loads'
                 functions that are compatible with the standard library
                 versions.
    """

    def __init__(self, token, userID, base_url=None, broadcast_mode = "FULL", reconnection=True, reconnection_attempts=0, reconnection_delay=1,
                 reconnection_delay_max=50000, randomization_factor=0.5, logger=False, binary=False, json=None,
                 **kwargs):
        self.sid = socketio.Client(logger=True, engineio_logger=True)
        self.eventlistener = self.sid

        self.sid.on('connect', self.on_connect)
        self.sid.on('message', self.on_message)

        #  """Similarly implement partial json full and binary json full."""
        self.sid.on('1501-json-full', self.on_message1501_json_full)
        self.sid.on('1501-json-partial', self.on_message1501_json_partial)

        self.sid.on('1502-json-full', self.on_message1502_json_full)
        self.sid.on('1502-json-partial', self.on_message1502_json_partial)

        self.sid.on('1505-json-full', self.on_message1505_json_full)
        self.sid.on('1505-json-partial', self.on_message1505_json_partial)

        self.sid.on('1507-json-full', self.on_message1507_json_full)

        self.sid.on('1510-json-full', self.on_message1510_json_full)
        self.sid.on('1510-json-partial', self.on_message1510_json_partial)

        self.sid.on('1512-json-full', self.on_message1512_json_full)
        self.sid.on('1512-json-partial', self.on_message1512_json_partial)

        self.sid.on('1105-json-full', self.on_message1105_json_full)
        self.sid.on('1105-json-partial', self.on_message1105_json_partial)

        self.sid.on('disconnect', self.on_disconnect)

        """Get the root url from config file"""
        currDirMain = os.getcwd()
        configParser = configparser.ConfigParser()
        configFilePath = os.path.join(currDirMain, 'config.ini')
        configParser.read(configFilePath)

        self.port = base_url if base_url else configParser.get('root_url', 'root')
        self.userID = userID
        publishFormat = 'JSON'
        self.broadcastMode = broadcast_mode if broadcast_mode else configParser.get('root_url', 'broadcastMode')
        self.token = token

        port = f'{self.port}/?token='

        self.connection_url = port + token + '&userID=' + self.userID + '&publishFormat=' + publishFormat + '&broadcastMode=' + self.broadcastMode
        self.socketio_path = '/api/V2/market/socket/socket.io'


    def connect(self, headers={}, transports='websocket', namespaces=None, verify=False):
        """
        
        Connect to the socket.
        """
        url = self.connection_url
        """Connected to the socket."""
        self.sid.connect(url, headers, transports, namespaces, self.socketio_path)
        self.sid.wait()
        """Disconnected from the socket."""
        # self.sid.disconnect()

    def on_connect(self):
        """Connect from the socket.

        This method is called when the socket connection is established.
        This method can be overridden to perform any action on successful connection.
        """
        print('Market Data Socket connected successfully!')

    def on_message(self, data):
        """On receiving message"""
        print('I received a message!' + data)

    def on_message1502_json_full(self, data):
        """On receiving message code 1502 full for Market depth message Event"""
        print('I received a 1502 Market depth message!' + data)

    def on_message1507_json_full(self, data):
            """On receiving message code 1507 full for MarketStatus message Event"""
            print('I received a 1507 MarketStatus message!' + data)
            
    def on_message1512_json_full(self, data):
            """On receiving message code 1512 full for LTP message Event"""
            print('I received a 1512 LTP message!' + data)     

    def on_message1505_json_full(self, data):
        """On receiving message code 1505 full for Candle data message Event"""
        print('I received a 1505 Candle data message!' + data)

    def on_message1510_json_full(self, data):
        """On receiving message code 1510 full for Open interest message Event"""
        print('I received a 1510 Open interest message!' + data)

    def on_message1501_json_full(self, data):
        """On receiving message code 1501 full for Level1,Touchline message Event"""
        print('I received a 1501 Level1,Touchline message!' + data)

    def on_message1502_json_partial(self, data):
        """On receiving message code 1502 partial for Market depth message Event"""
        print('I received a 1502 partial message!' + data)
    
    def on_message1512_json_partial(self, data):
        """On receiving message code 1512 partial for LTP message Event"""
        print('I received a 1512 LTP message!' + data)

    def on_message1505_json_partial(self, data):
        """On receiving message code 1505 partial for Candle data message Event"""
        print('I received a 1505 Candle data message!' + data)

    def on_message1510_json_partial(self, data):
        """On receiving message code 1510 partial for Open interest message Event"""
        print('I received a 1510 Open interest message!' + data)

    def on_message1501_json_partial(self, data):
        """On receiving message code 1501 partial for Touchline message Event"""
        now = datetime.now()
        today = now.strftime("%H:%M:%S")
        print(today, 'in main 1501 partial Level1,Touchline message!' + data + ' \n')

    def on_message1105_json_full(self, data):
        """On receiving message code 1501 full for Touchline message Event"""
        print('I received a 1501 Level1,Touchline message!' + data)

    def on_message1105_json_partial(self, data):
        """On receiving message code 1105 partial for Instrument Property Change Event"""
        now = datetime.now()
        today = now.strftime("%H:%M:%S")
        print(today, 'in main 1105 partial, Instrument Property Change Event!' + data + ' \n')

        print('I received a 1105 Instrument Property Change Event!' + data)

    def on_disconnect(self, data):
        """Disconnected from the socket"""
        print('Market Data Socket disconnected!')

    def on_error(self, data):
        """Error from the socket"""
        print('Market Data Error', data)

    def get_emitter(self):
        """For getting the event listener"""
        return self.eventlistener
