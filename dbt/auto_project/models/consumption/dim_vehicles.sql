-- Dimension table for vehicles
-- Enriched with warranty status and vehicle age

WITH stg AS (
    SELECT * FROM {{ ref('stg_vehicles') }}
),

final AS (
    SELECT
        vehicle_id,
        vin,
        plate_number,
        brand,
        model,
        variant,
        year                                AS model_year,
        color,
        engine_cc,
        fuel_type,
        transmission,
        purchase_date,
        owner_city,
        dealer_id,

        -- Derived fields
        DATE_DIFF(CURRENT_DATE(), purchase_date, YEAR)
                                            AS vehicle_age_years,
        DATE_DIFF(CURRENT_DATE(), purchase_date, MONTH)
                                            AS vehicle_age_months,

        -- Warranty status based on brand warranty period
        CASE
            WHEN brand IN ('HYUNDAI', 'KIA')
                AND DATE_DIFF(CURRENT_DATE(), purchase_date, YEAR) <= 5
                THEN TRUE
            WHEN brand IN ('BMW', 'MERCEDES', 'VOLKSWAGEN')
                AND DATE_DIFF(CURRENT_DATE(), purchase_date, YEAR) <= 2
                THEN TRUE
            WHEN DATE_DIFF(CURRENT_DATE(), purchase_date, YEAR) <= 3
                THEN TRUE
            ELSE FALSE
        END                                 AS is_under_warranty,

        -- Vehicle segment
        CASE
            WHEN brand IN ('BMW', 'MERCEDES', 'VOLKSWAGEN')
                THEN 'Premium'
            WHEN brand IN ('TOYOTA', 'HONDA', 'NISSAN', 'MITSUBISHI')
                THEN 'Mainstream Japanese'
            WHEN brand IN ('HYUNDAI', 'KIA')
                THEN 'Korean'
            WHEN brand IN ('SUZUKI', 'DAIHATSU')
                THEN 'Budget'
            ELSE 'Other'
        END                                 AS brand_segment,

        ingested_at
    FROM stg
)

SELECT * FROM final