# Network Configuration Generator

**Multi-Vendor NetDevOps Tool for Enterprise and Data Center Networks**

A comprehensive, production-ready web application and CLI tool that generates network device configurations from structured data (JSON/YAML) for multiple vendor platforms.

## 🌟 Features

### Multi-Vendor Support
- **Cisco IOS/IOS-XE** - Campus and Edge routers/switches
- **Cisco NX-OS** - Data Center switches (Nexus 9K/7K)
- **Arista EOS** - Data Center and campus switches
- **Juniper Junos** - EX/QFX switches, set-style configuration
- **FRRouting (FRR)** - Open-source routing platform

### Comprehensive Protocol Coverage

#### Layer 2
- **VLANs & Trunking** (802.1Q, QinQ)
- **Spanning Tree** (STP, RSTP, MSTP, PVST+)
- **Link Aggregation** (LAG/LACP - 802.1AX)
- **MLAG/vPC/MC-LAG** - Multi-chassis LAG with anycast VTEP
- **Discovery** - LLDP (802.1AB) / CDP
- **Security**:
  - Port Security (sticky MAC, violation modes)
  - DHCP Snooping (Option 82, trusted ports)
  - Dynamic ARP Inspection (DAI)
  - IP Source Guard (IPSG)
  - 802.1X (EAP, MAB, guest VLAN, critical VLAN)
  - MACsec (802.1AE)
- **IGMP/MLD Snooping** - Multicast optimization

#### Layer 3
- **Routing Protocols**:
  - **OSPFv2/v3** - All area types (normal, stub, NSSA), authentication, BFD
  - **IS-IS** - Multi-topology, wide metrics, SR-MPLS/SRv6
  - **EIGRP** - Named mode, stub, variance (Cisco)
  - **BGP** - IPv4/IPv6 unicast, L2VPN EVPN, route policies, RPKI/ROV
  - **RIP v2 / RIPng** (optional, legacy)
- **Static Routing & PBR** - Policy-based routing with tracking
- **VRF / VRF-Lite** - Route Distinguisher, Route Targets
- **FHRP** - HSRP, VRRP, GLBP with tracking and BFD
- **Multicast**:
  - PIM (Sparse-Mode, SSM, BiDir)
  - IGMP/MLD versions
  - RP configuration (static, BSR, Anycast-RP)
  - MSDP for Anycast-RP
- **NAT** - Static, Dynamic, PAT, NAT64, NPTv6

#### Advanced Features
- **VXLAN / EVPN** - Data Center fabric (L2VNI, L3VNI, anycast gateway)
- **MPLS** - LDP, RSVP-TE, L3VPN (VPNv4/VPNv6)
- **Segment Routing** - SR-MPLS and SRv6 with TI-LFA
- **BFD** - Bidirectional Forwarding Detection for fast failure detection
- **QoS / CoPP** - Classification, marking, policing, shaping, queuing

### Smart Validation & Linting
- **Strict Validation**:
  - IP address and CIDR format checking
  - ASN, VLAN, VNI range validation
  - VRF/VLAN/RP cross-reference checking
  - Route Distinguisher / Route Target format validation
- **Configuration Linter**:
  - Empty section detection
  - Duplicate line detection
  - Syntax error checking
  - Stable ordering verification

### Modern Web Interface
- **Tile-based UI** - Protocol selection by category (L2, L3, Advanced)
- **Vendor Selector** - Auto-hide unsupported features per platform
- **Live Preview** - Real-time configuration generation
- **Diff View** - Compare configurations before deployment
- **Import/Export** - JSON/YAML configuration profiles
- **Hierarchical Profiles** - Global → Site → Role → Device inheritance

### CLI Tool
- Offline configuration generation
- Batch processing for multiple devices
- Golden test generation and validation
- Scriptable for CI/CD pipelines

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip or Poetry

### Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd cisco-config-generator

# Install dependencies
pip install -r requirements.txt

# Run the web application
python app_modern.py

# Or use the CLI
python cli_generate.py --vendor ios --config examples/profiles/campus-access-switch.json --output output/
```

The web interface will be available at: `http://localhost:5000`

## 🚀 Usage

### Web Interface

