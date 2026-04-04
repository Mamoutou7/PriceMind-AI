from __future__ import annotations

import sqlite3


class Repository:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection
