with sales as (
    select
        product_id,
        sku,
        product_name,
        category,
        origin_country,
        roast_level,
        count(distinct order_id) filter (where status = 'completed') as completed_orders,
        sum(quantity) filter (where status = 'completed') as units_sold,
        sum(gross_item_amount) filter (where status = 'completed')::numeric(14, 2) as gross_revenue,
        sum(net_item_amount) filter (where status = 'completed')::numeric(14, 2) as net_revenue,
        sum(item_margin) filter (where status = 'completed')::numeric(14, 2) as gross_margin
    from {{ ref('int_order_line_items') }}
    group by 1, 2, 3, 4, 5, 6
),
views as (
    select
        product_id,
        count(distinct session_id) filter (where event_type = 'product_view') as product_view_sessions
    from {{ ref('stg_web_events') }}
    where product_id is not null
    group by 1
)

select
    s.product_id,
    s.sku,
    s.product_name,
    s.category,
    s.origin_country,
    s.roast_level,
    coalesce(s.completed_orders, 0) as completed_orders,
    coalesce(s.units_sold, 0) as units_sold,
    coalesce(s.gross_revenue, 0)::numeric(14, 2) as gross_revenue,
    coalesce(s.net_revenue, 0)::numeric(14, 2) as net_revenue,
    coalesce(s.gross_margin, 0)::numeric(14, 2) as gross_margin,
    coalesce(v.product_view_sessions, 0) as product_view_sessions,
    case
        when coalesce(v.product_view_sessions, 0) > 0
        then (coalesce(s.completed_orders, 0)::numeric / v.product_view_sessions)::numeric(10, 4)
        else 0
    end as product_view_to_order_rate
from sales s
left join views v using (product_id)
