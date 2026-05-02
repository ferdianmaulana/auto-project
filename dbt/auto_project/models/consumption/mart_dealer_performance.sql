-- Mart table for dealer performance
-- Combines sales + service revenue per dealer per month

WITH service AS (
    SELECT
        dealer_id,
        dealer_city,
        dealer_region,
        dealer_tier,
        order_year_month                    AS year_month,
        COUNT(order_id)                     AS total_service_orders,
        SUM(total_cost)                     AS total_service_revenue,
        ROUND(AVG(total_cost), 0)           AS avg_service_revenue,
        SUM(total_parts_cost)               AS total_parts_revenue,
        SUM(total_labor_cost)               AS total_labor_revenue,
        COUNTIF(is_warranty = TRUE)         AS warranty_service_count,
        ROUND(AVG(actual_hours), 2)         AS avg_actual_hours
    FROM {{ ref('fct_service_orders') }}
    GROUP BY 1, 2, 3, 4, 5
),

sales AS (
    SELECT
        dealer_id,
        sale_year_month                     AS year_month,
        COUNT(sale_id)                      AS total_sales_orders,
        SUM(final_price)                    AS total_sales_revenue,
        ROUND(AVG(final_price), 0)          AS avg_selling_price,
        SUM(discount)                       AS total_discount_given,
        COUNTIF(sale_type = 'Cash')         AS cash_sales,
        COUNTIF(sale_type = 'Credit')       AS credit_sales,
        COUNTIF(sale_type = 'Leasing')      AS leasing_sales
    FROM {{ ref('fct_sales_orders') }}
    GROUP BY 1, 2
),

warranty AS (
    SELECT
        dealer_id,
        claim_year_month                    AS year_month,
        COUNT(claim_id)                     AS total_warranty_claims,
        SUM(claim_amount)                   AS total_claim_amount,
        SUM(approved_amount)                AS total_approved_amount,
        COUNTIF(is_approved = TRUE)         AS approved_claims
    FROM {{ ref('fct_warranty_claims') }}
    GROUP BY 1, 2
),

combined AS (
    SELECT
        COALESCE(s.dealer_id, sv.dealer_id)         AS dealer_id,
        COALESCE(s.year_month, sv.year_month)        AS year_month,
        sv.dealer_city,
        sv.dealer_region,
        sv.dealer_tier,

        -- Service metrics
        COALESCE(sv.total_service_orders, 0)         AS total_service_orders,
        COALESCE(sv.total_service_revenue, 0)        AS total_service_revenue,
        COALESCE(sv.avg_service_revenue, 0)          AS avg_service_revenue,
        COALESCE(sv.total_parts_revenue, 0)          AS total_parts_revenue,
        COALESCE(sv.total_labor_revenue, 0)          AS total_labor_revenue,
        COALESCE(sv.warranty_service_count, 0)       AS warranty_service_count,
        COALESCE(sv.avg_actual_hours, 0)             AS avg_actual_hours,

        -- Sales metrics
        COALESCE(s.total_sales_orders, 0)            AS total_sales_orders,
        COALESCE(s.total_sales_revenue, 0)           AS total_sales_revenue,
        COALESCE(s.avg_selling_price, 0)             AS avg_selling_price,
        COALESCE(s.total_discount_given, 0)          AS total_discount_given,
        COALESCE(s.cash_sales, 0)                    AS cash_sales,
        COALESCE(s.credit_sales, 0)                  AS credit_sales,
        COALESCE(s.leasing_sales, 0)                 AS leasing_sales,

        -- Warranty metrics
        COALESCE(w.total_warranty_claims, 0)         AS total_warranty_claims,
        COALESCE(w.total_claim_amount, 0)            AS total_claim_amount,
        COALESCE(w.total_approved_amount, 0)         AS total_approved_amount,
        COALESCE(w.approved_claims, 0)               AS approved_claims,

        -- Combined metrics
        COALESCE(sv.total_service_revenue, 0) +
        COALESCE(s.total_sales_revenue, 0)           AS total_revenue,

        -- Warranty claim rate
        ROUND(
            COALESCE(w.total_warranty_claims, 0) /
            NULLIF(COALESCE(s.total_sales_orders, 0), 0) * 100,
        2)                                           AS warranty_claim_rate_pct

    FROM service sv
    FULL OUTER JOIN sales s
        ON sv.dealer_id  = s.dealer_id
        AND sv.year_month = s.year_month
    LEFT JOIN warranty w
        ON sv.dealer_id  = w.dealer_id
        AND sv.year_month = w.year_month
)

SELECT * FROM combined