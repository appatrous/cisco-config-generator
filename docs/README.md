# Cisco Configuration Generator

This project is a comprehensive offline web application that guides network engineers in creating configuration files for Cisco IOS, NX‑OS and ASA devices.  Using an intuitive web interface, you select a platform, fill out feature‑specific sections (routing, VLANs, AAA, etc.) and generate ready‑to‑apply CLI configuration as well as machine‑readable JSON and YAML representations.

The application runs completely locally.  All code, assets and templates are bundled in the repository, so there are no external dependencies or CDN requests when serving the interface.  This makes the tool suitable for use in air‑gapped or secure environments where internet access is restricted.

## Features

* **Platform selection** – choose between IOS, NX‑OS and ASA device families.
* **Layer 3 routing** – define static routes and OSPF process parameters.
* **Layer 2** – configure VLAN IDs with optional names.
* **NTP servers** – specify one or more time sources.
* **AAA** – enable TACACS+ and/or RADIUS servers and add local user accounts.
* **Extensible architecture** – modular directory layout supports adding new configuration sections, partial templates, form definitions and validation logic.
* **REST API** – programmatic access via `/api/generate` endpoint (JSON in, JSON/YAML/CLI out).

## Project structure

The root folder `cisco-config-generator` contains:

```
app.py               # Flask application factory and route definitions
config.py            # Global settings
requirements.txt     # Python dependencies (Flask, PyYAML)
templates/           # HTML and Jinja2 templates for the UI and configs
static/              # Local static assets (CSS, JS, images)
config_templates/    # Modular Jinja2 fragments for config generation
forms/               # (Optional) Python form definitions / data classes
utils/               # Helper modules (rendering, validation, parsing)
extensions/          # Blueprints for API, history, authentication
tests/               # Unit tests
docs/                # Project documentation
```

See `architecture.md` for a detailed breakdown of each component and how they interact.

## Getting started

1. **Install dependencies**: Use a Python environment with the packages listed in `requirements.txt`.  For example:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Run the application**:

   ```bash
   python app.py
   ```

   By default the app listens on `127.0.0.1:5000`.  Point your browser to this address to access the form.

3. **Fill out the form**: Choose a platform, add your routing, VLANs, NTP and AAA settings and submit.  The tool will render the configuration and display CLI, JSON and YAML outputs.

4. **Use the API**: POST JSON to `/api/generate` with your configuration model to receive CLI/JSON/YAML in the response.  See `api_spec.md` for details.

## Running with Docker

If you prefer to package the application and its dependencies into a container, a `Dockerfile` is provided at the project root.  Building and running the image will give you a self‑contained environment with the Flask server listening on port 5000.

To build the image (tagging it as `cisco-config-generator`):

```bash
docker build -t cisco-config-generator .
```

Once the image is built, run a container and map port 5000 on your host to the container’s port 5000:

```bash
docker run -p 5000:5000 cisco-config-generator
```

The web interface will be available at `http://localhost:5000`.  Because all static assets and dependencies are included in the image, no internet access is required inside the container.

## Contributing

This repository lays the groundwork for a powerful configuration generator.  Contributions are welcome!  To add a new feature:

1. Create or extend form fields in `templates/index.html` and/or a WTForms class under `forms/`.
2. Update `app.py` to parse the new inputs into the structured `config_data` dictionary.
3. Add or modify Jinja2 templates under `templates/` or `config_templates/` to render your new feature’s CLI.
4. Write validation rules in `utils/validators.py` and unit tests in `tests/`.

See `usage.md` for detailed user instructions and `architecture.md` for design insights.