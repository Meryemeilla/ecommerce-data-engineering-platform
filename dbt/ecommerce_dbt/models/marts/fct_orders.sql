SELECT
    order_id,
    customer_id,
    order_date,
    status,
    total_items,
    order_total
FROM {{ ref('int_orders_enriched') }}
