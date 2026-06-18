-- ================================================================
--  E-Commerce BI & Sales Prediction Platform
--  Script: 03_business_analysis_queries.sql
--  Purpose: 25 business intelligence queries for analytics
--  Database: ecommerce_bi  (MySQL 8.0+)
-- ================================================================

USE ecommerce_bi;

-- ────────────────────────────────────────────────────────────────
--  SECTION A — OVERALL KPIs
-- ────────────────────────────────────────────────────────────────

-- ── Q01: Total Revenue, Orders, Quantity, AOV ────────────────────
-- Business Question: What are the headline KPIs for the business?
SELECT
    COUNT(DISTINCT order_id)                AS total_orders,
    SUM(qty)                                AS total_quantity_sold,
    ROUND(SUM(amount), 2)                   AS total_revenue_inr,
    ROUND(AVG(amount), 2)                   AS avg_order_value,
    ROUND(SUM(amount) / COUNT(DISTINCT order_id), 2) AS revenue_per_order
FROM fact_orders;


-- ── Q02: Delivered vs All Orders — Fulfilment Rate ───────────────
-- Business Question: What percentage of orders were successfully delivered?
SELECT
    status,
    COUNT(*)                                             AS orders,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2)  AS pct_of_total,
    ROUND(SUM(amount), 2)                                AS revenue
FROM fact_orders
GROUP BY status
ORDER BY orders DESC;


-- ── Q03: B2B vs B2C Revenue Split ────────────────────────────────
-- Business Question: How significant is the B2B segment?
SELECT
    b2b                                              AS customer_type,
    COUNT(DISTINCT order_id)                         AS orders,
    SUM(qty)                                         AS qty_sold,
    ROUND(SUM(amount), 2)                            AS total_revenue,
    ROUND(AVG(amount), 2)                            AS avg_order_value,
    ROUND(SUM(amount) * 100 / SUM(SUM(amount)) OVER(), 2) AS revenue_pct
FROM fact_orders
GROUP BY b2b;


-- ────────────────────────────────────────────────────────────────
--  SECTION B — TIME-BASED ANALYSIS
-- ────────────────────────────────────────────────────────────────

-- ── Q04: Monthly Revenue Trend ───────────────────────────────────
-- Business Question: How is revenue trending month over month?
SELECT
    k.year,
    k.month_number,
    k.month_name,
    k.total_orders,
    k.total_qty,
    ROUND(k.total_revenue, 2)           AS total_revenue,
    ROUND(k.avg_order_value, 2)         AS avg_order_value,
    ROUND(k.total_revenue
          - LAG(k.total_revenue) OVER (ORDER BY k.year, k.month_number), 2)
                                        AS mom_revenue_change,
    ROUND((k.total_revenue
           - LAG(k.total_revenue) OVER (ORDER BY k.year, k.month_number))
          * 100 / NULLIF(LAG(k.total_revenue) OVER (ORDER BY k.year, k.month_number),0), 2)
                                        AS mom_growth_pct
FROM v_monthly_kpi k
ORDER BY k.year, k.month_number;


-- ── Q05: Revenue by Quarter ──────────────────────────────────────
-- Business Question: Which quarter performed the best?
SELECT
    d.year,
    d.quarter,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.qty)                          AS total_qty,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.amount), 2)             AS avg_order_value
FROM fact_orders f
JOIN dim_date    d ON f.date_key = d.date_key
GROUP BY d.year, d.quarter
ORDER BY d.year, d.quarter;


-- ── Q06: Day-of-Week Revenue Pattern ─────────────────────────────
-- Business Question: Which days drive the highest sales?
SELECT
    d.day_name,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.qty)                          AS total_qty,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.amount), 2)             AS avg_order_value
FROM fact_orders f
JOIN dim_date    d ON f.date_key = d.date_key
GROUP BY d.day_name
ORDER BY FIELD(d.day_name,'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday');


-- ── Q07: Weekly Revenue Trend ────────────────────────────────────
-- Business Question: How does revenue look on a week-by-week basis?
SELECT
    d.year,
    d.week_number,
    MIN(d.full_date)                    AS week_start,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    ROUND(SUM(f.amount), 2)             AS weekly_revenue
FROM fact_orders f
JOIN dim_date    d ON f.date_key = d.date_key
GROUP BY d.year, d.week_number
ORDER BY d.year, d.week_number;


-- ────────────────────────────────────────────────────────────────
--  SECTION C — PRODUCT & CATEGORY ANALYSIS
-- ────────────────────────────────────────────────────────────────

-- ── Q08: Revenue by Category ─────────────────────────────────────
-- Business Question: Which product categories generate the most revenue?
SELECT * FROM v_category_kpi;


-- ── Q09: Top 10 Best-Selling Products (by Revenue) ───────────────
-- Business Question: What are our top performing SKUs?
SELECT
    p.sku,
    p.style,
    p.category,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.qty)                          AS qty_sold,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.unit_price), 2)         AS avg_unit_price
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.sku, p.style, p.category
ORDER BY total_revenue DESC
LIMIT 10;


