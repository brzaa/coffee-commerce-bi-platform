select
    cohort_month,
    months_since_first_purchase,
    active_customers,
    completed_orders,
    net_revenue
from marts.mart_customer_cohorts
order by cohort_month, months_since_first_purchase;
