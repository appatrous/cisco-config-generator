# User Guide

This guide explains how to use the Cisco Configuration Generator application.  It assumes you have the project installed locally and that you are running the Flask development server via `python app.py`.

## Accessing the application

Navigate to `http://127.0.0.1:5000` in your web browser.  You will see the main form with sections for selecting the device platform and entering configuration parameters.

## Filling out the form

1. **Select platform**: Choose IOS, NX‑OS or ASA from the drop‑down menu.
2. **Static routes**: Add one or more destination networks with next hop addresses and optional administrative distance.  Click “Add Route” to create additional entries.
3. **OSPF**: Toggle “Enable OSPF” to reveal OSPF settings.  Choose the version (v2 for IPv4 or v3 for IPv6), process ID and optional router ID.  Use “Add Network” to define multiple network/area pairs.
4. **VLANs**: Provide VLAN IDs and optional names.  Click “Add VLAN” to create more entries.
5. **NTP servers**: Enter the addresses of NTP servers that your device should use.  Use the “Add NTP Server” button for multiple servers.
6. **AAA**: Toggle “Enable AAA” to configure authentication.  You can opt to use TACACS+ or RADIUS by enabling their respective switches.  Provide the server addresses for each.  Under “Local Users”, specify usernames, passwords and privilege levels.  Additional users can be added via the “Add User” button.
7. Click **Generate Configuration** to submit your inputs.

## Viewing results

After submission, you will be redirected to the results page.  The configuration is displayed in three formats:

* **CLI** – Cisco IOS/NX‑OS/ASA command‑line syntax.
* **JSON** – Structured key–value representation of your configuration.  Can be used as input to other automation tools.
* **YAML** – Human‑readable version of the configuration model.

Use the tabs to switch between these formats.  A back button returns you to the form with your previous values still populated (browser back navigation).

## Using the API

The application provides a REST endpoint at `/api/generate`.  Send a `POST` request with a JSON body that includes at least a `platform` field (``ios``, ``nxos`` or ``asa``) and any other configuration keys.  The response will contain the CLI configuration and the same model in JSON and YAML forms.

Example request via `curl`:

```bash
curl -X POST http://127.0.0.1:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "ios",
    "static_routes": [
      {"destination": "192.168.1.0/24", "next_hop": "10.0.0.1"}
    ],
    "vlans": [
      {"id": 10, "name": "Sales"}
    ]
  }'
```

The server will respond with a JSON object containing `cli`, `json` and `yaml` fields.

## Troubleshooting

* If the server does not start, ensure that the dependencies listed in `requirements.txt` are installed.
* When adding new sections, be sure to update both the form template and the back‑end parser to avoid missing or misnamed keys.
* Validation is minimal in this prototype; invalid inputs (e.g. malformed IP addresses) may result in incorrect output or device errors.  Implement stricter checks in `utils/validators.py` as needed.

## Further reading

Refer to `architecture.md` for a deep dive into the system design and `api_spec.md` for details of the REST API.