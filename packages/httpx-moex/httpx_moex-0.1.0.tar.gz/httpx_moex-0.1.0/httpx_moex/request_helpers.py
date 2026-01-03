"""
Copyright (C) 2026 LEX
Apache 2.0 License  http://www.apache.org/licenses/
---
based on project https://github.com/WLM1ke/aiomoex

Helper functions for building requests.
"""

from collections.abc import Iterable
from typing import Final
import httpx

from . import client

# Default modes for requests
DEFAULT_ENGINE: Final = "stock"
DEFAULT_MARKET: Final = "shares"
DEFAULT_BOARD: Final = "TQBR"
# Key placeholders and constants for requests
SECURITIES: Final = "securities"
SERIES: Final = "series"
CANDLE_BORDERS: Final = "candleborders"
CANDLES: Final = "candles"


def make_url(
    *,
    history: bool | None = None,
    statistics: bool | None = None,
    engine: str | None = None,
    market: str | None = None,
    board: str | None = None,
    security: str | None = None,
    ending: str | None = None,
) -> str:
    """Forms the URL for the request."""
    url_parts = ["https://iss.moex.com/iss"]
    if history:
        url_parts.append("/history")
    elif statistics:
        url_parts.append("/statistics")

    if engine:
        url_parts.append(f"/engines/{engine}")
    if market:
        url_parts.append(f"/markets/{market}")
    if board:
        url_parts.append(f"/boards/{board}")
    if security:
        url_parts.append(f"/securities/{security}")
    if ending:
        url_parts.append(f"/{ending}")
    url_parts.append(".json")
    return "".join(url_parts)


def make_query(
    *,
    question: str | None = None,
    interval: int | None = None,
    start: str | None = None,
    end: str | None = None,
    table: str | None = None,
    columns: Iterable[str] | None = None,
) -> client.WebQuery:
    """Forms additional request parameters for MOEX ISS.

    :param question:
        String with part of the security characteristics for search.
    :param interval:
        Candle size.
    :param start:
        Start date of quotes.
    :param end:
        End date of quotes.
    :param table:
        Table to be loaded (for requests assuming the presence of multiple tables).
    :param columns:
        Tuple of columns to be loaded.

    :return:
        Dictionary with additional request parameters.
    """
    query: client.WebQuery = {}
    if question:
        query["q"] = question
    if interval:
        query["interval"] = interval
    if start:
        query["from"] = start
    if end:
        query["till"] = end
    if table:
        query["iss.only"] = f"{table},history.cursor"
    if columns:
        query[f"{table}.columns"] = ",".join(columns)
    return query


def get_table(table_dict: client.TablesDict, table_name: str) -> client.Table:
    """Extracts a specific table from the data."""
    try:
        table = table_dict[table_name]
    except KeyError as err:
        raise client.ISSMoexError(f"Table {table_name} is missing in the data") from err
    return table


async def get_short_data(
    http_client: httpx.AsyncClient,
    url: str,
    table_name: str,
    query: client.WebQuery | None = None,
) -> client.Table:
    """Get data for a request with all information returned at once.

    :param http_client:
        HTTP client.
    :param url:
        Request URL.
    :param query:
        Additional request parameters - None if no parameters.
    :param table_name:
        Table to be selected.

    :return:
        Specific table from the request.
    """
    iss = client.ISSClient(http_client, url, query)
    table_dict = await iss.get()
    return get_table(table_dict, table_name)


async def get_long_data(
    http_client: httpx.AsyncClient,
    url: str,
    table_name: str,
    query: client.WebQuery | None = None,
) -> client.Table:
    """Get data for a request where information is returned in multiple blocks.

    :param http_client:
        HTTP client.
    :param url:
        Request URL.
    :param query:
        Additional request parameters - None if no parameters.
    :param table_name:
        Table to be selected.

    :return:
        Specific table from the request.
    """
    iss = client.ISSClient(http_client, url, query)
    table_dict = await iss.get_all()
    return get_table(table_dict, table_name)
