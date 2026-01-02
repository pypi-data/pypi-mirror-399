import os

import dotenv
import pytest
import pytest_asyncio

from csmarketapi import CSMarketAPI
from csmarketapi.enums import Market


@pytest.fixture(scope="session", autouse=True)
def load_env():
    dotenv.load_dotenv()


@pytest_asyncio.fixture
async def client():
    return CSMarketAPI(os.getenv("API_KEY"))


@pytest.mark.asyncio
async def test_get_listings_latest_aggregated(client: CSMarketAPI):
    await client.get_listings_latest_aggregated(
        market_hash_name="Chroma 2 Case",
        markets=list(Market),
    )


@pytest.mark.asyncio
async def test_get_listings_history_aggregated(client: CSMarketAPI):
    await client.get_listings_history_aggregated(
        market_hash_name="Chroma 2 Case",
        markets=list(Market),
    )


@pytest.mark.asyncio
async def test_get_sales_latest_aggregated(client: CSMarketAPI):
    await client.get_sales_latest_aggregated(
        market_hash_name="Chroma 2 Case",
        markets=list(Market),
    )


@pytest.mark.asyncio
async def test_get_sales_history_aggregated(client: CSMarketAPI):
    await client.get_sales_history_aggregated(
        market_hash_name="Chroma 2 Case",
        markets=list(Market),
    )


@pytest.mark.asyncio
async def test_get_items(client: CSMarketAPI):
    await client.get_items()


@pytest.mark.asyncio
async def test_get_currency_rates(client: CSMarketAPI):
    await client.get_currency_rates()


@pytest.mark.asyncio
async def test_get_player_counts_latest(client: CSMarketAPI):
    await client.get_player_counts_latest()


@pytest.mark.asyncio
async def test_get_player_counts_history(client: CSMarketAPI):
    await client.get_player_counts_history()


@pytest.mark.asyncio
async def test_get_steam_profile(client: CSMarketAPI):
    await client.get_steam_profile(
        steam_id="76561198032362775",
    )


@pytest.mark.asyncio
async def test_get_steam_inventory(client: CSMarketAPI):
    await client.get_steam_inventory(
        steam_id="76561198032362775",
    )


@pytest.mark.asyncio
async def test_get_steam_friendslist(client: CSMarketAPI):
    await client.get_steam_friendslist(
        steam_id="76561198032362775",
    )


@pytest.mark.asyncio
async def test_get_float_info(client: CSMarketAPI):
    await client.get_float_info(
        inspect_link="steam://rungame/730/76561202255233023/+csgo_econ_action_preview%20M637943594289708232A46177406910D291823901775499029",
    )


@pytest.mark.asyncio
async def test_get_markets(client: CSMarketAPI):
    await client.get_markets()

