"""
The `utradeconnect` module provides classes for connecting to the Utrade platform.

Available classes:
- `UtradeConnect`: Main class for establishing a connection to the Utrade platform.
- `MDSocket_io`: Class for handling market data socket connections.
- `OrderSocket_io`: Class for handling order socket connections.
"""

from utradeconnect.index import UtradeConnect
from utradeconnect.marketSocket import MDSocket_io
from utradeconnect.orderSocket import OrderSocket_io
from utradeconnect.__version__ import __version__
__all__= ["UtradeConnect", 'MDSocket_io', 'OrderSocket_io']

VERSION = __version__