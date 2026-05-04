from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SQL_DIR = PROJECT_ROOT / "metabase" / "sql"

MB_URL = os.getenv("MB_URL", "http://localhost:3000").rstrip("/")
MB_EMAIL = os.getenv("MB_ADMIN_EMAIL", "demo@coffee-bi.local")
MB_PASSWORD = os.getenv("MB_ADMIN_PASSWORD", "change_me_metabase")
MB_SITE_NAME = os.getenv("MB_SITE_NAME", "Coffee Commerce BI Demo")

DB_HOST = os.getenv("DB_HOST", "warehouse")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "coffee_warehouse")
DB_USER = os.getenv("DB_USER", "coffee_bi")
DB_PASSWORD = os.getenv("DB_PASSWORD", "change_me_locally")


def _request(method: str, path: str, **kwargs: Any) -> requests.Response:
    response = requests.request(method, f"{MB_URL}{path}", timeout=30, **kwargs)
    if response.status_code >= 400:
        raise RuntimeError(f"Metabase API {method} {path} failed: {response.status_code} {response.text[:500]}")
    return response


def wait_for_metabase() -> None:
    for _ in range(90):
        try:
            response = requests.get(f"{MB_URL}/api/health", timeout=5)
            if response.ok:
                return
        except requests.RequestException:
            pass
        time.sleep(2)
    raise TimeoutError(f"Metabase did not become ready at {MB_URL}")


def setup_or_login() -> str:
    props = _request("GET", "/api/session/properties").json()
    if not props.get("has-user-setup") and props.get("setup-token"):
        payload = {
            "token": props["setup-token"],
            "user": {
                "first_name": "Coffee",
                "last_name": "BI Demo",
                "email": MB_EMAIL,
                "password": MB_PASSWORD,
            },
            "prefs": {"site_name": MB_SITE_NAME, "allow_tracking": False},
            "database": {
                "engine": "postgres",
                "name": "Coffee Commerce Warehouse",
                "details": {
                    "host": DB_HOST,
                    "port": DB_PORT,
                    "dbname": DB_NAME,
                    "user": DB_USER,
                    "password": DB_PASSWORD,
                    "ssl": False,
                    "schema-filters-type": "all",
                },
            },
        }
        token = _request("POST", "/api/setup", json=payload).json()["id"]
        print("Created Metabase admin user and warehouse connection")
        return token

    token = _request("POST", "/api/session", json={"username": MB_EMAIL, "password": MB_PASSWORD}).json()["id"]
    print("Logged in to existing Metabase instance")
    return token


def _headers(token: str) -> dict[str, str]:
    return {"X-Metabase-Session": token}


def _warehouse_database_id(token: str) -> int:
    databases = _request("GET", "/api/database", headers=_headers(token)).json()["data"]
    for database in databases:
        if database["name"] == "Coffee Commerce Warehouse":
            return int(database["id"])
    payload = {
        "engine": "postgres",
        "name": "Coffee Commerce Warehouse",
        "details": {
            "host": DB_HOST,
            "port": DB_PORT,
            "dbname": DB_NAME,
            "user": DB_USER,
            "password": DB_PASSWORD,
            "ssl": False,
            "schema-filters-type": "all",
        },
    }
    return int(_request("POST", "/api/database", headers=_headers(token), json=payload).json()["id"])


def _create_card(token: str, database_id: int, title: str, sql_file: str, display: str) -> int:
    sql = (SQL_DIR / sql_file).read_text(encoding="utf-8")
    payload = {
        "name": title,
        "display": display,
        "dataset_query": {
            "type": "native",
            "database": database_id,
            "native": {"query": sql},
        },
        "visualization_settings": {},
    }
    card = _request("POST", "/api/card", headers=_headers(token), json=payload).json()
    print(f"Created Metabase card: {title}")
    return int(card["id"])


def _attach_cards_to_dashboard(token: str, dashboard_id: int, card_ids: list[int]) -> None:
    dashcards = []
    for position, card_id in enumerate(card_ids):
        dashcards.append(
            {
                "id": -(position + 1),
                "card_id": card_id,
                "row": (position // 2) * 6,
                "col": (position % 2) * 12,
                "size_x": 12,
                "size_y": 6,
                "parameter_mappings": [],
                "series": [],
                "visualization_settings": {},
            }
        )

    dashboard = _request("GET", f"/api/dashboard/{dashboard_id}", headers=_headers(token)).json()
    dashboard["dashcards"] = dashcards
    _request("PUT", f"/api/dashboard/{dashboard_id}", headers=_headers(token), json=dashboard)


def create_demo_dashboard(token: str) -> None:
    database_id = _warehouse_database_id(token)
    cards = [
        ("Daily KPI Trend", "daily_kpis.sql", "line"),
        ("Product Performance", "product_performance.sql", "bar"),
        ("Customer Cohorts", "customer_cohorts.sql", "table"),
        ("Inventory Risk", "inventory_risk.sql", "table"),
        ("Marketing ROI", "marketing_roi.sql", "bar"),
    ]
    card_ids = [_create_card(token, database_id, title, sql_file, display) for title, sql_file, display in cards]
    dashboard = _request(
        "POST",
        "/api/dashboard",
        headers=_headers(token),
        json={"name": "Coffee Commerce BI Executive Dashboard", "description": "Synthetic demo dashboard for BI engineering portfolio."},
    ).json()
    dashboard_id = int(dashboard["id"])

    _attach_cards_to_dashboard(token, dashboard_id, card_ids)

    try:
        _request("PUT", "/api/setting/enable-public-sharing", headers=_headers(token), json={"value": True})
        public_link = _request("POST", f"/api/dashboard/{dashboard_id}/public_link", headers=_headers(token)).json()
        print(f"Public dashboard path: /public/dashboard/{public_link['uuid']}")
    except RuntimeError as exc:
        print(f"Public sharing setup skipped: {exc}")

    print(f"Metabase dashboard id: {dashboard_id}")


def main() -> None:
    wait_for_metabase()
    token = setup_or_login()
    create_demo_dashboard(token)


if __name__ == "__main__":
    main()
