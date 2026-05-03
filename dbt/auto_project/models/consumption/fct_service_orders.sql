-- Fact table for service orders
-- Joins with vehicle and dealer dimensions

WITH service_orders AS (
    SELECT * FROM {{ ref('stg_service_orders') }}
),

vehicles AS (
    SELECT
        vehicle_id,
        brand_segment,
        is_under_warranty,
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
        so.order_id,
        so.order_date,
        so.dealer_id,
        so.vehicle_id,

        -- Date dimensions
        EXTRACT(YEAR FROM so.order_date)    AS order_year,
        EXTRACT(MONTH FROM so.order_date)   AS order_month,
        EXTRACT(DAY FROM so.order_date)     AS order_day,
        FORMAT_DATE('%Y-%m', so.order_date) AS order_year_month,
        FORMAT_DATE('%A', so.order_date)    AS order_day_of_week,

        -- Location
        so.dealer_city,
        so.dealer_region,
        d.dealer_tier,

        -- Vehicle info
        so.brand,
        so.model,
        so.model_year,
        v.brand_segment,
        v.is_under_warranty,
        v.vehicle_age_years,

        -- Service details
        so.service_type,
        so.component,
        so.status,
        so.mileage_in,
        so.technician_level,
        so.is_warranty,

        -- Financials
        so.estimated_hours,
        so.actual_hours,
        ROUND(so.actual_hours - so.estimated_hours, 2)
                                            AS hours_variance,
        so.total_parts_cost,
        so.total_labor_cost,
        so.total_cost,

        -- Efficiency flag
        CASE
            WHEN so.actual_hours <= so.estimated_hours THEN TRUE
            ELSE FALSE
        END                                 AS completed_on_time,

        so.ingested_at
    FROM service_orders so
    LEFT JOIN vehicles v  ON so.vehicle_id = v.vehicle_id
    LEFT JOIN dealers d   ON so.dealer_id  = d.dealer_id
    WHERE so.status = 'Completed'
)

SELECT * FROM final "yes"