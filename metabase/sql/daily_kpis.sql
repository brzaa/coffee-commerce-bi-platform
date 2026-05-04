select
    metric_date,
    net_revenue,
    completed_orders,
    average_order_value,
    session_conversion_rate,
    gross_margin_rate
from marts.fct_daily_kpis
order by metric_date;