-- ── Q10: Top 10 Best-Selling Products (by Quantity) ──────────────
-- Business Question: What are our highest volume SKUs?
SELECT
    p.sku,
    p.style,
    p.category,
    SUM(f.qty)                          AS qty_sold,
    ROUND(SUM(f.amount), 2)             AS total_revenue
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.sku, p.style, p.category
ORDER BY qty_sold DESC
LIMIT 10;


-- ── Q11: Category Performance — Monthly Breakdown ────────────────
-- Business Question: How does each category trend over time?
SELECT
    p.category,
    d.month_name,
    d.month_number,
    COUNT(DISTINCT f.order_id)          AS orders,
    ROUND(SUM(f.amount), 2)             AS revenue
FROM fact_orders f
JOIN dim_product p ON f.product_key  = p.product_key
JOIN dim_date    d ON f.date_key     = d.date_key
GROUP BY p.category, d.month_name, d.month_number
ORDER BY p.category, d.month_number;


-- ── Q12: Size Distribution per Category ──────────────────────────
-- Business Question: What sizes dominate each category?
SELECT
    p.category,
    p.size,
    COUNT(DISTINCT f.order_id)          AS orders,
    SUM(f.qty)                          AS qty_sold,
    ROUND(SUM(f.amount), 2)             AS revenue
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category, p.size
ORDER BY p.category, qty_sold DESC;


-- ────────────────────────────────────────────────────────────────
--  SECTION D — GEOGRAPHIC ANALYSIS
-- ────────────────────────────────────────────────────────────────

-- ── Q13: Top 10 States by Revenue ────────────────────────────────
-- Business Question: Which states contribute the most revenue?
SELECT * FROM v_state_kpi LIMIT 10;


-- ── Q14: Top 15 Cities by Orders ─────────────────────────────────
-- Business Question: Which cities are the most active markets?
SELECT
    l.ship_city,
    l.ship_state,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.qty)                          AS qty_sold,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.amount), 2)             AS avg_order_value
FROM fact_orders  f
JOIN dim_location l ON f.location_key = l.location_key
WHERE l.ship_city <> 'Unknown'
GROUP BY l.ship_city, l.ship_state
ORDER BY total_orders DESC
LIMIT 15;


-- ── Q15: State-Level Order Status Breakdown ──────────────────────
-- Business Question: Where are cancellations highest?
SELECT
    l.ship_state,
    COUNT(*)                                            AS total_orders,
    SUM(CASE WHEN f.status='Delivered'  THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN f.status='Shipped'    THEN 1 ELSE 0 END) AS shipped,
    SUM(CASE WHEN f.status='Cancelled'  THEN 1 ELSE 0 END) AS cancelled,
    SUM(CASE WHEN f.status='Returned'   THEN 1 ELSE 0 END) AS returned,
    ROUND(SUM(CASE WHEN f.status='Cancelled' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)                        AS cancel_rate_pct
FROM fact_orders  f
JOIN dim_location l ON f.location_key = l.location_key
WHERE l.ship_state <> 'Unknown'
GROUP BY l.ship_state
ORDER BY cancel_rate_pct DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────────
--  SECTION E — CHANNEL & FULFILMENT ANALYSIS
-- ────────────────────────────────────────────────────────────────

-- ── Q16: Revenue by Sales Channel ────────────────────────────────
-- Business Question: How does Amazon.in compare to non-Amazon channels?
SELECT
    c.sales_channel,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    SUM(f.qty)                          AS qty_sold,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.amount), 2)             AS avg_order_value,
    ROUND(SUM(f.amount) * 100 / SUM(SUM(f.amount)) OVER(), 2) AS revenue_pct
FROM fact_orders f
JOIN dim_channel c ON f.channel_key = c.channel_key
GROUP BY c.sales_channel;


-- ── Q17: Fulfilment Method Analysis ──────────────────────────────
-- Business Question: Amazon vs Merchant fulfiled comparison?
SELECT
    c.fulfilment,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.amount), 2)             AS avg_order_value,
    SUM(CASE WHEN f.status='Delivered' THEN 1 ELSE 0 END) AS delivered,
    SUM(CASE WHEN f.status='Cancelled' THEN 1 ELSE 0 END) AS cancelled,
    ROUND(SUM(CASE WHEN f.status='Cancelled' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)        AS cancel_rate_pct
FROM fact_orders f
JOIN dim_channel c ON f.channel_key = c.channel_key
GROUP BY c.fulfilment;


-- ── Q18: Shipping Speed Analysis ─────────────────────────────────
-- Business Question: Does expedited shipping correlate with higher AOV?
SELECT
    c.ship_service_level,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.amount), 2)             AS avg_order_value,
    ROUND(AVG(f.qty), 2)               AS avg_qty_per_order
FROM fact_orders f
JOIN dim_channel c ON f.channel_key = c.channel_key
GROUP BY c.ship_service_level;


-- ── Q19: Promotion Impact Analysis ───────────────────────────────
-- Business Question: Do promotions drive more orders/revenue?
SELECT
    CASE WHEN f.promotion_ids = 'No Promotion' THEN 'No Promotion'
         ELSE 'With Promotion' END AS promo_segment,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(AVG(f.amount), 2)             AS avg_order_value,
    SUM(f.qty)                          AS total_qty
