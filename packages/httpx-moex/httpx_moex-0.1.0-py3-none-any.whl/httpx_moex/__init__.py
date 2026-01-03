"""
Copyright (C) 2026 LEX
Apache 2.0 License  http://www.apache.org/licenses/
---
based on project https://github.com/WLM1ke/aiomoex

Implementation of some requests to MOEX ISS.

The results of the requests are lists of dictionaries and can be converted into pandas.DataFrame.

The operation of the request functions is based on a universal client that allows making arbitrary
requests to ISS MOEX, so the list of available request functions can be expanded if necessary:

- Full list of requests https://iss.moex.com/iss/reference/
- Additional description https://fs.moex.com/files/6523
"""
from .candles import (
    get_board_candle_borders,
    get_board_candles,
    get_market_candle_borders,
    get_market_candles,
)
from .client import ISSClient, TableRow, TablesDict, Values
from .history import get_board_dates, get_board_history, get_board_securities, get_market_history
from .reference import find_securities, get_reference

__all__ = [
    "get_board_candle_borders",
    "get_board_candles",
    "get_market_candle_borders",
    "get_market_candles",
    "ISSClient",
    "TableRow",
    "TablesDict",
    "Values",
    "get_board_dates",
    "get_board_history",
    "get_board_securities",
    "get_market_history",
    "find_securities",
    "get_reference",
]
