select *
from {{ ref('mart_inventory_risk') }}
where stock_on_hand < 0
   or stock_reserved < 0
   or available_stock < 0
   or reorder_point < 0
   or units_sold_30d < 0
   or avg_daily_units_30d < 0
   or estimated_days_of_cover < 0
