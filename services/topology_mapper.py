"""
Network Topology Mapper - Visualize network topologies from configurations.

This module analyzes Cisco configurations and automatically generates
network topology diagrams showing device connections, interfaces, and
protocol relationships (OSPF neighbors, BGP peers, etc.).
"""

import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
import json
import re
from collections import defaultdict


class TopologyMapper:
    """
    Analyze configurations and build network topology visualization.

    Supports:
    - Physical connections (based on interface configs and CDP/LLDP)
    - Logical connections (routing protocols)
    - Layer 2 (VLANs, trunks, EtherChannels)
    - Layer 3 (IP subnets, routing)
    """

    def __init__(self):
        self.graph = nx.Graph()
        self.devices = {}
        self.connections = []
        self.subnets = defaultdict(list)

    def parse_configuration(self, config_cli: str, device_name: str, platform: str = 'ios') -> None:
        """
        Parse a device configuration and extract topology information.

        Args:
            config_cli: CLI configuration text
            device_name: Name of the device
            platform: Platform type (ios, nxos, asa)
        """
        device_data = {
            'name': device_name,
            'platform': platform,
            'interfaces': {},
            'routing_protocols': [],
            'neighbors': [],
            'vlans': []
        }

        # Parse interfaces
        interface_blocks = self._extract_interface_blocks(config_cli)
        for intf_name, intf_config in interface_blocks.items():
            intf_data = self._parse_interface(intf_config)
            device_data['interfaces'][intf_name] = intf_data

            # Track subnets
            if 'ip_address' in intf_data and intf_data['ip_address']:
                subnet = self._get_subnet(intf_data['ip_address'], intf_data.get('subnet_mask'))
                if subnet:
                    self.subnets[subnet].append({
                        'device': device_name,
                        'interface': intf_name,
                        'ip': intf_data['ip_address']
                    })

        # Parse routing protocols
        device_data['routing_protocols'] = self._parse_routing_protocols(config_cli)

        # Parse VLANs
        device_data['vlans'] = self._parse_vlans(config_cli)

        # Store device
        self.devices[device_name] = device_data
        self.graph.add_node(device_name, **device_data)

    def _extract_interface_blocks(self, config: str) -> Dict[str, str]:
        """Extract interface configuration blocks."""
        interfaces = {}
        current_intf = None
        current_config = []

        for line in config.split('\n'):
            line = line.strip()

            # New interface block
            if line.startswith('interface '):
                if current_intf:
                    interfaces[current_intf] = '\n'.join(current_config)
                current_intf = line.replace('interface ', '').strip()
                current_config = [line]
            elif current_intf and (line.startswith(' ') or not line):
                current_config.append(line)
            elif current_intf:
                # End of interface block
                interfaces[current_intf] = '\n'.join(current_config)
                current_intf = None
                current_config = []

        # Add last interface
        if current_intf:
            interfaces[current_intf] = '\n'.join(current_config)

        return interfaces

    def _parse_interface(self, intf_config: str) -> Dict[str, Any]:
        """Parse interface configuration block."""
        data = {
            'description': None,
            'ip_address': None,
            'subnet_mask': None,
            'status': 'up',
            'speed': None,
            'duplex': None,
            'vlan': None,
            'trunk': False,
            'allowed_vlans': [],
            'channel_group': None
        }

        for line in intf_config.split('\n'):
            line = line.strip()

            # Description
            if line.startswith('description '):
                data['description'] = line.replace('description ', '').strip()

            # IP address
            elif line.startswith('ip address '):
                parts = line.split()
                if len(parts) >= 3:
                    data['ip_address'] = parts[2]
                    if len(parts) >= 4:
                        data['subnet_mask'] = parts[3]

            # Shutdown status
            elif line == 'shutdown':
                data['status'] = 'down'

            # VLAN access
            elif 'switchport access vlan' in line:
                match = re.search(r'vlan\s+(\d+)', line)
                if match:
                    data['vlan'] = int(match.group(1))

            # Trunk
            elif 'switchport mode trunk' in line:
                data['trunk'] = True

            # Allowed VLANs on trunk
            elif 'switchport trunk allowed vlan' in line:
                match = re.search(r'vlan\s+([\d,\-]+)', line)
                if match:
                    data['allowed_vlans'] = self._parse_vlan_list(match.group(1))

            # Channel group
            elif 'channel-group' in line:
                match = re.search(r'channel-group\s+(\d+)', line)
                if match:
                    data['channel_group'] = int(match.group(1))

            # Speed
            elif line.startswith('speed '):
                data['speed'] = line.replace('speed ', '').strip()

            # Duplex
            elif line.startswith('duplex '):
                data['duplex'] = line.replace('duplex ', '').strip()

        return data

    def _parse_routing_protocols(self, config: str) -> List[Dict[str, Any]]:
        """Parse routing protocol configurations."""
        protocols = []

        # OSPF
        if 'router ospf' in config:
            ospf_data = {'protocol': 'OSPF', 'process_id': None, 'router_id': None, 'networks': []}
            for line in config.split('\n'):
                if line.strip().startswith('router ospf'):
                    match = re.search(r'ospf\s+(\d+)', line)
                    if match:
                        ospf_data['process_id'] = int(match.group(1))
                elif 'router-id' in line:
                    match = re.search(r'router-id\s+([\d.]+)', line)
                    if match:
                        ospf_data['router_id'] = match.group(1)
                elif 'network' in line and 'area' in line:
                    match = re.search(r'network\s+([\d.]+)\s+([\d.]+)\s+area\s+([\d.]+)', line)
                    if match:
                        ospf_data['networks'].append({
                            'network': match.group(1),
                            'wildcard': match.group(2),
                            'area': match.group(3)
                        })
            protocols.append(ospf_data)

        # EIGRP
        if 'router eigrp' in config:
            eigrp_data = {'protocol': 'EIGRP', 'as_number': None, 'networks': []}
            for line in config.split('\n'):
                if line.strip().startswith('router eigrp'):
                    match = re.search(r'eigrp\s+(\d+)', line)
                    if match:
                        eigrp_data['as_number'] = int(match.group(1))
                elif 'network' in line:
                    match = re.search(r'network\s+([\d.]+)', line)
                    if match:
                        eigrp_data['networks'].append(match.group(1))
            protocols.append(eigrp_data)

        # BGP
        if 'router bgp' in config:
            bgp_data = {'protocol': 'BGP', 'as_number': None, 'neighbors': []}
            for line in config.split('\n'):
                if line.strip().startswith('router bgp'):
                    match = re.search(r'bgp\s+(\d+)', line)
                    if match:
                        bgp_data['as_number'] = int(match.group(1))
                elif 'neighbor' in line and 'remote-as' in line:
                    match = re.search(r'neighbor\s+([\d.]+)\s+remote-as\s+(\d+)', line)
                    if match:
                        bgp_data['neighbors'].append({
                            'ip': match.group(1),
                            'remote_as': int(match.group(2))
                        })
            protocols.append(bgp_data)

        return protocols

    def _parse_vlans(self, config: str) -> List[Dict[str, Any]]:
        """Parse VLAN configurations."""
        vlans = []
        for line in config.split('\n'):
            if line.strip().startswith('vlan '):
                match = re.search(r'vlan\s+(\d+)', line)
                if match:
                    vlan_id = int(match.group(1))
                    # Try to find name on same or next line
                    name_match = re.search(r'name\s+(\S+)', line)
                    vlans.append({
                        'id': vlan_id,
                        'name': name_match.group(1) if name_match else f"VLAN{vlan_id:04d}"
                    })
        return vlans

    def _parse_vlan_list(self, vlan_str: str) -> List[int]:
        """Parse VLAN list string (e.g., '1,2,5-10' -> [1, 2, 5, 6, 7, 8, 9, 10])."""
        vlans = []
        for part in vlan_str.split(','):
            if '-' in part:
                start, end = map(int, part.split('-'))
                vlans.extend(range(start, end + 1))
            else:
                vlans.append(int(part))
        return vlans

    def _get_subnet(self, ip: str, mask: Optional[str]) -> Optional[str]:
        """Get subnet in CIDR notation."""
        if not ip or not mask:
            return None
        try:
            from netaddr import IPNetwork
            network = IPNetwork(f"{ip}/{mask}")
            return str(network.cidr)
        except:
            return None

    def infer_connections(self) -> None:
        """
        Infer device connections based on:
        1. Same subnet connections (Layer 3)
        2. Routing protocol adjacencies
        3. Trunk links (Layer 2)
        """
        # Connect devices on same subnet
        for subnet, endpoints in self.subnets.items():
            if len(endpoints) >= 2:
                for i, ep1 in enumerate(endpoints):
                    for ep2 in endpoints[i + 1:]:
                        self._add_connection(
                            ep1['device'], ep2['device'],
                            connection_type='L3',
                            subnet=subnet,
                            interface1=ep1['interface'],
                            interface2=ep2['interface']
                        )

        # Connect devices with routing protocol relationships
        self._infer_routing_connections()

    def _infer_routing_connections(self) -> None:
        """Infer connections based on routing protocols."""
        # BGP neighbors
        for device_name, device_data in self.devices.items():
            for proto in device_data.get('routing_protocols', []):
                if proto['protocol'] == 'BGP':
                    for neighbor in proto.get('neighbors', []):
                        # Find device with this IP
                        target_device = self._find_device_by_ip(neighbor['ip'])
                        if target_device and target_device != device_name:
                            self._add_connection(
                                device_name, target_device,
                                connection_type='BGP',
                                details=f"AS {proto['as_number']} <-> AS {neighbor['remote_as']}"
                            )

    def _find_device_by_ip(self, ip: str) -> Optional[str]:
        """Find device name by IP address."""
        for device_name, device_data in self.devices.items():
            for intf_name, intf_data in device_data.get('interfaces', {}).items():
                if intf_data.get('ip_address') == ip:
                    return device_name
        return None

    def _add_connection(self, device1: str, device2: str, connection_type: str = 'physical',
                       **kwargs) -> None:
        """Add connection between two devices."""
        connection = {
            'source': device1,
            'target': device2,
            'type': connection_type,
            **kwargs
        }

        # Avoid duplicates
        if connection not in self.connections:
            self.connections.append(connection)
            self.graph.add_edge(device1, device2, **connection)

    def generate_visualization_data(self) -> Dict[str, Any]:
        """
        Generate data structure for visualization libraries.

        Returns:
            Dictionary with nodes and edges suitable for D3.js, Cytoscape, etc.
        """
        nodes = []
        for device_name, device_data in self.devices.items():
            nodes.append({
                'id': device_name,
                'label': device_name,
                'platform': device_data.get('platform', 'unknown'),
                'interfaces_count': len(device_data.get('interfaces', {})),
                'protocols': [p['protocol'] for p in device_data.get('routing_protocols', [])],
                'vlans_count': len(device_data.get('vlans', []))
            })

        edges = []
        for conn in self.connections:
            edges.append({
                'source': conn['source'],
                'target': conn['target'],
                'type': conn['type'],
                'label': conn.get('details', conn['type']),
                'subnet': conn.get('subnet'),
                'interface1': conn.get('interface1'),
                'interface2': conn.get('interface2')
            })

        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'devices_count': len(nodes),
                'connections_count': len(edges),
                'subnets_count': len(self.subnets)
            }
        }

    def export_to_json(self) -> str:
        """Export topology as JSON."""
        return json.dumps(self.generate_visualization_data(), indent=2)

    def export_to_graphml(self, filename: str) -> None:
        """Export topology as GraphML for use in graph visualization tools."""
        nx.write_graphml(self.graph, filename)

    def get_device_summary(self, device_name: str) -> Optional[Dict[str, Any]]:
        """Get summary information for a specific device."""
        if device_name not in self.devices:
            return None

        device_data = self.devices[device_name]
        connections = [c for c in self.connections
                      if c['source'] == device_name or c['target'] == device_name]

        return {
            'name': device_name,
            'platform': device_data.get('platform'),
            'interfaces': len(device_data.get('interfaces', {})),
            'vlans': len(device_data.get('vlans', [])),
            'routing_protocols': device_data.get('routing_protocols', []),
            'connections': len(connections),
            'neighbors': list(set([
                c['target'] if c['source'] == device_name else c['source']
                for c in connections
            ]))
        }

    def get_topology_statistics(self) -> Dict[str, Any]:
        """Get overall topology statistics."""
        return {
            'total_devices': len(self.devices),
            'total_connections': len(self.connections),
            'total_subnets': len(self.subnets),
            'platforms': {
                platform: sum(1 for d in self.devices.values() if d.get('platform') == platform)
                for platform in set(d.get('platform') for d in self.devices.values())
            },
            'routing_protocols': {
                proto: sum(1 for d in self.devices.values()
                          if any(p['protocol'] == proto for p in d.get('routing_protocols', [])))
                for proto in set(p['protocol']
                                for d in self.devices.values()
                                for p in d.get('routing_protocols', []))
            }
        }
