INSERT INTO clients
(phone, name)
VALUES
('{phone}', '{name}')
RETURNING id;