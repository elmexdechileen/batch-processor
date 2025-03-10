{{ config(materialized='table') }}

with source_data as (
    select
        num::int4
    from
        {{ source('staging', 'comics') }}
)

select
    num,
    round((random() * 9.0 + 1.0)::numeric, 2) as review
from
    source_data