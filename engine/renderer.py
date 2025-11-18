"""
Network Configuration Renderer Engine
Handles template rendering for multi-vendor network configurations
"""

import os
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import yaml
import json
from jinja2 import Environment, FileSystemLoader, ChainableUndefined, Template
from jinja2.exceptions import TemplateError, UndefinedError

class ConfigRenderer:
    """Main configuration renderer engine"""

    SUPPORTED_VENDORS = ['ios', 'nxos', 'eos', 'junos', 'frr', 'huawei']

    def __init__(self, templates_dir: str = 'config_templates'):
        """
        Initialize the renderer with template directory

        Args:
            templates_dir: Path to templates directory
        """
        self.templates_dir = Path(templates_dir)
        self.environments = {}

        # Create Jinja2 environments for each vendor
        for vendor in self.SUPPORTED_VENDORS:
            vendor_path = self.templates_dir / vendor
            if vendor_path.exists():
                env = Environment(
                    loader=FileSystemLoader(str(vendor_path)),
                    undefined=ChainableUndefined,  # Chainable mode - undefined vars return empty, allow chaining
                    trim_blocks=True,
                    lstrip_blocks=True,
                    keep_trailing_newline=True
                )
                # Add custom filters
                self._add_custom_filters(env)
                self.environments[vendor] = env

    def _add_custom_filters(self, env: Environment):
        """Add custom Jinja2 filters for network configuration"""

        def ipaddr_filter(value: str, query: str = ''):
            """
            Simple IP address filter
            Examples:
                - {{ '192.168.1.1/24' | ipaddr('network') }} -> 192.168.1.0
                - {{ '192.168.1.1/24' | ipaddr('netmask') }} -> 255.255.255.0
            """
            import ipaddress
            try:
                if '/' in value:
                    network = ipaddress.ip_network(value, strict=False)
                    if query == 'network':
                        return str(network.network_address)
                    elif query == 'netmask':
                        return str(network.netmask)
                    elif query == 'prefix':
                        return str(network.prefixlen)
                    elif query == 'broadcast':
                        return str(network.broadcast_address)
                return value
            except:
                return value

        def cidr_to_wildcard(cidr: str) -> str:
            """Convert CIDR netmask to wildcard mask"""
            import ipaddress
            try:
                if '/' in cidr:
                    network = ipaddress.ip_network(cidr, strict=False)
                    hostmask = network.hostmask
                    return str(hostmask)
                return cidr
            except:
                return cidr

        def regex_replace(value: str, pattern: str, replacement: str = '') -> str:
            """Regex replace filter"""
            return re.sub(pattern, replacement, value)

        env.filters['ipaddr'] = ipaddr_filter
        env.filters['cidr_to_wildcard'] = cidr_to_wildcard
        env.filters['regex_replace'] = regex_replace

    def render(self, vendor: str, config_data: Dict[str, Any],
               template_name: str = 'base.j2') -> str:
        """
        Render configuration for a specific vendor

        Args:
            vendor: Vendor name (ios, nxos, eos, junos, frr)
            config_data: Configuration data dictionary
            template_name: Template file name (default: base.j2)

        Returns:
            Rendered configuration string

        Raises:
            ValueError: If vendor not supported or template not found
            TemplateError: If template rendering fails
        """
        if vendor not in self.SUPPORTED_VENDORS:
            raise ValueError(f"Vendor '{vendor}' not supported. "
                           f"Supported: {', '.join(self.SUPPORTED_VENDORS)}")

        if vendor not in self.environments:
            raise ValueError(f"No templates found for vendor '{vendor}'")

        env = self.environments[vendor]

        try:
            template = env.get_template(template_name)
            rendered = template.render(**config_data)
            return rendered
        except UndefinedError as e:
            raise TemplateError(f"Undefined variable in template: {e}")
        except TemplateError as e:
            raise TemplateError(f"Template rendering error: {e}")

    def render_multi_vendor(self, config_data: Dict[str, Any],
                           vendors: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Render configuration for multiple vendors

        Args:
            config_data: Configuration data dictionary
            vendors: List of vendors to render (None = all)

        Returns:
            Dictionary mapping vendor -> rendered config
        """
        if vendors is None:
            vendors = self.SUPPORTED_VENDORS

        results = {}
        for vendor in vendors:
            if vendor in self.environments:
                try:
                    results[vendor] = self.render(vendor, config_data)
                except Exception as e:
                    results[vendor] = f"# ERROR: {str(e)}\n"

        return results

    def render_from_file(self, vendor: str, config_file: str,
                        format: str = 'json') -> str:
        """
        Render configuration from a JSON/YAML file

        Args:
            vendor: Vendor name
            config_file: Path to config file
            format: File format ('json' or 'yaml')

        Returns:
            Rendered configuration string
        """
        with open(config_file, 'r') as f:
            if format == 'json':
                config_data = json.load(f)
            elif format == 'yaml':
                config_data = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported format: {format}")

        return self.render(vendor, config_data)

    def save_config(self, config: str, output_file: str,
                   vendor: str = 'ios') -> None:
        """
        Save rendered configuration to file

        Args:
            config: Rendered configuration string
            output_file: Output file path
            vendor: Vendor name (for file extension)
        """
        # Add vendor-specific file extension
        extensions = {
            'ios': '.cfg',
            'nxos': '.cfg',
            'eos': '.cfg',
            'junos': '.conf',
            'frr': '.conf'
        }

        if not output_file.endswith(tuple(extensions.values())):
            output_file += extensions.get(vendor, '.cfg')

        with open(output_file, 'w') as f:
            f.write(config)


class ConfigLinter:
    """Configuration linter - checks for common issues"""

    def __init__(self):
        self.errors = []
        self.warnings = []

    def lint(self, config: str, vendor: str = 'ios') -> Dict[str, List[str]]:
        """
        Lint a configuration

        Args:
            config: Configuration string
            vendor: Vendor name

        Returns:
            Dictionary with 'errors' and 'warnings' lists
        """
        self.errors = []
        self.warnings = []

        lines = config.split('\n')

        # Check for empty sections
        self._check_empty_sections(lines, vendor)

        # Check for duplicate lines
        self._check_duplicates(lines)

        # Check for common syntax issues
        self._check_syntax(lines, vendor)

        # Check for unstable ordering
        self._check_ordering(lines, vendor)

        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'line_count': len(lines)
        }

    def _check_empty_sections(self, lines: List[str], vendor: str):
        """Check for empty configuration sections"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Check for section headers followed immediately by end marker
            if vendor in ['ios', 'nxos', 'eos']:
                if line.startswith('router ') or line.startswith('interface '):
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if next_line == '!' or next_line == '':
                            self.warnings.append(
                                f"Line {i+1}: Empty section detected: {line}"
                            )
            i += 1

    def _check_duplicates(self, lines: List[str]):
        """Check for duplicate configuration lines"""
        seen = {}
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped and not stripped.startswith('!') and not stripped.startswith('#'):
                # Ignore comments and banners
                if 'banner' not in stripped.lower():
                    if stripped in seen:
                        self.warnings.append(
                            f"Line {i+1}: Duplicate configuration: {stripped} "
                            f"(first seen at line {seen[stripped]+1})"
                        )
                    else:
                        seen[stripped] = i

    def _check_syntax(self, lines: List[str], vendor: str):
        """Check for common syntax errors"""
        for i, line in enumerate(lines):
            stripped = line.strip()

            # Check for incomplete commands
            if vendor in ['ios', 'nxos', 'eos']:
                if stripped.endswith('\\'):
                    self.errors.append(
                        f"Line {i+1}: Incomplete command (ends with backslash)"
                    )

            # Check for unbalanced quotes
            if stripped.count('"') % 2 != 0:
                self.warnings.append(
                    f"Line {i+1}: Unbalanced quotes"
                )

    def _check_ordering(self, lines: List[str], vendor: str):
        """Check for unstable ordering (e.g., IP addresses not sorted)"""
        # This is a simplified check - real implementation would be more sophisticated
        pass


def merge_configs(base_config: Dict[str, Any],
                 override_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge two configuration dictionaries (for hierarchical profiles)

    Args:
        base_config: Base configuration (lower priority)
        override_config: Override configuration (higher priority)

    Returns:
        Merged configuration dictionary
    """
    import copy

    merged = copy.deepcopy(base_config)

    def deep_merge(base: Dict, override: Dict) -> Dict:
        for key, value in override.items():
            if key in base:
                if isinstance(base[key], dict) and isinstance(value, dict):
                    base[key] = deep_merge(base[key], value)
                elif isinstance(base[key], list) and isinstance(value, list):
                    base[key].extend(value)
                else:
                    base[key] = value
            else:
                base[key] = value
        return base

    return deep_merge(merged, override_config)
