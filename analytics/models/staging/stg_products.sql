select
    product_id,
    sku,
    product_name,
    lower(category) as category,
    origin_country,
    roast_level,
    list_price::numeric(14, 2) as list_price,
    cogs::numeric(14, 2) as cogs
from {{ source('raw', 'products') }}
