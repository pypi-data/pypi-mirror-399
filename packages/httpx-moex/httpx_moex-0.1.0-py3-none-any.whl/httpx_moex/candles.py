"""
Copyright (C) 2026 LEX
Apache 2.0 License  http://www.apache.org/licenses/
---
based on project https://github.com/WLM1ke/aiomoex

Functions to get information about candles.
"""

from collections.abc import Iterable
import httpx

from . import client, request_helpers
from .request_helpers import (
    CANDLE_BORDERS,
    CANDLES,
    DEFAULT_BOARD,
    DEFAULT_ENGINE,
    DEFAULT_MARKET,
)

CANDLES_M1 = 1
CANDLES_M10 = 10
CANDLES_M60 = 60
CANDLES_D = 24
CANDLES_W = 7
CANDLES_M = 31
CANDLES_Q = 4


async def get_market_candle_borders(
    http_client: httpx.AsyncClient,
    security: str,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Get a table of available date intervals for all trading modes.

    Request description - https://iss.moex.com/iss/reference/156

    :param client:
        HTTP client.
    :param security:
        Ticker symbol of the security.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        A list of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(
        engine=engine,
        market=market,
        security=security,
        ending=CANDLE_BORDERS,
    )
    table = "borders"
    return await request_helpers.get_short_data(http_client, url, table)


async def get_board_candle_borders(
    http_client: httpx.AsyncClient,
    security: str,
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Get a table of available date intervals for the specified trading mode.

    Request description - https://iss.moex.com/iss/reference/48

    :param client:
        HTTP client.
    :param security:
        Ticker symbol of the security.
    :param board:
        Trading mode - default is the main trading mode T+2.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        A list of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(
        engine=engine,
        market=market,
        board=board,
        security=security,
        ending=CANDLE_BORDERS,
    )
    table = "borders"
    return await request_helpers.get_short_data(http_client, url, table)


async def get_market_candles(
    http_client: httpx.AsyncClient,
    security: str,
    interval: int = 24,
    start: str | None = None,
    end: str | None = None,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
    columns: Iterable[str] | None = ("begin", "open", "high", "low", "close", "volume"),
) -> client.Table:
    """Get candles in HLOCV format for the specified instrument on the market for the main trading mode.

    If trading occurs in multiple main modes, multiple candles may be returned for a single time interval - one candle per mode. This situation is likely to occur for candles longer than 1 day.

    Request description - https://iss.moex.com/iss/reference/155

    :param client:
        HTTP client.
    :param security:
        Ticker symbol of the security.
    :param interval:
        Candle size - an integer 1 (1 minute), 10 (10 minutes), 60 (1 hour), 24 (1 day), 7 (1 week),
        31 (1 month), or 4 (1 quarter). Default is daily data.
    :param start:
        Date in the format YYYY-MM-DD. If absent, data will be loaded from the beginning of history.
    :param end:
        Date in the format YYYY-MM-DD. If absent, data will be loaded until the end of history.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        A list of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(engine=engine, market=market, security=security, ending=CANDLES)
    table = CANDLES
    query = request_helpers.make_query(interval=interval, start=start, end=end, table=table, columns=columns)
    return await request_helpers.get_long_data(http_client, url, table, query)


async def get_board_candles(
    http_client: httpx.AsyncClient,
    security: str,
    interval: int = 24,
    start: str | None = None,
    end: str | None = None,
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
    columns: Iterable[str] | None = ("begin", "open", "high", "low", "close", "volume"),
) -> client.Table:
    """Get candles in HLOCV format for the specified instrument in the specified trading mode for a date interval.

    Request description - https://iss.moex.com/iss/reference/46

    :param client:
        HTTP client.
    :param security:
        Ticker symbol of the security.
    :param interval:
        Candle size - an integer 1 (1 minute), 10 (10 minutes), 60 (1 hour), 24 (1 day), 7 (1 week),
        31 (1 month), or 4 (1 quarter). Default is daily data.
    :param start:
        Date in the format YYYY-MM-DD. If absent, data will be loaded from the beginning of history.
    :param end:
        Date in the format YYYY-MM-DD. If absent, data will be loaded until the end of history.
    :param board:
        Trading mode - default is the main trading mode T+2.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        A list of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(
        engine=engine,
        market=market,
        board=board,
        security=security,
        ending=CANDLES,
    )
    table = CANDLES
    query = request_helpers.make_query(interval=interval, start=start, end=end, table=table, columns=columns)
    return await request_helpers.get_long_data(http_client, url, table, query)
