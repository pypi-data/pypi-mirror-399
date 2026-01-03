"""
Copyright (C) 2026 LEX
Apache 2.0 License  http://www.apache.org/licenses/
---
based on project https://github.com/WLM1ke/aiomoex

Functions to retrieve data on historical daily quotes.
"""

from collections.abc import Iterable
import httpx

from . import client, request_helpers
from .request_helpers import DEFAULT_BOARD, DEFAULT_ENGINE, DEFAULT_MARKET, SECURITIES


async def get_board_dates(
    http_client: httpx.AsyncClient,
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Get the date range available in the history for the market in the specified trading mode.

    Request description - https://iss.moex.com/iss/reference/26

    :param http_client:
        HTTP client.
    :param board:
        Trading mode - default is the main trading mode T+2.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        A list with one element - a dictionary with keys 'from' and 'till'.
    """
    url = request_helpers.make_url(
        history=True,
        engine=engine,
        market=market,
        board=board,
        ending="dates",
    )
    table = "dates"
    return await request_helpers.get_short_data(http_client, url, table)


async def get_board_securities(
    http_client: httpx.AsyncClient,
    table: str = SECURITIES,
    columns: Iterable[str] | None = ("SECID", "REGNUMBER", "LOTSIZE", "SHORTNAME"),
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Get a table of instruments in the trading mode with auxiliary information.

    Request description - https://iss.moex.com/iss/reference/32

    :param http_client:
        HTTP client.
    :param table:
        Data table to return: securities - directory of traded securities,
        marketdata - data with the results of today's trades.
    :param columns:
        Tuple of columns to load - default is ticker, state registration number,
        lot size, and short name. If empty or None, all columns are loaded.
    :param board:
        Trading mode - default is the main trading mode T+2.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        A list of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(engine=engine, market=market, board=board, ending=SECURITIES)
    query = request_helpers.make_query(table=table, columns=columns)
    return await request_helpers.get_short_data(http_client, url, table, query)


async def get_market_history(
    http_client: httpx.AsyncClient,
    security: str,
    start: str | None = None,
    end: str | None = None,
    columns: Iterable[str] | None = ("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Get the history of a single security on the market for all trading modes over a date range.

    There may be multiple values for a single date if trading occurred in multiple modes.

    Request description - https://iss.moex.com/iss/reference/63

    :param http_client:
        HTTP client.
    :param security:
        Security ticker.
    :param start:
        Date in the format YYYY-MM-DD. If absent, data will be loaded from the beginning of history.
    :param end:
        Date in the format YYYY-MM-DD. If absent, data will be loaded until the end of history.
    :param columns:
        Tuple of columns to load - default is trading mode, trade date, closing price,
        volume in pieces, and value. If empty or None, all columns are loaded.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        A list of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(history=True, engine=engine, market=market, security=security)
    table = "history"
    query = request_helpers.make_query(start=start, end=end, table=table, columns=columns)
    return await request_helpers.get_long_data(http_client, url, table, query)


async def get_board_history(
    http_client: httpx.AsyncClient,
    security: str,
    start: str | None = None,
    end: str | None = None,
    columns: Iterable[str] | None = ("BOARDID", "TRADEDATE", "CLOSE", "VOLUME", "VALUE"),
    board: str = DEFAULT_BOARD,
    market: str = DEFAULT_MARKET,
    engine: str = DEFAULT_ENGINE,
) -> client.Table:
    """Get the trading history for the specified security in the specified trading mode over the specified date range.

    Request description - https://iss.moex.com/iss/reference/65

    :param http_client:
        HTTP client.
    :param security:
        Security ticker.
    :param start:
        Date in the format YYYY-MM-DD. If absent, data will be loaded from the beginning of history.
    :param end:
        Date in the format YYYY-MM-DD. If absent, data will be loaded until the end of history.
    :param columns:
        Tuple of columns to load - default is trading mode, trade date, closing price,
        volume in pieces, and value. If empty or None, all columns are loaded.
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
        history=True,
        engine=engine,
        market=market,
        board=board,
        security=security,
    )
    table = "history"
    query = request_helpers.make_query(start=start, end=end, table=table, columns=columns)
    return await request_helpers.get_long_data(http_client, url, table, query)
