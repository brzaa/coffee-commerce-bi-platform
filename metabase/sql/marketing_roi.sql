select
    spend_date,
    channel,
    spend_amount,
    clicks,
    completed_orders,
    net_revenue,
    return_on_ad_spend,
    customer_acquisition_cost
from marts.mart_marketing_roi
order by spend_date, channel;
