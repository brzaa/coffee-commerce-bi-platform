select
    customer_id,
    created_at::timestamp as created_at,
    created_at::date as created_date,
    lower(province) as province,
    city,
    lower(acquisition_channel) as acquisition_channel,
    coffee_persona
from {{ source('raw', 'customers') }}
