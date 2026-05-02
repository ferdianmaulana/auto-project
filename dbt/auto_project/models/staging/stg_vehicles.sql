-- Staging model for vehicles master data
-- Deduplicates using vehicle_id keeping latest ingested record

WITH source AS (
    SELECT * FROM {{ source('raw', 'vehicles') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY vehicle_id
            ORDER BY ingested_at DESC
        ) AS row_num
    FROM source
),

final AS (
    SELECT
        vehicle_id,
        vin,
        plate_number,
        UPPER(TRIM(brand))          AS brand,
        UPPER(TRIM(model))          AS model,
        TRIM(variant)               AS variant,
        CAST(year AS INT64)         AS year,
        TRIM(color)                 AS color,
        CAST(engine_cc AS INT64)    AS engine_cc,
        TRIM(fuel_type)             AS fuel_type,
        TRIM(transmission)          AS transmission,
        CAST(purchase_date AS DATE) AS purchase_date,
        TRIM(owner_city)            AS owner_city,
        dealer_id,
        CAST(ingested_at AS TIMESTAMP) AS ingested_at
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final