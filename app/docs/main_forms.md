# app/main/forms.py — Main Blueprint Forms

## Purpose
WTForms form classes used by the main blueprint routes.

## Forms

### `SearchForm`
Single field `q` for the search query. Two important customisations in `__init__`:
- `formdata=request.args` — reads form data from URL query parameters instead of the POST body, since search is submitted as a GET request
- `meta={'csrf': False}` — CSRF protection is disabled because the search query is in the URL and safe to submit repeatedly

### `EditProfileForm`
Fields: `username`, `about_me`. Custom `validate_username()` method checks if the new username is already taken — but only if it differs from the user's current username (to allow saving without changing it).

### `EmptyForm`
No fields, just a submit button. Used anywhere a CSRF-protected action needs a form (follow, unfollow, delete) without displaying any input fields.

### `PostForm`
Single `TextAreaField` for post body. Validated for `DataRequired` and max 140 characters.

### `MessageForm`
Single `TextAreaField` for message body. Max 140 characters.
