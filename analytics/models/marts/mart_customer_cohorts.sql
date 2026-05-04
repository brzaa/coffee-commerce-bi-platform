select
    cohort_month,
    order_month,
    (
        extract(year from age(order_month, cohort_month)) * 12
        + extract(month from age(order_month, cohort_month))
    )::integer as months_since_first_purchase,
    count(distinct customer_id) as active_customers,
    count(order_id) as completed_orders,
    sum(net_revenue)::numeric(14, 2) as net_revenue
from {{ ref('int_customer_order_sequence') }}
group by 1, 2, 3
