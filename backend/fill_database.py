import json
import os
import shutil
from collections import defaultdict
from pathlib import Path

from werkzeug.security import generate_password_hash

from app import db, flask_app
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.dish import Dish
from app.models.order import Order
from app.routes.file_route import generate_file_path
from app.models.order_dishes import OrderDishes

IMAGES_DIR = Path(__file__).parent.parent.absolute()

def create_user(user_info: dict) -> User:
    new_user = User(email=user_info["email"], name=user_info["name"],
                    password=generate_password_hash(user_info["password"], method='sha256'))
    db.session.add(new_user)
    db.session.commit()
    return new_user


def create_restaurant(user: User, restaurant_info: dict) -> Restaurant:
    rest_image_path = restaurant_info.get("image_path")
    if "image_path" in restaurant_info.keys():
        del restaurant_info["image_path"]
    new_rest = Restaurant(user_id=user.id, **restaurant_info)
    db.session.add(new_rest)
    db.session.commit()

    if rest_image_path:
        try:
            ext = '.' + rest_image_path.split('.')[-1]
            file_path = generate_file_path("r", new_rest.id) + ext

            save_path = os.path.abspath(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_path))
            os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
            source_path = os.path.join(IMAGES_DIR, rest_image_path)
            shutil.copy(source_path, save_path)

            Restaurant.update(new_rest.id, image_path=file_path)
        except Exception:
            pass
    return new_rest


def create_dish(restaurant: Restaurant, dish_info: dict) -> Dish:
    dish_image_path = dish_info.get("image_path")
    if "image_path" in dish_info.keys():
        del dish_info["image_path"]
    new_dish = Dish(restaurant_id=restaurant.id, **dish_info)
    db.session.add(new_dish)
    db.session.commit()

    if dish_image_path:
        try:
            ext = '.' + dish_image_path.split('.')[-1]
            file_path = generate_file_path("d", new_dish.id) + ext

            save_path = os.path.abspath(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_path))
            os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
            source_path = os.path.join(IMAGES_DIR, dish_image_path)
            shutil.copy(source_path, save_path)

            Dish.update(new_dish.id, image_path=file_path)
        except Exception:
            pass
    return new_dish


def create_orders(user: User, order_info: dict, created_restaurants_dishes: dict):
    rest_user = User.query.filter_by(email=order_info["restaurant_email"]).first()
    order_restaurant = Restaurant.query.filter_by(user_id=rest_user.id).first()

    order_dishes = order_info["dishes"]
    del order_info["restaurant_email"]
    del order_info["dishes"]

    new_order = Order(card_id=user.id, restaurant_id=order_restaurant.id, **order_info)
    db.session.add(new_order)
    db.session.commit()

    for dish_info in order_dishes:
        cur_dish = created_restaurants_dishes[order_restaurant.id][dish_info["dish_idx"]]
        new_order_dish = OrderDishes(order_id=new_order.id, dish_id=cur_dish.id, number=dish_info["count"])
        db.session.add(new_order_dish)
        db.session.commit()


def fill_db(data: dict):
    created_restaurants_dishes = defaultdict(list)
    for init_rest_info in data["restaurants"]:
        new_user = create_user(init_rest_info["user_info"])
        new_rest = create_restaurant(new_user, init_rest_info["rest_info"])

        for dish_info in init_rest_info["dishes"]:
            new_dish = create_dish(new_rest, dish_info)
            created_restaurants_dishes[new_rest.id].append(new_dish)

    for init_client_info in data["clients"]:
        new_user = create_user(init_client_info["user_info"])

        for order_info in init_client_info["orders"]:
            create_orders(new_user, order_info, created_restaurants_dishes)


if __name__ == "__main__":
    with open("demo_data.json", "r") as f:
        data = json.load(f)
    with flask_app.app_context():
        fill_db(data)
