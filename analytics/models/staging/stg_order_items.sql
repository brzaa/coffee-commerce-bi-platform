select
    order_item_id,
    order_id,
    product_id,
    quantity::integer as quantity,
    unit_price::numeric(14, 2) as unit_price,
    item_discount::numeric(14, 2) as item_discount
from {{ source('raw', 'order_items') }}
