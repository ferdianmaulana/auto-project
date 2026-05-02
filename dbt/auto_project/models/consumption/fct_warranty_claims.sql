-- Fact table for warranty claims
-- Joins with vehicle and dealer dimensions

WITH warranty_claims AS (
    SELECT * FROM {{ ref('stg_warranty_claims') }}
),

vehicles AS (
    SELECT
        vehicle_id,
        brand_segment,
        vehicle_age_years,
        vehicle_age_months
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
        wc.claim_id,
        wc.claim_date,
        wc.vehicle_id,
        wc.dealer_id,

        -- Date dimensions
        EXTRACT(YEAR FROM wc.claim_date)    AS claim_year,
        EXTRACT(MONTH FROM wc.claim_date)   AS claim_month,
        FORMAT_DATE('%Y-%m', wc.claim_date) AS claim_year_month,

        -- Location
        d.dealer_tier,

        -- Vehicle info
        wc.brand,
        wc.model,
        wc.model_year,
        wc.purchase_date,
        v.brand_segment,
        v.vehicle_age_years,
        v.vehicle_age_months,

        -- Claim details
        wc.claim_type,
        wc.component,
        wc.defect_description,
        wc.claim_status,

        -- Financials
        wc.claim_amount,
        wc.approved_amount,
        ROUND(wc.approved_amount / NULLIF(wc.claim_amount, 0) * 100, 2)
                                            AS approval_rate_pct,

        -- Flags
        CASE
            WHEN wc.claim_status = 'Approved' THEN TRUE
            WHEN wc.claim_status = 'Paid'     THEN TRUE
            ELSE FALSE
        END                                 AS is_approved,

        wc.ingested_at
    FROM warranty_claims wc
    LEFT JOIN vehicles v  ON wc.vehicle_id = v.vehicle_id
    LEFT JOIN dealers d   ON wc.dealer_id  = d.dealer_id
)

SELECT * FROM final