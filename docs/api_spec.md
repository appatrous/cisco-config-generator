# API Specification

This document describes the REST API exposed by the Cisco Configuration Generator.  The API allows external tools or scripts to request configuration generation programmatically.  It is intended for integration with CI/CD pipelines or other automation systems.

## Base URL

Assuming the Flask server is running locally on the default port:

```
http://127.0.0.1:5000/api
```

## Endpoints

### POST `/generate`

Generate configuration based on the provided JSON payload.

#### Request

* **Method:** `POST`
* **Headers:** `Content-Type: application/json`
* **Body:** A JSON object containing at least a `platform` key.  All other keys correspond to fields from the web form.  There is no strict schema; unrecognised keys are passed through to templates.

Example:

```json
{
  "platform": "nxos",
  "vlans": [
    {"id": 20, "name": "Servers"},
    {"id": 30}
  ],
  "ntp_servers": ["192.0.2.1", "192.0.2.2"],
  "aaa": {
    "use_tacacs": true,
    "tacacs_servers": ["10.0.0.10"],
    "use_radius": false,
    "local_users": [
      {"username": "admin", "password": "P@ssw0rd", "privilege": "15"}
    ]
  }
}
```

#### Response

* **Status:** `200 OK` on success, `400 Bad Request` if the request is invalid (e.g. missing JSON body).
* **Body:** A JSON object with three fields:

  * `cli` – The generated device configuration in CLI syntax.
  * `json` – The structured configuration model in JSON format.
  * `yaml` – The same model in YAML format.

Example response:

```json
{
  "cli": "... IOS/NX-OS/ASA commands ...",
  "json": "{\n  \"platform\": \"nxos\", ... }",
  "yaml": "platform: nxos\n..."
}
```

#### Errors

* `400` – Returned when the `Content-Type` is not `application/json` or the payload cannot be parsed.

## Notes

* The API returns the JSON and YAML outputs as **strings** inside a JSON object.  To use these programmatically, you may need to parse them a second time.
* Unused or unknown keys in the request are ignored by the current templates.  Implement additional validation for strict schema enforcement.
* Authentication and rate limiting are not implemented in this prototype.  If exposing the API beyond local use, consider adding authentication (see `extensions/authentication.py`).