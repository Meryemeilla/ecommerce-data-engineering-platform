SELECT
    order_id,
    customer_id,
    order_date,
    LOWER(TRIM(status)) AS status
FROM {{ source('ecommerce_staging', 'orders') }}
