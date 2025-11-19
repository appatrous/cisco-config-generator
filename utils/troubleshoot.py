"""
Troubleshooting command dictionary for various network protocols.

Maps protocol slugs to lists of common show/debug commands that help
diagnose issues with each feature.
"""
from typing import Dict, List


TROUBLESHOOT_COMMANDS: Dict[str, List[str]] = {
    # Routing protocols and static routes
    'static-routing': [
        'show ip route static',
        'show ipv6 route static'
    ],
    'ospf': [
        'show ip ospf',
        'show ip ospf neighbor',
        'show ip ospf database'
    ],
    'eigrp': [
        'show ip eigrp neighbors',
        'show ip eigrp topology',
        'show ip eigrp interfaces'
    ],
    'rip': [
        'show ip rip database',
        'show ip rip interface',
        'debug ip rip'
    ],
    'bgp4-plus': [
        'show ip bgp summary',
        'show ip bgp',
        'show ip bgp neighbors'
    ],
    # IPv6 variants
    'ospfv3': [
        'show ipv6 ospf',
        'show ipv6 ospf neighbor',
        'show ipv6 ospf database'
    ],
    'eigrpv6': [
        'show ipv6 eigrp neighbors',
        'show ipv6 eigrp topology'
    ],

    # High availability and redundancy protocols
    'vrrp': [
        'show vrrp',
        'debug vrrp'
    ],
    'hsrp': [
        'show standby',
        'debug standby'
    ],
    'glbp': [
        'show glbp',
        'debug glbp'
    ],

    # Address translation
    'static-nat': [
        'show ip nat translations',
        'show ip nat statistics'
    ],
    'dynamic-nat': [
        'show ip nat translations',
        'show ip nat statistics'
    ],
    'pat': [
        'show ip nat translations',
        'show ip nat statistics'
    ],

    # VLAN and Layer 2
    'vlan': [
        'show vlan brief',
        'show interfaces status'
    ],
    'vtp': [
        'show vtp status',
        'show vtp counters'
    ],
    'stp': [
        'show spanning-tree',
        'show spanning-tree vlan'
    ],
    'pvst-plus': [
        'show spanning-tree',
        'show spanning-tree vlan'
    ],
    'etherchannel': [
        'show etherchannel summary',
        'show interfaces port-channel'
    ],
    'lacp': [
        'show etherchannel summary',
        'show lacp neighbor'
    ],
    'private-vlan': [
        'show vlan private-vlan',
        'show interfaces switchport'
    ],
    'voice-vlan': [
        'show interfaces status',
        'show run interface <port>'
    ],
    'stackwise': [
        'show switch',
        'show switch stack-ports'
    ],

    # Discovery protocols and mirroring
    'cdp': [
        'show cdp neighbors',
        'show cdp neighbors detail'
    ],
    'lldp': [
        'show lldp neighbors',
        'show lldp neighbors detail'
    ],
    'span': [
        'show monitor session',
        'show run | section monitor session'
    ],
    'rspan': [
        'show monitor session',
        'show vlan remote-span'
    ],
    'erspan': [
        'show monitor session',
        'show run interface tunnel'
    ],

    # Access control and security
    'acl': [
        'show access-lists',
        'show ip access-lists'
    ],
    'object-groups': [
        'show run object-group'
    ],
    'asa-failover-clustering': [
        'show failover',
        'show failover history'
    ],
    'unicast-rpf': [
        'show ip interface',
        'show cef interface',
        'show ip verify source'
    ],

    # IPv6 and multicast
    'igmp': [
        'show ip igmp groups',
        'show ip igmp interface'
    ],
    'pim': [
        'show ip pim neighbors',
        'show ip pim interface',
        'show ip pim rp-map'
    ],
    'multicast-routing': [
        'show ip mroute',
        'show ip pim rp-mappings'
    ],

    # Services and performance
    'netflow': [
        'show ip cache flow',
        'show ip flow export'
    ],
    'qos': [
        'show policy-map interface',
        'show policy-map'
    ],
    'ntp-ptp': [
        'show ntp status',
        'show ntp associations'
    ],
    'aaa': [
        'show aaa servers',
        'debug aaa authentication'
    ],
    'snmp': [
        'show snmp',
        'show snmp community'
    ],
    'syslog': [
        'show logging',
        'show logging history'
    ],
    'dhcp-server-relay': [
        'show ip dhcp pool',
        'show ip dhcp binding',
        'show ip dhcp server statistics'
    ],
    'dhcp-snooping': [
        'show ip dhcp snooping',
        'show ip dhcp snooping binding'
    ],
    'dynamic-arp-inspection': [
        'show ip arp inspection',
        'show ip arp inspection statistics'
    ],
    'ip-source-guard': [
        'show ip verify source'
    ],
    'igmp-snooping': [
        'show ip igmp snooping',
        'show ip igmp snooping groups'
    ],

    # VPN and tunnels
    'gre': [
        'show interface tunnel',
        'show ip route'
    ],
    'ipsec': [
        'show crypto isakmp sa',
        'show crypto ipsec sa',
        'debug crypto isakmp'
    ],
    'ipsec-vpn': [
        'show crypto isakmp sa',
        'show crypto ipsec sa',
        'debug crypto isakmp'
    ],

    # Firewall and security features
    'ids-ips': [
        'show ips',
        'show ips statistics'
    ],
    'ssl-tls-inspection': [
        'show policy-map type inspect ssl',
        'show ssl cert'
    ],
    'gnoc': [
        'show run | section gnoc'
    ],
    'threat-detection': [
        'show threat-detection',
        'show threat-detection statistics'
    ],
    'embedded-event-manager': [
        'show event manager policy registered',
        'show event manager history events'
    ],
    'ssl-vpn': [
        'show vpn-sessiondb anyconnect',
        'show webvpn session'
    ],
    'anyconnect': [
        'show vpn-sessiondb anyconnect',
        'show webvpn session'
    ],
    'zone-based-firewall': [
        'show policy-map type inspect zone-pair',
        'show zone-pair security'
    ]
}


def get_troubleshoot_commands(protocol_slug: str) -> List[str]:
    """
    Get troubleshooting commands for a specific protocol.

    Args:
        protocol_slug: The protocol identifier slug

    Returns:
        List of troubleshooting commands for the protocol
    """
    return TROUBLESHOOT_COMMANDS.get(protocol_slug, [
        'show running-config',
        'show version',
        'show interfaces'
    ])
