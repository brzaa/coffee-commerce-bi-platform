select
    snapshot_id,
    snapshot_date::date as snapshot_date,
    product_id,
    stock_on_hand::integer as stock_on_hand,
    stock_reserved::integer as stock_reserved,
    reorder_point::integer as reorder_point
from {{ source('raw', 'inventory_snapshots') }}
