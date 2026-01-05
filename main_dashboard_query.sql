WITH eight_week_date_series AS (
  SELECT
    DATEADD(week, -1 * (ROW_NUMBER() OVER (ORDER BY NULL) - 1), DATEADD(day, -1, DATE_TRUNC('week', CURRENT_DATE()))) AS week_ending
  FROM TABLE(GENERATOR(ROWCOUNT => 52))
),
tenants_expanded as (
    SELECT DISTINCT tenant
    FROM (
      SELECT primary_tenant AS tenant
      FROM prod.fishbowl.accounts
      WHERE salesforce_account_type = 'Customer'
        AND client_churn_date IS NULL
      UNION ALL
      SELECT f.value::VARCHAR AS tenant
      FROM prod.fishbowl.accounts,
           LATERAL FLATTEN(input => additional_tenants) f
      WHERE salesforce_account_type = 'Customer'
        AND client_churn_date IS NULL
        AND additional_tenants is not null
)),
orchestration_metrics AS (
  SELECT
    DATEADD(day, 6, DATE_TRUNC('week', o.completion_datetime)) AS week_ending,
    COUNT(CASE WHEN o.orchestration_type IN ('campaign', 'segment') THEN o.tenant_id END) AS cs_sends,
    COUNT(*) AS total_sends,
    (select count(*) from tenants_expanded) AS all_tenants,
    COUNT(DISTINCT CASE WHEN o.orchestration_type IN ('campaign', 'segment') THEN o.tenant_id END) AS cs_tenants,
    COUNT(CASE WHEN c.is_paid_media = TRUE THEN o.tenant_id END) AS paid_media_sends,
    SUM(o.rows_orchestrated) AS rows_sent,
    SUM(CASE WHEN o.orchestration_type IN ('campaign', 'segment') THEN o.rows_orchestrated ELSE 0 END) AS cs_rows_sent,
    SUM(CASE WHEN c.is_paid_media = TRUE THEN o.rows_orchestrated END) AS paid_media_rows,
    COUNT(DISTINCT CASE WHEN c.is_paid_media = TRUE THEN o.tenant_id END) AS paid_media_tenants,
    CASE
        WHEN COUNT(DISTINCT o.tenant_id) = 0 THEN 0.0
        ELSE (COUNT(DISTINCT CASE WHEN c.is_paid_media = TRUE THEN o.tenant_id END) * 1.0 / COUNT(DISTINCT o.tenant_id))
    END AS paid_media_percent,
    CASE
        WHEN COUNT(DISTINCT o.tenant_id) = 0 THEN 0.0
        ELSE (COUNT(DISTINCT CASE WHEN o.orchestration_type IN ('campaign', 'segment') THEN o.tenant_id END) * 1.0 / all_tenants)
    END AS cs_tenants_percent
  FROM prod.fishbowl.orchestration_events AS o
  INNER JOIN prod.fishbowl.connectors AS c
    ON o.connector_id = c.connector_id
  WHERE
    DATEADD(day, 6, DATE_TRUNC('week', o.completion_datetime)) >= (SELECT MIN(week_ending) FROM eight_week_date_series)
    AND DATEADD(day, 6, DATE_TRUNC('week', o.completion_datetime)) <= (SELECT MAX(week_ending) FROM eight_week_date_series)
    AND o.tenant_billing_flag = 'client'
    AND NOT o.tenant_is_sandbox
  GROUP BY
    week_ending
),
all_successful_journeys AS (
  SELECT
    w.tenant_id,
    w.workflow_id,
    t.task_id,
    w.start_datetime
  FROM prod.fishbowl.workflow_tasks t
  INNER JOIN prod.fishbowl.workflows w
    ON w.workflow_id = t.workflow_id
  WHERE
    CONTAINS(w.workflow_type, 'journey')
    AND w.workflow_state = 'succeeded'
    AND NOT w.tenant_is_sandbox
    AND w.tenant_billing_type = 'client'
),
journeys_data AS (
  SELECT
    DATEADD(day, 6, DATE_TRUNC('week', start_datetime)) AS week_ending,
    COUNT(DISTINCT workflow_id) AS journeys,
    COUNT(DISTINCT tenant_id) AS clients
  FROM all_successful_journeys
  GROUP BY
    week_ending
),
client_first_week AS (
  SELECT
    tenant_id,
    MIN(DATEADD(day, 6, DATE_TRUNC('week', start_datetime))) AS first_successful_week
  FROM all_successful_journeys
  GROUP BY
    tenant_id
),
connector_stats AS (
  SELECT
      ds.week_ending
    , SUM(IFF(c.is_source AND NOT c.is_destination, 1, 0)) AS source_connectors
    , SUM(IFF(c.is_destination AND NOT c.is_source, 1, 0)) AS destination_connectors
    , SUM(IFF(c.is_source AND c.is_destination, 1, 0)) AS bi_directional_connectors
  FROM eight_week_date_series AS ds
  CROSS JOIN prod.fishbowl.connectors AS c
  WHERE c.first_available_date <= ds.week_ending
    AND c.last_available_date >= DATEADD('day', -14, ds.week_ending)
  GROUP BY ds.week_ending
),
amps_metrics AS (
  SELECT
    DATEADD(day, 6, DATE_TRUNC('week', usage_date)) AS week_ending,
    SUM(CASE WHEN product_feature_v3 IN ('data-send-managed-connectors', 'data-send-cloud-storage') THEN amps_amount_v3 ELSE 0 END) AS amps_activation,
    SUM(CASE WHEN product_feature_v3 = 'campaign-audience-building' THEN amps_amount_v3 ELSE 0 END) AS amps_campaigns,
    SUM(CASE WHEN product_feature_v3 = 'journey-audience-building' THEN amps_amount_v3 ELSE 0 END) AS amps_journeys,
    SUM(CASE WHEN product_feature_v3 = 'orchestration-audience-building' THEN amps_amount_v3 ELSE 0 END) AS amps_orchestration,
    SUM(CASE WHEN product_feature_v3 = 'profile-api' THEN amps_amount_v3 ELSE 0 END) AS amps_profile_api,
    SUM(amps_amount_v3) AS amps_total
  FROM prod.fishbowl.amps
  WHERE DATEADD(day, 6, DATE_TRUNC('week', usage_date)) >= (SELECT MIN(week_ending) FROM eight_week_date_series)
    AND DATEADD(day, 6, DATE_TRUNC('week', usage_date)) <= (SELECT MAX(week_ending) FROM eight_week_date_series)
    AND tenant_billing_type = 'client' AND amps_category = 'Activation'
  GROUP BY 1
),
final_metrics AS (
  SELECT
    ds.week_ending,
    COALESCE(om.cs_sends, 0) AS cs_sends,
    COALESCE(om.total_sends, 0) AS total_sends,
    COALESCE(om.all_tenants, 0) AS all_tenants,
    COALESCE(om.cs_tenants, 0) AS cs_tenants,
    COALESCE(om.cs_tenants_percent, 0) AS cs_tenants_percent,
    COALESCE(om.paid_media_sends, 0) AS paid_media_sends,
    COALESCE(om.rows_sent, 0) AS rows_sent,
    COALESCE(om.cs_rows_sent, 0) AS cs_rows_sent,
    COALESCE(om.paid_media_rows, 0) AS paid_media_rows,
    COALESCE(om.paid_media_tenants, 0) AS paid_media_tenants,
    COALESCE(om.paid_media_percent, 0) AS paid_media_percent,
    COALESCE(jat.journeys, 0) AS journeys,
    COALESCE(jat.clients, 0) AS clients,
    COUNT(DISTINCT CASE WHEN ds.week_ending >= cfw.first_successful_week THEN cfw.tenant_id END) AS running_total_clients,
    COALESCE(ap.amps_activation, 0) as amps_activation,
    COALESCE(ap.amps_campaigns, 0) as amps_campaigns,
    COALESCE(ap.amps_journeys, 0) as amps_journeys,
    COALESCE(ap.amps_orchestration, 0) as amps_orchestration,
    COALESCE(ap.amps_profile_api, 0) as amps_profile_api,
    COALESCE(ap.amps_total, 0) as amps_total
  FROM eight_week_date_series AS ds
  LEFT JOIN orchestration_metrics AS om ON ds.week_ending = om.week_ending
  LEFT JOIN journeys_data AS jat ON ds.week_ending = jat.week_ending
  LEFT JOIN amps_metrics AS ap ON ds.week_ending = ap.week_ending
  CROSS JOIN client_first_week AS cfw
  GROUP BY
    ds.week_ending,
    om.cs_sends, om.total_sends, om.all_tenants, om.cs_tenants, om.cs_tenants_percent,
    om.paid_media_sends, om.rows_sent, om.cs_rows_sent, om.paid_media_rows, om.paid_media_tenants, om.paid_media_percent,
    jat.journeys, jat.clients,
    ap.amps_activation, ap.amps_campaigns, ap.amps_journeys, ap.amps_orchestration, ap.amps_profile_api, ap.amps_total
)
SELECT 'Campaign & Segment Sends' AS "Metric", week_ending AS "Week Ending", ROUND(cs_sends / 1000, 0) || 'k' AS "Value", 1 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Total Sends' AS Metric, week_ending AS "Week Ending", ROUND(total_sends / 1000, 0) || 'k' AS "Value", 0.5 AS sort_order FROM final_metrics
UNION ALL
SELECT 'All Tenants' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(all_tenants) AS "Value", 0.6 AS sort_order FROM final_metrics
UNION ALL
SELECT 'CS Tenants' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(cs_tenants) AS "Value", 0.7 AS sort_order FROM final_metrics
UNION ALL
SELECT 'CS Tenants Percent' AS Metric, week_ending AS "Week Ending", ROUND(cs_tenants_percent * 100, 0) || '%' AS "Value", 0.8 AS sort_order FROM final_metrics
UNION ALL
SELECT '% Campaign & Segment' AS Metric, week_ending AS "Week Ending", CASE WHEN total_sends = 0 THEN '0%' ELSE ROUND((cs_sends::FLOAT / total_sends) * 100, 0) || '%' END AS "Value", 2 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Campaign & Segment Rows Sent' AS Metric, week_ending AS "Week Ending", ROUND(cs_rows_sent / 1000000000000, 2) || 'T' AS "Value", 2.5 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Rows Sent' AS Metric, week_ending AS "Week Ending", ROUND(rows_sent / 1000000000000, 2) || 'T' AS "Value", 3 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Paid Media Tenants' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(paid_media_tenants) AS "Value", 4 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Paid Media Sends' AS Metric, week_ending AS "Week Ending", ROUND(paid_media_sends / 1000, 1) || 'k' AS "Value", 5 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Paid Media Rows' AS Metric, week_ending AS "Week Ending", ROUND(paid_media_rows / 1000000000, 1) || 'B' AS "Value", 6 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Paid Media %' AS Metric, week_ending AS "Week Ending", ROUND(paid_media_percent * 100, 0) || '%' AS "Value", 7 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Journey Clients' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(ROUND(clients)) AS "Value", 8 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Journeys' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(ROUND(journeys)) AS "Value", 9 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Journey Adoption' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(running_total_clients) AS "Value", 10 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Source Connectors' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(source_connectors) AS "Value", 11 AS sort_order FROM connector_stats
UNION ALL
SELECT 'Destination Connectors' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(destination_connectors) AS "Value", 11.1 AS sort_order FROM connector_stats
UNION ALL
SELECT 'Bi-Directional Connectors' AS Metric, week_ending AS "Week Ending", TO_VARCHAR(bi_directional_connectors) AS "Value", 11.2 AS sort_order FROM connector_stats
UNION ALL
SELECT 'Amps - Total' AS "Metric", week_ending AS "Week Ending", TO_VARCHAR(ROUND(amps_total)) AS "Value", 12 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Amps - Activation' AS "Metric", week_ending AS "Week Ending", TO_VARCHAR(ROUND(amps_activation)) AS "Value", 12.1 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Amps - Campaigns' AS "Metric", week_ending AS "Week Ending", TO_VARCHAR(ROUND(amps_campaigns)) AS "Value", 12.2 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Amps - Journeys' AS "Metric", week_ending AS "Week Ending", TO_VARCHAR(ROUND(amps_journeys)) AS "Value", 12.3 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Amps - Orchestration' AS "Metric", week_ending AS "Week Ending", TO_VARCHAR(ROUND(amps_orchestration)) AS "Value", 12.4 AS sort_order FROM final_metrics
UNION ALL
SELECT 'Amps - Profile API' AS "Metric", week_ending AS "Week Ending", TO_VARCHAR(ROUND(amps_profile_api)) AS "Value", 12.5 AS sort_order FROM final_metrics
ORDER BY sort_order, "Week Ending";
