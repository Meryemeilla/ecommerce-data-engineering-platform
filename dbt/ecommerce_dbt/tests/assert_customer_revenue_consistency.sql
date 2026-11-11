SELECT *
FROM {{ ref('fct_customer_revenue') }}
WHERE
    total_orders < 0
    OR delivered_orders < 0
    OR delivered_orders > total_orders
    OR total_order_amount < 0
    OR delivered_revenue < 0
    OR delivered_revenue > total_order_amount
