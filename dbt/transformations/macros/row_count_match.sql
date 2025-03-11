{% macro test_row_count_match(model, source_model, threshold) %}

WITH counts AS (
    SELECT 
        (SELECT COUNT(*) FROM {{ source_model }}) AS source_count,
        (SELECT COUNT(*) FROM {{ model }}) AS dim_count
)
SELECT 
    *
FROM counts
WHERE abs(source_count - dim_count) > {{ threshold }}

{% endmacro %}
