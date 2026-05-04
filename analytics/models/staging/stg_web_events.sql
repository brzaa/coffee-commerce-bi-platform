select
    event_id,
    event_ts::timestamp as event_ts,
    event_ts::date as event_date,
    nullif(customer_id, '') as customer_id,
    session_id,
    lower(event_type) as event_type,
    lower(channel) as channel,
    nullif(product_id, '') as product_id,
    nullif(order_id, '') as order_id
from {{ source('raw', 'web_events') }}
