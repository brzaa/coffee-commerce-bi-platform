select
    product_name,
    category,
    available_stock,
    reorder_point,
    units_sold_30d,
    estimated_days_of_cover,
    inventory_risk_status
from marts.mart_inventory_risk
order by
    case inventory_risk_status
        when 'reorder_now' then 1
        when 'watchlist' then 2
        else 3
    end,
    estimated_days_of_cover nulls last;
