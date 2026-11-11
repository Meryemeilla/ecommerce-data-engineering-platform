SELECT
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    o.order_date,
    o.status,

    oi.product_id,
    p.product_name,
    p.category,

    oi.quantity,
    oi.unit_price,

    oi.quantity * oi.unit_price AS line_total

FROM {{ ref('stg_order_items') }} AS oi

INNER JOIN {{ ref('stg_orders') }} AS o
    ON oi.order_id = o.order_id

INNER JOIN {{ ref('stg_products') }} AS p
    ON oi.product_id = p.product_id