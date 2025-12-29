SELECT COUNT(DISTINCT t.tenant_id) AS unique_journey_tenants
FROM prod.product.ga4_product_usage g
INNER JOIN prod.fishbowl.tenants t ON g.tenant = t.tenant_id
WHERE LOWER(g.event_name) = 'create journey'
  AND t.tenant_billing_flag = 'client' -- Changed from tenant_billing_type to tenant_billing_flag for consistency
  AND NOT t.tenant_is_sandbox
  -- Use date trunc for consistency with other queries
  AND DATE_TRUNC('week', g.date) <= (
    SELECT DATEADD(day, -1, DATE_TRUNC('week', CURRENT_DATE()))
  )
