from __future__ import annotations

import csv
import random
from datetime import date, datetime, timedelta
from pathlib import Path

from pipeline.settings import DATA_DIR

RANDOM_SEED = 42
START_DATE = date(2025, 9, 1)
END_DATE = date(2026, 4, 30)

CHANNELS = ["direct", "email", "paid_search", "paid_social", "marketplace", "referral"]
PAID_CHANNELS = ["email", "paid_search", "paid_social", "marketplace", "referral"]
PROVINCES = [
    ("DKI Jakarta", ["Jakarta Selatan", "Jakarta Barat", "Jakarta Utara"]),
    ("Jawa Barat", ["Bandung", "Bekasi", "Depok"]),
    ("Jawa Timur", ["Surabaya", "Malang", "Sidoarjo"]),
    ("Bali", ["Denpasar", "Badung"]),
    ("Sumatera Utara", ["Medan", "Binjai"]),
]
PERSONAS = ["home_brewer", "office_buyer", "cafe_owner", "espresso_hobbyist", "gift_buyer"]
PAYMENT_METHODS = ["bank_transfer", "credit_card", "e_wallet", "cod"]

PRODUCTS = [
    ("P001", "BEAN-GAYO-250", "Gayo Wine Process 250g", "beans", "Indonesia", "medium", 145000, 72000),
    ("P002", "BEAN-TORAJA-250", "Toraja Sapan 250g", "beans", "Indonesia", "medium_dark", 132000, 68000),
    ("P003", "BEAN-KINTAMANI-250", "Bali Kintamani Natural 250g", "beans", "Indonesia", "light", 128000, 61000),
    ("P004", "BEAN-FLORES-250", "Flores Bajawa 250g", "beans", "Indonesia", "medium", 118000, 57000),
    ("P005", "SUB-HOUSE-1M", "Monthly House Blend Subscription", "subscription", "Indonesia", "medium", 399000, 210000),
    ("P006", "GEAR-V60-02", "V60 Dripper 02", "brewing_gear", "Japan", "none", 98000, 53000),
    ("P007", "GEAR-FRENCHPRESS", "French Press 600ml", "brewing_gear", "France", "none", 215000, 122000),
    ("P008", "GRINDER-MANUAL", "Manual Burr Grinder", "grinder", "China", "none", 485000, 292000),
    ("P009", "GRINDER-ELECTRIC", "Electric Grinder Pro", "grinder", "China", "none", 1890000, 1250000),
    ("P010", "MACHINE-ESPRESSO", "Home Espresso Machine", "machine", "Italy", "none", 4950000, 3550000),
    ("P011", "ACC-FILTER-100", "Paper Filter 100pcs", "accessory", "Japan", "none", 65000, 28000),
    ("P012", "ACC-SCALE", "Digital Coffee Scale", "accessory", "China", "none", 325000, 188000),
    ("P013", "BEAN-ETHIOPIA-200", "Ethiopia Yirgacheffe 200g", "beans", "Ethiopia", "light", 169000, 91000),
    ("P014", "BEAN-BRAZIL-250", "Brazil Cerrado 250g", "beans", "Brazil", "medium", 109000, 52000),
    ("P015", "GEAR-AEROPRESS", "AeroPress Brewer", "brewing_gear", "United States", "none", 695000, 430000),
]


def _date_range(start: date, end: date) -> list[date]:
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _pick_location(rng: random.Random) -> tuple[str, str]:
    province, cities = rng.choice(PROVINCES)
    return province, rng.choice(cities)


def _random_ts(rng: random.Random, day: date) -> datetime:
    return datetime.combine(day, datetime.min.time()) + timedelta(
        hours=rng.randint(8, 22),
        minutes=rng.randint(0, 59),
        seconds=rng.randint(0, 59),
    )


