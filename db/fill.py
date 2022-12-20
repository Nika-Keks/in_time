import psycopg2 as postgres
import collections


class QueruesExecuret:

    def __init__(self) -> None:
        self.conn = postgres.connect(
            user="admin",
            password="qwer",
            host="localhost",
            dbname="intime"
            )

        self.files = "./../queries"


    def exec(self, file: str, args: dict):
        with open(file, "r") as f:
            query = f.read()
        cursor = self.conn.cursor()
        cursor.execute(query.format(**args))
        try:
            out = list(cursor)
        except Exception:
            out = []
        cursor.close()

        return out
    
    def add_restaurant(self, restaurant_data: dict):
        out = self.exec("./db/queries/add_restaurant.sql", restaurant_data)
        self.conn.commit()
        
        return out

    def add_client(self, client_data: dict):
        out = self.exec("./db/queries/add_client.sql", client_data)
        self.conn.commit()

        return out

    def add_dish(self, dish_data: dict):
        out = self.exec("./db/queries/add_dish.sql", dish_data)
        self.conn.commit()

        return out

    def add_order(self, order_data: dict, dish_ids: list):
        order_id = self.exec("./db/queries/add_order.sql", order_data)[0][0]
        for dish_id, count in collections.Counter(dish_ids).items():
            self.exec("./db/queries/add_order_dish.sql", {
                "dish_id": dish_id,
                "order_id": order_id,
                "num": count
            })
        self.conn.commit()
        return [(order_id,)]

    def add_client_card(self, card_data: dict):
        out = self.exec("./db/queries/add_client_card.sql", card_data)
        self.conn.commit()

        return out


restaurants = {
    "args": {},
    "data": {
        "name": ["welocom", "gogo", "super food"],
        "position": ["0", "0", "0"],
        "description": ["0", "0", "0"],
        "phone": ["112", "991", "666"],
        "password": ["123", "234", "343"],
        "wday_opening": ["00:00:00", "00:00:00", "00:00:00"],
        "wday_closing": ["00:00:00", "00:00:00", "00:00:00"],
        "wend_opening": ["00:00:00", "00:00:00", "00:00:00"],
        "wend_closing": ["00:00:00", "00:00:00", "00:00:00"]
    }
}

clients = {
    "args": {},
    "data": {
        "name": ["Nika", "Ura", "Slava"],
        "phone": ["333", "555", "555"],
        "password": ["123", "234", "343"]
    }
}

dishes = {
    "args": {},
    "data": {
        "name": ["шаверма", "суп", "гречка"],
        "description": ["sdesf", "nvgbxftbf", "gxfgf"],
        "status": ["active", "active", "active"],
        "restaurant_id": [2, 2, 3],
        "price": [12, 13, 100]
    }
}

cards = {
    "args": {},
    "data": {
        "client_id": [1, 2, 3],
        "number": ["0000", "0001", "0002"]
    }
}

orders = {
    "args": {"dish_ids": [[1, 1], [2]]},
    "data": {
        "card_id": [1, 2],
        "restaurant_id": [2, 2],
        "status": ["closed", "closed"],
        "opening": ["00:00:00", "00:00:00"],
        # "cooking": ["00:00:00", "00:00:00"],
        # "closing": ["00:00:00", "00:00:00"]
    }
}

def any_call(call_back, qdata: dict, n: int):
    args = qdata["args"]
    data = qdata["data"]
    for i in range(n):
        args_dict = {k: v[i] for k, v in data.items()}
        argsi = {k: v[i] for k, v in args.items()}
        call_back(args_dict, **argsi)

if __name__ == "__main__":
    ex = QueruesExecuret()
    
    any_call(ex.add_restaurant, restaurants, 3)
    any_call(ex.add_dish, dishes, 3)
    any_call(ex.add_client, clients, 3)
    any_call(ex.add_client_card, cards, 3)
    any_call(ex.add_order, orders, 2)
    
    ex.conn.close()