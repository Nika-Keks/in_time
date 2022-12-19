INSERT INTO orders
(card_id, restaurant_id, status, opening)
VALUES
('{card_id}', {restaurant_id}, '{status}', '{opening}')
RETURNING id;