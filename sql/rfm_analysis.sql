-- =============================================================
--  Customer Segmentation — RFM Analysis SQL Queries
--  Dataset : Online Retail II (UCI)
--  Author  : Rihab Douhab
--  Engine  : Compatible with PostgreSQL / MySQL / SQLite
-- =============================================================


-- =============================================================
--  SECTION 0 — SCHEMA SETUP
-- =============================================================

CREATE TABLE IF NOT EXISTS online_retail (
    invoice      VARCHAR(20),
    stock_code   VARCHAR(20),
    description  TEXT,
    quantity     INTEGER,
    invoice_date TIMESTAMP,
    price        NUMERIC(10, 2),
    customer_id  INTEGER,
    country      VARCHAR(60)
);

-- After loading rfm_clustered.csv:
CREATE TABLE IF NOT EXISTS rfm_segments (
    customer_id  INTEGER PRIMARY KEY,
    recency      INTEGER,        -- days since last purchase
    frequency    INTEGER,        -- number of distinct invoices
    monetary     NUMERIC(12, 2), -- total spend (£)
    cluster      INTEGER,        -- K-Means cluster id (0-3)
    segment      VARCHAR(40)     -- human-readable label
);


-- =============================================================
--  SECTION 1 — DATA EXPLORATION
-- =============================================================

-- 1.1  Row count & date range
SELECT
    COUNT(*)                        AS total_rows,
    COUNT(DISTINCT customer_id)     AS unique_customers,
    COUNT(DISTINCT invoice)         AS unique_invoices,
    MIN(invoice_date)               AS earliest_date,
    MAX(invoice_date)               AS latest_date
FROM online_retail;


-- 1.2  Missing-value audit
SELECT
    COUNT(*)                                            AS total_rows,
    SUM(CASE WHEN customer_id  IS NULL THEN 1 ELSE 0 END) AS missing_customer_id,
    SUM(CASE WHEN description  IS NULL THEN 1 ELSE 0 END) AS missing_description,
    SUM(CASE WHEN quantity     <= 0    THEN 1 ELSE 0 END) AS non_positive_quantity,
    SUM(CASE WHEN price        <= 0    THEN 1 ELSE 0 END) AS non_positive_price,
    SUM(CASE WHEN invoice LIKE 'C%'   THEN 1 ELSE 0 END) AS cancelled_orders
FROM online_retail;


-- 1.3  Top 10 countries by revenue
SELECT
    country,
    COUNT(DISTINCT customer_id) AS customers,
    ROUND(SUM(quantity * price), 2) AS total_revenue
FROM online_retail
WHERE customer_id IS NOT NULL
  AND quantity > 0
  AND price > 0
  AND invoice NOT LIKE 'C%'
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;


-- 1.4  Top 10 best-selling products
SELECT
    stock_code,
    MAX(description) AS description,
    SUM(quantity)    AS units_sold,
    ROUND(SUM(quantity * price), 2) AS revenue
FROM online_retail
WHERE quantity > 0
  AND price > 0
  AND invoice NOT LIKE 'C%'
GROUP BY stock_code
ORDER BY units_sold DESC
LIMIT 10;


-- 1.5  Monthly revenue trend
SELECT
    DATE_TRUNC('month', invoice_date) AS month,      -- PostgreSQL
    -- DATE_FORMAT(invoice_date, '%Y-%m') AS month,  -- MySQL
    ROUND(SUM(quantity * price), 2)   AS revenue,
    COUNT(DISTINCT customer_id)       AS active_customers,
    COUNT(DISTINCT invoice)           AS total_invoices
FROM online_retail
WHERE customer_id IS NOT NULL
  AND quantity > 0
  AND price > 0
  AND invoice NOT LIKE 'C%'
GROUP BY 1
ORDER BY 1;


-- =============================================================
--  SECTION 2 — DATA CLEANING (VIEW)
-- =============================================================

-- 2.1  Clean view — removes nulls, cancelled orders, bad values
CREATE OR REPLACE VIEW v_clean_retail AS
SELECT
    invoice,
    stock_code,
    description,
    quantity,
    invoice_date,
    price,
    customer_id,
    country,
    (quantity * price) AS line_revenue
FROM online_retail
WHERE customer_id IS NOT NULL
  AND quantity     > 0
  AND price        > 0
  AND invoice NOT LIKE 'C%';


-- =============================================================
--  SECTION 3 — RFM CALCULATION
-- =============================================================

-- 3.1  Snapshot date (1 day after the last transaction)
-- Used as the reference point for Recency
-- SELECT MAX(invoice_date) + INTERVAL '1 day' FROM v_clean_retail;

-- 3.2  Compute raw RFM metrics per customer
WITH snapshot AS (
    SELECT MAX(invoice_date) + INTERVAL '1 day' AS snap_date
    FROM v_clean_retail
),
rfm_raw AS (
    SELECT
        r.customer_id,
        CAST(
            EXTRACT(EPOCH FROM (s.snap_date - MAX(r.invoice_date))) / 86400
        AS INTEGER)                         AS recency,     -- days
        COUNT(DISTINCT r.invoice)           AS frequency,
        ROUND(SUM(r.line_revenue), 2)       AS monetary
    FROM v_clean_retail r
    CROSS JOIN snapshot s
    GROUP BY r.customer_id
)
SELECT *
FROM rfm_raw
ORDER BY monetary DESC
LIMIT 20;


-- =============================================================
--  SECTION 4 — SEGMENT ANALYSIS
-- =============================================================

-- 4.1  Customer count & share per segment
SELECT
    segment,
    COUNT(*)                                          AS customers,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_base
