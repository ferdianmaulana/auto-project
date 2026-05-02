-- Staging model for spare parts master catalog
-- Deduplicates using part_number keeping latest ingested record

WITH source AS (
    SELECT * FROM {{ source('raw', 'spare_parts') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY part_number
            ORDER BY ingested_at DESC
        ) AS row_num
    FROM source
),

final AS (
    SELECT
        part_number,
        TRIM(part_name)             AS part_name,
        TRIM(category)              AS category,
        CAST(unit_price AS FLOAT64) AS unit_price,
        TRIM(unit)                  AS unit,
        CAST(ingested_at AS TIMESTAMP) AS ingested_at
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final