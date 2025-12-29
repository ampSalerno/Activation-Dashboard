-- Query to get tenants with any journey (draft, archive, or live)
WITH DailyCounts AS (
  SELECT
    t.tenant_name,
    g.date,
    COUNT(*) AS journeys_on_date
  FROM
    prod.product.ga4_product_usage AS g
    INNER JOIN prod.fishbowl.tenants AS t ON t.tenant_id = g.tenant
  WHERE
    STARTSWITH(g.event_category, 'Journeys')
    AND LOWER(g.event_name) = 'create journey'
    AND t.tenant_billing_flag = 'client'
    AND NOT t.tenant_is_sandbox
    AND g.date < DATE_TRUNC('week', CURRENT_DATE())
  GROUP BY
    1, 2
),
AllDates (calendar_date) AS (
  SELECT MIN(date) FROM DailyCounts
  UNION ALL
  SELECT DATEADD('day', 1, calendar_date)
  FROM AllDates
  WHERE calendar_date <= (SELECT MAX(date) FROM DailyCounts)
),
TenantDateGrid AS (
  SELECT
    t.tenant_name,
    d.calendar_date
  FROM
    (SELECT DISTINCT tenant_name FROM DailyCounts) AS t
  CROSS JOIN
    AllDates AS d
),

-- Calculate the running total for every single day first
DailyRunningTotal AS (
  SELECT
    grid.tenant_name,
    grid.calendar_date AS date,
    SUM(COALESCE(dc.journeys_on_date, 0)) OVER (PARTITION BY grid.tenant_name ORDER BY grid.calendar_date) AS running_total_journeys
  FROM
    TenantDateGrid AS grid
  LEFT JOIN
    DailyCounts AS dc
    ON grid.tenant_name = dc.tenant_name
    AND grid.calendar_date = dc.date
)

-- Final SELECT: Aggregate the daily running totals into weekly buckets
SELECT
  tenant_name,
  DATE_TRUNC('week', date) AS week,
  MAX(running_total_journeys) AS running_total_at_week_end
FROM
  DailyRunningTotal
GROUP BY
  1, 2
ORDER BY
  1, 2;
