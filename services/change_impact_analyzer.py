"""
Change Impact Analyzer - Predict the impact of configuration changes.

This module analyzes proposed configuration changes and predicts their
potential impact on:
- Network connectivity
- Routing protocols
- Security policies
- Performance
- Other devices and services
"""

import difflib
from typing import Dict, List, Any, Optional, Set, Tuple
from enum import Enum
from dataclasses import dataclass, field
import re


class ImpactLevel(Enum):
    """Impact severity levels."""
    CRITICAL = "critical"  # Service disruption, network outage
    HIGH = "high"          # Significant impact on multiple services
    MEDIUM = "medium"      # Limited impact on specific services
    LOW = "low"            # Minimal impact
    INFO = "info"          # Informational change, no impact


class ChangeType(Enum):
    """Types of configuration changes."""
    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"
    REPLACE = "replace"


@dataclass
class ImpactAssessment:
    """Assessment of a single change's impact."""
    change_description: str
    change_type: ChangeType
    impact_level: ImpactLevel
    affected_components: List[str]
    potential_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    rollback_plan: Optional[str] = None
    testing_steps: List[str] = field(default_factory=list)


class ChangeImpactAnalyzer:
    """Analyze impact of configuration changes."""

    def __init__(self, platform: str = 'ios'):
        """
        Initialize impact analyzer.

        Args:
            platform: Device platform (ios, nxos, asa)
        """
        self.platform = platform
        self.assessments: List[ImpactAssessment] = []

    def analyze_changes(self, old_config: str, new_config: str) -> Dict[str, Any]:
        """
        Analyze changes between two configurations.

        Args:
            old_config: Original configuration
            new_config: New configuration

        Returns:
            Comprehensive impact analysis report
        """
        self.assessments = []

        # Get configuration diff
        diff = self._get_config_diff(old_config, new_config)

        # Analyze each change
        added_lines, removed_lines, modified_sections = self._parse_diff(diff)

        # Analyze additions
        for line in added_lines:
            self._analyze_addition(line, old_config)

        # Analyze deletions
        for line in removed_lines:
            self._analyze_deletion(line, new_config)

        # Analyze modifications
        for section, changes in modified_sections.items():
            self._analyze_modification(section, changes, old_config, new_config)

        # Perform cross-impact analysis
        self._analyze_cross_impacts(old_config, new_config)

        return self._generate_report()

    def _get_config_diff(self, old_config: str, new_config: str) -> List[str]:
        """Get unified diff between configurations."""
        old_lines = old_config.split('\n')
        new_lines = new_config.split('\n')

        return list(difflib.unified_diff(
            old_lines,
            new_lines,
            lineterm='',
            n=0  # No context lines
        ))

    def _parse_diff(self, diff: List[str]) -> Tuple[List[str], List[str], Dict[str, List[str]]]:
        """
        Parse diff into added, removed, and modified lines.

        Returns:
            Tuple of (added_lines, removed_lines, modified_sections)
        """
        added = []
        removed = []
        modified_sections = {}
        current_section = None

        for line in diff:
            if line.startswith('+++') or line.startswith('---') or line.startswith('@@'):
                continue

            if line.startswith('+'):
                added.append(line[1:].strip())
            elif line.startswith('-'):
                removed.append(line[1:].strip())

            # Detect section changes (interface, router, etc.)
            if line.startswith('+') or line.startswith('-'):
                section_match = re.match(r'[+-](interface|router|line|vlan|access-list)\s+(.+)', line)
                if section_match:
                    current_section = f"{section_match.group(1)} {section_match.group(2)}"
                    if current_section not in modified_sections:
                        modified_sections[current_section] = []
                elif current_section:
                    modified_sections[current_section].append(line)

        return added, removed, modified_sections

    def _analyze_addition(self, line: str, old_config: str) -> None:
        """Analyze impact of adding a configuration line."""
        if not line or line.startswith('!'):
            return

        # Interface changes
        if line.startswith('interface '):
            self._assess_interface_addition(line)

        # Routing protocol changes
        elif 'router ' in line.lower():
            self._assess_routing_addition(line)

        # ACL changes
        elif 'access-list' in line.lower() or 'ip access-group' in line.lower():
            self._assess_acl_addition(line)

        # NAT changes
        elif 'nat' in line.lower():
            self._assess_nat_addition(line)

        # VLAN changes
        elif line.startswith('vlan '):
            self._assess_vlan_addition(line)

        # Route changes
        elif 'ip route' in line.lower():
            self._assess_route_addition(line)

        # Security changes
        elif any(keyword in line.lower() for keyword in ['aaa', 'authentication', 'authorization', 'crypto']):
            self._assess_security_addition(line)

    def _analyze_deletion(self, line: str, new_config: str) -> None:
        """Analyze impact of deleting a configuration line."""
        if not line or line.startswith('!'):
            return

        # Interface deletion/shutdown
        if 'shutdown' in line.lower() or line.startswith('no interface'):
            self.assessments.append(ImpactAssessment(
                change_description=f"Interface shutdown or removal: {line}",
                change_type=ChangeType.DELETE,
                impact_level=ImpactLevel.CRITICAL,
                affected_components=['connectivity', 'routing', 'services'],
                potential_issues=[
                    "Network connectivity loss",
                    "Service disruption for connected devices",
                    "Routing protocol adjacencies will be lost"
                ],
                recommendations=[
                    "Verify no critical services on this interface",
                    "Check for alternate paths",
                    "Notify affected users before change"
                ],
                rollback_plan=f"no {line}" if line.startswith('shutdown') else f"Restore full interface config",
                testing_steps=[
                    "Ping test from connected devices",
                    "Verify routing table entries",
                    "Check routing protocol neighbors"
                ]
            ))

        # Route deletion
        elif line.startswith('no ip route') or (line.startswith('ip route') and 'no ' not in new_config):
            self._assess_route_deletion(line)

        # ACL deletion
        elif line.startswith('no access-list') or line.startswith('no ip access-group'):
            self._assess_acl_deletion(line)

        # Routing protocol removal
        elif line.startswith('no router '):
            self._assess_routing_deletion(line)

    def _analyze_modification(self, section: str, changes: List[str], old_config: str, new_config: str) -> None:
        """Analyze impact of modifying a configuration section."""
        if 'interface' in section:
            self._assess_interface_modification(section, changes)
        elif 'router' in section:
            self._assess_routing_modification(section, changes)
        elif 'vlan' in section:
            self._assess_vlan_modification(section, changes)

    def _assess_interface_addition(self, line: str) -> None:
        """Assess impact of adding/modifying an interface."""
        self.assessments.append(ImpactAssessment(
            change_description=f"Interface configuration change: {line}",
            change_type=ChangeType.ADD,
            impact_level=ImpactLevel.MEDIUM,
            affected_components=['interface', 'connectivity'],
            potential_issues=[
                "May affect connected devices if parameters change",
                "Duplex/speed mismatch possible"
            ],
            recommendations=[
                "Verify interface parameters match connected device",
                "Test connectivity after change"
            ],
            testing_steps=[
                "show interface status",
                "show interface <name>",
                "ping test to connected device"
            ]
        ))

    def _assess_routing_addition(self, line: str) -> None:
        """Assess impact of routing protocol changes."""
        protocol = re.search(r'router\s+(\w+)', line, re.IGNORECASE)
        protocol_name = protocol.group(1).upper() if protocol else "routing protocol"

        self.assessments.append(ImpactAssessment(
            change_description=f"Routing protocol change: {line}",
            change_type=ChangeType.ADD,
            impact_level=ImpactLevel.HIGH,
            affected_components=['routing', 'convergence', 'traffic-flow'],
            potential_issues=[
                f"{protocol_name} adjacencies may flap during configuration",
                "Routing table changes will affect traffic flow",
                "Potential routing loops if misconfigured",
                "Convergence time may cause temporary packet loss"
            ],
            recommendations=[
                "Verify router ID and autonomous system numbers",
                "Check network statements match interface subnets",
                "Monitor routing table before and after",
                "Schedule during maintenance window"
            ],
            rollback_plan=f"no router {protocol_name.lower()}",
            testing_steps=[
                f"show ip {protocol_name.lower()}",
                f"show ip {protocol_name.lower()} neighbors",
                "show ip route",
                "traceroute to critical destinations"
            ]
        ))

    def _assess_acl_addition(self, line: str) -> None:
        """Assess impact of ACL changes."""
        self.assessments.append(ImpactAssessment(
            change_description=f"Access control list change: {line}",
            change_type=ChangeType.ADD,
            impact_level=ImpactLevel.HIGH,
            affected_components=['security', 'access-control', 'traffic-flow'],
            potential_issues=[
                "May block legitimate traffic if rules too restrictive",
                "Incorrect order of ACL entries can cause issues",
                "Performance impact on high-traffic interfaces"
            ],
            recommendations=[
                "Review ACL rules carefully before applying",
                "Test ACL with simulation tools",
                "Apply to interface in non-production first",
                "Have 'no ip access-group' command ready"
            ],
            rollback_plan="no ip access-group <acl-name> <in|out>",
            testing_steps=[
                "show access-lists",
                "show ip interface <name>",
                "Test connectivity from affected sources"
            ]
        ))

    def _assess_nat_addition(self, line: str) -> None:
        """Assess impact of NAT configuration."""
        self.assessments.append(ImpactAssessment(
            change_description=f"NAT configuration change: {line}",
            change_type=ChangeType.ADD,
            impact_level=ImpactLevel.HIGH,
            affected_components=['nat', 'addressing', 'connectivity'],
            potential_issues=[
                "Existing connections may be dropped",
                "Address pool exhaustion possible",
                "DNS resolution may be affected"
            ],
            recommendations=[
                "Clear existing NAT translations carefully",
                "Monitor NAT pool utilization",
                "Update DNS records if using static NAT"
            ],
            testing_steps=[
                "show ip nat translations",
                "show ip nat statistics",
                "Test connectivity from inside network"
            ]
        ))

    def _assess_vlan_addition(self, line: str) -> None:
        """Assess impact of VLAN changes."""
        vlan_match = re.search(r'vlan\s+(\d+)', line)
        vlan_id = vlan_match.group(1) if vlan_match else "unknown"

        self.assessments.append(ImpactAssessment(
            change_description=f"VLAN configuration change: {line}",
            change_type=ChangeType.ADD,
            impact_level=ImpactLevel.MEDIUM,
            affected_components=['layer2', 'vlan', 'switching'],
            potential_issues=[
                "VLAN may not propagate via VTP",
                "Trunk links must allow new VLAN",
                "STP topology may change"
            ],
            recommendations=[
                "Verify VTP mode and domain",
                "Check trunk allowed VLANs",
                "Monitor STP topology changes"
            ],
            testing_steps=[
                "show vlan brief",
                "show vlan id " + vlan_id,
                "show interfaces trunk"
            ]
        ))

    def _assess_route_addition(self, line: str) -> None:
        """Assess impact of adding static routes."""
        self.assessments.append(ImpactAssessment(
            change_description=f"Static route addition: {line}",
            change_type=ChangeType.ADD,
            impact_level=ImpactLevel.MEDIUM,
            affected_components=['routing', 'traffic-flow'],
            potential_issues=[
                "May create routing loops",
                "Could override dynamic routing",
                "Next-hop must be reachable"
            ],
            recommendations=[
                "Verify next-hop is reachable",
                "Check administrative distance",
                "Verify route doesn't conflict with existing routes"
            ],
            testing_steps=[
                "show ip route",
                "show ip route <destination>",
                "traceroute <destination>"
            ]
        ))

    def _assess_security_addition(self, line: str) -> None:
        """Assess impact of security-related changes."""
        self.assessments.append(ImpactAssessment(
            change_description=f"Security configuration change: {line}",
            change_type=ChangeType.ADD,
            impact_level=ImpactLevel.CRITICAL,
            affected_components=['security', 'authentication', 'access'],
            potential_issues=[
                "May lock out legitimate users",
                "Authentication failures possible",
                "VPN connections may break"
            ],
            recommendations=[
                "Test with non-critical user first",
                "Have console access available",
                "Document rollback procedure",
                "Keep backup authentication method"
            ],
            rollback_plan="Document current config before change",
            testing_steps=[
                "Test login from multiple sources",
                "Verify AAA server connectivity",
                "Check authentication logs"
            ]
        ))

    def _assess_route_deletion(self, line: str) -> None:
        """Assess impact of route deletion."""
        self.assessments.append(ImpactAssessment(
            change_description=f"Static route removal: {line}",
            change_type=ChangeType.DELETE,
            impact_level=ImpactLevel.HIGH,
            affected_components=['routing', 'connectivity'],
            potential_issues=[
                "Destination may become unreachable",
                "Traffic may take suboptimal path",
                "Services may fail"
            ],
            recommendations=[
                "Verify alternate route exists",
                "Check routing table after removal",
                "Notify users of potential impact"
            ],
            rollback_plan=line.replace('no ', ''),
            testing_steps=[
                "show ip route",
                "traceroute to affected destination",
                "Verify service availability"
            ]
        ))

    def _assess_acl_deletion(self, line: str) -> None:
        """Assess impact of ACL deletion."""
        self.assessments.append(ImpactAssessment(
            change_description=f"ACL removal: {line}",
            change_type=ChangeType.DELETE,
            impact_level=ImpactLevel.CRITICAL,
            affected_components=['security', 'access-control'],
            potential_issues=[
                "Removes traffic filtering - security risk",
                "Unauthorized access may be allowed",
                "Compliance violations possible"
            ],
            recommendations=[
                "Verify ACL is truly unused",
                "Check all interfaces for ACL references",
                "Review security policy before removal"
            ],
            rollback_plan="Restore full ACL configuration",
            testing_steps=[
                "show ip interface",
                "show access-lists",
                "Test access from untrusted sources"
            ]
        ))

    def _assess_routing_deletion(self, line: str) -> None:
        """Assess impact of routing protocol removal."""
        self.assessments.append(ImpactAssessment(
            change_description=f"Routing protocol removal: {line}",
            change_type=ChangeType.DELETE,
            impact_level=ImpactLevel.CRITICAL,
            affected_components=['routing', 'connectivity', 'network-wide'],
            potential_issues=[
                "All routes from this protocol will be removed",
                "Network-wide connectivity loss possible",
                "Routing protocol neighbors will be lost"
            ],
            recommendations=[
                "Ensure alternate routing protocol is active",
                "Coordinate with other network teams",
                "Schedule during maintenance window",
                "Have complete configuration backup"
            ],
            rollback_plan="Restore full routing protocol configuration",
            testing_steps=[
                "show ip route",
                "show ip protocols",
                "Ping/traceroute to all critical destinations"
            ]
        ))

    def _assess_interface_modification(self, section: str, changes: List[str]) -> None:
        """Assess impact of interface modifications."""
        has_critical = any(
            'shutdown' in c.lower() or 'ip address' in c.lower()
            for c in changes
        )

        impact = ImpactLevel.CRITICAL if has_critical else ImpactLevel.MEDIUM

        self.assessments.append(ImpactAssessment(
            change_description=f"Interface modification: {section}",
            change_type=ChangeType.MODIFY,
            impact_level=impact,
            affected_components=['interface', 'connectivity'],
            potential_issues=[
                "Connected devices may lose connectivity",
                "IP address change requires client reconfiguration",
                "Protocol adjacencies may flap"
            ],
            recommendations=[
                "Schedule during maintenance window",
                "Notify affected users",
                "Test on non-production interface first"
            ],
            testing_steps=[
                "show interface " + section.replace('interface ', ''),
                "show ip interface brief",
                "Ping test to gateway"
            ]
        ))

    def _assess_routing_modification(self, section: str, changes: List[str]) -> None:
        """Assess impact of routing protocol modifications."""
        self.assessments.append(ImpactAssessment(
            change_description=f"Routing protocol modification: {section}",
            change_type=ChangeType.MODIFY,
            impact_level=ImpactLevel.HIGH,
            affected_components=['routing', 'protocol-adjacencies'],
            potential_issues=[
                "Protocol may restart, causing convergence delay",
                "Routing table will change",
                "Traffic patterns may shift"
            ],
            recommendations=[
                "Monitor routing protocol during change",
                "Verify no flapping occurs",
                "Check route metrics after change"
            ],
            testing_steps=[
                "show ip protocols",
                "show ip route",
                "Monitor for route flaps"
            ]
        ))

    def _assess_vlan_modification(self, section: str, changes: List[str]) -> None:
        """Assess impact of VLAN modifications."""
        self.assessments.append(ImpactAssessment(
            change_description=f"VLAN modification: {section}",
            change_type=ChangeType.MODIFY,
            impact_level=ImpactLevel.MEDIUM,
            affected_components=['layer2', 'vlan'],
            potential_issues=[
                "Devices in VLAN may temporarily lose connectivity",
                "STP may reconverge"
            ],
            recommendations=[
                "Schedule during maintenance window",
                "Monitor STP state"
            ],
            testing_steps=[
                "show vlan brief",
                "show spanning-tree vlan " + section.replace('vlan ', '')
            ]
        ))

    def _analyze_cross_impacts(self, old_config: str, new_config: str) -> None:
        """Analyze cross-component impacts."""
        # Check for multiple high-impact changes
        critical_count = sum(1 for a in self.assessments if a.impact_level == ImpactLevel.CRITICAL)
        high_count = sum(1 for a in self.assessments if a.impact_level == ImpactLevel.HIGH)

        if critical_count > 1 or high_count > 3:
            self.assessments.append(ImpactAssessment(
                change_description="Multiple high-impact changes detected",
                change_type=ChangeType.MODIFY,
                impact_level=ImpactLevel.CRITICAL,
                affected_components=['network-wide'],
                potential_issues=[
                    "Complex interactions between changes",
                    "Difficult to troubleshoot if issues arise",
                    "Higher risk of network outage"
                ],
                recommendations=[
                    "Consider implementing changes in phases",
                    "Have dedicated rollback window",
                    "Ensure full team availability during change",
                    "Have out-of-band management access ready"
                ],
                testing_steps=[
                    "Complete end-to-end testing after all changes",
                    "Verify all critical services",
                    "Monitor for 30+ minutes post-change"
                ]
            ))

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive impact analysis report."""
        # Calculate risk score
        impact_weights = {
            ImpactLevel.CRITICAL: 10,
            ImpactLevel.HIGH: 7,
            ImpactLevel.MEDIUM: 4,
            ImpactLevel.LOW: 2,
            ImpactLevel.INFO: 0
        }

        total_risk_score = sum(impact_weights[a.impact_level] for a in self.assessments)
        max_possible = len(self.assessments) * 10
        risk_percentage = (total_risk_score / max_possible * 100) if max_possible > 0 else 0

        # Categorize by impact level
        by_impact = {level.value: [] for level in ImpactLevel}
        for assessment in self.assessments:
            by_impact[assessment.impact_level.value].append({
                'change_description': assessment.change_description,
                'change_type': assessment.change_type.value,
                'affected_components': assessment.affected_components,
                'potential_issues': assessment.potential_issues,
                'recommendations': assessment.recommendations,
                'rollback_plan': assessment.rollback_plan,
                'testing_steps': assessment.testing_steps
            })

        # Get all affected components
        all_components = set()
        for assessment in self.assessments:
            all_components.update(assessment.affected_components)

        # Determine overall risk level
        if risk_percentage >= 70:
            risk_level = "CRITICAL"
        elif risk_percentage >= 50:
            risk_level = "HIGH"
        elif risk_percentage >= 30:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return {
            'summary': {
                'total_changes': len(self.assessments),
                'risk_score': round(risk_percentage, 2),
                'risk_level': risk_level,
                'affected_components': sorted(list(all_components)),
                'critical_count': len(by_impact['critical']),
                'high_count': len(by_impact['high']),
                'medium_count': len(by_impact['medium']),
                'low_count': len(by_impact['low'])
            },
            'assessments_by_impact': by_impact,
            'recommendations': self._generate_recommendations(risk_level, by_impact),
            'pre_change_checklist': self._generate_pre_change_checklist(),
            'post_change_checklist': self._generate_post_change_checklist()
        }

    def _generate_recommendations(self, risk_level: str, by_impact: Dict) -> List[str]:
        """Generate overall recommendations based on risk level."""
        recommendations = []

        if risk_level in ['CRITICAL', 'HIGH']:
            recommendations.extend([
                "Schedule change during maintenance window",
                "Notify all stakeholders of planned change",
                "Have rollback plan documented and ready",
                "Ensure console/out-of-band access available",
                "Have full network team on standby",
                "Take complete configuration backup",
                "Test in lab environment if possible"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Schedule during low-traffic period",
                "Notify affected users",
                "Have rollback commands ready",
                "Monitor closely after implementation"
            ])
        else:
            recommendations.extend([
                "Standard change procedures apply",
                "Document change in change management system"
            ])

        return recommendations

    def _generate_pre_change_checklist(self) -> List[str]:
        """Generate pre-change checklist."""
        return [
            "Back up current configuration (copy running-config startup-config)",
            "Save configuration to TFTP/FTP server",
            "Document current state (show commands output)",
            "Verify maintenance window scheduled",
            "Confirm stakeholder notification sent",
            "Review rollback procedures",
            "Ensure out-of-band access available",
            "Verify tools and access ready (SSH, console, monitoring)"
        ]

    def _generate_post_change_checklist(self) -> List[str]:
        """Generate post-change checklist."""
        return [
            "Verify all intended changes applied",
            "Test connectivity to critical systems",
            "Check routing protocol neighbors/adjacencies",
            "Verify routing table correctness",
            "Test application functionality",
            "Monitor system logs for errors",
            "Collect 'show' command outputs for comparison",
            "Monitor for 15-30 minutes for stability",
            "Update documentation",
            "Close change ticket with results"
        ]
