SELECT dishes.name, order_dishes.num, order_dishes.num * dishes.price AS sum_price FROM order_dishes
JOIN dishes
ON dishes.id = order_dishes.dishe_id
WHERE order_id = 1;