def _build_customers(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for idx in range(1, 551):
        created_day = START_DATE - timedelta(days=rng.randint(0, 220))
        created = datetime.combine(created_day, datetime.min.time()) + timedelta(hours=rng.randint(0, 23))
        province, city = _pick_location(rng)
        rows.append(
            {
                "customer_id": f"C{idx:05d}",
                "created_at": created.isoformat(sep=" "),
                "province": province,
                "city": city,
                "acquisition_channel": rng.choices(CHANNELS, weights=[25, 18, 22, 16, 13, 6], k=1)[0],
                "coffee_persona": rng.choice(PERSONAS),
            }
        )
    return rows


def _build_products() -> list[dict[str, object]]:
    return [
        {
            "product_id": product_id,
            "sku": sku,
            "product_name": name,
            "category": category,
            "origin_country": origin,
            "roast_level": roast,
            "list_price": price,
            "cogs": cogs,
        }
        for product_id, sku, name, category, origin, roast, price, cogs in PRODUCTS
    ]


def _build_orders(
    rng: random.Random,
    customers: list[dict[str, object]],
    products: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], dict[str, list[str]]]:
    orders: list[dict[str, object]] = []
    order_items: list[dict[str, object]] = []
    order_to_products: dict[str, list[str]] = {}
    customer_rows = customers[:]
    order_idx = 1
    item_idx = 1

    for day_number, day in enumerate(_date_range(START_DATE, END_DATE), start=1):
        weekday_boost = 1.25 if day.weekday() in (4, 5, 6) else 1.0
        trend = 1 + (day_number / 365)
        daily_orders = max(4, int(rng.gauss(13 * trend * weekday_boost, 4)))

        eligible_customers = [
            c for c in customer_rows if datetime.fromisoformat(str(c["created_at"])).date() <= day
        ]
        for _ in range(daily_orders):
            customer = rng.choice(eligible_customers)
            order_id = f"O{order_idx:06d}"
            order_idx += 1
            order_ts = _random_ts(rng, day)
            province = str(customer["province"])
            city = str(customer["city"])
            status = rng.choices(
                ["completed", "processing", "cancelled", "refunded"],
                weights=[86, 5, 6, 3],
                k=1,
            )[0]
            payment = rng.choices(PAYMENT_METHODS, weights=[35, 18, 37, 10], k=1)[0]
            line_count = rng.choices([1, 2, 3, 4], weights=[48, 32, 15, 5], k=1)[0]
            selected_products = rng.sample(products, k=line_count)
            gross = 0.0
            product_ids: list[str] = []

            for product in selected_products:
                quantity = rng.choices([1, 2, 3], weights=[75, 20, 5], k=1)[0]
                unit_price = int(product["list_price"])
                item_discount = 0
                if rng.random() < 0.18:
                    item_discount = int(round(unit_price * quantity * rng.uniform(0.03, 0.12), -2))
                gross += (unit_price * quantity) - item_discount
                product_ids.append(str(product["product_id"]))
                order_items.append(
                    {
                        "order_item_id": f"OI{item_idx:07d}",
                        "order_id": order_id,
                        "product_id": product["product_id"],
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "item_discount": item_discount,
                    }
                )
                item_idx += 1

            voucher_amount = int(round(gross * rng.choice([0, 0, 0, 0.03, 0.05, 0.08]), -2))
            shipping_fee = rng.choice([0, 12000, 18000, 25000, 35000])
            orders.append(
                {
                    "order_id": order_id,
                    "customer_id": customer["customer_id"],
                    "order_ts": order_ts.isoformat(sep=" "),
                    "status": status,
                    "payment_method": payment,
                    "province": province,
                    "city": city,
                    "voucher_amount": voucher_amount,
                    "shipping_fee": shipping_fee,
                }
            )
            order_to_products[order_id] = product_ids

    return orders, order_items, order_to_products


