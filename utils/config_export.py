"""
Utility functions for exporting configuration data into various formats.

This module provides functions to render a CLI configuration from a
structured data model using Jinja2 templates, and to serialise the
same data to JSON and YAML for programmatic consumption.
"""

from __future__ import annotations

import json
import yaml
import os
from typing import Tuple, Dict, Any
from jinja2 import Environment, FileSystemLoader

# Determine path to the templates directory relative to this file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

# Map platforms to specific CLI template filenames
PLATFORM_TEMPLATES = {
    'ios': 'ios_config.j2',
    'nxos': 'nxos_config.j2',
    'asa': 'asa_config.j2',
}


def render_cli_config(platform: str, config: Dict[str, Any]) -> str:
    """Render CLI configuration for the given platform.

    Args:
        platform: One of the supported platforms (ios, nxos, asa).
        config: Structured configuration data model.

    Returns:
        String containing the rendered CLI configuration.
    """
    # Ensure we have a valid template mapping; default to IOS if unknown
    template_file = PLATFORM_TEMPLATES.get(platform, PLATFORM_TEMPLATES['ios'])
    # Create Jinja2 environment each call (thread‑safe).  Autoescape is
    # disabled because CLI syntax is not HTML.
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=False, trim_blocks=True, lstrip_blocks=True)
    template = env.get_template(template_file)
    return template.render(config=config)


def serialize_config(config: Dict[str, Any]) -> Tuple[str, str]:
    """Serialise configuration data to JSON and YAML strings.

    Args:
        config: The structured configuration data model.

    Returns:
        A tuple of two strings: (JSON, YAML).
    """
    json_output = json.dumps(config, indent=2)
    yaml_output = yaml.dump(config, sort_keys=False, default_flow_style=False)
    return json_output, yaml_output