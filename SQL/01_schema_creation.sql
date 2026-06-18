-- ================================================================
--  E-Commerce BI & Sales Prediction Platform
--  Script: 01_schema_creation.sql
--  Database: MySQL 8.0+
--  Purpose: Create all tables for the e-commerce analytics schema
-- ================================================================

-- ── Create & Select Database ──────────────────────────────────────
CREATE DATABASE IF NOT EXISTS ecommerce_bi
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE ecommerce_bi;

-- ── Drop tables if rebuilding ─────────────────────────────────────
DROP TABLE IF EXISTS fact_orders;
DROP TABLE IF EXISTS dim_date;
DROP TABLE IF EXISTS dim_product;
DROP TABLE IF EXISTS dim_location;
DROP TABLE IF EXISTS dim_channel;

-- ================================================================
--  DIMENSION TABLE: dim_date
--  Stores all date-related attributes for time intelligence
-- ================================================================
CREATE TABLE dim_date (
    date_key        INT           NOT NULL,          -- YYYYMMDD surrogate key
    full_date       DATE          NOT NULL,
    day_of_month    TINYINT       NOT NULL,
    day_name        VARCHAR(10)   NOT NULL,
    week_number     TINYINT       NOT NULL,
    month_number    TINYINT       NOT NULL,
    month_name      VARCHAR(10)   NOT NULL,
    quarter         TINYINT       NOT NULL,          -- 1–4
    year            SMALLINT      NOT NULL,
    is_weekend      BOOLEAN       NOT NULL DEFAULT FALSE,
    PRIMARY KEY (date_key),
    INDEX idx_full_date  (full_date),
    INDEX idx_year_month (year, month_number)
) ENGINE=InnoDB COMMENT='Date dimension for time-series analysis';

-- ================================================================
--  DIMENSION TABLE: dim_product
--  Product master data
-- ================================================================
CREATE TABLE dim_product (
    product_key     INT           NOT NULL AUTO_INCREMENT,
    sku             VARCHAR(30)   NOT NULL,
    asin            VARCHAR(20)   NOT NULL,
    style           VARCHAR(100)  NOT NULL,
    category        VARCHAR(50)   NOT NULL,
    size            VARCHAR(10)   NOT NULL,
    PRIMARY KEY (product_key),
    UNIQUE KEY uk_sku  (sku),
    INDEX idx_category (category),
    INDEX idx_asin     (asin)
) ENGINE=InnoDB COMMENT='Product dimension';

-- ================================================================
--  DIMENSION TABLE: dim_location
--  Ship-to location master
-- ================================================================
CREATE TABLE dim_location (
    location_key    INT           NOT NULL AUTO_INCREMENT,
    ship_city       VARCHAR(100)  NOT NULL DEFAULT 'Unknown',
    ship_state      VARCHAR(100)  NOT NULL DEFAULT 'Unknown',
    ship_postal     VARCHAR(10),
    ship_country    CHAR(2)       NOT NULL DEFAULT 'IN',
    PRIMARY KEY (location_key),
    INDEX idx_state (ship_state),
    INDEX idx_city  (ship_city)
) ENGINE=InnoDB COMMENT='Location dimension';

-- ================================================================
--  DIMENSION TABLE: dim_channel
--  Sales channel and fulfilment info
-- ================================================================
CREATE TABLE dim_channel (
    channel_key         INT           NOT NULL AUTO_INCREMENT,
    sales_channel       VARCHAR(50)   NOT NULL,
    fulfilment          VARCHAR(20)   NOT NULL,
    ship_service_level  VARCHAR(20)   NOT NULL,
    courier_status      VARCHAR(50),
    fulfilled_by        VARCHAR(30),
    PRIMARY KEY (channel_key),
    INDEX idx_channel (sales_channel)
) ENGINE=InnoDB COMMENT='Sales channel dimension';

