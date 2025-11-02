# Application Architecture

This document outlines the major components of the Cisco Configuration Generator and describes how they interact.  The goal is to separate concerns so that the application remains maintainable and extensible as new features are added.

## Overview

The application is built around the Flask web framework.  It serves a single‑page form to gather user inputs and uses Jinja2 templates to generate configuration snippets.  The architecture includes supporting modules for configuration export, validation, history, authentication and a REST API.

![Architecture Diagram](architecture.png)

### Key components

#### `app.py`

Contains the Flask application factory and route definitions.  It loads configuration from `config.py`, registers blueprints (such as the API) and defines the main routes:

* `/` – Renders the index page with the input form.
* `/generate` – Parses form data, constructs a configuration model, renders CLI using Jinja2 and then displays results via `templates/result.html`.

#### `config.py`

Stores global settings such as the secret key for sessions and the list of supported platforms.  Keeping configuration separate avoids hard‑coding values in multiple places.

#### Templates

The `templates/` directory contains HTML pages and Jinja2 templates:

* `base.html` – Base layout with Bootstrap and site header.  Child templates extend this.
* `index.html` – Main form page.  Uses dynamic JavaScript to add/remove form rows.
* `result.html` – Displays generated configuration with tabbed CLI/JSON/YAML views.
* `ios_config.j2`, `nxos_config.j2`, `asa_config.j2` – CLI templates for each platform.
* `_partials/form_field.j2` – Macro to render form inputs (not heavily used yet).

#### Static Assets

Located under `static/`.  Includes `css/style.css` for custom styling, placeholder files for `bootstrap.min.css` and `bootstrap.bundle.min.js`, JavaScript logic in `js/script.js` and the application logo in `img/logo.png`.

#### `config_templates/`

Holds modular fragments for configuration generation.  For example, `ios/routing.j2` can be included in other templates to generate static routes and OSPF.  These small templates make it easier to build complex device configurations by composing parts.

#### Forms (`forms/`)

Data classes and (optionally) WTForms definitions.  Currently the application uses a custom JavaScript form, but the data classes show how configuration data can be structured.  Validators could be added to ensure correctness before rendering.

#### Utils (`utils/`)

Provides helper functions for rendering configurations (`config_export.py`), validating inputs (`validators.py`), parsing values (`parsing.py`) and adding Jinja2 helper functions (`jinja_helpers.py`).  These modules encapsulate logic separate from the Flask views.

#### Extensions (`extensions/`)

Blueprints and pluggable components.  The API blueprint is implemented in `api.py`, exposing a `/api/generate` endpoint for programmatic access.  `history.py` and `authentication.py` are placeholders for future features such as storing generated configs or multi‑user support.

#### Tests

The `tests/` directory includes unit tests to exercise the rendering logic (`test_generation.py`), validators (`test_validation.py`) and data structures (`test_forms.py`).  Use pytest or unittest to run them.

#### Documentation

Documentation lives in `docs/`, providing user guides (`usage.md`), API specifications (`api_spec.md`) and this architecture description.

## Data Flow

1. The user accesses the main page (`/`) and fills out the form.
2. On submission, the form posts data to `/generate`.
3. The view function builds a nested data model representing the configuration.
4. `utils/config_export.render_cli_config()` selects the appropriate Jinja2 template based on the platform and renders CLI text.
5. `utils/config_export.serialize_config()` converts the data model to JSON and YAML.
6. The results are displayed in `result.html` and can be downloaded or copied.
7. Alternatively, the same process can be triggered via the `/api/generate` endpoint by posting JSON.

This separation of input handling, data modelling and rendering simplifies the addition of new features and ensures that templates remain declarative.