-- Mart table for brand performance
-- Combines sales volume + service revenue + warranty claims per brand per month

WITH service AS (
    SELECT
        brand,
        brand_segment,
        order_year_month                    AS year_month,
        COUNT(order_id)                     AS total_service_orders,
        SUM(total_cost)                     AS total_service_revenue,
        ROUND(AVG(total_cost), 0)           AS avg_service_cost,
        COUNTIF(service_type = 'Periodic')  AS periodic_services,
        COUNTIF(service_type = 'Repair')    AS repair_services,
        COUNTIF(is_warranty = TRUE)         AS warranty_services
    FROM {{ ref('fct_service_orders') }}
    GROUP BY 1, 2, 3
),

sales AS (
    SELECT
        brand,
        sale_year_month                     AS year_month,
        COUNT(sale_id)                      AS total_units_sold,
        SUM(final_price)                    AS total_sales_revenue,
        ROUND(AVG(final_price), 0)          AS avg_selling_price,
        COUNTIF(fuel_type = 'Electric')     AS ev_units_sold
    FROM {{ ref('fct_sales_orders') }}
    GROUP BY 1, 2
),

warranty AS (
    SELECT
        brand,
        claim_year_month                    AS year_month,
        COUNT(claim_id)                     AS total_claims,
        SUM(claim_amount)                   AS total_claim_amount,
        SUM(approved_amount)                AS total_approved_amount,
        COUNTIF(is_approved = TRUE)         AS approved_claims
    FROM {{ ref('fct_warranty_claims') }}
    GROUP BY 1, 2
),

final AS (
    SELECT
        COALESCE(sv.brand, s.brand)         AS brand,
        COALESCE(sv.year_month, s.year_month) AS year_month,
        sv.brand_segment,

        -- Service metrics
        COALESCE(sv.total_service_orders, 0) AS total_service_orders,
        COALESCE(sv.total_service_revenue, 0) AS total_service_revenue,
        COALESCE(sv.avg_service_cost, 0)    AS avg_service_cost,
        COALESCE(sv.periodic_services, 0)   AS periodic_services,
        COALESCE(sv.repair_services, 0)     AS repair_services,
        COALESCE(sv.warranty_services, 0)   AS warranty_services,

        -- Sales metrics
        COALESCE(s.total_units_sold, 0)     AS total_units_sold,
        COALESCE(s.total_sales_revenue, 0)  AS total_sales_revenue,
        COALESCE(s.avg_selling_price, 0)    AS avg_selling_price,
        COALESCE(s.ev_units_sold, 0)        AS ev_units_sold,

        -- Warranty metrics
        COALESCE(w.total_claims, 0)         AS total_warranty_claims,
        COALESCE(w.total_claim_amount, 0)   AS total_claim_amount,
        COALESCE(w.total_approved_amount, 0) AS total_approved_amount,

        -- Derived metrics
        ROUND(
            COALESCE(w.total_claims, 0) /
            NULLIF(COALESCE(s.total_units_sold, 0), 0) * 100,
        2)                                  AS warranty_claim_rate_pct,

        ROUND(
            COALESCE(sv.repair_services, 0) /
            NULLIF(COALESCE(sv.total_service_orders, 0), 0) * 100,
        2)                                  AS repair_rate_pct

    FROM service sv
    FULL OUTER JOIN sales s
        ON sv.brand     = s.brand
        AND sv.year_month = s.year_month
    LEFT JOIN warranty w
        ON sv.brand     = w.brand
        AND sv.year_month = w.year_month
)

SELECT * FROM final