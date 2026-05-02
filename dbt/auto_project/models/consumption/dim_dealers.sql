-- Dimension table for dealers
-- Derived from service and sales order data since there's no dealer master endpoint

WITH service_dealers AS (
    SELECT DISTINCT
        dealer_id,
        dealer_city,
        dealer_region
    FROM {{ ref('stg_service_orders') }}
    WHERE dealer_id IS NOT NULL
),

sales_dealers AS (
    SELECT DISTINCT
        dealer_id,
        dealer_city,
        dealer_region
    FROM {{ ref('stg_sales_orders') }}
    WHERE dealer_id IS NOT NULL
),

all_dealers AS (
    SELECT * FROM service_dealers
    UNION DISTINCT
    SELECT * FROM sales_dealers
),

final AS (
    SELECT
        dealer_id,
        dealer_city,
        dealer_region,

        -- Dealer tier based on city
        CASE
            WHEN dealer_city = 'Jakarta'    THEN 'Tier 1'
            WHEN dealer_city IN ('Surabaya', 'Bandung') THEN 'Tier 2'
            WHEN dealer_city IN ('Medan', 'Makassar', 'Semarang') THEN 'Tier 3'
            ELSE 'Tier 4'
        END                                 AS dealer_tier
    FROM all_dealers
)

SELECT * FROM final