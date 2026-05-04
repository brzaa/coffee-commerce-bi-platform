with spend as (
    select
        spend_date,
        channel,
        sum(spend_amount) as spend_amount,
        sum(impressions) as impressions,
        sum(clicks) as clicks
    from {{ ref('stg_marketing_spend') }}
    group by 1, 2
),
orders as (
    select
        order_date,
        acquisition_channel as channel,
        count(*) filter (where status = 'completed') as completed_orders,
        sum(net_revenue) filter (where status = 'completed') as net_revenue,
        sum(gross_margin) filter (where status = 'completed') as gross_margin
    from {{ ref('fct_orders') }}
    group by 1, 2
)

select
    s.spend_date,
    s.channel,
    s.spend_amount::numeric(14, 2) as spend_amount,
    s.impressions,
    s.clicks,
    coalesce(o.completed_orders, 0) as completed_orders,
    coalesce(o.net_revenue, 0)::numeric(14, 2) as net_revenue,
    coalesce(o.gross_margin, 0)::numeric(14, 2) as gross_margin,
    case when s.clicks > 0 then (s.spend_amount / s.clicks)::numeric(14, 2) else 0 end as cost_per_click,
    case when s.spend_amount > 0 then (coalesce(o.net_revenue, 0) / s.spend_amount)::numeric(10, 2) else 0 end as return_on_ad_spend,
    case when coalesce(o.completed_orders, 0) > 0 then (s.spend_amount / o.completed_orders)::numeric(14, 2) else 0 end as customer_acquisition_cost
from spend s
left join orders o
    on s.spend_date = o.order_date
   and s.channel = o.channel
