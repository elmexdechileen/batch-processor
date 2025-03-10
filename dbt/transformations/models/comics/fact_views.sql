{{ config(
    materialized='table',
    unique_key='num'
) }}


with source_data as (
    select
        num::int4
    from
        {{ source('staging', 'comics') }}
)

select
    num,
    round(random() * 10000) as views
from
    source_data