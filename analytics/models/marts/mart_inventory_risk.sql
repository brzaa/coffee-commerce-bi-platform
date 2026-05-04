with latest_inventory as (
    select *
    from (
        select
            inv.*,
            row_number() over (partition by product_id order by snapshot_date desc) as rn
        from {{ ref('stg_inventory_snapshots') }} inv
    ) ranked
    where rn = 1
),
sales_30d as (
    select
        product_id,
        sum(quantity) as units_sold_30d
    from {{ ref('int_order_line_items') }}
    where status = 'completed'
      and order_date >= (select max(order_date) from {{ ref('int_order_line_items') }}) - interval '30 day'
    group by 1
)

select
    p.product_id,
    p.sku,
    p.product_name,
    p.category,
    inv.snapshot_date,
    inv.stock_on_hand,
    inv.stock_reserved,
    greatest(inv.stock_on_hand - inv.stock_reserved, 0) as available_stock,
    inv.reorder_point,
    coalesce(s.units_sold_30d, 0) as units_sold_30d,
    (coalesce(s.units_sold_30d, 0)::numeric / 30)::numeric(10, 2) as avg_daily_units_30d,
    case
        when coalesce(s.units_sold_30d, 0) > 0
        then (greatest(inv.stock_on_hand - inv.stock_reserved, 0)::numeric / (coalesce(s.units_sold_30d, 0)::numeric / 30))::numeric(10, 2)
        else null
    end as estimated_days_of_cover,
    case
        when greatest(inv.stock_on_hand - inv.stock_reserved, 0) <= inv.reorder_point then 'reorder_now'
        when coalesce(s.units_sold_30d, 0) > 0
             and (greatest(inv.stock_on_hand - inv.stock_reserved, 0)::numeric / (coalesce(s.units_sold_30d, 0)::numeric / 30)) < 14 then 'watchlist'
        else 'healthy'
    end as inventory_risk_status
from latest_inventory inv
join {{ ref('stg_products') }} p using (product_id)
left join sales_30d s using (product_id)
