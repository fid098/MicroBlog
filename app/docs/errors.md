# app/errors/ — Error Handlers Blueprint

## Purpose
Global error handlers for 404 and 500 errors. Registered with `app_errorhandler` so they apply to the entire application, not just the blueprint.

## `wants_json_response()`
Compares the client's preference for JSON vs HTML by inspecting the `Accept` header. Returns `True` if the client prefers JSON (used by API clients). This allows the same error handler to serve either an HTML error page or a JSON error response depending on who's asking.

## `not_found_error` (404)
- JSON clients → `api_error_response(404)`
- Browser clients → renders `errors/404.html`

## `internal_error` (500)
- Calls `db.session.rollback()` first to reset the database session to a clean state (500 errors are often caused by failed database operations, and a dirty session would cause every subsequent request to fail too)
- JSON clients → `api_error_response(500)`
- Browser clients → renders `errors/500.html`
