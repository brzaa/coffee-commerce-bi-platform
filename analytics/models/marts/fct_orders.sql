select
    o.order_id,
    o.customer_id,
    c.acquisition_channel,
    o.order_ts,
    o.order_date,
    o.order_month,
    o.status,
    o.payment_method,
    o.province,
    o.city,
    o.total_items,
    o.gross_revenue,
    o.item_discount_amount,
    o.voucher_amount,
    o.total_discount_amount,
    o.net_revenue,
    o.shipping_fee,
    o.total_cogs,
    o.gross_margin,
    case
        when o.net_revenue > 0 then (o.gross_margin / o.net_revenue)::numeric(10, 4)
        else 0
    end as gross_margin_rate,
    o.is_completed_order
from {{ ref('int_orders_enriched') }} o
join {{ ref('stg_customers') }} c using (customer_id)
