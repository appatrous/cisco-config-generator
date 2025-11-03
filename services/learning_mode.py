"""
Learning Mode - Educational explanations for Cisco commands.

This module provides detailed explanations of Cisco IOS commands,
their syntax, purpose, best practices, and common pitfalls. Ideal
for network engineers learning Cisco technologies.
"""

from typing import Dict, List, Any, Optional
import re


class CommandExplainer:
    """Explain Cisco commands with educational context."""

    def __init__(self, platform: str = 'ios'):
        """
        Initialize command explainer.

        Args:
            platform: Device platform (ios, nxos, asa)
        """
        self.platform = platform
        self.command_database = self._load_command_database()

    def explain_configuration(self, config_cli: str) -> Dict[str, Any]:
        """
        Provide explanations for an entire configuration.

        Args:
            config_cli: Configuration text

        Returns:
            Dictionary with line-by-line explanations
        """
        explanations = []

        for line_num, line in enumerate(config_cli.split('\n'), 1):
            line = line.strip()
            if not line or line.startswith('!'):
                continue

            explanation = self.explain_command(line)
            if explanation:
                explanations.append({
                    'line_number': line_num,
                    'command': line,
                    **explanation
                })

        return {
            'total_commands': len(explanations),
            'explanations': explanations,
            'learning_resources': self._get_learning_resources()
        }

    def explain_command(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Explain a single command.

        Args:
            command: Command line to explain

        Returns:
            Dictionary with explanation, syntax, examples, etc.
        """
        command = command.strip()

        # Match command pattern
        for pattern, explanation_func in self.command_database.items():
            if re.match(pattern, command, re.IGNORECASE):
                return explanation_func(command)

        # Generic explanation for unknown commands
        return self._generic_explanation(command)

    def _load_command_database(self) -> Dict[str, callable]:
        """Load command patterns and their explanation functions."""
        return {
            # Global configuration
            r'^hostname\s+': self._explain_hostname,
            r'^enable\s+secret': self._explain_enable_secret,
            r'^enable\s+password': self._explain_enable_password,
            r'^service\s+password-encryption': self._explain_service_password_encryption,
            r'^banner\s+': self._explain_banner,

            # Interface configuration
            r'^interface\s+': self._explain_interface,
            r'^ip\s+address\s+': self._explain_ip_address,
            r'^no\s+shutdown': self._explain_no_shutdown,
            r'^shutdown': self._explain_shutdown,
            r'^description\s+': self._explain_description,
            r'^duplex\s+': self._explain_duplex,
            r'^speed\s+': self._explain_speed,

            # Switching
            r'^switchport\s+mode\s+': self._explain_switchport_mode,
            r'^switchport\s+access\s+vlan': self._explain_switchport_access_vlan,
            r'^switchport\s+trunk\s+': self._explain_switchport_trunk,
            r'^spanning-tree\s+': self._explain_spanning_tree,
            r'^vlan\s+\d+': self._explain_vlan,

            # Routing
            r'^ip\s+route\s+': self._explain_ip_route,
            r'^router\s+ospf': self._explain_router_ospf,
            r'^router\s+eigrp': self._explain_router_eigrp,
            r'^router\s+bgp': self._explain_router_bgp,
            r'^router\s+rip': self._explain_router_rip,
            r'^network\s+': self._explain_network,

            # Security
            r'^aaa\s+': self._explain_aaa,
            r'^access-list\s+': self._explain_access_list,
            r'^ip\s+access-group': self._explain_ip_access_group,
            r'^username\s+': self._explain_username,
            r'^line\s+': self._explain_line,
            r'^transport\s+input': self._explain_transport_input,
            r'^login\s+': self._explain_login,

            # Services
            r'^ntp\s+server': self._explain_ntp_server,
            r'^logging\s+': self._explain_logging,
            r'^snmp-server\s+': self._explain_snmp_server,
            r'^ip\s+dhcp\s+': self._explain_ip_dhcp,

            # NAT
            r'^ip\s+nat\s+': self._explain_ip_nat,

            # VPN & Crypto
            r'^crypto\s+': self._explain_crypto,
            r'^tunnel\s+': self._explain_tunnel,
        }

    # Explanation methods for specific commands

    def _explain_hostname(self, command: str) -> Dict[str, Any]:
        """Explain hostname command."""
        hostname = command.split(maxsplit=1)[1] if len(command.split()) > 1 else ""

        return {
            'category': 'Basic Configuration',
            'purpose': 'Sets the device hostname displayed in the CLI prompt',
            'explanation': f"This command changes the device name to '{hostname}'. The hostname appears in the "
                          "command prompt and is used in logging, SNMP, and other management protocols. "
                          "It helps identify the device in a network of many routers and switches.",
            'syntax': 'hostname <name>',
            'parameters': {
                'name': 'Alphanumeric name for the device (max 63 characters)'
            },
            'best_practices': [
                'Use descriptive, consistent naming convention',
                'Include location or function in the name (e.g., CORE-SW-01, BRANCH-RTR-NY)',
                'Avoid spaces and special characters',
                'Keep names relatively short but meaningful'
            ],
            'common_mistakes': [
                'Using default hostname (Router, Switch)',
                'Not following organizational naming standards',
                'Using names that are too generic'
            ],
            'related_commands': ['show running-config | include hostname'],
            'cli_level': 'Global configuration mode',
            'example': 'Router(config)# hostname CORE-ROUTER-01'
        }

    def _explain_enable_secret(self, command: str) -> Dict[str, Any]:
        """Explain enable secret command."""
        return {
            'category': 'Security',
            'purpose': 'Sets an encrypted password for privileged EXEC mode',
            'explanation': "Creates an MD5-hashed password required to enter enable mode (privilege level 15). "
                          "This is more secure than 'enable password' because it uses stronger encryption. "
                          "The enable secret takes precedence over enable password if both are configured.",
            'syntax': 'enable secret [level <level>] [0 | 5] <password>',
            'parameters': {
                'level': 'Privilege level (0-15), default is 15',
                '0': 'Password is in clear text (will be encrypted)',
                '5': 'Password is already MD5-hashed',
                'password': 'The password string'
            },
            'security_level': 'CRITICAL',
            'best_practices': [
                'Always use "enable secret" instead of "enable password"',
                'Use strong passwords (8+ characters, mixed case, numbers, symbols)',
                'Change default passwords immediately',
                'Use unique passwords for each device',
                'Consider using AAA authentication instead for centralized management'
            ],
            'common_mistakes': [
                'Using weak or default passwords (cisco, password, 123456)',
                'Using "enable password" instead of "enable secret"',
                'Sharing enable passwords across multiple devices'
            ],
            'related_commands': [
                'service password-encryption',
                'security passwords min-length <length>',
                'enable password'
            ],
            'cli_level': 'Global configuration mode',
            'example': 'Router(config)# enable secret MyStr0ngP@ssw0rd'
        }

    def _explain_interface(self, command: str) -> Dict[str, Any]:
        """Explain interface command."""
        interface_name = command.replace('interface', '').strip()

        return {
            'category': 'Interface Configuration',
            'purpose': 'Enters interface configuration mode for a specific interface',
            'explanation': f"Enters configuration mode for interface '{interface_name}'. In this mode, you can "
                          "configure IP addresses, speed, duplex, VLANs, and other interface-specific settings.",
            'syntax': 'interface <type> <number>',
            'parameters': {
                'type': 'Interface type (e.g., GigabitEthernet, FastEthernet, Serial, Loopback, Tunnel)',
                'number': 'Interface number (e.g., 0/0/1, 1/0, 100)'
            },
            'best_practices': [
                'Always add a description to document the interface purpose',
                'Configure appropriate speed and duplex settings',
                'Use "no shutdown" to activate the interface',
                'Consider using interface ranges for bulk configuration'
            ],
            'common_mistakes': [
                'Forgetting to use "no shutdown" to bring interface up',
                'Not documenting interface purpose in description',
                'Misconfiguring speed/duplex causing performance issues'
            ],
            'related_commands': [
                'show interfaces',
                'show ip interface brief',
                'interface range <type> <range>'
            ],
            'cli_level': 'Global configuration mode',
            'example': 'Router(config)# interface GigabitEthernet0/0/1'
        }

    def _explain_ip_address(self, command: str) -> Dict[str, Any]:
        """Explain IP address command."""
        parts = command.split()
        ip = parts[2] if len(parts) > 2 else 'X.X.X.X'
        mask = parts[3] if len(parts) > 3 else 'Y.Y.Y.Y'

        return {
            'category': 'IP Configuration',
            'purpose': 'Assigns an IP address and subnet mask to an interface',
            'explanation': f"Configures the interface with IP address {ip} and subnet mask {mask}. "
                          "This enables the router to forward IP packets on this interface and participate "
                          "in IP routing.",
            'syntax': 'ip address <ip-address> <subnet-mask> [secondary]',
            'parameters': {
                'ip-address': 'IPv4 address in dotted decimal format',
                'subnet-mask': 'Subnet mask in dotted decimal format',
                'secondary': '(Optional) Adds a secondary IP address to the interface'
            },
            'best_practices': [
                'Use consistent subnetting scheme across network',
                'Document IP addressing in a spreadsheet or IPAM tool',
                'Avoid using first and last addresses in subnet (network and broadcast)',
                'Use /30 or /31 for point-to-point links',
                'Consider using DHCP for client networks'
            ],
            'common_mistakes': [
                'Using wrong subnet mask',
                'IP address conflicts with other devices',
                'Forgetting to configure default gateway on end devices',
                'Not documenting IP assignments'
            ],
            'related_commands': [
                'show ip interface brief',
                'show ip interface <interface>',
                'show ip route connected'
            ],
            'cli_level': 'Interface configuration mode',
            'example': 'Router(config-if)# ip address 192.168.1.1 255.255.255.0'
        }

    def _explain_router_ospf(self, command: str) -> Dict[str, Any]:
        """Explain OSPF routing protocol."""
        process_id = re.search(r'ospf\s+(\d+)', command)
        pid = process_id.group(1) if process_id else 'N'

        return {
            'category': 'Routing Protocols',
            'purpose': 'Enables OSPF routing protocol and enters OSPF configuration mode',
            'explanation': f"Starts OSPF (Open Shortest Path First) routing process {pid}. OSPF is a link-state "
                          "routing protocol that uses Dijkstra's algorithm to calculate the shortest path. "
                          "It's ideal for large enterprise networks and supports VLSM, fast convergence, and "
                          "hierarchical network design with areas.",
            'syntax': 'router ospf <process-id>',
            'parameters': {
                'process-id': 'Local process identifier (1-65535). Only locally significant, '
                             'does not need to match on other routers'
            },
            'how_it_works': [
                '1. OSPF routers discover neighbors using Hello packets',
                '2. Routers exchange link-state information (LSAs)',
                '3. Each router builds a complete topology map (LSDB)',
                '4. SPF algorithm calculates best paths',
                '5. Routing table is populated with best routes'
            ],
            'key_concepts': {
                'Areas': 'OSPF uses areas for scalability. Area 0 is the backbone',
                'Router ID': 'Unique identifier for each OSPF router',
                'Cost': 'Metric based on bandwidth (100 Mbps / interface bandwidth)',
                'DR/BDR': 'Designated Router elected on multi-access networks',
                'LSA Types': 'Different types of link-state advertisements'
            },
            'best_practices': [
                'Use area 0 as the backbone, all areas must connect to it',
                'Manually set router ID for consistency',
                'Use interface costs or reference bandwidth to control paths',
                'Implement route summarization at area boundaries',
                'Use passive interfaces on user-facing interfaces',
                'Tune hello/dead timers for faster convergence if needed'
            ],
            'common_mistakes': [
                'Forgetting to configure "network" statements',
                'Mismatched OSPF timers preventing neighbor adjacency',
                'Incorrect area configuration',
                'Not setting router ID explicitly',
                'Running OSPF on management interfaces'
            ],
            'related_commands': [
                'network <network> <wildcard> area <area-id>',
                'router-id <ip-address>',
                'passive-interface <interface>',
                'show ip ospf neighbor',
                'show ip ospf database',
                'show ip route ospf'
            ],
            'cli_level': 'Global configuration mode',
            'example': f'Router(config)# router ospf {pid}\\nRouter(config-router)# network 192.168.1.0 0.0.0.255 area 0',
            'protocol_info': {
                'type': 'Link-State',
                'metric': 'Cost (based on bandwidth)',
                'administrative_distance': '110',
                'multicast_address': '224.0.0.5 (All OSPF routers), 224.0.0.6 (DR/BDR)',
                'standard': 'RFC 2328 (OSPFv2)'
            }
        }

    def _explain_access_list(self, command: str) -> Dict[str, Any]:
        """Explain access list command."""
        is_extended = bool(re.search(r'access-list\s+(10[0-9]|1[1-9][0-9]|2[0-5][0-9][0-9])', command))
        acl_type = "Extended" if is_extended else "Standard"

        return {
            'category': 'Security - Access Control',
            'purpose': 'Creates an access control list (ACL) to filter traffic',
            'explanation': f"Defines a {acl_type} ACL entry that filters traffic based on specified criteria. "
                          "ACLs are used for security (blocking unwanted traffic), QoS (classifying traffic), "
                          "NAT (identifying traffic to translate), and routing (filtering route updates).",
            'syntax': f'{acl_type} ACL syntax varies based on type',
            'acl_types': {
                'Standard (1-99, 1300-1999)': 'Filters based on source IP address only',
                'Extended (100-199, 2000-2699)': 'Filters based on source/dest IP, protocol, ports, etc.',
                'Named': 'Uses descriptive names instead of numbers'
            },
            'how_it_works': [
                '1. Traffic is compared against ACL entries from top to bottom',
                '2. First matching entry determines action (permit/deny)',
                '3. Implicit "deny any" at the end of every ACL',
                '4. ACL must be applied to interface (inbound or outbound) to take effect'
            ],
            'best_practices': [
                'Use named ACLs for better documentation',
                'Put most specific rules first',
                'Use "remarks" to document ACL entries',
                'Test ACLs before applying to production interfaces',
                'Place standard ACLs close to destination',
                'Place extended ACLs close to source',
                'Always include an explicit permit at the end if needed'
            ],
            'common_mistakes': [
                'Forgetting implicit deny at end',
                'Wrong order of ACL entries',
                'Applying ACL to wrong interface or direction',
                'Using standard ACL when extended is needed',
                'Not using "any" keyword correctly'
            ],
            'security_level': 'HIGH',
            'related_commands': [
                'ip access-group <acl> {in | out}',
                'show access-lists',
                'show ip interface <interface>',
                'clear access-list counters'
            ],
            'cli_level': 'Global configuration mode',
            'example': 'Router(config)# access-list 100 permit tcp any any eq 80\\n'
                      'Router(config)# access-list 100 deny ip any any\\n'
                      'Router(config)# interface gi0/0\\n'
                      'Router(config-if)# ip access-group 100 in'
        }

    def _explain_aaa(self, command: str) -> Dict[str, Any]:
        """Explain AAA configuration."""
        return {
            'category': 'Security - Authentication',
            'purpose': 'Configures AAA (Authentication, Authorization, and Accounting)',
            'explanation': "AAA provides a framework for controlling who can access the device (authentication), "
                          "what they can do (authorization), and tracking what they did (accounting). "
                          "This is essential for secure, auditable network device management.",
            'syntax': 'Various AAA commands for different functions',
            'aaa_components': {
                'Authentication': 'Verifies user identity (username/password, certificates, etc.)',
                'Authorization': 'Determines what authenticated users can do',
                'Accounting': 'Logs user activities for audit and billing'
            },
            'how_it_works': [
                '1. User attempts to access device',
                '2. Device checks authentication policy',
                '3. If using external AAA server (TACACS+/RADIUS), query is sent',
                '4. Server responds with permit/deny',
                '5. If permit, authorization is checked',
                '6. User commands are logged for accounting'
            ],
            'common_aaa_commands': {
                'aaa new-model': 'Enables AAA functionality',
                'aaa authentication login default': 'Sets default login authentication method',
                'aaa authorization exec default': 'Sets authorization for EXEC shell',
                'aaa accounting exec default': 'Enables accounting for EXEC sessions',
                'tacacs-server host': 'Configures TACACS+ server',
                'radius server': 'Configures RADIUS server'
            },
            'security_level': 'CRITICAL',
            'best_practices': [
                'Always configure "local" as backup authentication method',
                'Use TACACS+ for device administration (better accounting)',
                'Use RADIUS for network access control (802.1X)',
                'Encrypt server communication',
                'Have console access available before enabling AAA',
                'Test authentication before logging out'
            ],
            'common_mistakes': [
                'Not configuring local fallback - can lock yourself out',
                'Not testing before disconnecting',
                'Using weak shared secrets for AAA servers',
                'Not monitoring AAA server availability'
            ],
            'related_commands': [
                'aaa new-model',
                'aaa authentication login default group tacacs+ local',
                'tacacs-server host <ip> key <secret>',
                'show aaa sessions',
                'debug aaa authentication'
            ],
            'cli_level': 'Global configuration mode',
            'example': 'Router(config)# aaa new-model\\n'
                      'Router(config)# aaa authentication login default group tacacs+ local\\n'
                      'Router(config)# tacacs-server host 10.1.1.100 key MyS3cretKey'
        }

    def _explain_ntp_server(self, command: str) -> Dict[str, Any]:
        """Explain NTP server configuration."""
        return {
            'category': 'Services - Time Management',
            'purpose': 'Configures Network Time Protocol (NTP) server for time synchronization',
            'explanation': "Synchronizes the device clock with an NTP server. Accurate time is crucial for "
                          "log correlation, troubleshooting, certificate validation, and time-based ACLs. "
                          "Without NTP, device clocks drift and logs become unreliable.",
            'syntax': 'ntp server <ip-address> [prefer] [version <1-4>] [key <key-id>]',
            'parameters': {
                'ip-address': 'IP address or hostname of NTP server',
                'prefer': 'Makes this the preferred NTP server',
                'version': 'NTP protocol version (default is 3)',
                'key': 'Authentication key ID for secure NTP'
            },
            'importance': 'Critical for security auditing and troubleshooting',
            'best_practices': [
                'Configure at least two NTP servers for redundancy',
                'Use internal NTP servers that sync to external sources',
                'Use NTP authentication in secure environments',
                'Configure timezone correctly for local log readability',
                'Verify NTP synchronization status regularly'
            ],
            'common_mistakes': [
                'Configuring only one NTP server (no redundancy)',
                'Using public NTP servers directly from all devices',
                'Not checking if NTP is blocked by firewall',
                'Forgetting to configure timezone'
            ],
            'related_commands': [
                'show ntp associations',
                'show ntp status',
                'clock timezone <zone> <offset>',
                'clock summer-time <zone> recurring',
                'ntp authenticate',
                'ntp authentication-key'
            ],
            'cli_level': 'Global configuration mode',
            'example': 'Router(config)# ntp server 10.1.1.10 prefer\\n'
                      'Router(config)# ntp server 10.1.1.11\\n'
                      'Router(config)# clock timezone EST -5'
        }

    def _explain_logging(self, command: str) -> Dict[str, Any]:
        """Explain logging configuration."""
        return {
            'category': 'Services - Logging',
            'purpose': 'Configures system logging (syslog) for monitoring and troubleshooting',
            'explanation': "Enables logging of system events, errors, and security events. Logs can be sent to "
                          "local buffer, console, terminal lines, or remote syslog server. Essential for "
                          "troubleshooting, security monitoring, and compliance.",
            'syntax': 'Various logging commands',
            'logging_destinations': {
                'Console': 'Logs to console port (logging console)',
                'Monitor': 'Logs to VTY lines (logging monitor)',
                'Buffer': 'Logs to RAM (logging buffered)',
                'Host': 'Logs to syslog server (logging host <ip>)',
                'Trap': 'Sets syslog level for remote logging'
            },
            'severity_levels': {
                '0 - emergencies': 'System unusable',
                '1 - alerts': 'Immediate action needed',
                '2 - critical': 'Critical conditions',
                '3 - errors': 'Error conditions',
                '4 - warnings': 'Warning conditions',
                '5 - notifications': 'Normal but significant',
                '6 - informational': 'Informational messages',
                '7 - debugging': 'Debug messages'
            },
            'best_practices': [
                'Always configure remote syslog server',
                'Use appropriate severity levels (informational for production)',
                'Increase buffer size for local logging',
                'Disable console logging in production (performance impact)',
                'Use NTP for accurate log timestamps',
                'Configure logging source-interface for consistent source IP'
            ],
            'common_mistakes': [
                'Console logging enabled in production (causes performance issues)',
                'Buffer size too small',
                'Not configuring remote logging',
                'Using debug level in production',
                'Not correlating logs from multiple devices'
            ],
            'related_commands': [
                'logging buffered 51200 informational',
                'logging host 10.1.1.50',
                'logging trap informational',
                'logging source-interface <interface>',
                'no logging console',
                'show logging',
                'clear logging'
            ],
            'cli_level': 'Global configuration mode',
            'example': 'Router(config)# logging buffered 51200 informational\\n'
                      'Router(config)# logging host 10.1.1.50\\n'
                      'Router(config)# logging trap informational\\n'
                      'Router(config)# no logging console'
        }

    def _explain_generic(self, command: str) -> Dict[str, Any]:
        """Generic explanation for unknown commands."""
        return {
            'category': 'Configuration Command',
            'command': command,
            'explanation': 'This is a Cisco IOS configuration command. Refer to Cisco documentation for detailed '
                          'information about this specific command.',
            'recommendation': 'Use "?" in the CLI for context-sensitive help on this command',
            'related_commands': ['show running-config', '?'],
            'cli_level': 'Varies by command'
        }

    # Add more explanation methods for other commands...
    # (For brevity, I'm including placeholders for remaining methods)

    def _explain_enable_password(self, cmd): return self._generic_explanation(cmd)
    def _explain_service_password_encryption(self, cmd): return self._generic_explanation(cmd)
    def _explain_banner(self, cmd): return self._generic_explanation(cmd)
    def _explain_no_shutdown(self, cmd): return self._generic_explanation(cmd)
    def _explain_shutdown(self, cmd): return self._generic_explanation(cmd)
    def _explain_description(self, cmd): return self._generic_explanation(cmd)
    def _explain_duplex(self, cmd): return self._generic_explanation(cmd)
    def _explain_speed(self, cmd): return self._generic_explanation(cmd)
    def _explain_switchport_mode(self, cmd): return self._generic_explanation(cmd)
    def _explain_switchport_access_vlan(self, cmd): return self._generic_explanation(cmd)
    def _explain_switchport_trunk(self, cmd): return self._generic_explanation(cmd)
    def _explain_spanning_tree(self, cmd): return self._generic_explanation(cmd)
    def _explain_vlan(self, cmd): return self._generic_explanation(cmd)
    def _explain_ip_route(self, cmd): return self._generic_explanation(cmd)
    def _explain_router_eigrp(self, cmd): return self._generic_explanation(cmd)
    def _explain_router_bgp(self, cmd): return self._generic_explanation(cmd)
    def _explain_router_rip(self, cmd): return self._generic_explanation(cmd)
    def _explain_network(self, cmd): return self._generic_explanation(cmd)
    def _explain_ip_access_group(self, cmd): return self._generic_explanation(cmd)
    def _explain_username(self, cmd): return self._generic_explanation(cmd)
    def _explain_line(self, cmd): return self._generic_explanation(cmd)
    def _explain_transport_input(self, cmd): return self._generic_explanation(cmd)
    def _explain_login(self, cmd): return self._generic_explanation(cmd)
    def _explain_snmp_server(self, cmd): return self._generic_explanation(cmd)
    def _explain_ip_dhcp(self, cmd): return self._generic_explanation(cmd)
    def _explain_ip_nat(self, cmd): return self._generic_explanation(cmd)
    def _explain_crypto(self, cmd): return self._generic_explanation(cmd)
    def _explain_tunnel(self, cmd): return self._generic_explanation(cmd)

    def _get_learning_resources(self) -> List[Dict[str, str]]:
        """Return learning resources and references."""
        return [
            {
                'title': 'Cisco IOS Command Reference',
                'url': 'https://www.cisco.com/c/en/us/support/ios-nx-os-software/ios-15-4m-t/products-command-reference-list.html',
                'description': 'Official Cisco IOS command reference documentation'
            },
            {
                'title': 'Cisco Networking Academy',
                'url': 'https://www.netacad.com/',
                'description': 'Free and paid courses on Cisco technologies (CCNA, CCNP, etc.)'
            },
            {
                'title': 'Packet Tracer',
                'url': 'https://www.netacad.com/courses/packet-tracer',
                'description': 'Network simulation tool for practicing configurations'
            },
            {
                'title': 'Cisco Learning Network',
                'url': 'https://learningnetwork.cisco.com/',
                'description': 'Community forums and study materials'
            }
        ]


def generate_tutorial(topic: str) -> Dict[str, Any]:
    """
    Generate a tutorial for a specific networking topic.

    Args:
        topic: Topic name (e.g., 'ospf', 'vlans', 'acl')

    Returns:
        Tutorial content with examples and exercises
    """
    tutorials = {
        'ospf': {
            'title': 'OSPF Configuration Tutorial',
            'difficulty': 'Intermediate',
            'duration': '30 minutes',
            'objectives': [
                'Understand OSPF operation and terminology',
                'Configure single-area OSPF',
                'Verify OSPF neighbors and routes',
                'Troubleshoot common OSPF issues'
            ],
            'steps': [
                {
                    'step': 1,
                    'title': 'Enable OSPF Process',
                    'commands': ['router ospf 1', 'router-id 1.1.1.1'],
                    'explanation': 'Start OSPF process with ID 1 and set router ID'
                },
                {
                    'step': 2,
                    'title': 'Advertise Networks',
                    'commands': ['network 192.168.1.0 0.0.0.255 area 0'],
                    'explanation': 'Advertise network into OSPF area 0'
                },
                {
                    'step': 3,
                    'title': 'Verify Configuration',
                    'commands': ['show ip ospf neighbor', 'show ip route ospf'],
                    'explanation': 'Check OSPF neighbors and routes learned'
                }
            ],
            'practice_exercises': [
                'Configure OSPF on a 3-router topology',
                'Implement multi-area OSPF with area 0 and area 1',
                'Configure OSPF authentication',
                'Troubleshoot OSPF neighbor issues'
            ]
        },
        'vlans': {
            'title': 'VLAN Configuration Tutorial',
            'difficulty': 'Beginner',
            'duration': '20 minutes',
            'objectives': [
                'Understand VLAN concepts and benefits',
                'Create and configure VLANs',
                'Assign ports to VLANs',
                'Configure trunk links'
            ],
            'steps': [
                {
                    'step': 1,
                    'title': 'Create VLANs',
                    'commands': ['vlan 10', 'name SALES', 'vlan 20', 'name ENGINEERING'],
                    'explanation': 'Create VLANs with descriptive names'
                },
                {
                    'step': 2,
                    'title': 'Assign Ports to VLANs',
                    'commands': ['interface gi0/1', 'switchport mode access', 'switchport access vlan 10'],
                    'explanation': 'Configure port as access port in VLAN 10'
                },
                {
                    'step': 3,
                    'title': 'Configure Trunk',
                    'commands': ['interface gi0/24', 'switchport mode trunk', 'switchport trunk allowed vlan 10,20'],
                    'explanation': 'Configure trunk to carry multiple VLANs'
                }
            ],
            'practice_exercises': [
                'Create 4 VLANs for different departments',
                'Configure inter-VLAN routing',
                'Implement VLAN pruning',
                'Configure voice VLAN'
            ]
        }
    }

    return tutorials.get(topic.lower(), {
        'error': 'Tutorial not found',
        'available_tutorials': list(tutorials.keys())
    })
