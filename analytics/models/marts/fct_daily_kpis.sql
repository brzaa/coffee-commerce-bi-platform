with order_daily as (
    select
        order_date as metric_date,
        count(*) filter (where status = 'completed') as completed_orders,
        count(distinct customer_id) filter (where status = 'completed') as purchasing_customers,
        sum(gross_revenue) filter (where status = 'completed') as gmv,
        sum(net_revenue) filter (where status = 'completed') as net_revenue,
        sum(gross_margin) filter (where status = 'completed') as gross_margin,
        sum(total_items) filter (where status = 'completed') as units_sold,
        count(*) filter (where status in ('cancelled', 'refunded')) as failed_orders
    from {{ ref('fct_orders') }}
    group by 1
),
web_daily as (
    select
        event_date as metric_date,
        count(distinct session_id) as sessions,
        count(distinct session_id) filter (where event_type = 'product_view') as product_view_sessions,
        count(distinct session_id) filter (where event_type = 'add_to_cart') as add_to_cart_sessions,
        count(distinct session_id) filter (where event_type = 'purchase') as purchase_sessions
    from {{ ref('stg_web_events') }}
    group by 1
)

select
    coalesce(o.metric_date, w.metric_date) as metric_date,
    coalesce(o.completed_orders, 0) as completed_orders,
    coalesce(o.purchasing_customers, 0) as purchasing_customers,
    coalesce(o.gmv, 0)::numeric(14, 2) as gmv,
    coalesce(o.net_revenue, 0)::numeric(14, 2) as net_revenue,
    coalesce(o.gross_margin, 0)::numeric(14, 2) as gross_margin,
    coalesce(o.units_sold, 0) as units_sold,
    coalesce(o.failed_orders, 0) as failed_orders,
    coalesce(w.sessions, 0) as sessions,
    coalesce(w.product_view_sessions, 0) as product_view_sessions,
    coalesce(w.add_to_cart_sessions, 0) as add_to_cart_sessions,
    coalesce(w.purchase_sessions, 0) as purchase_sessions,
    case when coalesce(o.completed_orders, 0) > 0 then (coalesce(o.net_revenue, 0) / o.completed_orders)::numeric(14, 2) else 0 end as average_order_value,
    case when coalesce(w.sessions, 0) > 0 then (coalesce(o.completed_orders, 0)::numeric / w.sessions)::numeric(10, 4) else 0 end as session_conversion_rate,
    case when coalesce(o.net_revenue, 0) > 0 then (coalesce(o.gross_margin, 0) / o.net_revenue)::numeric(10, 4) else 0 end as gross_margin_rate
from order_daily o
full outer join web_daily w using (metric_date)
