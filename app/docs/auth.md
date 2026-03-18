# app/auth/ — Authentication Blueprint

## Purpose
Handles all user authentication: login, logout, registration, and password reset. Mounted at `/auth`.

---

## routes.py

### `GET/POST /auth/login`
- Redirects to index if already authenticated
- Validates `LoginForm`, queries user by username, checks password hash
- Calls `login_user(user, remember=...)` to set the session cookie
- Handles safe redirect: checks `next` query parameter but rejects external URLs (`urlsplit(next_page).netloc != ''`) to prevent open redirect attacks

### `GET /auth/logout`
Calls `logout_user()` and redirects to index.

### `GET/POST /auth/register`
Creates a new `User`, calls `set_password()` to hash before storing, commits, redirects to login.

### `GET/POST /auth/reset_password_request`
Looks up user by email. If found, calls `send_password_reset_email()`. Always flashes the same message regardless of whether the email exists (prevents user enumeration).

### `GET/POST /auth/reset_password/<token>`
Calls `User.verify_reset_password_token(token)` to decode the JWT and load the user. If valid, shows the reset form and calls `set_password()` on submit.

---

## forms.py

### `LoginForm`
Fields: `username`, `password`, `remember_me`.

### `RegistrationForm`
Fields: `username`, `email`, `password`, `password2`. Custom validators `validate_username` and `validate_email` query the database to enforce uniqueness.

### `ResetPasswordRequestForm`
Single `email` field.

### `ResetPasswordForm`
Fields: `password`, `password2` with `EqualTo` validator to confirm they match.

---

## email.py

### `send_password_reset_email(user)`
Generates a JWT reset token via `user.get_reset_password_token()` and calls `send_email()` with both a plain-text and HTML version of the reset email rendered from templates.
