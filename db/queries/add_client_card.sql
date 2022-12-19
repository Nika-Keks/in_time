INSERT INTO cards
(client_id, number)
VALUES
({client_id}, '{number}')
RETURNING id;