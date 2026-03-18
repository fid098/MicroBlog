# app/cli.py — Translation CLI Commands

## Purpose
Registers custom Flask CLI commands for managing Babel translations. Commands are grouped under `flask translate`.

## Commands

### `flask translate init <lang>`
Initialises a new language for the app.
1. Runs `pybabel extract` to scan the source code for translatable strings and write them to `messages.pot`
2. Runs `pybabel init` to create a new `.po` file for the specified language in `app/translations/<lang>/`
3. Deletes the temporary `messages.pot` file

### `flask translate update`
Updates all existing language `.po` files when new translatable strings have been added to the source code.
1. Extracts all current translatable strings to `messages.pot`
2. Merges new strings into all existing `.po` files
3. Deletes `messages.pot`

### `flask translate compile`
Compiles all `.po` files into binary `.mo` files that Flask-Babel reads at runtime. Must be run after any `.po` file is edited.

## Implementation Detail
The blueprint uses `cli_group=None` which merges the commands directly into the `flask` CLI namespace rather than creating a sub-group, so the commands are accessed as `flask translate <command>` rather than `flask cli translate <command>`.
