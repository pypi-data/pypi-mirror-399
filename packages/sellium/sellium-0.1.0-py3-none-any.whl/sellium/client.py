from __future__ import annotations

from typing import Optional
import httpx

from ._http import HTTPClient
from .services.store import StoreService
from .services.products import ProductsService
from .services.orders import OrdersService
from .services.coupons import CouponsService
from .services.customers import CustomersService
from .services.tickets import TicketsService
from .services.feedback import FeedbackService
from .services.blacklist import BlacklistService
from .services.groups import GroupsService


class SelliumClient:
    def __init__(
        self,
        api_key: str,
        store_id: str,
        *,
        base_url: str,
        user_agent: str = "sellium-python/0.1",
        timeout: float = 30.0,
        http_client: Optional[httpx.Client] = None,
    ) -> None:
        self._http = HTTPClient(
            api_key=api_key,
            store_id=store_id,
            base_url=base_url,
            user_agent=user_agent,
            timeout=timeout,
            client=http_client,
        )

        self.store = StoreService(self._http)
        self.products = ProductsService(self._http)
        self.orders = OrdersService(self._http)
        self.coupons = CouponsService(self._http)
        self.customers = CustomersService(self._http)
        self.tickets = TicketsService(self._http)
        self.feedback = FeedbackService(self._http)
        self.blacklist = BlacklistService(self._http)
        self.groups = GroupsService(self._http)

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SelliumClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()
