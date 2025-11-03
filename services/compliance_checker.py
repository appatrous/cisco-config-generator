"""
Compliance Checker - Verify configurations against security standards.

Supports multiple compliance frameworks:
- PCI-DSS (Payment Card Industry Data Security Standard)
- NIST (National Institute of Standards and Technology)
- CIS (Center for Internet Security) Cisco Benchmarks
- Custom organization policies
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field


class Severity(Enum):
    """Severity levels for compliance findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Status(Enum):
    """Compliance check status."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class ComplianceFinding:
    """Individual compliance check result."""
    rule_id: str
    title: str
    description: str
    status: Status
    severity: Severity
    current_config: Optional[str] = None
    recommendation: Optional[str] = None
    remediation: Optional[str] = None
    references: List[str] = field(default_factory=list)


class ComplianceChecker:
    """Check Cisco configurations against compliance standards."""

    def __init__(self, platform: str = 'ios'):
        """
        Initialize compliance checker.

        Args:
            platform: Device platform (ios, nxos, asa)
        """
        self.platform = platform
        self.findings: List[ComplianceFinding] = []
        self.config_lines: List[str] = []

    def check_configuration(self, config_cli: str, standards: List[str] = None) -> Dict[str, Any]:
        """
        Check configuration against specified standards.

        Args:
            config_cli: Configuration text
            standards: List of standards to check ['pci-dss', 'nist', 'cis']
                      If None, checks all standards.

        Returns:
            Dictionary with compliance results
        """
        self.config_lines = config_cli.split('\n')
        self.findings = []

        if standards is None:
            standards = ['pci-dss', 'nist', 'cis']

        # Run checks for each standard
        if 'pci-dss' in standards:
            self._check_pci_dss()
        if 'nist' in standards:
            self._check_nist()
        if 'cis' in standards:
            self._check_cis()

        return self._generate_report()

    def _check_pci_dss(self) -> None:
        """Check PCI-DSS compliance requirements."""

        # PCI-DSS Requirement 2.1: Always change vendor-supplied defaults
        self._check_default_passwords()

        # PCI-DSS Requirement 2.2.1: Implement only one primary function per server
        # (Network device specific checks)
        self._check_unnecessary_services()

        # PCI-DSS Requirement 2.3: Encrypt non-console administrative access
        self._check_encrypted_management()

        # PCI-DSS Requirement 8.2: Strong authentication
        self._check_strong_authentication()

        # PCI-DSS Requirement 8.2.3: Strong passwords
        self._check_password_complexity()

        # PCI-DSS Requirement 10.1: Log all access
        self._check_logging()

        # PCI-DSS Requirement 1.1: Firewall standards
        if self.platform == 'asa':
            self._check_firewall_rules()

    def _check_nist(self) -> None:
        """Check NIST Cybersecurity Framework compliance."""

        # NIST AC-2: Account Management
        self._check_account_management()

        # NIST AC-7: Unsuccessful Login Attempts
        self._check_login_block()

        # NIST AU-2: Audit Events
        self._check_audit_logging()

        # NIST IA-5: Authenticator Management
        self._check_authenticator_management()

        # NIST SC-8: Transmission Confidentiality
        self._check_transmission_encryption()

        # NIST SC-10: Network Disconnect
        self._check_session_timeout()

    def _check_cis(self) -> None:
        """Check CIS Cisco Benchmarks."""

        # CIS 1.1: Set hostname
        self._check_hostname_configured()

        # CIS 1.2: Set enable secret
        self._check_enable_secret()

        # CIS 1.3: Service password-encryption
        self._check_service_password_encryption()

        # CIS 1.4: Set banner
        self._check_login_banner()

        # CIS 2.1: Disable unnecessary services
        self._check_disable_unnecessary_services()

        # CIS 3.1: Configure NTP
        self._check_ntp_configured()

        # CIS 3.2: Set timezone
        self._check_timezone()

        # CIS 4.1: Configure AAA
        self._check_aaa_authentication()

        # CIS 5.1: Configure SSH
        self._check_ssh_version()

        # CIS 6.1: Configure logging
        self._check_logging_configured()

    # Individual check methods

    def _check_default_passwords(self) -> None:
        """Check for default or weak passwords."""
        weak_passwords = ['cisco', 'password', '123456', 'admin']

        for line in self.config_lines:
            line_lower = line.lower().strip()
            if any(pwd in line_lower for pwd in weak_passwords):
                if 'password' in line_lower or 'secret' in line_lower:
                    self.findings.append(ComplianceFinding(
                        rule_id="PCI-2.1-001",
                        title="Default/Weak Password Detected",
                        description="Configuration contains potential default or weak password",
                        status=Status.FAILED,
                        severity=Severity.CRITICAL,
                        current_config=line.strip(),
                        recommendation="Change all default passwords to strong, unique values",
                        remediation="Use: enable secret <strong-password>\nusername <user> secret <strong-password>"
                    ))

    def _check_unnecessary_services(self) -> None:
        """Check for unnecessary services that should be disabled."""
        dangerous_services = [
            ('ip http server', 'HTTP server should be disabled'),
            ('ip finger', 'Finger service should be disabled'),
            ('service tcp-small-servers', 'TCP small servers should be disabled'),
            ('service udp-small-servers', 'UDP small servers should be disabled'),
            ('ip bootp server', 'BOOTP server should be disabled'),
            ('ip identd', 'IDENTD service should be disabled')
        ]

        for service, message in dangerous_services:
            if self._config_contains(service) and not self._config_contains(f'no {service}'):
                self.findings.append(ComplianceFinding(
                    rule_id="PCI-2.2-001",
                    title=f"Unnecessary Service Enabled: {service}",
                    description=message,
                    status=Status.FAILED,
                    severity=Severity.HIGH,
                    current_config=service,
                    recommendation=f"Disable service: no {service}",
                    remediation=f"Router(config)# no {service}"
                ))

    def _check_encrypted_management(self) -> None:
        """Ensure management access is encrypted."""
        # Check for unencrypted Telnet
        if self._config_contains('transport input telnet'):
            self.findings.append(ComplianceFinding(
                rule_id="PCI-2.3-001",
                title="Unencrypted Management Access (Telnet)",
                description="Telnet provides unencrypted access to device",
                status=Status.FAILED,
                severity=Severity.CRITICAL,
                recommendation="Use SSH instead of Telnet for management access",
                remediation="line vty 0 4\n transport input ssh\n"
            ))

        # Check for HTTP (should use HTTPS)
        if self._config_contains('ip http server') and not self._config_contains('ip http secure-server'):
            self.findings.append(ComplianceFinding(
                rule_id="PCI-2.3-002",
                title="HTTP Server Enabled Without HTTPS",
                description="HTTP provides unencrypted web access",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Enable HTTPS and disable HTTP",
                remediation="ip http secure-server\nno ip http server\n"
            ))

    def _check_strong_authentication(self) -> None:
        """Check for strong authentication mechanisms."""
        if not self._config_contains('aaa new-model'):
            self.findings.append(ComplianceFinding(
                rule_id="PCI-8.2-001",
                title="AAA Not Configured",
                description="AAA (Authentication, Authorization, Accounting) is not enabled",
                status=Status.FAILED,
                severity=Severity.CRITICAL,
                recommendation="Enable AAA for centralized authentication",
                remediation="aaa new-model\naaa authentication login default group tacacs+ local\n",
                references=["PCI-DSS 8.2"]
            ))

    def _check_password_complexity(self) -> None:
        """Check password complexity requirements."""
        if not self._config_contains('security passwords min-length'):
            self.findings.append(ComplianceFinding(
                rule_id="PCI-8.2.3-001",
                title="Minimum Password Length Not Configured",
                description="Password minimum length requirement is not set",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Set minimum password length to at least 8 characters",
                remediation="security passwords min-length 8\n"
            ))

    def _check_logging(self) -> None:
        """Check logging configuration."""
        if not self._config_contains('logging'):
            self.findings.append(ComplianceFinding(
                rule_id="PCI-10.1-001",
                title="Logging Not Configured",
                description="System logging is not configured",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Configure logging to a syslog server",
                remediation="logging host <syslog-server>\nlogging trap informational\n"
            ))

        # Check for logging buffer size
        if not self._config_contains('logging buffered'):
            self.findings.append(ComplianceFinding(
                rule_id="PCI-10.1-002",
                title="Logging Buffer Not Configured",
                description="Local logging buffer is not configured",
                status=Status.WARNING,
                severity=Severity.MEDIUM,
                recommendation="Configure logging buffer for local log storage",
                remediation="logging buffered 51200 informational\n"
            ))

    def _check_firewall_rules(self) -> None:
        """Check firewall rule configuration (ASA specific)."""
        if not self._config_contains('access-list'):
            self.findings.append(ComplianceFinding(
                rule_id="PCI-1.1-001",
                title="No Access Lists Configured",
                description="No ACLs found in firewall configuration",
                status=Status.FAILED,
                severity=Severity.CRITICAL,
                recommendation="Configure access control lists to restrict traffic",
                remediation="Create appropriate access-list rules for your security zones"
            ))

    def _check_account_management(self) -> None:
        """Check account management practices."""
        # Check for privilege levels
        if self._config_contains('privilege exec level 15'):
            local_users = sum(1 for line in self.config_lines if 'username' in line.lower())
            if local_users > 5:
                self.findings.append(ComplianceFinding(
                    rule_id="NIST-AC-2-001",
                    title="Excessive Local User Accounts",
                    description=f"Found {local_users} local user accounts. Consider AAA.",
                    status=Status.WARNING,
                    severity=Severity.MEDIUM,
                    recommendation="Use centralized AAA for user management",
                    references=["NIST AC-2"]
                ))

    def _check_login_block(self) -> None:
        """Check for login failure blocking."""
        if not self._config_contains('login block-for'):
            self.findings.append(ComplianceFinding(
                rule_id="NIST-AC-7-001",
                title="Login Failure Blocking Not Configured",
                description="Device does not block login attempts after failures",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Configure login blocking after failed attempts",
                remediation="login block-for 300 attempts 3 within 60\n",
                references=["NIST AC-7"]
            ))

    def _check_audit_logging(self) -> None:
        """Check comprehensive audit logging."""
        required_logs = ['logging trap', 'logging buffered', 'logging console']
        missing = [log for log in required_logs if not self._config_contains(log)]

        if missing:
            self.findings.append(ComplianceFinding(
                rule_id="NIST-AU-2-001",
                title="Incomplete Audit Logging",
                description=f"Missing logging configuration: {', '.join(missing)}",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Configure all logging destinations",
                references=["NIST AU-2"]
            ))

    def _check_authenticator_management(self) -> None:
        """Check authenticator (password) management."""
        if not self._config_contains('service password-encryption'):
            self.findings.append(ComplianceFinding(
                rule_id="NIST-IA-5-001",
                title="Password Encryption Not Enabled",
                description="Service password-encryption is not configured",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Enable password encryption",
                remediation="service password-encryption\n",
                references=["NIST IA-5"]
            ))

    def _check_transmission_encryption(self) -> None:
        """Check for encrypted transmission protocols."""
        if self._config_contains('transport input') and 'ssh' not in self._get_config_value('transport input'):
            self.findings.append(ComplianceFinding(
                rule_id="NIST-SC-8-001",
                title="Unencrypted Remote Access Allowed",
                description="Non-SSH protocols allowed for remote access",
                status=Status.FAILED,
                severity=Severity.CRITICAL,
                recommendation="Restrict remote access to SSH only",
                remediation="line vty 0 4\n transport input ssh\n",
                references=["NIST SC-8"]
            ))

    def _check_session_timeout(self) -> None:
        """Check for session timeout configuration."""
        if not self._config_contains('exec-timeout'):
            self.findings.append(ComplianceFinding(
                rule_id="NIST-SC-10-001",
                title="Session Timeout Not Configured",
                description="Exec timeout not set for console/vty lines",
                status=Status.FAILED,
                severity=Severity.MEDIUM,
                recommendation="Configure session timeout (recommend 10 minutes)",
                remediation="line con 0\n exec-timeout 10 0\nline vty 0 4\n exec-timeout 10 0\n",
                references=["NIST SC-10"]
            ))

    def _check_hostname_configured(self) -> None:
        """Check if hostname is configured."""
        hostname = self._get_config_value('hostname')
        if not hostname or hostname.lower() in ['router', 'switch', 'firewall']:
            self.findings.append(ComplianceFinding(
                rule_id="CIS-1.1-001",
                title="Default Hostname",
                description="Device is using default or generic hostname",
                status=Status.FAILED,
                severity=Severity.LOW,
                recommendation="Set a unique, descriptive hostname",
                remediation="hostname <unique-name>\n",
                references=["CIS Benchmark 1.1"]
            ))

    def _check_enable_secret(self) -> None:
        """Check if enable secret is configured."""
        if not self._config_contains('enable secret'):
            if self._config_contains('enable password'):
                self.findings.append(ComplianceFinding(
                    rule_id="CIS-1.2-001",
                    title="Using Enable Password Instead of Enable Secret",
                    description="Enable password is less secure than enable secret",
                    status=Status.FAILED,
                    severity=Severity.HIGH,
                    recommendation="Use enable secret instead of enable password",
                    remediation="enable secret <strong-password>\nno enable password\n",
                    references=["CIS Benchmark 1.2"]
                ))
            else:
                self.findings.append(ComplianceFinding(
                    rule_id="CIS-1.2-002",
                    title="No Enable Secret Configured",
                    description="Enable secret is not configured",
                    status=Status.FAILED,
                    severity=Severity.CRITICAL,
                    recommendation="Configure enable secret",
                    remediation="enable secret <strong-password>\n",
                    references=["CIS Benchmark 1.2"]
                ))
        else:
            self.findings.append(ComplianceFinding(
                rule_id="CIS-1.2-003",
                title="Enable Secret Configured",
                description="Enable secret is properly configured",
                status=Status.PASSED,
                severity=Severity.INFO,
                references=["CIS Benchmark 1.2"]
            ))

    def _check_service_password_encryption(self) -> None:
        """Check if service password-encryption is enabled."""
        if not self._config_contains('service password-encryption'):
            self.findings.append(ComplianceFinding(
                rule_id="CIS-1.3-001",
                title="Password Encryption Not Enabled",
                description="Service password-encryption is not configured",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Enable service password-encryption",
                remediation="service password-encryption\n",
                references=["CIS Benchmark 1.3"]
            ))

    def _check_login_banner(self) -> None:
        """Check if login banner is configured."""
        if not self._config_contains('banner') and not self._config_contains('banner motd'):
            self.findings.append(ComplianceFinding(
                rule_id="CIS-1.4-001",
                title="Login Banner Not Configured",
                description="No login banner/warning message configured",
                status=Status.FAILED,
                severity=Severity.LOW,
                recommendation="Configure login banner with legal warning",
                remediation='banner motd # Authorized Access Only #\n',
                references=["CIS Benchmark 1.4"]
            ))

    def _check_disable_unnecessary_services(self) -> None:
        """Check that unnecessary services are disabled."""
        services_to_disable = [
            'cdp run',
            'ip source-route',
            'ip proxy-arp'
        ]

        for service in services_to_disable:
            if self._config_contains(service) and not self._config_contains(f'no {service}'):
                self.findings.append(ComplianceFinding(
                    rule_id=f"CIS-2.1-{service.replace(' ', '-')}",
                    title=f"Unnecessary Service Enabled: {service}",
                    description=f"{service} should be disabled for security",
                    status=Status.WARNING,
                    severity=Severity.MEDIUM,
                    recommendation=f"Disable service: no {service}",
                    remediation=f"no {service}\n",
                    references=["CIS Benchmark 2.1"]
                ))

    def _check_ntp_configured(self) -> None:
        """Check if NTP is configured."""
        if not self._config_contains('ntp server'):
            self.findings.append(ComplianceFinding(
                rule_id="CIS-3.1-001",
                title="NTP Not Configured",
                description="No NTP servers configured",
                status=Status.FAILED,
                severity=Severity.MEDIUM,
                recommendation="Configure NTP for accurate time synchronization",
                remediation="ntp server <ntp-server-ip>\n",
                references=["CIS Benchmark 3.1"]
            ))

    def _check_timezone(self) -> None:
        """Check if timezone is configured."""
        if not self._config_contains('clock timezone'):
            self.findings.append(ComplianceFinding(
                rule_id="CIS-3.2-001",
                title="Timezone Not Configured",
                description="Clock timezone is not set",
                status=Status.WARNING,
                severity=Severity.LOW,
                recommendation="Configure timezone for accurate log timestamps",
                remediation="clock timezone EST -5\n",
                references=["CIS Benchmark 3.2"]
            ))

    def _check_aaa_authentication(self) -> None:
        """Check AAA authentication configuration."""
        if not self._config_contains('aaa new-model'):
            self.findings.append(ComplianceFinding(
                rule_id="CIS-4.1-001",
                title="AAA Not Configured",
                description="AAA authentication is not enabled",
                status=Status.FAILED,
                severity=Severity.CRITICAL,
                recommendation="Enable AAA for centralized authentication",
                remediation="aaa new-model\naaa authentication login default group tacacs+ local\n",
                references=["CIS Benchmark 4.1"]
            ))

    def _check_ssh_version(self) -> None:
        """Check SSH version configuration."""
        if not self._config_contains('ip ssh version 2'):
            self.findings.append(ComplianceFinding(
                rule_id="CIS-5.1-001",
                title="SSH Version 2 Not Enforced",
                description="SSH version 2 is not explicitly configured",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Configure SSH version 2 only",
                remediation="ip ssh version 2\n",
                references=["CIS Benchmark 5.1"]
            ))

    def _check_logging_configured(self) -> None:
        """Check logging configuration."""
        if not self._config_contains('logging host') and not self._config_contains('logging server'):
            self.findings.append(ComplianceFinding(
                rule_id="CIS-6.1-001",
                title="Remote Logging Not Configured",
                description="No remote syslog server configured",
                status=Status.FAILED,
                severity=Severity.HIGH,
                recommendation="Configure remote syslog server",
                remediation="logging host <syslog-server>\nlogging trap informational\n",
                references=["CIS Benchmark 6.1"]
            ))

    # Helper methods

    def _config_contains(self, pattern: str) -> bool:
        """Check if configuration contains a pattern."""
        return any(pattern in line for line in self.config_lines)

    def _get_config_value(self, key: str) -> Optional[str]:
        """Get value for a configuration key."""
        for line in self.config_lines:
            if line.strip().startswith(key):
                parts = line.strip().split(maxsplit=1)
                return parts[1] if len(parts) > 1 else None
        return None

    def _generate_report(self) -> Dict[str, Any]:
        """Generate compliance report."""
        total = len(self.findings)
        passed = sum(1 for f in self.findings if f.status == Status.PASSED)
        failed = sum(1 for f in self.findings if f.status == Status.FAILED)
        warnings = sum(1 for f in self.findings if f.status == Status.WARNING)

        # Calculate score
        score = (passed / total * 100) if total > 0 else 0

        # Group by severity
        by_severity = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': [],
            'info': []
        }

        for finding in self.findings:
            by_severity[finding.severity.value].append({
                'rule_id': finding.rule_id,
                'title': finding.title,
                'description': finding.description,
                'status': finding.status.value,
                'current_config': finding.current_config,
                'recommendation': finding.recommendation,
                'remediation': finding.remediation,
                'references': finding.references
            })

        return {
            'summary': {
                'total_checks': total,
                'passed': passed,
                'failed': failed,
                'warnings': warnings,
                'compliance_score': round(score, 2),
                'overall_status': 'passed' if failed == 0 else 'failed'
            },
            'findings_by_severity': by_severity,
            'all_findings': [
                {
                    'rule_id': f.rule_id,
                    'title': f.title,
                    'description': f.description,
                    'status': f.status.value,
                    'severity': f.severity.value,
                    'current_config': f.current_config,
                    'recommendation': f.recommendation,
                    'remediation': f.remediation,
                    'references': f.references
                }
                for f in self.findings
            ]
        }
