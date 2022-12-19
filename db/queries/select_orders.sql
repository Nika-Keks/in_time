SELECT * FROM orders
WHERE card_id IN (
    SELECT id FROM cards
    WHERE client_id = 1
);
