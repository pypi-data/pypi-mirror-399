import os
import sys
from .auth import get_session_token

# Allow absolute imports for bundled openapi_client
sys.path.append(os.path.dirname(__file__))
from openapi_client.api import orders_api, market_data_api, funds_api

class Tradejini:
    def __init__(self):
        self.bearer_token = get_session_token()
        # Initializing core SDK APIs
        self.orders = orders_api.OrdersApi()
        self.market = market_data_api.MarketDataApi()
        self.funds = funds_api.FundsApi()
        print("🚀 Tradejini Unified API Connected")

    def place_order(self, sym_id, qty, side, order_type="market", product="intraday"):
        """Wrapper for order placement."""
        # Logic to call self.orders.place_order with bearer_token
        pass