def _build_inventory(
    rng: random.Random,
    products: list[dict[str, object]],
    order_items: list[dict[str, object]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    item_sales: dict[str, int] = {}
    for item in order_items:
        item_sales[str(item["product_id"])] = item_sales.get(str(item["product_id"]), 0) + int(item["quantity"])

    snapshot_idx = 1
    for snapshot_day in _date_range(END_DATE - timedelta(days=89), END_DATE):
        for product in products:
            sold_velocity = max(1, item_sales.get(str(product["product_id"]), 0) // 180)
            baseline = rng.randint(40, 220) + sold_velocity * rng.randint(5, 16)
            reserved = rng.randint(0, max(2, baseline // 8))
            reorder_point = max(12, sold_velocity * rng.randint(7, 18))
            rows.append(
                {
                    "snapshot_id": f"IS{snapshot_idx:07d}",
                    "snapshot_date": snapshot_day.isoformat(),
                    "product_id": product["product_id"],
                    "stock_on_hand": baseline,
                    "stock_reserved": reserved,
                    "reorder_point": reorder_point,
                }
            )
            snapshot_idx += 1
    return rows


def _build_marketing_spend(rng: random.Random) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    spend_idx = 1
    for day in _date_range(START_DATE, END_DATE):
        for channel in PAID_CHANNELS:
            active = rng.random() < 0.88
            spend = 0 if not active else int(round(rng.uniform(350000, 3500000), -3))
            impressions = 0 if spend == 0 else int(spend / rng.uniform(180, 700))
            clicks = 0 if spend == 0 else int(impressions * rng.uniform(0.015, 0.07))
            rows.append(
                {
                    "spend_id": f"MS{spend_idx:07d}",
                    "spend_date": day.isoformat(),
                    "channel": channel,
                    "campaign": f"{channel}_coffee_{day.strftime('%Y%m')}",
                    "spend_amount": spend,
                    "impressions": impressions,
                    "clicks": clicks,
                }
            )
            spend_idx += 1
    return rows


def _build_web_events(
    rng: random.Random,
    customers: list[dict[str, object]],
    products: list[dict[str, object]],
    orders: list[dict[str, object]],
    order_to_products: dict[str, list[str]],
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    event_idx = 1

    def add_event(
        event_ts: datetime,
        customer_id: str,
        session_id: str,
        event_type: str,
        channel: str,
        product_id: str = "",
        order_id: str = "",
    ) -> None:
        nonlocal event_idx
        rows.append(
            {
                "event_id": f"WE{event_idx:08d}",
                "event_ts": event_ts.isoformat(sep=" "),
                "customer_id": customer_id,
                "session_id": session_id,
                "event_type": event_type,
                "channel": channel,
                "product_id": product_id,
                "order_id": order_id,
            }
        )
        event_idx += 1

    customer_by_id = {str(c["customer_id"]): c for c in customers}
    for order in orders:
        order_ts = datetime.fromisoformat(str(order["order_ts"]))
        customer = customer_by_id[str(order["customer_id"])]
        channel = str(customer["acquisition_channel"])
        session_id = f"S_{order['order_id']}"
        product_id = order_to_products[str(order["order_id"])][0]
        add_event(order_ts - timedelta(minutes=18), str(order["customer_id"]), session_id, "page_view", channel)
        add_event(order_ts - timedelta(minutes=14), str(order["customer_id"]), session_id, "product_view", channel, product_id)
        add_event(order_ts - timedelta(minutes=9), str(order["customer_id"]), session_id, "add_to_cart", channel, product_id)
        add_event(order_ts - timedelta(minutes=4), str(order["customer_id"]), session_id, "checkout_started", channel, product_id)
        if order["status"] == "completed":
            add_event(order_ts, str(order["customer_id"]), session_id, "purchase", channel, product_id, str(order["order_id"]))

    for day in _date_range(START_DATE, END_DATE):
        for session_number in range(rng.randint(24, 58)):
            session_id = f"S_BROWSE_{day.strftime('%Y%m%d')}_{session_number:04d}"
            channel = rng.choices(CHANNELS, weights=[30, 18, 22, 16, 9, 5], k=1)[0]
            customer = rng.choice(customers) if rng.random() < 0.45 else None
            customer_id = "" if customer is None else str(customer["customer_id"])
            product = rng.choice(products)
            ts = _random_ts(rng, day)
            add_event(ts, customer_id, session_id, "page_view", channel)
            if rng.random() < 0.72:
                add_event(ts + timedelta(minutes=1), customer_id, session_id, "product_view", channel, str(product["product_id"]))
            if rng.random() < 0.20:
                add_event(ts + timedelta(minutes=3), customer_id, session_id, "add_to_cart", channel, str(product["product_id"]))
            if rng.random() < 0.06:
                add_event(ts + timedelta(minutes=5), customer_id, session_id, "checkout_started", channel, str(product["product_id"]))

    return rows


def generate_dataset(output_dir: Path = DATA_DIR) -> Path:
    rng = random.Random(RANDOM_SEED)
    products = _build_products()
    customers = _build_customers(rng)
    orders, order_items, order_to_products = _build_orders(rng, customers, products)
    inventory = _build_inventory(rng, products, order_items)
    marketing = _build_marketing_spend(rng)
    web_events = _build_web_events(rng, customers, products, orders, order_to_products)

    output_dir.mkdir(parents=True, exist_ok=True)
    _write_csv(output_dir / "customers.csv", list(customers[0].keys()), customers)
    _write_csv(output_dir / "products.csv", list(products[0].keys()), products)
    _write_csv(output_dir / "orders.csv", list(orders[0].keys()), orders)
    _write_csv(output_dir / "order_items.csv", list(order_items[0].keys()), order_items)
    _write_csv(output_dir / "inventory_snapshots.csv", list(inventory[0].keys()), inventory)
    _write_csv(output_dir / "marketing_spend.csv", list(marketing[0].keys()), marketing)
    _write_csv(output_dir / "web_events.csv", list(web_events[0].keys()), web_events)
    print(f"Generated synthetic coffee-commerce data in {output_dir}")
    return output_dir


if __name__ == "__main__":
    generate_dataset()
