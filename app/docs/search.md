# app/search.py — Elasticsearch Adapter

## Purpose
A thin abstraction layer between the app and Elasticsearch. All direct Elasticsearch calls are isolated here so the rest of the app never imports from the `elasticsearch` library directly.

## Functions

### `add_to_index(index, model)`
Indexes a model instance into Elasticsearch. Iterates over `model.__searchable__` to build the document payload, then calls `elasticsearch.index()` with the table name as the index name and the model's `id` as the document ID. Silently returns if `app.elasticsearch` is `None`.

### `remove_from_index(index, model)`
Deletes a document from the Elasticsearch index by model ID. Silently returns if Elasticsearch is not configured.

### `query_index(index, query, page, per_page)`
Runs a `multi_match` search against all fields (`'fields': ['*']`) with pagination (`from_` and `size`). Returns a tuple of `(list_of_ids, total_count)`. Returns `([], 0)` if Elasticsearch is not configured or if an error occurs.

## Design Decision
Returning only IDs (not full documents) keeps Elasticsearch as a search engine only — full model data stays in the relational database. The caller is responsible for fetching the actual objects by ID from SQLAlchemy.
