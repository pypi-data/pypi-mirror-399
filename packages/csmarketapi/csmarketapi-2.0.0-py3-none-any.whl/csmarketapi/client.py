import httpx

from .enums import Currency, Market
from .models import (
    CurrencyRates,
    Items,
    ListingsHistoryAggregated,
    ListingsLatestAggregated,
    Markets,
    PlayerCountsHistory,
    PlayerCountsLatest,
    SalesHistoryAggregated,
    SalesLatestAggregated,
)


class CSMarketAPI:
    def __init__(self, api_key: str):
        self.client = httpx.AsyncClient(
            base_url="https://api.csmarketapi.com",
            params={
                "key": api_key,
            },
            follow_redirects=True,
        )

    async def __aenter__(self) -> "CSMarketAPI":
        return self

    async def __aexit__(
        self,
        exc_type: type[Exception] | None,
        exc_value: Exception | None,
        traceback: any,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        await self.client.aclose()
        self.client = None

    async def get_listings_latest_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        currency: Currency = Currency.USD,
        max_age: str | None = None,
    ) -> ListingsLatestAggregated:
        r = await self.client.get(
            "/v1/listings/latest/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                "currency": currency.value,
                **({"max_age": max_age} if max_age is not None else {}),
            },
        )
        r.raise_for_status()
        return ListingsLatestAggregated(**r.json())

    async def get_listings_history_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        currency: Currency = Currency.USD,
        max_age: str | None = None,
    ) -> ListingsHistoryAggregated:
        r = await self.client.get(
            "/v1/listings/history/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                "currency": currency.value,
                **({"max_age": max_age} if max_age is not None else {}),
            },
        )
        r.raise_for_status()
        return ListingsHistoryAggregated(items=r.json())

    async def get_sales_latest_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        currency: Currency = Currency.USD,
    ) -> SalesLatestAggregated:
        r = await self.client.get(
            "/v1/sales/latest/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                "currency": currency.value,
            },
        )
        r.raise_for_status()
        return SalesLatestAggregated(**r.json())

    async def get_sales_history_aggregated(
        self,
        market_hash_name: str,
        markets: list[Market],
        start: str | None = None,
        end: str | None = None,
        currency: Currency = Currency.USD,
    ) -> SalesHistoryAggregated:
        r = await self.client.get(
            "/v1/sales/history/aggregate",
            params={
                "market_hash_name": market_hash_name,
                "markets": [market.value for market in markets],
                **({"start": start} if start is not None else {}),
                **({"end": end} if end is not None else {}),
                "currency": currency.value,
            },
        )
        r.raise_for_status()

        return SalesHistoryAggregated(items=r.json())

    async def get_items(self) -> Items:
        r = await self.client.get("/v1/items")
        r.raise_for_status()
        return Items(items=r.json())

    async def get_markets(self) -> Markets:
        r = await self.client.get("/v1/markets")
        r.raise_for_status()
        return Markets(items=r.json())

    async def get_currency_rates(self) -> CurrencyRates:
        r = await self.client.get("/v1/currency_rates")
        r.raise_for_status()
        return CurrencyRates(items=r.json())

    async def get_player_counts_latest(self) -> PlayerCountsLatest:
        r = await self.client.get("/v1/player_counts/latest")
        r.raise_for_status()
        return PlayerCountsLatest(**r.json())

    async def get_player_counts_history(
        self,
        start: str | None = None,
        end: str | None = None,
    ) -> PlayerCountsHistory:
        r = await self.client.get(
            "/v1/player_counts/history",
            params={
                **({"start": start} if start is not None else {}),
                **({"end": end} if end is not None else {}),
            },
        )
        r.raise_for_status()
        return PlayerCountsHistory(items=r.json())
