-- Active: 1671262384862@@127.0.0.1@5432@intime

CREATE TABLE IF NOT EXISTS restaurants
(
    id INTEGER GENERATED ALWAYS AS IDENTITY,
    name TEXT,
    position TEXT,
    description TEXT,
    phone TEXT,
    password TEXT,
    wday_opening TIME,
    wday_closing TIME,
    wend_opening TIME,
    wend_closing TIME,

    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS dishes
(
    id INTEGER GENERATED ALWAYS AS IDENTITY,
    restaurant_id INTEGER,
    name TEXT,
    description TEXT,
    status TEXT,
    price INTEGER,

    CONSTRAINT fk_restaurant_id_dishes
    FOREIGN KEY (restaurant_id)
    REFERENCES restaurants(id),

    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS clients
(
    id INTEGER GENERATED ALWAYS AS IDENTITY,
    phone TEXT,
    password TEXT,
    name TEXT,

    PRIMARY KEY (id)

);
CREATE TABLE IF NOT EXISTS cards
(
    id INTEGER GENERATED ALWAYS AS IDENTITY,
    client_id INTEGER,
    number TEXT,

    CONSTRAINT fk_owner_cards
    FOREIGN KEY (client_id)
    REFERENCES clients(id),

    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS orders
(
    id INTEGER GENERATED ALWAYS AS IDENTITY,
    card_id INTEGER,
    restaurant_id INTEGER,
    status TEXT,
    opening TIME,
    cooking TIME,
    closing TIME,

    CONSTRAINT fk_card_id_orders
    FOREIGN KEY (card_id)
    REFERENCES cards(id),

    CONSTRAINT fk_restaurant_id_orders
    FOREIGN KEY (restaurant_id)
    REFERENCES restaurants(id),

    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS order_dishes
(
    dishe_id INTEGER,
    order_id INTEGER,
    num INTEGER,

    CONSTRAINT fk_dishe_id_order_dishes
    FOREIGN KEY (dishe_id)
    REFERENCES dishes(id),

    CONSTRAINT fk_order_id_order_dishes
    FOREIGN KEY (order_id)
    REFERENCES orders(id),

    PRIMARY KEY (dishe_id, order_id)
);