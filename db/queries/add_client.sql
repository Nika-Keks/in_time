INSERT INTO clients
(phone, name, password)
VALUES
('{phone}', '{name}', '{password}')
RETURNING id;