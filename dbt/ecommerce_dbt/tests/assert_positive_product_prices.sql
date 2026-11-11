SELECT *
FROM {{ ref('dim_products') }}
WHERE price <= 0