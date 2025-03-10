{{ config(
    materialized='table',
    unique_key='num'
) }}

with source_data as (

    select
        num::int4,
        make_date(year::int, month::int, day::int) as date,
        link::text,
        alt::text,
        img::text,
        title::text
    from
        {{ source('staging', 'comics') }}

)

select *
from source_data
