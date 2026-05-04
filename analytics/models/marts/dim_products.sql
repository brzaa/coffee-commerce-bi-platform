select
    product_id,
    sku,
    product_name,
    category,
    origin_country,
    roast_level,
    list_price,
    cogs,
    (list_price - cogs)::numeric(14, 2) as unit_margin,
    case
        when list_price > 0 then ((list_price - cogs) / list_price)::numeric(10, 4)
        else 0
    end as unit_margin_rate
from {{ ref('stg_products') }}