1. **Select Vendor** - Choose target platform (IOS, NX-OS, EOS, Junos, FRR)
2. **Activate Protocols** - Click on tiles to enable desired protocols
3. **Configure** - Fill in protocol-specific forms (or import JSON)
4. **Generate** - Click "Generate Configuration"
5. **Review** - Preview configuration, view validation results
6. **Download** - Save as `.cfg` or `.conf` file

### REST API

#### Generate Configuration

```bash
POST /api/generate
Content-Type: application/json

{
  "vendor": "ios",
  "config": {
    "global": {
      "hostname": "router1"
    },
    "l3": {
      "ospf": [{
        "process_id": 10,
        "router_id": "1.1.1.1"
      }]
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "config": "hostname router1\n...",
  "validation": {
    "is_valid": true,
    "errors": [],
    "warnings": []
  },
  "linting": {
    "errors": [],
    "warnings": [],
    "line_count": 42
  }
}
```

#### Validate Configuration

```bash
POST /api/validate
Content-Type: application/json

{
  "config": { ... },
  "vendor": "ios"
}
```

#### Multi-Vendor Generation

```bash
POST /api/generate-multi
Content-Type: application/json

{
  "vendors": ["ios", "nxos", "eos"],
  "config": { ... }
}
```

**Response:**
```json
{
  "success": true,
  "configs": {
    "ios": "hostname router1\n...",
    "nxos": "hostname router1\n...",
    "eos": "hostname router1\n..."
  }
}
```

### CLI Tool

```bash
# Generate from JSON
python cli_generate.py \
  --vendor ios \
  --config examples/profiles/campus-access-switch.json \
  --output configs/

# Validate without generating
python cli_generate.py \
  --validate-only \
  --config examples/profiles/dc-leaf-evpn.json

# Multi-vendor generation
python cli_generate.py \
  --vendors ios,nxos,eos \
  --config myconfig.json \
  --output configs/

# Lint existing configuration
python cli_generate.py \
  --lint \
  --file router1.cfg \
  --vendor ios
```

## 📐 Configuration Schema

The tool uses a comprehensive JSON/YAML schema. See `schemas/network_config_schema.yaml` for the complete reference.

### Basic Example

```json
{
  "global": {
    "hostname": "router1",
    "domain_name": "example.com",
    "ntp_servers": ["10.0.0.1"]
  },
  "l2": {
    "vlans": [
      {"id": 10, "name": "DATA"},
      {"id": 20, "name": "VOICE"}
    ]
  },
  "l3": {
    "interfaces": [
      {
        "interface": "Vlan10",
        "ipv4": [{"address": "10.1.10.1/24"}]
      }
    ],
    "ospf": [{
      "process_id": 10,
      "router_id": "1.1.1.1",
      "areas": [{"id": "0.0.0.0"}],
      "interfaces": [
        {"interface": "Vlan10", "area": "0.0.0.0"}
      ]
    }]
  }
}
```

## 📚 Examples

The `examples/profiles/` directory contains real-world scenarios:

1. **campus-access-switch.json** - Access layer with port security, 802.1X, DHCP snooping
2. **campus-distribution-l3.json** - Distribution layer with OSPF and HSRP
3. **core-router-bgp.json** - Core router with BGP, OSPF, and MPLS
4. **dc-leaf-evpn.json** - Data Center leaf with VXLAN EVPN and vPC
5. **edge-router-nat.json** - Edge router with BGP, NAT, and firewall

Load examples in the web UI: Click **"Load Example"** button.

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest tests/

# Run specific test category
pytest tests/test_renderer.py
pytest tests/test_validator.py
pytest tests/golden/

