# app/api/ — REST API Blueprint

## Purpose
A token-authenticated REST API for third-party access to user data. Mounted at `/api`. Uses `flask-httpauth` for both Basic Auth (token acquisition) and Bearer Token Auth (all other endpoints).

---

## auth.py — Authentication Handlers

Two auth schemes are configured:

### `basic_auth` (HTTPBasicAuth)
Used only for the token endpoint. `verify_password` queries the user by username and calls `user.check_password()`. Error responses go through `error_response()`.

### `token_auth` (HTTPTokenAuth)
Used on all other API routes. `verify_token` calls `User.check_token(token)` which checks the token exists and hasn't expired.

---

## tokens.py — Token Management

### `POST /api/tokens`
Protected by Basic Auth. Calls `user.get_token()` which returns the existing token if it has more than 60 seconds left, or generates a new one. Returns `{'token': token}`.

### `DELETE /api/tokens`
Protected by token auth. Calls `user.revoke_token()` which backdates `token_expiration` by 1 second, effectively invalidating it. Returns 204 No Content.

---

## users.py — User Resources

All endpoints except `POST /api/users` require token authentication.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/users/<id>` | Get a single user by ID |
| GET | `/api/users` | Get paginated list of all users |
| GET | `/api/users/<id>/followers` | Get paginated followers of a user |
| GET | `/api/users/<id>/following` | Get paginated following list of a user |
| POST | `/api/users` | Create a new user (no auth required) |
| PUT | `/api/users/<id>` | Update a user (only own account) |

`PUT /api/users/<id>` checks `token_auth.current_user().id != id` and aborts with 403 to prevent modifying other users' accounts.

All responses use `User.to_dict()` and `User.to_collection_dict()` for consistent JSON structure with hypermedia `_links`.

---

## errors.py — API Error Responses

### `error_response(status_code, message=None)`
Returns a JSON payload with an `error` key (using `werkzeug.http.HTTP_STATUS_CODES` for the description) and an optional `message` key, plus the HTTP status code.

### `bad_request(message)`
Shortcut for `error_response(400, message)`.

### `@bp.errorhandler(HTTPException)`
Catches all unhandled HTTP exceptions within the API blueprint and converts them to JSON error responses instead of HTML.
