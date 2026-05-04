select
    order_id,
    customer_id,
    order_ts::timestamp as order_ts,
    order_ts::date as order_date,
    lower(status) as status,
    lower(payment_method) as payment_method,
    lower(province) as province,
    city,
    voucher_amount::numeric(14, 2) as voucher_amount,
    shipping_fee::numeric(14, 2) as shipping_fee
from {{ source('raw', 'orders') }}
