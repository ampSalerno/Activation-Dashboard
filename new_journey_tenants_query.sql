-- Define the same date series as the main dashboard query to ensure consistency
WITH eight_week_date_series AS (
  SELECT
    DATEADD(week, -1 * (ROW_NUMBER() OVER (ORDER BY NULL) - 1), DATEADD(day, -1, DATE_TRUNC('week', CURRENT_DATE()))) AS week_ending
  FROM TABLE(GENERATOR(ROWCOUNT => 52))
),
-- First, get journey creation data
JourneyCreations AS (
  SELECT
    t.tenant_id,
    t.tenant_name,
    g.date,
    DATE_TRUNC('week', g.date) AS week,
    COUNT(*) AS journeys_created_count
  FROM
    prod.product.ga4_product_usage AS g
    INNER JOIN prod.fishbowl.tenants AS t ON t.tenant_id = g.tenant
  WHERE
    STARTSWITH(g.event_category, 'Journeys')
    AND LOWER(g.event_name) = 'create journey'
    AND t.tenant_billing_flag = 'client'
    AND NOT t.tenant_is_sandbox
    AND DATE_TRUNC('week', g.date) <= (SELECT MAX(week_ending) FROM eight_week_date_series)
  GROUP BY
    1, 2, 3, 4
),
-- Get first journey date for each tenant
FirstJourneyDate AS (
  SELECT
    tenant_id,
    tenant_name,
    MIN(date) AS first_journey_date
  FROM
    JourneyCreations
  GROUP BY
    1, 2
),
-- Summarize journey creations by week
JourneyCreationsByWeek AS (
  SELECT
    week,
    tenant_id,
    tenant_name,
    SUM(journeys_created_count) AS journeys_created_in_week,
    MIN(date) AS first_creation_date_in_week
  FROM
    JourneyCreations
  GROUP BY
    1, 2, 3
),
-- Get journey run information directly from workflows table with more details
JourneyRunsByWeek AS (
  SELECT
    DATE_TRUNC('week', w.start_datetime) AS week,
    w.tenant_id,
    t.tenant_name,
    COUNT(DISTINCT w.workflow_id) AS journey_runs_in_week,
    SUM(CASE WHEN w.workflow_state = 'succeeded' THEN 1 ELSE 0 END) AS successful_runs,
    MIN(w.start_datetime) AS earliest_run,
    MAX(w.start_datetime) AS latest_run
  FROM
    prod.fishbowl.workflows w
    JOIN prod.fishbowl.tenants t ON w.tenant_id = t.tenant_id
  WHERE
    CONTAINS(w.workflow_type, 'journey')
    AND w.workflow_state IN ('succeeded', 'failed', 'running')
    AND NOT w.tenant_is_sandbox
    AND w.tenant_billing_type = 'client'
    AND DATE_TRUNC('week', w.start_datetime) <= (SELECT MAX(week_ending) FROM eight_week_date_series)
  GROUP BY
    1, 2, 3
  HAVING
    COUNT(DISTINCT w.workflow_id) > 0
),
-- Combine all weeks and tenants
AllData AS (
  SELECT
    COALESCE(jc.week, jr.week) AS week,
    COALESCE(jc.tenant_id, jr.tenant_id) AS tenant_id,
    COALESCE(jc.tenant_name, jr.tenant_name) AS tenant_name,
    jc.journeys_created_in_week,
    jc.first_creation_date_in_week,
    COALESCE(jr.journey_runs_in_week, 0) AS journey_runs_in_week,
    COALESCE(jr.successful_runs, 0) AS successful_runs,
    jr.earliest_run,
    jr.latest_run
  FROM
    JourneyCreationsByWeek jc
    FULL OUTER JOIN JourneyRunsByWeek jr
      ON jc.week = jr.week AND jc.tenant_id = jr.tenant_id
)
SELECT
  a.week AS ACTIVITY_WEEK,
  a.tenant_id AS TENANT_ID,
  a.tenant_name AS TENANT_NAME,
  fj.first_journey_date AS FIRST_JOURNEY_DATE,
  DATE_TRUNC('week', fj.first_journey_date) AS FIRST_JOURNEY_WEEK,
  COALESCE(a.journeys_created_in_week, 0) AS JOURNEYS_CREATED_IN_WEEK,
  -- Determine if this is an additional journey (not the first)
  CASE
    WHEN a.week > DATE_TRUNC('week', fj.first_journey_date) THEN TRUE
    ELSE FALSE
  END AS IS_ADDITIONAL_JOURNEY,
  -- Journey run data - ensure we're using numeric values
  a.journey_runs_in_week AS JOURNEY_RUNS_IN_WEEK,
  a.successful_runs,
  CASE
    WHEN a.journey_runs_in_week > 0 THEN TRUE
    ELSE FALSE
  END AS HAS_JOURNEY_RUNS,
  a.earliest_run,
  a.latest_run
FROM
  AllData a
  JOIN FirstJourneyDate fj ON a.tenant_id = fj.tenant_id
WHERE
  -- Only include weeks where there was either journey creation or runs
  (COALESCE(a.journeys_created_in_week, 0) > 0 OR COALESCE(a.journey_runs_in_week, 0) > 0)
ORDER BY
  ACTIVITY_WEEK DESC, TENANT_NAME
