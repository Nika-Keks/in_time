import os

from flask import request, send_file
from flask_login import current_user
from flask_restx import Resource, reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app import api, flask_app
from app.models.dish import Dish
from app.models.restaurant import Restaurant
from app.utils.exceptions import ITPForbiddenError, ITPNotModified, ITPInvalidError, ok

ns = api.namespace('File', description='Operations with files stored in server: dishes images and restaurant logos')
upload_parser = reqparse.RequestParser()
upload_parser.add_argument('image', location='files', type=FileStorage, required=True)


def generate_file_path(model_prefix: str, id: int) -> str:
    return model_prefix[0] + str(id).zfill(19)


def check_file_path(path: str) -> str:
    secure_path = secure_filename(path)
    if not allowed_extension(secure_path):
        raise ValueError

    ext = '.' + secure_path.split('.')[-1] if '.' in secure_path else ""
    if len(ext) > 0:
        secure_path = secure_path[:-len(ext)]
    number = int(secure_path[1:])
    if len(secure_path) != 20 or secure_path[0] not in ["r", "d"] or str(number).zfill(19) != secure_path[1:]:
        raise ValueError
    return secure_path + ext


def extract_file_arg(args):
    if "image" not in args or args['image'].filename == '':
        raise ITPNotModified('No selected file')
    file = args['image']
    if not allowed_extension(file.filename):
        raise ITPInvalidError('Invalid file extension')
    return file, '.' + file.filename.split('.')[-1]


def save_file(file_name, file):
    save_path = os.path.abspath(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_name))
    os.makedirs(flask_app.config['UPLOAD_FOLDER'], exist_ok=True)
    file.save(save_path)


def allowed_extension(path: str):
    return '.' in path and path.split('.')[-1] in ["png", "jpeg", "jpg"]


@ns.route('/upload/dish/<int:dish_id>')
class UploadDish(Resource):
    @ns.expect(upload_parser)
    def post(self, dish_id):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()

        file, ext = extract_file_arg(request.files)
        file_path = generate_file_path("d", dish_id) + ext

        dish = Dish.query.filter_by(id=dish_id).first_or_404(description=f"Dish with id {dish_id} was not found")
        if Restaurant.query.filter_by(user_id=current_user.id, id=dish.restaurant_id).first() is None:
            raise ITPForbiddenError()

        try:
            Dish.update(dish_id, image_path=file_path)
        except ValueError:
            raise ITPInvalidError()

        save_file(file_path, file)
        return dish.to_dict(), ok


@ns.route('/upload/restaurant/<int:rest_id>')
class UploadRestaurant(Resource):
    @ns.expect(upload_parser)
    def post(self, rest_id):
        if not current_user.is_authenticated or current_user.is_anonymous or\
                Restaurant.query.filter_by(user_id=current_user.id).first() is None:
            raise ITPForbiddenError()

        file, ext = extract_file_arg(request.files)
        file_path = generate_file_path("r", rest_id) + ext

        rest = Restaurant.query.filter_by(id=rest_id).first_or_404(description=f"Restaurant with id {rest_id} was not "
                                                                               f"found")
        try:
            Restaurant.update(rest_id, image_path=file_path)
        except ValueError:
            raise ITPInvalidError()
        save_file(file_path, file)
        return rest.to_dict(), ok


@ns.route('/load/<file_path>')
class Load(Resource):
    def get(self, file_path):
        if not current_user.is_authenticated or current_user.is_anonymous:
            raise ITPForbiddenError()
        try:
            secure_path = check_file_path(file_path)
        except ValueError:
            raise ITPInvalidError("invalid file path")
        full_path = os.path.abspath(os.path.join(flask_app.config['UPLOAD_FOLDER'], secure_path))
        if not os.path.exists(full_path):
            raise ITPInvalidError("file does not exist")
        return send_file(full_path)
