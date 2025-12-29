WITH base AS (
    SELECT
        CASE
            WHEN product_feature_v3 = 'journey-audience-building' THEN 'Journeys'
            WHEN product_feature_v3 = 'profile-api' THEN 'Profile API'
            WHEN product_feature_v3 = 'data-send-managed-connectors' THEN 'Activation'
            WHEN product_feature_v3 = 'data-send-cloud-storage' THEN 'Activation'
            WHEN product_feature_v3 = 'orchestration-audience-building' THEN 'Orchestration'
            WHEN product_feature_v3 = 'campaign-audience-building' THEN 'Campaigns'
            ELSE product_feature_v3
        END AS Category,
        IFF(usage_date < DATE_TRUNC('week', DATEADD('week', -1, CURRENT_DATE())), amps_amount_v3, 0) as last_week_amps,
        IFF(usage_date >= DATE_TRUNC('week', DATEADD('week', -1, CURRENT_DATE())), amps_amount_v3, 0) as this_week_amps
    FROM prod.fishbowl.amps
    WHERE tenant_billing_type = 'client'
      AND amps_category = 'Activation'
      AND usage_date >= DATE_TRUNC('week', DATEADD('week', -2, CURRENT_DATE()))
      AND usage_date < DATE_TRUNC('week', CURRENT_DATE())
),
aggregated AS (
    SELECT
        Category,
        SUM(last_week_amps) as lw_amps,
        SUM(this_week_amps) as tw_amps
    FROM base
    GROUP BY 1
)
SELECT
    Category,
    ROUND(tw_amps, 0) as AMPS,
    CASE
        WHEN lw_amps IS NULL OR lw_amps = 0 THEN NULL
        WHEN tw_amps IS NULL OR tw_amps = 0 THEN 100
        ELSE (1 - (tw_amps / lw_amps)) * 100
    END as DELTA,
    1 as sort_order
FROM aggregated
UNION ALL
SELECT
    'Total' as Category,
    ROUND(SUM(tw_amps), 0) as AMPS,
    CASE
        WHEN SUM(lw_amps) IS NULL OR SUM(lw_amps) = 0 THEN NULL
        WHEN SUM(tw_amps) IS NULL OR SUM(tw_amps) = 0 THEN 100
        ELSE (1 - (SUM(tw_amps) / SUM(lw_amps))) * 100
    END as DELTA,
    0 as sort_order
FROM aggregated
ORDER BY sort_order, Category;
