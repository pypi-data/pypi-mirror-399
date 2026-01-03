# Define API routes for Orders
orders_routes = {
    "interactive.prefix": "interactive",
    "user.login": "/api/V2/accounts/login/",
    "user.logout": "/api/V2/accounts/logout",
    "user.profile": "api/V2/accounts/profile",
    "user.balance": "/api/V2/accounts/balance",
    "orders": "/interactive/orders",
    "trades": "api/V2/orders/trades",
    "order.status": "/api/V2/orders",
    "order.place": "/api/V2/orders/",
    "order.modify": "/api/V2/orders/",
    "order.cancel": "/api/V2/orders/",
    "order.cancelall": "/api/V2/orders/cancelAll",
    "order.history": "api/V2/orders",
    "portfolio.positions": "/api/V2/orders/positions/",
    "portfolio.holdings": "/api/V2/orders/holdings/",
    "portfolio.positions.convert": "/api/V2/orders/position/convert",
    "portfolio.squareoff": "/interactive/portfolio/squareoff",
    "portfolio.dealerpositions": "/api/V2/orders/positions/",
    "order.dealer.status": "api/V2/orders/trades",
    "dealer.trades": "api/V2/orders/trades"
}

# Define API routes for Market Data
market_routes = {
    "marketdata.prefix": "marketdata",
    "market.login": "/api/V2/marketData/auth/login",
    "market.logout": "/api/V2/marketData/auth/logout",
    "market.config": "/api/V2/marketData/clientConfig",
    "market.instruments.master": "/api/V2/marketData/master",
    "market.instruments.subscription": "/api/V2/marketData/subscription",
    "market.instruments.unsubscription": "/api/V2/marketData/subscription",
    "market.instruments.ohlc": "/api/V2/marketData/ohlc",
    "market.instruments.indexlist": "/api/V2/marketData/getIndices",
    "market.instruments.quotes": "/api/V2/marketData/getQuotes",
    "market.search.instrumentsbyid": '/api/V2/marketData/search/instrumentsbyid',
    "market.search.instrumentsbystring": '/api/V2/marketData/search/instrumentsByString',
    "market.instruments.instrument.series": "/api/V2/marketData/getSeries",
    "market.instruments.instrument.equitysymbol": "/api/V2/marketData/getEquity",
    "market.instruments.instrument.futuresymbol": "/api/V2/marketData/getFuture",
    "market.instruments.instrument.optionsymbol": "/api/V2/marketData/getOption",
    "market.instruments.instrument.optiontype": "/api/V2/marketData/optionType",
    "market.instruments.instrument.expirydate": "/api/V2/marketData/getExpiry"
}

all_routes = {**orders_routes, **market_routes}

def get_orders_routes():
    """
    Returns the dictionary containing API routes for Orders.

    Returns:
        dict: Dictionary containing API routes for Orders.
    """
    return orders_routes

def get_market_routes():
    """
    Returns the dictionary containing API routes for Market Data.

    Returns:
        dict: Dictionary containing API routes for Market Data.
    """
    return market_routes

def get_all_routes():
    """
    Returns the dictionary containing all API routes.

    Returns:
        dict: Dictionary containing all API routes.
    """
    return all_routes
