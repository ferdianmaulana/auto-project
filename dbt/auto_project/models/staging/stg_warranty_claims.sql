-- Staging model for warranty claims
-- Deduplicates using claim_id keeping latest ingested record

WITH source AS (
    SELECT * FROM {{ source('raw', 'warranty_claims') }}
),

deduplicated AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY claim_id
            ORDER BY ingested_at DESC
        ) AS row_num
    FROM source
),

final AS (
    SELECT
        claim_id,
        CAST(claim_date AS DATE)            AS claim_date,
        vehicle_id,
        UPPER(TRIM(brand))                  AS brand,
        UPPER(TRIM(model))                  AS model,
        CAST(model_year AS INT64)           AS model_year,
        CAST(purchase_date AS DATE)         AS purchase_date,
        dealer_id,
        TRIM(claim_type)                    AS claim_type,
        TRIM(component)                     AS component,
        TRIM(defect_description)            AS defect_description,
        TRIM(claim_status)                  AS claim_status,
        CAST(claim_amount AS FLOAT64)       AS claim_amount,
        CAST(approved_amount AS FLOAT64)    AS approved_amount,
        CAST(ingested_at AS TIMESTAMP)      AS ingested_at
    FROM deduplicated
    WHERE row_num = 1
)

SELECT * FROM final