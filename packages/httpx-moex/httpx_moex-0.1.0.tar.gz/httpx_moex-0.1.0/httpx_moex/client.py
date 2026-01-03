"""
Copyright (C) 2026 LEX
Apache 2.0 License  http://www.apache.org/licenses/
---
based on project https://github.com/WLM1ke/aiomoex

"""

from collections.abc import AsyncIterable, AsyncIterator
from typing import cast

import httpx

Values = str | int | float
TableRow = dict[str, Values]
Table = list[TableRow]
TablesDict = dict[str, Table]
WebQuery = dict[str, str | int]


class ISSMoexError(Exception):
    """Errors during request processing."""


def _cursor_block_size(start: int, cursor_table: Table) -> int:
    cursor, *wrong_data = cursor_table

    if wrong_data or cast(int, cursor["INDEX"]) != start:
        raise ISSMoexError(f"Incorrect data in history.cursor: {cursor_table}")

    block_size = cast(int, cursor["PAGESIZE"])

    if start + block_size < cast(int, cursor["TOTAL"]):
        return block_size
    return 0


class ISSClient(AsyncIterable[TablesDict]):
    """Asynchronous client for MOEX ISS - can be used with async for.

    Loads data for simple responses using the get method. For responses consisting of multiple blocks,
    the asynchronous generator protocol for individual blocks or the get_all method for their
    automatic collection is supported.
    """

    def __init__(self, http_client: httpx.AsyncClient, url: str, query: WebQuery | None = None) -> None:
        """MOEX ISS is a REST server.

        Full list of requests and their parameters https://iss.moex.com/iss/reference/
        Additional description https://fs.moex.com/files/6523

        :param http_client:
            HTTP client for connections.
        :param url:
            Request address.
        :param query:
            List of additional request parameters. The list of additional parameters always
            includes the requirement to provide the response as an extended json without metadata.
        """
        self._client = http_client
        self._url = url
        self._query = query or {}

    def __repr__(self) -> str:
        """Class name and content of the request to ISS Moex."""
        class_name = self.__class__.__name__
        return f"{class_name}(url={self._url}, query={self._query})"

    def __aiter__(self) -> AsyncIterator[TablesDict]:
        """Asynchronous generator for responses consisting of multiple blocks."""
        return self._iterator_maker()

    async def get(self, start: int | None = None) -> TablesDict:
        """Data loading.

        :param start:
            Element number from which to load data. Used for additional data loading,
            consisting of multiple blocks. If absent, data is loaded from the initial element.

        :return:
            Data block with auxiliary information discarded - a dictionary, each key of which
            corresponds to one of the data tables. Tables are lists of dictionaries that are directly
            converted to pandas.DataFrame.
        :raises ISSMoexError:
            Error when accessing ISS Moex.
        """
        url = self._url
        query = self._make_query(start)
        try:
            response = await self._client.get(url, params=query)
            response.raise_for_status()
            raw_respond: list[dict[str, Table]] = response.json()
            return raw_respond[1]
        except httpx.RequestError as err:
            raise ISSMoexError("Connection error", err.request.url) from err
        except httpx.HTTPStatusError as err:
            raise ISSMoexError("HTTP error", err.request.url) from err


    async def get_all(self) -> TablesDict:
        """Collects all data blocks for requests.

        :return:
            Combined data from all blocks with auxiliary information discarded - a dictionary,
            each key of which corresponds to one of the data tables. Tables are lists of
            dictionaries that are directly converted to pandas.DataFrame.
        """
        all_data: TablesDict = {}
        async for block in self:
            for table_name, table_rows in block.items():
                all_data.setdefault(table_name, []).extend(table_rows)
        return all_data


    def _make_query(self, start: int | None = None) -> WebQuery:
        """Forms the query parameters."""
        query: WebQuery = {"iss.json": "extended", "iss.meta": "off"} | self._query
        if start:
            query["start"] = start
        return query


    async def _iterator_maker(self) -> AsyncIterator[TablesDict]:
        start = 0
        while True:
            respond = await self.get(start)
            if (cursor_table := respond.get("history.cursor")) is not None:
                respond.pop("history.cursor")
                yield respond

                block_size = _cursor_block_size(start, cursor_table)
            else:
                yield respond

                table_name = next(iter(respond))
                block_size = len(respond[table_name])

            if not block_size:
                return
            start += block_size
