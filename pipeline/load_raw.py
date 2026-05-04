from __future__ import annotations

from pathlib import Path

import psycopg

from pipeline.settings import DATA_DIR, WarehouseSettings

RAW_TABLES: dict[str, list[str]] = {
    "customers": ["customer_id", "created_at", "province", "city", "acquisition_channel", "coffee_persona"],
    "products": ["product_id", "sku", "product_name", "category", "origin_country", "roast_level", "list_price", "cogs"],
    "orders": ["order_id", "customer_id", "order_ts", "status", "payment_method", "province", "city", "voucher_amount", "shipping_fee"],
    "order_items": ["order_item_id", "order_id", "product_id", "quantity", "unit_price", "item_discount"],
    "inventory_snapshots": ["snapshot_id", "snapshot_date", "product_id", "stock_on_hand", "stock_reserved", "reorder_point"],
    "marketing_spend": ["spend_id", "spend_date", "channel", "campaign", "spend_amount", "impressions", "clicks"],
    "web_events": ["event_id", "event_ts", "customer_id", "session_id", "event_type", "channel", "product_id", "order_id"],
}


def _connect(settings: WarehouseSettings) -> psycopg.Connection:
    return psycopg.connect(
        host=settings.host,
        port=settings.port,
        dbname=settings.dbname,
        user=settings.user,
        password=settings.password,
    )


def _create_raw_tables(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute("create schema if not exists raw;")
        for table_name, columns in RAW_TABLES.items():
            column_defs = ", ".join(f"{column} text" for column in columns)
            cur.execute(f"create table if not exists raw.{table_name} ({column_defs});")
        cur.execute(
            "truncate table "
            + ", ".join(f"raw.{table_name}" for table_name in RAW_TABLES)
            + ";"
        )
    conn.commit()


def _copy_csv(conn: psycopg.Connection, table_name: str, columns: list[str], path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Missing generated source file: {path}")
    column_sql = ", ".join(columns)
    with conn.cursor() as cur:
        with cur.copy(f"copy raw.{table_name} ({column_sql}) from stdin with (format csv, header true)") as copy:
            copy.write(path.read_text(encoding="utf-8"))
    conn.commit()


def load_raw_data(input_dir: Path = DATA_DIR, settings: WarehouseSettings | None = None) -> None:
    settings = settings or WarehouseSettings()
    with _connect(settings) as conn:
        _create_raw_tables(conn)
        for table_name, columns in RAW_TABLES.items():
            _copy_csv(conn, table_name, columns, input_dir / f"{table_name}.csv")
            print(f"Loaded raw.{table_name}")


if __name__ == "__main__":
    load_raw_data()
