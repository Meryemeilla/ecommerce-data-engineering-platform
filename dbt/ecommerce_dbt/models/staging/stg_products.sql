SELECT
    product_id,
    TRIM(product_name) AS product_name,
    TRIM(category) AS category,
    price,
    stock_quantity,
    created_at
FROM {{ source('ecommerce_staging', 'products') }}