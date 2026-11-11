
SELECT
    c.customer_id,
    c.full_name,
    c.city,
    c.country,

    COUNT(o.order_id) AS total_orders,

    COUNT(
        CASE
            WHEN o.status = 'delivered' THEN o.order_id
        END
    ) AS delivered_orders,

    COALESCE(SUM(o.order_total), 0) AS total_order_amount,

    COALESCE(
        SUM(
            CASE
                WHEN o.status = 'delivered' THEN o.order_total
                ELSE 0
            END
        ),
        0
    ) AS delivered_revenue

FROM {{ ref('dim_customers') }} AS c

LEFT JOIN {{ ref('fct_orders') }} AS o
    ON c.customer_id = o.customer_id

GROUP BY
    c.customer_id,
    c.full_name,
    c.city,
    c.country
