from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WarehouseSettings:
    host: str = os.getenv("DB_HOST", "localhost")
    port: int = int(os.getenv("DB_PORT", "5432"))
    dbname: str = os.getenv("DB_NAME", "coffee_warehouse")
    user: str = os.getenv("DB_USER", "coffee_bi")
    password: str = os.getenv("DB_PASSWORD", "change_me_locally")


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("DATA_DIR", PROJECT_ROOT / "data" / "generated"))
ANALYTICS_DIR = PROJECT_ROOT / "analytics"
