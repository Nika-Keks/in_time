from sqlalchemy_serializer import SerializerMixin

from app import db, flask_app
from app.utils.serach import query_index, add_to_index, remove_from_index, get_saved_indices


class CustomSerializerMixin(SerializerMixin):
    pass


class SearchableMixin(object):
    @classmethod
    def search(cls, expression, page, per_page):
        if cls.__tablename__ not in get_saved_indices():
            cls.reindex()
        ids, total = query_index(cls.__tablename__, expression, page, per_page)
        if total == 0 or len(ids) == 0:
            return cls.query.filter_by(id=0), 0
        matched = {index: i for i, index in enumerate(ids)}
        return cls.query.filter(cls.id.in_(ids)).order_by(
            db.case(matched, value=cls.id)), total["value"]

    @classmethod
    def before_commit(cls, session):
        session._changes = {
            'add': list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted)
        }

    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None

    @classmethod
    def reindex(cls):
        for obj in cls.query:
            add_to_index(cls.__tablename__, obj)
