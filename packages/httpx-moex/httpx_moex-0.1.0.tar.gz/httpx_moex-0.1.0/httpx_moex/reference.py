"""
Copyright (C) 2026 LEX
Apache 2.0 License  http://www.apache.org/licenses/
---
based on project https://github.com/WLM1ke/aiomoex

Functions for obtaining reference information.
"""

from collections.abc import Iterable

import httpx

from . import client, request_helpers
from .request_helpers import SECURITIES, SERIES


async def get_reference(
    http_client: httpx.AsyncClient,
    placeholder: str = "boards"
) -> client.Table:
    """Get a list of available placeholder values in the request address.

    For example, in the request description https://iss.moex.com/iss/reference/32, the following address
    /iss/engines/[engine]/markets/[market]/boards/[board]/securities contains placeholders engines, markets, and
    boards.

    Request description - https://iss.moex.com/iss/reference/28

    :param http_client:
        Http client.
    :param placeholder:
        Name of the placeholder in the request address: engines, markets, boards, boardgroups, durations,
        securitytypes, securitygroups, securitycollections.

    :return:
        List of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(ending="index")
    return await request_helpers.get_short_data(http_client, url, placeholder)


async def find_securities(
    http_client: httpx.AsyncClient,
    string: str,
    columns: Iterable[str] | None = ("secid", "regnumber"),
) -> client.Table:
    """Find instruments by part of the Code, Name, ISIN, Issuer ID, State Registration Number.

    One use case is to find previous tickers of an issuer by registration number and use multiple
    historical quote requests to compile a long history using all previous tickers.

    Request description - https://iss.moex.com/iss/reference/5

    :param http_client:
        Http client.
    :param string:
        Part of the Code, Name, ISIN, Issuer ID, State Registration Number.
    :param columns:
        Tuple of columns to load - by default, ticker and state registration number.
        If empty or None, all columns are loaded.

    :return: List of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(ending=SECURITIES)
    table = SECURITIES
    query = request_helpers.make_query(question=string, table=table, columns=columns)
    return await request_helpers.get_short_data(http_client, url, table, query)


async def get_statistics_series(
    http_client: httpx.AsyncClient,
    asset_code: str | None = None,
    show_expired: bool | None = True,
    market: str = 'forts',
    engine: str = 'futures',
) -> client.Table:
    """Get a list of statistics.

    https://iss.moex.com/iss/reference/151

    :param http_client:
        HTTP client.
    :param asset_code:
        Base asset code.
    :param show_expired:
        Show already non-trading series.
    :param market:
        Market - default is stocks.
    :param engine:
        Engine - default is stocks.

    :return:
        List of dictionaries that can be directly converted into a pandas.DataFrame.
    """
    url = request_helpers.make_url(
        statistics=True,
        history=False,
        engine=engine,
        market=market,
        ending=SERIES,
    )
    table = SERIES
    query = request_helpers.make_query()
    if asset_code:
        query["asset_code"] = asset_code
    if show_expired:
        query["show_expired"] = 1
    return await request_helpers.get_short_data(http_client, url, table, query)
