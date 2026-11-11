SELECT *
FROM {{ ref('dim_products') }}
WHERE stock_quantity < 0