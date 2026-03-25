from flask import current_app


def add_to_index(index, model):
    if not current_app.elasticsearch:
        return
    payload = {}
    for field in model.__searchable__:
        payload[field] = getattr(model, field)
    try:
        current_app.elasticsearch.index(index=index, id=model.id, document=payload)
    except Exception as e:
        current_app.logger.exception(f"Error indexing document {model.id} in Elasticsearch: {e}")


def remove_from_index(index, model):
    if not current_app.elasticsearch:
        return
    try:
        current_app.elasticsearch.delete(index=index, id=model.id)
    except Exception as e:
        current_app.logger.exception(f"Error removing document {model.id} from Elasticsearch: {e}")


def query_index(index, query, page, per_page):
    if not current_app.elasticsearch:
        return [], 0
    try:
        search = current_app.elasticsearch.search(
            index=index,
            query={'multi_match': {'query': query, 'fields': ['*']}},
            from_=(page - 1) * per_page,
            size=per_page
        )
    except Exception as e:
        current_app.logger.exception(f"Error querying Elasticsearch: {e}")
        return [], 0
    res = search.body
    ids = [int(hit['_id']) for hit in res['hits']['hits']]
    total = res['hits']['total']['value']
    return ids, total
