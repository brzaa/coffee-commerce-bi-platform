select
    order_id,
    customer_id,
    order_ts,
    order_date,
    order_month,
    net_revenue,
    row_number() over (
        partition by customer_id
        order by order_ts, order_id
    ) as completed_order_number,
    min(order_date) over (partition by customer_id) as first_order_date,
    min(order_month) over (partition by customer_id) as cohort_month
from {{ ref('int_orders_enriched') }}
where status = 'completed'