-- ================================================================
--  FACT TABLE: fact_orders
--  Central fact table — one row per order line
-- ================================================================
CREATE TABLE fact_orders (
    order_line_key      BIGINT        NOT NULL AUTO_INCREMENT,
    order_id            VARCHAR(30)   NOT NULL,
    date_key            INT           NOT NULL,
    product_key         INT           NOT NULL,
    location_key        INT           NOT NULL,
    channel_key         INT           NOT NULL,
    -- measures
    qty                 SMALLINT      NOT NULL DEFAULT 1,
    unit_price          DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    amount              DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    -- attributes
    status              VARCHAR(60)   NOT NULL,
    currency            CHAR(3)       NOT NULL DEFAULT 'INR',
    promotion_ids       VARCHAR(100),
    b2b                 CHAR(3)       NOT NULL DEFAULT 'No',
    PRIMARY KEY (order_line_key),
    INDEX idx_order_id   (order_id),
    INDEX idx_date_key   (date_key),
    INDEX idx_product_key(product_key),
    INDEX idx_location_key(location_key),
    INDEX idx_status     (status),
    CONSTRAINT fk_date     FOREIGN KEY (date_key)     REFERENCES dim_date(date_key),
    CONSTRAINT fk_product  FOREIGN KEY (product_key)  REFERENCES dim_product(product_key),
    CONSTRAINT fk_location FOREIGN KEY (location_key) REFERENCES dim_location(location_key),
    CONSTRAINT fk_channel  FOREIGN KEY (channel_key)  REFERENCES dim_channel(channel_key)
) ENGINE=InnoDB COMMENT='Fact table — order transactions';

-- ================================================================
--  VIEWS for simplified reporting
-- ================================================================

-- ── v_orders_flat: denormalised view for BI tools ────────────────
CREATE OR REPLACE VIEW v_orders_flat AS
SELECT
    f.order_id,
    d.full_date          AS order_date,
    d.year,
    d.month_number       AS month,
    d.month_name,
    d.quarter,
    d.day_name,
    p.sku,
    p.asin,
    p.style,
    p.category,
    p.size,
    l.ship_city,
    l.ship_state,
    l.ship_country,
    c.sales_channel,
    c.fulfilment,
    c.ship_service_level,
    f.qty,
    f.unit_price,
    f.amount,
    f.status,
    f.b2b,
    f.promotion_ids
FROM fact_orders   f
JOIN dim_date      d ON f.date_key     = d.date_key
JOIN dim_product   p ON f.product_key  = p.product_key
JOIN dim_location  l ON f.location_key = l.location_key
JOIN dim_channel   c ON f.channel_key  = c.channel_key;

-- ── v_monthly_kpi: monthly KPIs ──────────────────────────────────
CREATE OR REPLACE VIEW v_monthly_kpi AS
SELECT
    d.year,
    d.month_number,
    d.month_name,
    COUNT(DISTINCT f.order_id)  AS total_orders,
    SUM(f.qty)                  AS total_qty,
    SUM(f.amount)               AS total_revenue,
    AVG(f.amount)               AS avg_order_value,
    COUNT(CASE WHEN f.status = 'Delivered' THEN 1 END)  AS delivered_orders,
    COUNT(CASE WHEN f.status = 'Cancelled' THEN 1 END)  AS cancelled_orders
FROM fact_orders f
JOIN dim_date    d ON f.date_key = d.date_key
GROUP BY d.year, d.month_number, d.month_name
ORDER BY d.year, d.month_number;

-- ── v_category_kpi: category-level KPIs ─────────────────────────
CREATE OR REPLACE VIEW v_category_kpi AS
SELECT
    p.category,
    COUNT(DISTINCT f.order_id)                         AS total_orders,
    SUM(f.qty)                                         AS total_qty,
    ROUND(SUM(f.amount), 2)                            AS total_revenue,
    ROUND(AVG(f.amount), 2)                            AS avg_order_value,
    ROUND(SUM(f.amount) * 100.0 /
          SUM(SUM(f.amount)) OVER (), 2)               AS revenue_pct
FROM fact_orders f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;

-- ── v_state_kpi: state-level KPIs ───────────────────────────────
CREATE OR REPLACE VIEW v_state_kpi AS
SELECT
    l.ship_state,
    COUNT(DISTINCT f.order_id)                         AS total_orders,
    SUM(f.qty)                                         AS total_qty,
    ROUND(SUM(f.amount), 2)                            AS total_revenue,
    ROUND(AVG(f.amount), 2)                            AS avg_order_value,
    ROUND(SUM(f.amount) * 100.0 /
          SUM(SUM(f.amount)) OVER (), 2)               AS revenue_pct
FROM fact_orders f
JOIN dim_location l ON f.location_key = l.location_key
WHERE l.ship_state <> 'Unknown'
GROUP BY l.ship_state
ORDER BY total_revenue DESC;

SELECT 'Schema creation complete.' AS status;
