SELECT
    order_id,
    customer_id,
    order_date,
    status,
    COUNT(order_item_id) AS total_items,
    SUM(line_total) AS order_total

FROM {{ ref('int_order_items_enriched') }}

GROUP BY
    order_id,
    customer_id,
    order_date,
    status