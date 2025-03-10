{{ config(materialized='table') }}

with source_data as (

    select
        month::varchar,
        num::int4,
        link::text,
        year::varchar,
        news::text,
        safe_title::text,
        transcript::text,
        alt::text,
        img::text,
        title::text,
        day::varchar
    from
        {{ source('staging', 'comics') }}

)

select *
from source_data
