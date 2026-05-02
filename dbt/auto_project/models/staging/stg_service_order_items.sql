-- Staging model for service order line items
-- Deduplicates using item_id keeping latest ingested record

WITH source AS (
    SELECT * FROM {{ source('raw', 'service_order_items') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY item_id
            ORDER BY ingested_at DESC
        ) AS row_num
    FROM source
),

final AS (
    SELECT
        item_id,
        order_id,
        CAST(order_date AS DATE)        AS order_date,
        TRIM(item_type)                 AS item_type,
        part_number,
        TRIM(part_name)                 AS part_name,
        TRIM(category)                  AS category,
        CAST(quantity AS INT64)         AS quantity,
        CAST(unit_price AS FLOAT64)     AS unit_price,
        CAST(total_price AS FLOAT64)    AS total_price,
        CAST(is_warranty AS BOOL)       AS is_warranty,
        CAST(ingested_at AS TIMESTAMP)  AS ingested_at
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final