"""
Configuration Comparison and Merge Module
Handles intelligent config diffing, merging, and rollback operations
"""

import re
import difflib
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import json


class ConfigComparator:
    """
    Advanced configuration comparison and merge engine
    """

    def __init__(self):
        self.section_headers = [
            'interface ', 'router ', 'line ', 'vlan ', 'class-map ',
            'policy-map ', 'route-map ', 'access-list ', 'ip access-list ',
            'vrf definition ', 'aaa ', 'snmp-server '
        ]

    def compare_configs_detailed(self, old_config: str, new_config: str) -> Dict:
        """
        Detailed comparison with section-aware diff

        Args:
            old_config: Current/old configuration
            new_config: New/proposed configuration

        Returns:
            Dict with detailed comparison results
        """
        old_lines = self._normalize_config(old_config).split('\n')
        new_lines = self._normalize_config(new_config).split('\n')

        # Use difflib for intelligent diffing
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=0
        ))

        # Parse diff results
        added = []
        removed = []
        modified_sections = []

        current_section = None

        for line in diff:
            if line.startswith('---') or line.startswith('+++') or line.startswith('@@'):
                continue

            if line.startswith('+'):
                added_line = line[1:].strip()
                if added_line:
                    added.append(added_line)
                    # Track which section was modified
                    section = self._get_section_name(added_line)
                    if section and section not in modified_sections:
                        modified_sections.append(section)

            elif line.startswith('-'):
                removed_line = line[1:].strip()
                if removed_line:
                    removed.append(removed_line)
                    section = self._get_section_name(removed_line)
                    if section and section not in modified_sections:
                        modified_sections.append(section)

        # Generate human-readable summary
        summary = self._generate_change_summary(added, removed, modified_sections)

        return {
            'added_lines': len(added),
            'removed_lines': len(removed),
            'modified_sections': modified_sections,
            'added': added,
            'removed': removed,
            'summary': summary,
            'risk_level': self._assess_risk(added, removed),
            'affected_interfaces': self._extract_affected_interfaces(added, removed),
            'affected_vlans': self._extract_affected_vlans(added, removed),
            'routing_changes': self._detect_routing_changes(added, removed)
        }

    def merge_configs(self, base_config: str, overlay_config: str, strategy: str = 'overlay') -> Dict:
        """
        Merge two configurations with intelligent conflict resolution

        Args:
            base_config: Base/current configuration
            overlay_config: Configuration to overlay/merge
            strategy: Merge strategy ('overlay', 'additive', 'replace')

        Returns:
            Dict with merged config and conflict information
        """
        if strategy == 'replace':
            return {
                'success': True,
                'merged_config': overlay_config,
                'conflicts': [],
                'strategy': 'replace'
            }

        base_sections = self._parse_into_sections(base_config)
        overlay_sections = self._parse_into_sections(overlay_config)

        merged_sections = {}
        conflicts = []

        if strategy == 'overlay':
            # Overlay strategy: new config overlays base, conflicts favor overlay
            merged_sections = {**base_sections}

            for section_name, overlay_content in overlay_sections.items():
                if section_name in base_sections:
                    # Section exists in both - check for conflicts
                    if base_sections[section_name] != overlay_content:
                        conflicts.append({
                            'section': section_name,
                            'base': base_sections[section_name][:200],
                            'overlay': overlay_content[:200],
                            'resolution': 'Used overlay version'
                        })

                merged_sections[section_name] = overlay_content

        elif strategy == 'additive':
            # Additive strategy: combine both, keep existing, add new
            merged_sections = {**base_sections}

            for section_name, overlay_content in overlay_sections.items():
                if section_name not in base_sections:
                    # New section - add it
                    merged_sections[section_name] = overlay_content
                else:
                    # Section exists - merge lines
                    base_lines = set(base_sections[section_name].split('\n'))
                    overlay_lines = set(overlay_content.split('\n'))
                    all_lines = base_lines | overlay_lines
                    merged_sections[section_name] = '\n'.join(sorted(all_lines))

                    if base_lines != overlay_lines:
                        conflicts.append({
                            'section': section_name,
                            'resolution': 'Merged both versions'
                        })

        # Reconstruct full config
        merged_config = self._reconstruct_config(merged_sections)

        return {
            'success': True,
            'merged_config': merged_config,
            'conflicts': conflicts,
            'strategy': strategy,
            'sections_merged': len(merged_sections)
        }

    def generate_rollback_config(self, current_config: str, target_config: str) -> Dict:
        """
        Generate configuration to rollback from current to target state

        Args:
            current_config: Current running configuration
            target_config: Target (previous/desired) configuration

        Returns:
            Dict with rollback commands
        """
        current_lines = set(self._normalize_config(current_config).split('\n'))
        target_lines = set(self._normalize_config(target_config).split('\n'))

        # Lines to remove (in current but not in target)
        to_remove = current_lines - target_lines

        # Lines to add (in target but not in current)
        to_add = target_lines - current_lines

        # Generate rollback commands
        rollback_commands = []

        # Add 'no' commands for removals
        for line in sorted(to_remove):
            if line.strip() and not line.strip().startswith('!'):
                # Determine if this needs a 'no' command
                if self._needs_no_command(line):
                    rollback_commands.append(f'no {line}')

        # Add commands for additions
        for line in sorted(to_add):
            if line.strip() and not line.strip().startswith('!'):
                rollback_commands.append(line)

        return {
            'rollback_commands': rollback_commands,
            'commands_count': len(rollback_commands),
            'removals': len(to_remove),
            'additions': len(to_add),
            'estimated_time_seconds': self._estimate_rollback_time(len(rollback_commands))
        }

    def _normalize_config(self, config: str) -> str:
        """Normalize configuration for comparison"""
        lines = []
        for line in config.split('\n'):
            # Remove trailing whitespace
            line = line.rstrip()
            # Skip empty lines
            if not line:
                continue
            # Skip pure comment lines
            if line.strip().startswith('!') and not any(x in line for x in ['Building', 'Current', '=====']):
                continue
            lines.append(line)
        return '\n'.join(lines)

    def _parse_into_sections(self, config: str) -> Dict[str, str]:
        """Parse configuration into logical sections"""
        sections = {}
        current_section = 'global'
        current_content = []

        for line in config.split('\n'):
            line = line.strip()

            # Check if this is a section header
            is_section_start = False
            section_name = None

            for header_prefix in self.section_headers:
                if line.startswith(header_prefix):
                    is_section_start = True
                    section_name = line
                    break

            if is_section_start:
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content)
                # Start new section
                current_section = section_name
                current_content = [line]
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def _reconstruct_config(self, sections: Dict[str, str]) -> str:
        """Reconstruct configuration from sections"""
        # Order: global first, then interfaces, then everything else
        config_parts = []

        if 'global' in sections:
            config_parts.append(sections['global'])

        # Interfaces
        interface_sections = sorted([k for k in sections.keys() if k.startswith('interface ')])
        for section in interface_sections:
            config_parts.append(sections[section])

        # Other sections
        other_sections = sorted([k for k in sections.keys() if k != 'global' and not k.startswith('interface ')])
        for section in other_sections:
            config_parts.append(sections[section])

        return '\n!\n'.join(config_parts)

    def _get_section_name(self, line: str) -> Optional[str]:
        """Extract section name from a configuration line"""
        for header in self.section_headers:
            if line.startswith(header):
                return line.split()[0:2]  # e.g., ['interface', 'GigabitEthernet0/1']
        return None

    def _generate_change_summary(self, added: List[str], removed: List[str], sections: List[str]) -> str:
        """Generate human-readable change summary"""
        summary_parts = []

        if len(added) > 0:
            summary_parts.append(f'{len(added)} lines added')
        if len(removed) > 0:
            summary_parts.append(f'{len(removed)} lines removed')
        if len(sections) > 0:
            summary_parts.append(f'{len(sections)} sections modified')

        return ', '.join(summary_parts) if summary_parts else 'No changes detected'

    def _assess_risk(self, added: List[str], removed: List[str]) -> str:
        """Assess risk level of configuration changes"""
        high_risk_keywords = ['no router', 'no ip route', 'shutdown', 'no interface',
                             'no vlan', 'no spanning-tree', 'no ip address']

        medium_risk_keywords = ['interface', 'router', 'access-list', 'route-map',
                               'vlan', 'spanning-tree']

        high_risk_count = sum(1 for line in added + removed
                             if any(keyword in line.lower() for keyword in high_risk_keywords))

        medium_risk_count = sum(1 for line in added + removed
                               if any(keyword in line.lower() for keyword in medium_risk_keywords))

        if high_risk_count > 0:
            return 'HIGH'
        elif medium_risk_count > 3:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _extract_affected_interfaces(self, added: List[str], removed: List[str]) -> List[str]:
        """Extract list of interfaces affected by changes"""
        interfaces = set()
        for line in added + removed:
            if line.startswith('interface '):
                interfaces.add(line.split()[1])
        return sorted(list(interfaces))

    def _extract_affected_vlans(self, added: List[str], removed: List[str]) -> List[int]:
        """Extract list of VLANs affected by changes"""
        vlans = set()
        for line in added + removed:
            match = re.search(r'vlan\s+(\d+)', line, re.IGNORECASE)
            if match:
                vlans.add(int(match.group(1)))
        return sorted(list(vlans))

    def _detect_routing_changes(self, added: List[str], removed: List[str]) -> Dict:
        """Detect routing protocol changes"""
        routing_changes = {
            'ospf': False,
            'eigrp': False,
            'bgp': False,
            'static_routes': False
        }

        all_lines = added + removed
        for line in all_lines:
            if 'router ospf' in line.lower():
                routing_changes['ospf'] = True
            if 'router eigrp' in line.lower():
                routing_changes['eigrp'] = True
            if 'router bgp' in line.lower():
                routing_changes['bgp'] = True
            if 'ip route' in line.lower():
                routing_changes['static_routes'] = True

        return routing_changes

    def _needs_no_command(self, line: str) -> bool:
        """Determine if a line needs 'no' prefix for removal"""
        # Commands that don't use 'no' for removal
        no_removal_commands = ['end', 'exit', '!']

        return not any(line.strip().startswith(cmd) for cmd in no_removal_commands)

    def _estimate_rollback_time(self, command_count: int) -> int:
        """Estimate time required for rollback in seconds"""
        # Assume ~0.5 seconds per command on average
        return int(command_count * 0.5) + 10  # +10 for overhead


