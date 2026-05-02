-- Fact table for sales orders
-- Joins with vehicle and dealer dimensions

WITH sales_orders AS (
    SELECT * FROM {{ ref('stg_sales_orders') }}
),

vehicles AS (
    SELECT
        vehicle_id,
        brand_segment,
        vehicle_age_years
    FROM {{ ref('dim_vehicles') }}
),

dealers AS (
    SELECT
        dealer_id,
        dealer_tier
    FROM {{ ref('dim_dealers') }}
),

final AS (
    SELECT
        -- Keys
        so.sale_id,
        so.sale_date,
        so.dealer_id,
        so.vehicle_id,

        -- Date dimensions
        EXTRACT(YEAR FROM so.sale_date)     AS sale_year,
        EXTRACT(MONTH FROM so.sale_date)    AS sale_month,
        EXTRACT(DAY FROM so.sale_date)      AS sale_day,
        FORMAT_DATE('%Y-%m', so.sale_date)  AS sale_year_month,
        FORMAT_DATE('%A', so.sale_date)     AS sale_day_of_week,

        -- Location
        so.dealer_city,
        so.dealer_region,
        d.dealer_tier,

        -- Vehicle info
        so.brand,
        so.model,
        so.model_year,
        so.variant,
        so.fuel_type,
        so.color,
        v.brand_segment,

        -- Sales details
        so.sale_type,
        so.leasing_company,
        so.sales_person_id,
        so.customer_city,

        -- Financials
        so.otr_price,
        so.discount,
        so.final_price,
        ROUND(so.discount / NULLIF(so.otr_price, 0) * 100, 2)
                                            AS discount_pct,

        -- Delivery
        so.delivery_date,
        DATE_DIFF(so.delivery_date, so.sale_date, DAY)
                                            AS delivery_lead_days,

        so.ingested_at
    FROM sales_orders so
    LEFT JOIN vehicles v  ON so.vehicle_id = v.vehicle_id
    LEFT JOIN dealers d   ON so.dealer_id  = d.dealer_id
)

SELECT * FROM final