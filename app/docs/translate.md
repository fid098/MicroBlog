# app/translate.py — Microsoft Translator Integration

## Purpose
Provides a single `translate()` function that calls the Microsoft Cognitive Translator API to translate post text on demand.

## `translate(text, source_language, dest_language)`

### Authentication
Uses two config values set in `.flaskenv`:
- `MS_TRANSLATOR_KEY` — the API subscription key
- `MS_TRANSLATOR_REGION` — the Azure region (e.g. `ukwest`)

Both are passed as HTTP headers (`Ocp-Apim-Subscription-Key` and `Ocp-Apim-Subscription-Region`).

### Language Normalisation
Language codes from Flask-Babel come in formats like `en_US` or `es_ES`. The function strips the region suffix (`split("_")[0]`) before passing to the API since Microsoft Translator expects simple codes like `en` or `es`.

### Request
A POST request is made to the Microsoft Translator v3 endpoint with a JSON body of `[{'Text': text}]`.

### Response
The API returns a nested JSON structure. The translated string is extracted at `r.json()[0]['translations'][0]['text']`.

### Error Handling
- Returns a user-visible error string if `MS_TRANSLATOR_KEY` is not configured
- Returns a user-visible error string if the API returns a non-200 status code
- No exceptions are raised — errors surface as translated error messages in the UI

## How it's called
The `/translate` route in `main/routes.py` receives an AJAX POST request from the browser with `text`, `source_language`, and `dest_language`, calls this function, and returns the result as JSON. The entire flow is synchronous — no background processing needed.
