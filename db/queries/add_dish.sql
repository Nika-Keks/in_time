INSERT INTO dishes
(name, restaurant_id, description, status, price)
VALUES
('{name}', {restaurant_id}, '{description}', '{status}', {price})
RETURNING id;