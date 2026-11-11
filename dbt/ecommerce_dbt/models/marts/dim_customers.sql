
SELECT
    customer_id,
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name) AS full_name,
    email,
    city,
    country,
    created_at
FROM {{ ref('stg_customers') }}
