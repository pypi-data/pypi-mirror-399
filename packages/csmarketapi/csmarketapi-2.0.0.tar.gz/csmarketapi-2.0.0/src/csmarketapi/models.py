from __future__ import annotations

import datetime
from typing import Any

from pydantic import BaseModel

from .enums import Market


class ListingsLatestAggregated(BaseModel):
    class Listing(BaseModel):
        id: int
        market: Market
        market_link: str
        mean_price: float | None
        min_price: float | None
        max_price: float | None
        median_price: float | None
        listings: int
        timestamp: datetime.datetime

    market_hash_name: str
    listings: list[Listing]


class ListingsHistoryAggregated(BaseModel):

    class Item(BaseModel):
        class Listing(BaseModel):
            id: int
            market: Market
            mean_price: float | None
            min_price: float | None
            max_price: float | None
            median_price: float | None
            listings: int

        timestamp: datetime.datetime
        listings: list[Listing]

    items: list[Item]


class SalesLatestAggregated(BaseModel):

    class Sale(BaseModel):
        id: int
        market: Market
        mean_price: float | None
        min_price: float | None
        max_price: float | None
        median_price: float | None
        volume: int | None
        day: datetime.date

    market_hash_name: str
    sales: list[Sale]


class SalesHistoryAggregated(BaseModel):

    class Item(BaseModel):
        class Sale(BaseModel):
            id: int
            market: Market
            mean_price: float | None
            min_price: float | None
            max_price: float | None
            median_price: float | None
            volume: int | None

        day: datetime.date
        sales: list[Sale]

    items: list[Item]


class Items(BaseModel):
    class Item(BaseModel):
        market_hash_name: str
        hash_name: str
        nameid: int | None = None
        classid: str | None = None
        exterior: str | None = None
        category: str | None = None
        weapon: str | None = None
        max_sticker_amount: int | None = None
        used_by_class: str | None = None
        quality: str | None = None
        type: str | None = None
        sticker_type: str | None = None
        graffiti_type: str | None = None
        patch_type: str | None = None
        collection: str | None = None
        sticker_collection: str | None = None
        graffiti_collection: str | None = None
        patch_collection: str | None = None
        graffiti_color: str | None = None
        professional_player: str | None = None
        tournament: str | None = None
        team: str | None = None
        min_float: float | None = None
        max_float: float | None = None
        droppool: str | None = None
        release_dt: str | None = None
        akamai_icon_url: str | None = None
        cloudflare_icon_url: str | None = None

    items: list[Item]


class CurrencyRates(BaseModel):

    class CurrencyRate(BaseModel):
        currency_code: str
        currency_name: str
        currency_symbol: str
        rate: float
        timestamp: datetime.datetime

    items: list[CurrencyRate]


class PlayerCountsLatest(BaseModel):
    timestamp: datetime.datetime
    count: int


class PlayerCountsHistory(BaseModel):
    class Item(BaseModel):
        timestamp: datetime.datetime
        count: int

    items: list[Item]


class Markets(BaseModel):
    class Trustpilot(BaseModel):
        rating: float | None = None
        reviews: int | None = None
        link: str | None = None

    class FeeRange(BaseModel):
        min: float | None = None
        max: float | None = None

    class Fees(BaseModel):
        deposit: float | Markets.FeeRange | None = None
        buyer: float | Markets.FeeRange | None = None
        seller: float | Markets.FeeRange | None = None
        withdrawal: float | Markets.FeeRange | None = None

    class Market(BaseModel):
        market: str
        url: str
        description: str | None = None
        type: str | None = None
        country: str | None = None
        icon: str | None = None
        trustpilot: Markets.Trustpilot | None = None
        fees: Markets.Fees | None = None
        updated_at: datetime.datetime | None = None

    items: list[Market]