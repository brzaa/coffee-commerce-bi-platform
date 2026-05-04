with line_items as (
    select
        order_id,
        sum(quantity) as total_items,
        sum(gross_item_amount) as gross_revenue,
        sum(item_discount) as item_discount_amount,
        sum(net_item_amount) as line_net_revenue,
        sum(item_cogs) as total_cogs,
        sum(item_margin) as line_margin
    from {{ ref('int_order_line_items') }}
    group by 1
)

select
    o.order_id,
    o.customer_id,
    o.order_ts,
    o.order_date,
    date_trunc('month', o.order_date)::date as order_month,
    o.status,
    o.payment_method,
    o.province,
    o.city,
    li.total_items,
    li.gross_revenue::numeric(14, 2) as gross_revenue,
    li.item_discount_amount::numeric(14, 2) as item_discount_amount,
    o.voucher_amount,
    (li.item_discount_amount + o.voucher_amount)::numeric(14, 2) as total_discount_amount,
    greatest(li.line_net_revenue - o.voucher_amount, 0)::numeric(14, 2) as net_revenue,
    o.shipping_fee,
    li.total_cogs::numeric(14, 2) as total_cogs,
    (greatest(li.line_net_revenue - o.voucher_amount, 0) - li.total_cogs)::numeric(14, 2) as gross_margin,
    case when o.status = 'completed' then 1 else 0 end as is_completed_order
from {{ ref('stg_orders') }} o
join line_items li using (order_id)
