with completed_orders as (
    select
        customer_id,
        count(*) as completed_orders,
        sum(net_revenue) as lifetime_revenue,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date
    from {{ ref('fct_orders') }}
    where status = 'completed'
    group by 1
)

select
    c.customer_id,
    c.created_at,
    c.created_date,
    c.province,
    c.city,
    c.acquisition_channel,
    c.coffee_persona,
    coalesce(o.completed_orders, 0) as completed_orders,
    coalesce(o.lifetime_revenue, 0)::numeric(14, 2) as lifetime_revenue,
    o.first_order_date,
    o.last_order_date,
    case
        when coalesce(o.completed_orders, 0) >= 5 then 'loyalist'
        when coalesce(o.completed_orders, 0) >= 2 then 'repeat'
        when coalesce(o.completed_orders, 0) = 1 then 'new_buyer'
        else 'prospect'
    end as customer_segment
from {{ ref('stg_customers') }} c
left join completed_orders o using (customer_id)
