SELECT
    product_id,
    product_name,
    category,
    price,
    stock_quantity,
    created_at
FROM {{ ref('stg_products') }}
