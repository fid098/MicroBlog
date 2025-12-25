from flask import current_app

def add_to_index(index, model):
    #this function adds a model instance to the specified Elasticsearch index
    if not current_app.elasticsearch:
        return
    payload = {} #this will hold the data to be indexed
    for field in model.__searchable__:
        payload[field] = getattr(model, field) #get the value of each searchable field from the model instance
    current_app.elasticsearch.index(index=index, id=model.id, document=payload) #index the document in Elasticsearch

def remove_from_index(index, model):
    #this function removes a model instance from the specified Elasticsearch index
    if not current_app.elasticsearch:
        return
    current_app.elasticsearch.delete(index=index, id=model.id) #delete the document from Elasticsearch

def query_index(index, query, page, per_page):
    #this function performs a search query on the specified Elasticsearch index
    if not current_app.elasticsearch:
        return [], 0 #if Elasticsearch is not configured, return empty results
    search = current_app.elasticsearch.search(
        index=index,
        query={
            'multi_match': {'query': query, 'fields': ['*']}
        }#search query to match the query string against all fields
        ,from_=(page - 1) * per_page, #pagination: starting point
        size=per_page #number of results to return
)
    res = search.body
    ids = [int(hit['_id']) for hit in res['hits']['hits']] #extract the IDs of the matching documents using comprehension which iterates over the search hits and collects the _id field from each hit
    total = res['hits']['total']['value'] #get the total number of matches
    return ids, total