# Generate golden test configs
python tests/generate_golden.py
```

### Golden Tests

Golden tests ensure configuration stability. Each scenario has:
- Input JSON (e.g., `examples/profiles/campus-access-switch.json`)
- Expected output (e.g., `golden/configs/campus-access-switch_ios.cfg`)

Re-generate golden configs:
```bash
python tests/generate_golden.py --regenerate
```

## 🏗️ Architecture

```
cisco-config-generator/
├── app_modern.py              # Flask application (web + API)
├── cli_generate.py            # CLI tool
├── engine/
│   ├── renderer.py            # Jinja2 rendering engine
│   ├── validator.py           # Configuration validator
│   └── __init__.py
├── config_templates/          # Jinja2 templates per vendor
│   ├── ios/
│   │   ├── base.j2
│   │   ├── _l2.j2
│   │   ├── _l3.j2
│   │   ├── _ospf.j2
│   │   └── _bgp.j2
│   ├── nxos/
│   ├── eos/
│   ├── junos/
│   └── frr/
├── templates/                 # HTML templates (web UI)
│   └── modern_index.html
├── static/
│   ├── css/modern-style.css
│   └── js/app.js
├── examples/profiles/         # Example configurations
├── golden/configs/            # Golden test outputs
├── schemas/                   # JSON/YAML schema definition
└── tests/                     # Unit and integration tests
```

### Technology Stack
- **Backend**: Flask, Jinja2
- **Frontend**: Vanilla JavaScript, CSS Grid/Flexbox
- **Validation**: Custom validators with ipaddress library
- **Templating**: Modular Jinja2 templates with partials
- **CLI**: argparse

## 🔧 Advanced Configuration

### Hierarchical Profiles

Use profile inheritance for consistent multi-site deployments:

```json
{
  "profiles": {
    "global": {
      "ntp_servers": ["10.0.0.1"],
      "dns_servers": ["10.0.1.10"]
    },
    "sites": [
      {
        "name": "site-A",
        "ntp_servers": ["10.1.0.1"]
      }
    ],
    "roles": [
      {
        "name": "campus-access",
        "site": "site-A",
        "protocols": ["vlans", "stp", "security"]
      }
    ],
    "devices": [
      {
        "hostname": "access-sw01",
        "role": "campus-access",
        "management_ip": "10.99.1.10"
      }
    ]
  }
}
```

Merge profiles via API:
```bash
POST /api/merge-profiles
```

### Vendor-Specific Notes

#### Cisco IOS/IOS-XE
- Uses wildcard masks for OSPF networks
- HSRP standby groups
- TCP MD5 authentication for BGP

#### Cisco NX-OS
- Feature enablement required (`feature ospf`, `feature vpc`)
- vPC for MLAG
- NVE interface for VXLAN

#### Arista EOS
- MLAG (not vPC)
- `Vxlan1` interface
- Route-map syntax for BGP policies

#### Juniper Junos
- Set-style configuration
- `routing-instances` for VRFs
- Interface units (`unit 0`)
- VRRP integrated into interface config

#### FRRouting
- Integrated vtysh configuration
- Interface-based OSPF/IS-IS
- Standard Linux routing

### Default Values (Security & Stability)

- **STP**: Rapid-PVST (campus) or MST (DC), PortFast + BPDU Guard on access
- **LACP**: Active mode, min-links=1, L2+L3 hashing
- **OSPF**: Hello/Dead 10/40s, reference-bandwidth 100000 Mbps
- **BGP**: Keepalive/Hold 60/180s, next-hop-self for iBGP, max-prefix warnings
- **BFD**: 300ms Tx/Rx, multiplier 3
- **EVPN**: Ingress replication, anycast gateway, symmetric IRB

## 🛡️ Security Considerations

- **No sensitive data in examples** - Use environment variables or secrets management
- **Enable AAA** - Use TACACS+/RADIUS for authentication
- **Disable unused services** - HTTP server, CDP (if not needed)
- **Apply CoPP** - Control Plane Policing to protect device CPU
- **Use ACLs** - Restrict management access (SSH, SNMP)

## 🚧 Known Limitations

- **RSVP-TE** - Optional, not all tunnel features implemented
- **SR-TE Policies** - Basic support, advanced constraints WIP
- **Platform Variations** - Some features vary by hardware/software version
- **ASA Firewall** - Limited support (focus on routing/switching)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Run linter: `flake8 engine/ tests/`
5. Submit a pull request

## 📄 License

[Specify your license here]

## 📞 Support

- **Issues**: [GitHub Issues](link-to-issues)
- **Docs**: See `docs/` directory for detailed guides
- **Email**: netops@example.com

## 🎯 Roadmap

- [ ] Ansible integration (inventory → configs)
- [ ] Terraform provider
- [ ] GitOps workflow (commit → CI/CD → deploy)
- [ ] Configuration compliance checking
- [ ] Rollback mechanism
- [ ] Multi-device diff view
- [ ] REST API rate limiting
- [ ] User authentication and RBAC

---

**Built with ❤️ for Network Engineers**
