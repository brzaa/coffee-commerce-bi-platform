select *
from {{ ref('fct_orders') }}
where gross_revenue < 0
   or item_discount_amount < 0
   or voucher_amount < 0
   or total_discount_amount < 0
   or net_revenue < 0
   or total_items <= 0
   or total_discount_amount > gross_revenue
   or net_revenue > gross_revenue
