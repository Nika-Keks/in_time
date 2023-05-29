from app import flask_app


def get_saved_indices():
    try:
        return set(flask_app.elasticsearch.indices.get_alias("*"))
    except Exception:
        return set()


def add_to_index(index, model):
    try:
        payload = {}
        for field in model.__searchable__:
            payload[field] = getattr(model, field)
        flask_app.elasticsearch.index(index=index, doc_type=index, id=model.id,
                                      body=payload)
    except Exception:
        pass


def remove_from_index(index, model):
    try:
        flask_app.elasticsearch.delete(index=index, doc_type=index, id=model.id)
    except Exception:
        pass


def query_index(index, query, page, per_page):
    try:
        if query[0] != '*':
            query = '*' + query
        if query[-1] != '*':
            query = query + '*'

        search = flask_app.elasticsearch.search(
            index=index, doc_type=index,
            body={'query': {'query_string': {'query': query, 'fields': ['*']}},
                  'from': (page - 1) * per_page, 'size': per_page})
        ids = [int(hit['_id']) for hit in search['hits']['hits']]
        return ids, search['hits']['total']
    except Exception:
        return [], 0

