SELECT *
FROM {{ ref('dim_customers') }}
WHERE
    email NOT LIKE '%_@_%._%'
    OR email LIKE '% %'