class ChangeTracker:
    """
    Track configuration changes over time
    """

    def __init__(self):
        self.changes = []

    def record_change(self, device_id: str, change_type: str, old_config: str,
                     new_config: str, user: str = 'admin', notes: str = '') -> Dict:
        """
        Record a configuration change

        Args:
            device_id: Device identifier
            change_type: Type of change (manual, pull, push, rollback)
            old_config: Previous configuration
            new_config: New configuration
            user: User who made the change
            notes: Additional notes

        Returns:
            Dict with change record
        """
        change_id = f'change_{int(datetime.utcnow().timestamp())}_{device_id}'

        comparator = ConfigComparator()
        comparison = comparator.compare_configs_detailed(old_config, new_config)

        change_record = {
            'id': change_id,
            'device_id': device_id,
            'timestamp': datetime.utcnow().isoformat(),
            'user': user,
            'change_type': change_type,
            'notes': notes,
            'old_config_hash': hash(old_config),
            'new_config_hash': hash(new_config),
            'old_config_size': len(old_config),
            'new_config_size': len(new_config),
            'comparison': {
                'added_lines': comparison['added_lines'],
                'removed_lines': comparison['removed_lines'],
                'modified_sections': comparison['modified_sections'],
                'risk_level': comparison['risk_level'],
                'summary': comparison['summary']
            },
            'rollback_available': True
        }

        self.changes.append(change_record)
        return change_record

    def get_device_history(self, device_id: str, limit: int = 50) -> List[Dict]:
        """Get change history for a specific device"""
        device_changes = [c for c in self.changes if c['device_id'] == device_id]
        return sorted(device_changes, key=lambda x: x['timestamp'], reverse=True)[:limit]

    def get_change_by_id(self, change_id: str) -> Optional[Dict]:
        """Get a specific change record by ID"""
        for change in self.changes:
            if change['id'] == change_id:
                return change
        return None
