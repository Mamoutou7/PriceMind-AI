from __future__ import annotations

from apps.storage_mcp.db.connection import get_connection


def main() -> None:
    connection = get_connection()
    connection.close()
    print("Database bootstrapped successfully.")


if __name__ == "__main__":
    main()
