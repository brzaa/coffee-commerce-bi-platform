select
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    o.order_ts,
    o.order_date,
    o.status,
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    p.origin_country,
    p.roast_level,
    oi.quantity,
    oi.unit_price,
    oi.item_discount,
    p.cogs,
    (oi.quantity * oi.unit_price)::numeric(14, 2) as gross_item_amount,
    greatest((oi.quantity * oi.unit_price) - oi.item_discount, 0)::numeric(14, 2) as net_item_amount,
    (oi.quantity * p.cogs)::numeric(14, 2) as item_cogs,
    (greatest((oi.quantity * oi.unit_price) - oi.item_discount, 0) - (oi.quantity * p.cogs))::numeric(14, 2) as item_margin
from {{ ref('stg_order_items') }} oi
join {{ ref('stg_orders') }} o using (order_id)
join {{ ref('stg_products') }} p using (product_id)
