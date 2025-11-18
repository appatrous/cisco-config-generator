"""
Advanced Configuration Validator
Detects conflicts, enforces best practices, performs security auditing
"""

import re
from typing import Dict, List, Tuple
from collections import defaultdict


class ConfigValidator:
    """
    Advanced validator for network configurations
    """

    def validate_config(self, config: str, vendor: str = 'cisco') -> Dict:
        """
        Comprehensive configuration validation

        Args:
            config: Configuration to validate
            vendor: Vendor type (cisco, arista, juniper)

        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'best_practices': [],
            'security_issues': [],
            'compliance_issues': [],
            'conflicts': []
        }

        # Run all validators
        results['conflicts'] = self._detect_conflicts(config)
        results['best_practices'] = self._check_best_practices(config)
        results['security_issues'] = self._security_audit(config)

        # Determine overall validity
        results['valid'] = len(results['errors']) == 0
        results['score'] = self._calculate_score(results)
        results['risk_level'] = self._assess_overall_risk(results)

        return results

    def _detect_conflicts(self, config: str) -> List[Dict]:
        """Detect configuration conflicts"""
        conflicts = []

        # Detect duplicate IP addresses
        ip_conflicts = self._detect_duplicate_ips(config)
        conflicts.extend(ip_conflicts)

        # Detect VLAN ID conflicts
        vlan_conflicts = self._detect_vlan_conflicts(config)
        conflicts.extend(vlan_conflicts)

        # Detect routing conflicts
        routing_conflicts = self._detect_routing_conflicts(config)
        conflicts.extend(routing_conflicts)

        return conflicts

    def _detect_duplicate_ips(self, config: str) -> List[Dict]:
        """Detect duplicate IP address assignments"""
        conflicts = []
        ip_pattern = r'ip address (\d+\.\d+\.\d+\.\d+)'

        ip_assignments = defaultdict(list)

        for match in re.finditer(ip_pattern, config, re.MULTILINE):
            ip = match.group(1)
            line_num = config[:match.start()].count('\n') + 1
            ip_assignments[ip].append(line_num)

        for ip, lines in ip_assignments.items():
            if len(lines) > 1:
                conflicts.append({
                    'type': 'duplicate_ip',
                    'severity': 'HIGH',
                    'ip_address': ip,
                    'lines': lines,
                    'message': f'IP address {ip} is assigned to multiple interfaces'
                })

        return conflicts

    def _detect_vlan_conflicts(self, config: str) -> List[Dict]:
        """Detect VLAN configuration conflicts"""
        conflicts = []

        # Check for invalid VLAN IDs (must be 1-4094)
        vlan_pattern = r'vlan (\d+)'
        for match in re.finditer(vlan_pattern, config, re.MULTILINE):
            vlan_id = int(match.group(1))
            if vlan_id < 1 or vlan_id > 4094:
                conflicts.append({
                    'type': 'invalid_vlan',
                    'severity': 'HIGH',
                    'vlan_id': vlan_id,
                    'message': f'VLAN ID {vlan_id} is outside valid range (1-4094)'
                })

        return conflicts

    def _detect_routing_conflicts(self, config: str) -> List[Dict]:
        """Detect routing protocol conflicts"""
        conflicts = []

        # Check for OSPF area 0 requirement in multi-area setups
        ospf_areas = re.findall(r'area (\d+)', config)
        if ospf_areas and '0' not in ospf_areas:
            conflicts.append({
                'type': 'ospf_no_backbone',
                'severity': 'MEDIUM',
                'message': 'OSPF multi-area configuration without backbone area 0'
            })

        return conflicts

    def _check_best_practices(self, config: str) -> List[Dict]:
        """Check for best practice violations"""
        issues = []

        # Check for SSH configuration
        if 'ip ssh' not in config.lower():
            issues.append({
                'category': 'management',
                'severity': 'MEDIUM',
                'message': 'SSH not configured - recommend enabling for secure remote access'
            })

        # Check for NTP configuration
        if 'ntp server' not in config.lower():
            issues.append({
                'category': 'management',
                'severity': 'LOW',
                'message': 'NTP not configured - time synchronization recommended'
            })

        # Check for logging
        if 'logging' not in config.lower() and 'log' not in config.lower():
            issues.append({
                'category': 'management',
                'severity': 'MEDIUM',
                'message': 'Logging not configured - event logging recommended'
            })

        # Check for STP on switch configs
        if 'interface' in config.lower() and 'spanning-tree' not in config.lower():
            issues.append({
                'category': 'layer2',
                'severity': 'MEDIUM',
                'message': 'Spanning-Tree not explicitly configured - recommend enabling'
            })

        # Check for interface descriptions
        interface_count = len(re.findall(r'^interface ', config, re.MULTILINE))
        description_count = len(re.findall(r'^\s+description ', config, re.MULTILINE))

        if interface_count > 0 and description_count < interface_count * 0.5:
            issues.append({
                'category': 'documentation',
                'severity': 'LOW',
                'message': f'Only {description_count}/{interface_count} interfaces have descriptions'
            })

        return issues

    def _security_audit(self, config: str) -> List[Dict]:
        """Perform security audit"""
        issues = []

        # Check for weak passwords (if visible)
        if re.search(r'password\s+(cisco|admin|password|123)', config, re.IGNORECASE):
            issues.append({
                'category': 'authentication',
                'severity': 'CRITICAL',
                'message': 'Weak or default password detected'
            })

        # Check for insecure protocols
        if 'telnet' in config.lower():
            issues.append({
                'category': 'protocols',
                'severity': 'HIGH',
                'message': 'Telnet enabled - use SSH instead for secure access'
            })

        if re.search(r'snmp-server community \w+', config):
            issues.append({
                'category': 'protocols',
                'severity': 'MEDIUM',
                'message': 'SNMPv1/v2c in use - consider upgrading to SNMPv3'
            })

        # Check for HTTP server
        if 'ip http server' in config and 'ip http secure-server' not in config:
            issues.append({
                'category': 'protocols',
                'severity': 'HIGH',
                'message': 'HTTP server enabled without HTTPS - security risk'
            })

        # Check for no AAA
        if 'aaa new-model' not in config:
            issues.append({
                'category': 'authentication',
                'severity': 'MEDIUM',
                'message': 'AAA not configured - recommend implementing centralized authentication'
            })

        # Check for ACLs on management interfaces
        if 'line vty' in config and 'access-class' not in config:
            issues.append({
                'category': 'access_control',
                'severity': 'HIGH',
                'message': 'VTY lines without access-class - unrestricted remote access'
            })

        return issues

    def _calculate_score(self, results: Dict) -> int:
        """Calculate configuration quality score (0-100)"""
        score = 100

        # Deduct points for issues
        score -= len(results['errors']) * 10
        score -= len(results['conflicts']) * 5
        score -= len(results['security_issues']) * 3
        score -= len(results['best_practices']) * 1

        return max(0, min(100, score))

    def _assess_overall_risk(self, results: Dict) -> str:
        """Assess overall risk level"""
        if len(results['errors']) > 0 or any(i.get('severity') == 'CRITICAL' for i in results['security_issues']):
            return 'CRITICAL'
        elif len(results['conflicts']) > 0 or any(i.get('severity') == 'HIGH' for i in results['security_issues']):
            return 'HIGH'
        elif len(results['best_practices']) > 3:
            return 'MEDIUM'
        else:
            return 'LOW'


class ComplianceChecker:
    """
    Check configuration compliance against standards
    """

    def __init__(self):
        self.compliance_rules = {
            'pci_dss': self._check_pci_dss,
            'hipaa': self._check_hipaa,
            'general': self._check_general_security
        }

    def check_compliance(self, config: str, standards: List[str] = None) -> Dict:
        """
        Check configuration against compliance standards

        Args:
            config: Configuration to check
            standards: List of standards to check (pci_dss, hipaa, general)

        Returns:
            Dict with compliance results
        """
        if standards is None:
            standards = ['general']

        results = {
            'compliant': True,
            'standards_checked': standards,
            'violations': []
        }

        for standard in standards:
            if standard in self.compliance_rules:
                violations = self.compliance_rules[standard](config)
                results['violations'].extend(violations)

        results['compliant'] = len(results['violations']) == 0
        results['compliance_score'] = self._calculate_compliance_score(results['violations'])

        return results

    def _check_pci_dss(self, config: str) -> List[Dict]:
        """Check PCI-DSS compliance"""
        violations = []

        # Requirement 2.3: Encrypt all non-console administrative access
        if 'telnet' in config.lower():
            violations.append({
                'standard': 'PCI-DSS',
                'requirement': '2.3',
                'severity': 'HIGH',
                'message': 'Telnet detected - PCI-DSS requires encrypted protocols'
            })

        # Requirement 8: Strong authentication
        if 'aaa new-model' not in config:
            violations.append({
                'standard': 'PCI-DSS',
                'requirement': '8.1',
                'severity': 'HIGH',
                'message': 'AAA not configured - PCI-DSS requires strong authentication'
            })

        return violations

    def _check_hipaa(self, config: str) -> List[Dict]:
        """Check HIPAA compliance"""
        violations = []

        # Access controls
        if 'line vty' in config and 'access-class' not in config:
            violations.append({
                'standard': 'HIPAA',
                'requirement': '164.312(a)(1)',
                'severity': 'HIGH',
                'message': 'Inadequate access controls on management interfaces'
            })

        # Audit controls
        if 'logging' not in config.lower():
            violations.append({
                'standard': 'HIPAA',
                'requirement': '164.312(b)',
                'severity': 'MEDIUM',
                'message': 'Audit logging not configured'
            })

        return violations

    def _check_general_security(self, config: str) -> List[Dict]:
        """Check general security best practices"""
        violations = []

        # Password encryption
        if 'service password-encryption' not in config:
            violations.append({
                'standard': 'General Security',
                'severity': 'MEDIUM',
                'message': 'Password encryption not enabled'
            })

        # Source routing
        if 'no ip source-route' not in config:
            violations.append({
                'standard': 'General Security',
                'severity': 'LOW',
                'message': 'IP source routing not disabled'
            })

        return violations

    def _calculate_compliance_score(self, violations: List[Dict]) -> int:
        """Calculate compliance score"""
        if not violations:
            return 100

        score = 100
        for violation in violations:
            if violation.get('severity') == 'HIGH':
                score -= 15
            elif violation.get('severity') == 'MEDIUM':
                score -= 10
            else:
                score -= 5

        return max(0, score)