FROM rfm_segments
GROUP BY segment
ORDER BY customers DESC;


-- 4.2  Average RFM metrics per segment
SELECT
    segment,
    ROUND(AVG(recency),   1) AS avg_recency_days,
    ROUND(AVG(frequency), 1) AS avg_frequency,
    ROUND(AVG(monetary),  2) AS avg_monetary_gbp,
    ROUND(SUM(monetary),  2) AS total_revenue_gbp
FROM rfm_segments
GROUP BY segment
ORDER BY avg_monetary_gbp DESC;


-- 4.3  Revenue contribution per segment (with % share)
SELECT
    segment,
    ROUND(SUM(monetary), 2)                                          AS segment_revenue,
    ROUND(SUM(monetary) * 100.0 / SUM(SUM(monetary)) OVER (), 1)    AS revenue_pct,
    COUNT(*)                                                         AS customers,
    ROUND(AVG(monetary), 2)                                          AS avg_customer_value
FROM rfm_segments
GROUP BY segment
ORDER BY segment_revenue DESC;


-- 4.4  Full descriptive stats per segment (min / median / max)
SELECT
    segment,
    MIN(recency)                       AS min_recency,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY recency) AS median_recency,   -- PostgreSQL
    MAX(recency)                       AS max_recency,
    MIN(monetary)                      AS min_spend,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY monetary) AS median_spend,
    MAX(monetary)                      AS max_spend,
    MIN(frequency)                     AS min_freq,
    MAX(frequency)                     AS max_freq
FROM rfm_segments
GROUP BY segment
ORDER BY median_spend DESC;


-- =============================================================
--  SECTION 5 — BUSINESS INSIGHTS
-- =============================================================

-- 5.1  Champions — top 20 VIP customers by spend
SELECT
    customer_id,
    recency   AS days_since_last_purchase,
    frequency AS total_orders,
    monetary  AS total_spend_gbp
FROM rfm_segments
WHERE segment = '🏆 Champions'
ORDER BY monetary DESC
LIMIT 20;


-- 5.2  At-Risk customers who were once high-value (monetary > £1,000)
SELECT
    customer_id,
    recency   AS days_inactive,
    frequency AS past_orders,
    monetary  AS lifetime_spend_gbp
FROM rfm_segments
WHERE segment  = '⚠️  At Risk'
  AND monetary > 1000
ORDER BY monetary DESC;


-- 5.3  Lost customers — potential win-back list
--      Sorted by highest past spend (biggest recovery opportunity)
SELECT
    customer_id,
    recency   AS days_since_last_purchase,
    frequency AS total_past_orders,
    monetary  AS total_past_spend_gbp
FROM rfm_segments
WHERE segment = '💤 Lost / Inactive'
ORDER BY monetary DESC
LIMIT 50;


-- 5.4  Loyal customers eligible for upsell
--      (medium-high spend, moderately frequent buyers)
SELECT
    customer_id,
    frequency AS orders,
    monetary  AS spend_gbp,
    recency   AS days_since_last_purchase
FROM rfm_segments
WHERE segment  = '💛 Loyal Customers'
  AND frequency >= 3
  AND monetary  >= 500
ORDER BY monetary DESC;


-- 5.5  Cumulative revenue (top 20% of customers → Pareto check)
WITH ranked AS (
    SELECT
        customer_id,
        monetary,
        NTILE(5) OVER (ORDER BY monetary DESC) AS quintile
    FROM rfm_segments
)
SELECT
    quintile,
    COUNT(*)                           AS customers,
    ROUND(SUM(monetary), 2)            AS total_revenue,
    ROUND(SUM(monetary) * 100.0
          / SUM(SUM(monetary)) OVER(), 1) AS revenue_pct
FROM ranked
GROUP BY quintile
ORDER BY quintile;


-- 5.6  Segment migration helper view
--      (placeholder — ready to use when you add a date column)
--      Run this query after adding a snapshot_date column to rfm_segments
-- SELECT
--     a.customer_id,
--     a.segment AS segment_period_1,
--     b.segment AS segment_period_2
-- FROM rfm_segments a
-- JOIN rfm_segments_prev b ON a.customer_id = b.customer_id
-- WHERE a.segment <> b.segment;


-- =============================================================
--  SECTION 6 — KPI SUMMARY DASHBOARD QUERY
-- =============================================================

-- Single query that returns all headline KPIs
SELECT
    COUNT(*)                                 AS total_customers,
    ROUND(AVG(recency),   1)                 AS avg_recency_days,
    ROUND(AVG(frequency), 1)                 AS avg_frequency,
    ROUND(AVG(monetary),  2)                 AS avg_monetary_gbp,
    ROUND(SUM(monetary),  2)                 AS total_revenue_gbp,
    -- Segment breakdown
    SUM(CASE WHEN segment = '🏆 Champions'       THEN 1 ELSE 0 END) AS champions,
    SUM(CASE WHEN segment = '💛 Loyal Customers' THEN 1 ELSE 0 END) AS loyal,
    SUM(CASE WHEN segment LIKE '%At Risk%'       THEN 1 ELSE 0 END) AS at_risk,
    SUM(CASE WHEN segment LIKE '%Lost%'          THEN 1 ELSE 0 END) AS lost,
    -- Revenue at risk (At Risk + Lost segments)
    ROUND(SUM(CASE WHEN segment LIKE '%At Risk%' OR segment LIKE '%Lost%'
                   THEN monetary ELSE 0 END), 2) AS revenue_at_risk_gbp
FROM rfm_segments;
