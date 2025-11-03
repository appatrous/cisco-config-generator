"""Utilities for validating and normalising API payloads."""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

from config import SUPPORTED_PLATFORMS
from utils.validators import is_valid_ipv4, is_valid_ipv4_network, is_valid_vlan_id

_TRUE_VALUES = {"1", "true", "yes", "on", "enable", "enabled"}


def _as_bool(value: Any) -> bool:
    """Normalise a loosely-typed boolean value."""
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if isinstance(value, str):
        return value.strip().lower() in _TRUE_VALUES
    return False


def _coerce_int(value: Any) -> Tuple[bool, int | None]:
    """Attempt to coerce a value to ``int``. Returns ``(success, int)``."""
    if value in (None, ""):
        return True, None
    try:
        return True, int(value)
    except (TypeError, ValueError):
        return False, None


def validate_api_payload(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """Validate and normalise payload received by the REST API.

    Returns a tuple ``(sanitised_payload, errors)``.  When ``errors`` is
    non-empty the caller should not proceed with generation and instead
    return the aggregated error messages to the client.
    """

    errors: List[str] = []
    sanitised: Dict[str, Any] = {
        "platform": "ios",
        "static_routes": [],
        "ospf": None,
        "vlans": [],
        "ntp_servers": [],
        "aaa": None,
    }

    # Platform validation
    platform = str(data.get("platform", "ios")).lower()
    if platform not in SUPPORTED_PLATFORMS:
        errors.append(
            f"Unsupported platform '{platform}'. Supported platforms: {', '.join(SUPPORTED_PLATFORMS)}."
        )
    else:
        sanitised["platform"] = platform

    # Static routes
    static_routes = data.get("static_routes", []) or []
    if not isinstance(static_routes, list):
        errors.append("'static_routes' must be a list of objects.")
    else:
        for index, route in enumerate(static_routes, start=1):
            if not isinstance(route, dict):
                errors.append(f"Static route #{index} must be an object with destination/next_hop keys.")
                continue
            destination = route.get("destination")
            next_hop = route.get("next_hop")
            distance = route.get("distance")

            if not destination or not is_valid_ipv4_network(str(destination)):
                errors.append(f"Static route #{index} has invalid destination '{destination}'. Use IPv4 CIDR notation.")
                continue
            if not next_hop or not is_valid_ipv4(str(next_hop)):
                errors.append(f"Static route #{index} has invalid next hop '{next_hop}'.")
                continue

            ok, distance_value = _coerce_int(distance)
            if not ok or (distance_value is not None and not 1 <= distance_value <= 255):
                errors.append(f"Static route #{index} has invalid administrative distance '{distance}'.")
                continue

            sanitised["static_routes"].append(
                {
                    "destination": str(destination),
                    "next_hop": str(next_hop),
                    "distance": distance_value,
                }
            )

    # VLANs
    vlans = data.get("vlans", []) or []
    if not isinstance(vlans, list):
        errors.append("'vlans' must be a list of objects.")
    else:
        for index, vlan in enumerate(vlans, start=1):
            if not isinstance(vlan, dict):
                errors.append(f"VLAN #{index} must be an object with 'id' and optional 'name'.")
                continue
            ok, vlan_id = _coerce_int(vlan.get("id"))
            if not ok or vlan_id is None or not is_valid_vlan_id(vlan_id):
                errors.append(f"VLAN #{index} has invalid ID '{vlan.get('id')}'. Use a value between 1 and 4094.")
                continue
            name = vlan.get("name") or None
            sanitised["vlans"].append({"id": vlan_id, "name": name})

    # NTP servers
    ntp_servers = data.get("ntp_servers", []) or []
    if not isinstance(ntp_servers, list):
        errors.append("'ntp_servers' must be a list of IPv4 addresses.")
    else:
        for index, server in enumerate(ntp_servers, start=1):
            if not server:
                continue
            if not isinstance(server, str) or not is_valid_ipv4(server):
                errors.append(f"NTP server #{index} has invalid address '{server}'.")
                continue
            sanitised["ntp_servers"].append(server)

    # OSPF
    ospf = data.get("ospf")
    if ospf:
        if not isinstance(ospf, dict):
            errors.append("'ospf' section must be an object.")
        else:
            version = str(ospf.get("version", "v2")).lower()
            if version not in {"v2", "v3"}:
                errors.append(f"OSPF version '{version}' is not supported. Use 'v2' or 'v3'.")
                version = "v2"
            ok, process_id = _coerce_int(ospf.get("process_id"))
            if not ok or process_id is None or process_id <= 0:
                errors.append("OSPF process_id must be a positive integer.")
                process_id = None
            router_id = ospf.get("router_id") or None
            if router_id and not is_valid_ipv4(str(router_id)):
                errors.append(f"OSPF router_id '{router_id}' must be a valid IPv4 address.")
                router_id = None
            networks_data = ospf.get("networks", []) or []
            networks: List[Dict[str, Any]] = []
            if not isinstance(networks_data, list):
                errors.append("OSPF networks must be provided as a list.")
            else:
                for index, entry in enumerate(networks_data, start=1):
                    if not isinstance(entry, dict):
                        errors.append(f"OSPF network #{index} must be an object with 'network' and 'area'.")
                        continue
                    network = entry.get("network")
                    area = entry.get("area", "0")
                    if not network or not is_valid_ipv4_network(str(network)):
                        errors.append(f"OSPF network #{index} has invalid prefix '{network}'.")
                        continue
                    networks.append({"network": str(network), "area": str(area)})

            if process_id is not None and networks:
                sanitised["ospf"] = {
                    "version": version,
                    "process_id": process_id,
                    "router_id": router_id,
                    "networks": networks,
                }
            else:
                errors.append("OSPF section must include a valid process_id and at least one network.")

    # AAA
    aaa = data.get("aaa")
    if aaa:
        if not isinstance(aaa, dict):
            errors.append("'aaa' section must be an object.")
        else:
            use_tacacs = _as_bool(aaa.get("use_tacacs"))
            tacacs_input = aaa.get("tacacs_servers", []) or []
            tacacs_servers: List[str] = []
            if not isinstance(tacacs_input, list):
                errors.append("'tacacs_servers' must be a list of IPv4 addresses.")
            else:
                for index, server in enumerate(tacacs_input, start=1):
                    if not server:
                        continue
                    if not isinstance(server, str) or not is_valid_ipv4(server):
                        errors.append(f"TACACS+ server #{index} has invalid address '{server}'.")
                        continue
                    tacacs_servers.append(server)
            if use_tacacs and not tacacs_servers:
                errors.append("AAA configuration enables TACACS+ but no valid servers were provided.")

            use_radius = _as_bool(aaa.get("use_radius"))
            radius_input = aaa.get("radius_servers", []) or []
            radius_servers: List[str] = []
            if not isinstance(radius_input, list):
                errors.append("'radius_servers' must be a list of IPv4 addresses.")
            else:
                for index, server in enumerate(radius_input, start=1):
                    if not server:
                        continue
                    if not isinstance(server, str) or not is_valid_ipv4(server):
                        errors.append(f"RADIUS server #{index} has invalid address '{server}'.")
                        continue
                    radius_servers.append(server)
            if use_radius and not radius_servers:
                errors.append("AAA configuration enables RADIUS but no valid servers were provided.")

            users_input = aaa.get("local_users", []) or []
            local_users: List[Dict[str, Any]] = []
            if not isinstance(users_input, list):
                errors.append("'local_users' must be a list of user objects.")
            else:
                for index, user in enumerate(users_input, start=1):
                    if not isinstance(user, dict):
                        errors.append(f"Local user #{index} must be an object with username/password.")
                        continue
                    username = user.get("username") or user.get("name")
                    password = user.get("password") or user.get("secret")
                    ok, privilege = _coerce_int(user.get("privilege", 15))
                    if not username or not password:
                        errors.append(f"Local user #{index} requires both username and password.")
                        continue
                    if not ok or privilege is None or not 0 <= privilege <= 15:
                        errors.append(f"Local user #{index} has invalid privilege '{user.get('privilege')}'.")
                        continue
                    local_users.append({
                        "username": str(username),
                        "password": str(password),
                        "privilege": privilege,
                    })

            if use_tacacs or use_radius or local_users:
                sanitised["aaa"] = {
                    "use_tacacs": use_tacacs,
                    "tacacs_servers": tacacs_servers,
                    "use_radius": use_radius,
                    "radius_servers": radius_servers,
                    "local_users": local_users,
                }

    return sanitised, errors
