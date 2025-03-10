WITH comic_details AS (
    SELECT
        num,
        date,
        link,
        alt,
        img,
        title
    FROM {{ ref('dim_comics') }}
),

comic_cost AS (
    SELECT
        num,
        cost
    FROM {{ ref('fact_cost') }}
),

comic_reviews AS (
    SELECT
        num,
        review
    FROM {{ ref('fact_review') }}
),

comic_views AS (
    SELECT
        num,
        views
    FROM {{ ref('fact_views') }}
)

SELECT
    cd.num as comic_number,
    cd.title as comic_title,
    cd.date as comic_date,
    cd.link as comic_link,
    cd.alt as alttext,
    cs.cost as comic_cost,
    cr.review as comic_review_score,
    cv.views as comic_views
FROM comic_details cd
LEFT JOIN comic_cost cs ON cd.num = cs.num
LEFT JOIN comic_reviews cr ON cd.num = cr.num
LEFT JOIN comic_views cv ON cd.num = cv.num