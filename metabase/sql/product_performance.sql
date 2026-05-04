select
    product_name,
    category,
    units_sold,
    net_revenue,
    gross_margin,
    product_view_sessions,
    product_view_to_order_rate
from marts.mart_product_performance
order by net_revenue desc
limit 15;
