-- ================================================================
--  E-Commerce BI & Sales Prediction Platform
--  Script: 02_data_import.sql
--  Purpose: Staging table + LOAD DATA + dimension population
--           Run AFTER 01_schema_creation.sql
-- ================================================================

USE ecommerce_bi;

-- ================================================================
--  STAGING TABLE — receives flat CSV rows
-- ================================================================
DROP TABLE IF EXISTS stg_amazon_orders;

CREATE TABLE stg_amazon_orders (
    idx                 INT,
    order_id            VARCHAR(30),
    order_date          VARCHAR(20),       -- raw string from CSV
    status              VARCHAR(60),
    fulfilment          VARCHAR(20),
    sales_channel       VARCHAR(50),
    ship_service_level  VARCHAR(20),
    style               VARCHAR(100),
    sku                 VARCHAR(30),
    category            VARCHAR(50),
    size                VARCHAR(10),
    asin                VARCHAR(20),
    courier_status      VARCHAR(50),
    qty                 INT,
    currency            CHAR(3),
    amount              DECIMAL(12,2),
    ship_city           VARCHAR(100),
    ship_state          VARCHAR(100),
    ship_postal_code    VARCHAR(10),
    ship_country        CHAR(2),
    promotion_ids       VARCHAR(100),
    b2b                 VARCHAR(5),
    fulfilled_by        VARCHAR(30),
    year                SMALLINT,
    month               TINYINT,
    month_name          VARCHAR(10),
    quarter             TINYINT,
    week                TINYINT,
    day_of_week         VARCHAR(10),
    unit_price          DECIMAL(10,2)
) ENGINE=InnoDB;

-- ================================================================
--  LOAD from CSV
--  Update the path to match your local file location.
-- ================================================================
-- NOTE: Run this block only if LOAD DATA INFILE is available.
--       Alternatively use Python/mysqlimport or a GUI tool.
-- ================================================================
/*
LOAD DATA LOCAL INFILE '/path/to/Dataset/Amazon_Sale_Report_Cleaned.csv'
INTO TABLE stg_amazon_orders
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES  TERMINATED BY '\n'
IGNORE 1 ROWS
(idx, order_id, order_date, status, fulfilment, sales_channel,
 ship_service_level, style, sku, category, size, asin,
 courier_status, qty, currency, amount, ship_city, ship_state,
 ship_postal_code, ship_country, promotion_ids, b2b, fulfilled_by,
 year, month, month_name, quarter, week, day_of_week, unit_price);
*/

-- ================================================================
--  POPULATE dim_date  (generate a 3-year calendar)
-- ================================================================
DROP PROCEDURE IF EXISTS sp_populate_dim_date;

DELIMITER $$
CREATE PROCEDURE sp_populate_dim_date(p_start DATE, p_end DATE)
BEGIN
    DECLARE v_date DATE DEFAULT p_start;
    WHILE v_date <= p_end DO
        INSERT IGNORE INTO dim_date VALUES (
            YEAR(v_date)*10000 + MONTH(v_date)*100 + DAY(v_date),  -- date_key
            v_date,
            DAY(v_date),
            DAYNAME(v_date),
            WEEK(v_date, 1),
            MONTH(v_date),
            MONTHNAME(v_date),
            QUARTER(v_date),
            YEAR(v_date),
            DAYOFWEEK(v_date) IN (1, 7)                             -- is_weekend
        );
        SET v_date = DATE_ADD(v_date, INTERVAL 1 DAY);
    END WHILE;
END$$
DELIMITER ;

CALL sp_populate_dim_date('2022-01-01', '2023-12-31');
SELECT COUNT(*) AS dim_date_rows FROM dim_date;

-- ================================================================
--  POPULATE dim_product from staging
-- ================================================================
INSERT IGNORE INTO dim_product (sku, asin, style, category, size)
SELECT DISTINCT sku, asin, style, category, size
FROM   stg_amazon_orders
WHERE  sku IS NOT NULL;

SELECT COUNT(*) AS dim_product_rows FROM dim_product;

-- ================================================================
--  POPULATE dim_location from staging
-- ================================================================
INSERT IGNORE INTO dim_location (ship_city, ship_state, ship_postal, ship_country)
SELECT DISTINCT
    COALESCE(ship_city, 'Unknown'),
    COALESCE(ship_state,'Unknown'),
    ship_postal_code,
    COALESCE(ship_country, 'IN')
FROM stg_amazon_orders;

SELECT COUNT(*) AS dim_location_rows FROM dim_location;

-- ================================================================
--  POPULATE dim_channel from staging
-- ================================================================
INSERT IGNORE INTO dim_channel (sales_channel, fulfilment, ship_service_level,
                                courier_status, fulfilled_by)
SELECT DISTINCT
    COALESCE(sales_channel, 'Unknown'),
    COALESCE(fulfilment, 'Unknown'),
    COALESCE(ship_service_level, 'Unknown'),
    courier_status,
    fulfilled_by
FROM stg_amazon_orders;

SELECT COUNT(*) AS dim_channel_rows FROM dim_channel;

-- ================================================================
--  POPULATE fact_orders from staging (via dimension lookups)
-- ================================================================
INSERT INTO fact_orders
    (order_id, date_key, product_key, location_key, channel_key,
     qty, unit_price, amount, status, currency, promotion_ids, b2b)
SELECT
    s.order_id,
    d.date_key,
    p.product_key,
    l.location_key,
    c.channel_key,
    s.qty,
    s.unit_price,
    s.amount,
    COALESCE(s.status, 'Unknown'),
    COALESCE(s.currency, 'INR'),
    s.promotion_ids,
    COALESCE(s.b2b, 'No')
FROM stg_amazon_orders s
JOIN dim_date d ON d.date_key = YEAR(STR_TO_DATE(s.order_date,'%Y-%m-%d'))*10000
                             + MONTH(STR_TO_DATE(s.order_date,'%Y-%m-%d'))*100
                             + DAY(STR_TO_DATE(s.order_date,'%Y-%m-%d'))
JOIN dim_product  p ON p.sku          = s.sku
JOIN dim_location l ON l.ship_city    = COALESCE(s.ship_city,'Unknown')
                   AND l.ship_state   = COALESCE(s.ship_state,'Unknown')
JOIN dim_channel  c ON c.sales_channel= COALESCE(s.sales_channel,'Unknown')
                   AND c.fulfilment   = COALESCE(s.fulfilment,'Unknown')
                   AND c.ship_service_level = COALESCE(s.ship_service_level,'Unknown');

SELECT COUNT(*) AS fact_orders_rows FROM fact_orders;

SELECT 'Data import complete.' AS status;
