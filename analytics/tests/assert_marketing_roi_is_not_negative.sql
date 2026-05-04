select *
from {{ ref('mart_marketing_roi') }}
where spend_amount < 0
   or impressions < 0
   or clicks < 0
   or completed_orders < 0
   or net_revenue < 0
   or cost_per_click < 0
   or return_on_ad_spend < 0
   or customer_acquisition_cost < 0
