select
    spend_id,
    spend_date::date as spend_date,
    lower(channel) as channel,
    campaign,
    spend_amount::numeric(14, 2) as spend_amount,
    impressions::integer as impressions,
    clicks::integer as clicks
from {{ source('raw', 'marketing_spend') }}
