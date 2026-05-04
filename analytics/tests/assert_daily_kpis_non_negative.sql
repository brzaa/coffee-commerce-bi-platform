select *
from {{ ref('fct_daily_kpis') }}
where completed_orders < 0
   or purchasing_customers < 0
   or gmv < 0
   or net_revenue < 0
   or gross_margin < -1000000000
   or units_sold < 0
   or sessions < 0
   or average_order_value < 0
   or session_conversion_rate < 0
