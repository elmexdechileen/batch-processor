-- init-schema.sql
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.comics (
    month VARCHAR(2),
    num INT,
    link TEXT,
    year VARCHAR(4),
    news TEXT,
    safe_title TEXT,
    transcript TEXT,
    alt TEXT,
    img TEXT,
    title TEXT,
    day VARCHAR(2)
);
