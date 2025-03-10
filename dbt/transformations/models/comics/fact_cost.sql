{{ config(
    materialized='table',
    unique_key='num'
) }}

with source_data as (
    select
        num::int4,
        title
    from
        {{ source('staging', 'comics') }}
)

select
    num,
    length(regexp_replace(title, '[^a-zA-Z0-9]', '', 'g')) * 5 as cost
from
    source_data