FROM fact_orders f
GROUP BY promo_segment;


-- ────────────────────────────────────────────────────────────────
--  SECTION F — CUSTOMER INSIGHTS
-- ────────────────────────────────────────────────────────────────

-- ── Q20: Repeat Order Analysis by State ──────────────────────────
-- Business Question: Which states have the highest order frequency?
SELECT
    l.ship_state,
    COUNT(DISTINCT f.order_id)          AS total_orders,
    ROUND(SUM(f.amount), 2)             AS total_revenue,
    ROUND(SUM(f.amount) / COUNT(DISTINCT f.order_id), 2) AS revenue_per_order
FROM fact_orders  f
JOIN dim_location l ON f.location_key = l.location_key
WHERE l.ship_state <> 'Unknown'
GROUP BY l.ship_state
ORDER BY revenue_per_order DESC
LIMIT 15;


-- ── Q21: High-Value Order Segments (Quartile Analysis) ───────────
-- Business Question: What share of orders/revenue comes from each value tier?
WITH order_amounts AS (
    SELECT
        order_id,
        SUM(amount) AS order_total
    FROM fact_orders
    GROUP BY order_id
),
quartiles AS (
    SELECT
        order_id,
        order_total,
        NTILE(4) OVER (ORDER BY order_total) AS quartile
    FROM order_amounts
)
SELECT
    quartile                            AS value_tier,
    COUNT(*)                            AS orders,
    ROUND(MIN(order_total), 2)          AS min_order_value,
    ROUND(MAX(order_total), 2)          AS max_order_value,
    ROUND(AVG(order_total), 2)          AS avg_order_value,
    ROUND(SUM(order_total), 2)          AS total_revenue,
    ROUND(SUM(order_total) * 100 / SUM(SUM(order_total)) OVER(), 2) AS revenue_pct
FROM quartiles
GROUP BY quartile
ORDER BY quartile;


-- ── Q22: Category × State Revenue Matrix (Top 5 States) ──────────
-- Business Question: Which categories are strongest in which states?
SELECT
    l.ship_state,
    p.category,
    ROUND(SUM(f.amount), 2)             AS revenue
FROM fact_orders  f
JOIN dim_product  p ON f.product_key  = p.product_key
JOIN dim_location l ON f.location_key = l.location_key
WHERE l.ship_state IN (
    SELECT ship_state FROM v_state_kpi LIMIT 5
)
GROUP BY l.ship_state, p.category
ORDER BY l.ship_state, revenue DESC;


-- ── Q23: Running Total Revenue (Cumulative) ───────────────────────
-- Business Question: What is the cumulative revenue progression?
SELECT
    m.year,
    m.month_number,
    m.month_name,
    ROUND(m.total_revenue, 2)           AS monthly_revenue,
    ROUND(SUM(m.total_revenue) OVER (
              PARTITION BY m.year
              ORDER BY m.month_number), 2) AS cumulative_revenue_ytd
FROM v_monthly_kpi m
ORDER BY m.year, m.month_number;


-- ── Q24: Return Rate by Category ─────────────────────────────────
-- Business Question: Which categories have the highest return rates?
SELECT
    p.category,
    COUNT(*)                            AS total_orders,
    SUM(CASE WHEN f.status = 'Returned' THEN 1 ELSE 0 END) AS returned_orders,
    ROUND(SUM(CASE WHEN f.status='Returned' THEN 1 ELSE 0 END)
          * 100.0 / COUNT(*), 2)        AS return_rate_pct,
    ROUND(SUM(CASE WHEN f.status='Returned' THEN f.amount ELSE 0 END), 2) AS returned_revenue
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY return_rate_pct DESC;


-- ── Q25: Executive Summary — Full Dashboard Query ────────────────
-- Business Question: Single query for a management summary view
SELECT
    'Total Revenue (INR)'               AS metric,
    CONCAT('₹ ', FORMAT(SUM(amount),2)) AS value
FROM fact_orders
UNION ALL
SELECT 'Total Orders', FORMAT(COUNT(DISTINCT order_id),0)
FROM fact_orders
UNION ALL
SELECT 'Total Qty Sold', FORMAT(SUM(qty),0)
FROM fact_orders
UNION ALL
SELECT 'Avg Order Value (INR)', CONCAT('₹ ', FORMAT(AVG(amount),2))
FROM fact_orders
UNION ALL
SELECT 'Delivered Orders', FORMAT(SUM(CASE WHEN status='Delivered' THEN 1 ELSE 0 END),0)
FROM fact_orders
UNION ALL
SELECT 'Cancellation Rate (%)',
       CONCAT(ROUND(SUM(CASE WHEN status='Cancelled' THEN 1 ELSE 0 END)*100.0/COUNT(*),2),'%')
FROM fact_orders
UNION ALL
SELECT 'Top Category',
       (SELECT category FROM v_category_kpi LIMIT 1)
UNION ALL
SELECT 'Top State',
       (SELECT ship_state FROM v_state_kpi LIMIT 1);
