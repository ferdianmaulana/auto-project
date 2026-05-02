-- Staging model for sales orders
-- Deduplicates using sale_id keeping latest ingested record

WITH source AS (
    SELECT * FROM {{ source('raw', 'sales_orders') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY sale_id
            ORDER BY ingested_at DESC
        ) AS row_num
    FROM source
),

final AS (
    SELECT
        sale_id,
        CAST(sale_date AS DATE)         AS sale_date,
        dealer_id,
        TRIM(dealer_city)               AS dealer_city,
        TRIM(dealer_region)             AS dealer_region,
        vehicle_id,
        UPPER(TRIM(brand))              AS brand,
        UPPER(TRIM(model))              AS model,
        CAST(model_year AS INT64)       AS model_year,
        TRIM(variant)                   AS variant,
        TRIM(fuel_type)                 AS fuel_type,
        TRIM(color)                     AS color,
        TRIM(sale_type)                 AS sale_type,
        TRIM(leasing_company)           AS leasing_company,
        CAST(otr_price AS FLOAT64)      AS otr_price,
        CAST(discount AS FLOAT64)       AS discount,
        CAST(final_price AS FLOAT64)    AS final_price,
        CAST(delivery_date AS DATE)     AS delivery_date,
        sales_person_id,
        TRIM(customer_city)             AS customer_city,
        CAST(ingested_at AS TIMESTAMP)  AS ingested_at
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final