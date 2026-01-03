# ``uTrade Connect`` Python SDK ![version](https://img.shields.io/badge/version-1.0.4-blue)

`uTrade Connect` encompasses a suite of `REST-like APIs` designed to expose a broad 
spectrum of functionalities crucial for the development of a comprehensive `investment 
and trading platform`. These capabilities include the `real-time execution of orders`, 
`efficient management of user portfolios`, `streaming of live market data via WebSockets`, 
and other features—all seamlessly accessible through a concise and `well-structured 
HTTP API collection`.

> [uTrade](https://utradesolutions.com) (c) 2023. All rights reserved. Licensed under the MIT License.


## Installation

There are two methods to install `uTrade Connect`:

1. **Using pip:**

    `uTrade Connect` is available on PyPI and can be installed using pip. Ensure you have Python 3.8 or above and internet access. Run the following command in your terminal:

    ```bash
    pip install utradeconnect
    ```

2. **Using the provided shell script:**

    Alternatively, you can use the `runPackage.sh` shell script provided in the project's root directory. This script creates a Python wheel for the project and installs it. To use this method, navigate to the project's root directory in your terminal and run the following command:

    ```bash
    sh runPackage.sh
    ```

After installation, check the `config.ini` file in the project's root directory and ensure you add the `root url`, keep `source` as `WEBAPI`, and `disable_ssl` as `true`.

### Usage

There are two methods to configure base parameters for `uTrade Connect`:

1. **Using config.ini:**

configure an .ini file named as `config.ini` in your application's working directory, the sample content is as below:

```ini
    [user]
    source=WEBAPI

    [SSL]
    disable_ssl=True

    [root_url]
    root="Provided Url"
    broadcastMode=Full
```

2. **Passing root url, disable_ssl while creating `uTrade Connect` Object**

```python
connect_object = UtradeConnect(
      apiKey=<your_api_key>,
      secretKey=<your_secret_key>,
      source=<source>,
      root=<provided_url>,
      debug=<debug_mode_boolean>,
      disable_ssl=<boolean>
  )            
```


### Create uTrade Connect Object 

- #### API Credentials and Config

        API_KEY = "YOUR_API_KEY_HERE"
        API_SECRET = "YOUR_API_SECRET_HERE"
        source = "WEBAPI"
        BASE_URL = "Provided Url"

    To securely manage your API credentials, it is recommended to use a `.env` file in your project

- ### uTradeConnect 
  - Instantiate a `UtradeConnect` object by specifying your API `appKey`, `secretKey`, `source`, `root`[optional] as parameters when employing market APIs. 
  - Conversely, if `interactive APIs` are preferred, furnish the requisite credentials for interactive functionality.

    ```python
    utradeConnect = UtradeConnect(api_key=API_KEY, secretKey=API_SECRET, source=source, root=BASE_URL)
    ```
###
### API Usage
+ #### Login ( API authentication )
  - To initiate API authentication, invoke the login service, which will provide a token for continued access to various services throughout the session.
      - #### Marketdata Login
          ```python
              response = utradeConnect.marketdata_login()
          ```
  
      - #### Interactive Login
        >   The acquisition of an `access token` is `mandatory for client interactive login`.
          - For Client Interactive login
             ```python
              response = utradeConnect.interactive_login(accessToken)
            ```
###
+ #### Subscribe Symbol
  To commence a subscription to a specific symbol, employ the marketdata API. 
  This API facilitates the retrieval of a Subscribe Response object, which 
  encapsulates relevant tick data, including metrics such as Last Traded Price (LTP), 
  Open, High, and other pertinent information, depending on the subscribed event type
  + CandleData event: `1505`
  + Index event: `1512`
  + MarketDepth event: `1502`
  + Market event: `1507`
  + OpenInterest event: `1510`
  + TouchLine event: `1501`
    ```python
        instruments = [
              {"exchangeSegment": 1, "exchangeInstrumentID": 22},
              {"exchangeSegment": 1, "exchangeInstrumentID": 2885},
          ]
  
        response = utradeConnect.send_subscription(
              instruments=instruments, eventCode=1501
          )
    ```
###
+ #### Quotes
  + The Quote service furnishes details pertaining to Asks, Bids and other pertinent information
     ```python
          instruments = [
                {"exchangeSegment": 1, "exchangeInstrumentID": 22},
                {"exchangeSegment": 1, "exchangeInstrumentID": 2885},
            ]
    
          response = utradeConnect.get_quote(
                instruments=instruments, eventCode=1501, publishFormat="JSON"
            )
      ```
###
+ #### Place Order Request
  + To execute an order, leverage the `Interactive API`. The resulting response will include an `AppOrderId`.
    ```python
          response = utradeConnect.place_order(
            exchangeSegment="NSECM",
            exchangeInstrumentID=2885,
            productType="MIS",
            orderType="LIMIT",
            orderSide="BUY",
            timeInForce="DAY",
            disclosedQuantity=0,
            orderQuantity=10,
            limitPrice=300,
            stopPrice=0,
            orderUniqueIdentifier="123abc",
            clientID="C1",
        )
    ```
###
+ #### Cancel Order Request
  + To cancel an order, leverage the `Interactive API`. The resulting response will include an `AppOrderId`.
    ```python
          response = utradeConnect.place_order(
            appOrderID = OrderID
            clientID="C1",
        )
    ``` 
###
> Refer to the [**Python client postman documentation**]() for the complete list of supported methods.

### WebSocket usage
+ #### Market WebSocket
  Transmission of events, including `TouchLine`, `MarketData`, `CandleData`, `OpenInterest`, 
  and `Index`, occurs through the socket. To capture these events, implementation of 
  the `UtradeAPIMarketdataEvents` interface is required. The relevant events will 
  be received through the methods that are specifically overridden within this 
  interface.
    ####
  + Connecting to `Marketdata socket`
    ```
        # Authenticate to obtain an authorization token if you are not currently logged in.
        response = utradeConnect.marketdata_login()
        # Store the token and userid
        set_marketDataToken = response['result']['token']
        set_muserID = response['result']['userID']
        socketInstance = MDSocket_io(set_marketDataToken, set_muserID, base_url, broadcast_mode )
    ```
  + Callback for `Connection` 
    ```
        def on_connect():
            print('Market Data Socket connected successfully!')

            # Subscribe to instruments
            response = utradeConnect.send_subscription(Instruments, 1501)
            print("Subscription response: ", response)
    ```
  + Callback for `Disconnection`
    ```
      def on_disconnect(data):
         print('Market Data Socket disconnected!')
    ```
  + Callback for `overridden methods`
    ```
    # Callback on receiving message
    def on_message(data):
       print('I received a message!')
    
    # Callback for Touchline message with code 1501 FULL
    def on_message1501_json_full(data):
        print('I received a 1501 Touchline message!' , data)
    
    # Callback for Market depth message with code 1502 FULL
    def on_message1502_json_full(data):
        print('I received a 1502 Market depth message!' , data)
    
    # Callback for Candle data message with code 1505 FULL
    def on_message1505_json_full(data):
        print('I received a 1505 Candle data message!' , data)
    
    # Callback for MarketStatus data message with code 1507 FULL
    def on_message1507_json_full(data):
        print('I received a 1507 MarketStatus data message!' , data)
    
    # Callback for Open interest message with code 1510 FULL
    def on_message1510_json_full(data):
        print('I received a 1510 Open interest message!' , data)
    
    # Callback for LTP message with code 1512 FULL
    def on_message1512_json_full(data):
        print('I received a 1512 Level1,LTP message!' , data)
    
    # Callback for Instrument Property Change message with code 1105 FULL 
    def on_message1105_json_full(data):
        print('I received a 1105, Instrument Property Change Event message!' , data)
    ```

+ #### Order WebSocket
  Transmission of events, including `Order`, `Trade Conversion`, `Position`,
  and `Trade`, occurs through the socket. To capture these events, implementation of
  the `UtradeAPIOrderdataEvents` interface is required. The relevant events will
  be received through the methods that are specifically overridden within this
  interface.
  ####
    + Connecting to `Interactive socket`
      ```
          # Authenticate to obtain an authorization token if you are not currently logged in.
          response = utradeConnect.interactive_login(ACCESS_TOKEN)
          # Store the token and userid
          set_interactiveToken = response['result']['token']
          set_iuserID = response['result']['userID']
          socketInstance = OrderSocket_io(set_interactiveToken, set_iuserID, base_url)
      ```
    + Callback for `Connection`
      ```
          def on_connect():
              print('Interactive socket connected successfully!')
      ```
    + Callback for `Disconnection`
      ```
        def on_disconnect(data):
           print('Interactive Socket disconnected!')
      ```
    + Callback for `overridden methods`
      ```
      # Callback for receiving message
      def on_message():
          print('I received a message!')
    
      # Callback for joined event
      def on_joined(data):
          print('Interactive socket joined successfully!' , data)
    
    
      # Callback for error
      def on_error(data):
          print('Interactive socket error!' , data)
    
    
      # Callback for order
      def on_order(data):
          print("Order placed!" , data)
    
    
      # Callback for trade
      def on_trade(data):
          print("Trade Received!" , data)
    
    
      # Callback for position
      def on_position(data):
          print("Position Retrieved!" , data)
    
    
      # Callback for trade conversion event
      def on_tradeconversion(data):
          print("Trade Conversion Received!" , data)
      ```
## Examples

### Example Code

Example code demonstrating how to use the uTrade API can be found in the `utrade-python-api-sdk` example directory.

- `runMarketExample.py`: Examples of all the API calls for Interactive as well as Marketdata APIs.
- `runOrderExample.py`: Examples of all the API calls for Interactive as well as Marketdata APIs.
- `runOrderSocketExample.py`: Interactive Socket Streaming Example.
- `runMarketSocketExample.py`: Marketdata Socket Streaming Example.

