-- Staging model for service orders
-- Deduplicates using order_id keeping latest ingested record

WITH source AS (
    SELECT * FROM {{ source('raw', 'service_orders') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY order_id
            ORDER BY ingested_at DESC
        ) AS row_num
    FROM source
),

final AS (
    SELECT
        order_id,
        CAST(order_date AS DATE)        AS order_date,
        dealer_id,
        TRIM(dealer_city)               AS dealer_city,
        TRIM(dealer_region)             AS dealer_region,
        vehicle_id,
        UPPER(TRIM(brand))              AS brand,
        UPPER(TRIM(model))              AS model,
        CAST(model_year AS INT64)       AS model_year,
        TRIM(service_type)              AS service_type,
        TRIM(component)                 AS component,
        TRIM(status)                    AS status,
        CAST(mileage_in AS INT64)       AS mileage_in,
        CAST(estimated_hours AS FLOAT64) AS estimated_hours,
        CAST(actual_hours AS FLOAT64)   AS actual_hours,
        CAST(total_parts_cost AS FLOAT64) AS total_parts_cost,
        CAST(total_labor_cost AS FLOAT64) AS total_labor_cost,
        CAST(total_cost AS FLOAT64)     AS total_cost,
        CAST(is_warranty AS BOOL)       AS is_warranty,
        technician_id,
        TRIM(technician_level)          AS technician_level,
        CAST(ingested_at AS TIMESTAMP)  AS ingested_at
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final