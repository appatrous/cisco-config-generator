# Quickstart Guide

Get started with Network Configuration Generator in 5 minutes!

## 🚀 Installation

```bash
# 1. Clone the repository
git clone <repository-url>
cd cisco-config-generator

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the web server
python app_modern.py
```

Open your browser to: **http://localhost:5000**

## 📋 Your First Configuration

### Option 1: Web Interface

1. **Select Vendor**: Click on "Cisco IOS/IOS-XE"
2. **Click "Load Example"**: This loads a pre-configured campus access switch
3. **Review Active Protocols**: See VLANs, OSPF, and BGP are activated
4. **Click "Generate Configuration"**: View the rendered config
5. **Download**: Save as `campus-dist1_ios.cfg`

### Option 2: CLI

```bash
# Generate from example
python cli_generate.py \
  --vendor ios \
  --config examples/profiles/campus-access-switch.json \
  --output configs/

# Output: configs/campus-access-sw01_ios.cfg
```

### Option 3: API

```bash
# Using curl
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

## 🎯 Common Scenarios

### 1. Campus Access Switch (IOS)

**File**: `examples/profiles/campus-access-switch.json`

Features:
- VLANs (DATA, VOICE, GUEST, IoT, MGMT)
- 802.1X with MAB
- DHCP Snooping + DAI
- Port Security
- LLDP/CDP
- Management SVI

```bash
python cli_generate.py --vendor ios --config examples/profiles/campus-access-switch.json --output configs/
```

### 2. Campus Distribution L3 (IOS)

**File**: `examples/profiles/campus-distribution-l3.json`

Features:
- OSPF routing
- HSRP with tracking
- LAG/LACP uplinks
- STP Root Bridge
- SVIs for VLANs

```bash
python cli_generate.py --vendor ios --config examples/profiles/campus-distribution-l3.json --output configs/
```

### 3. Data Center Leaf (NX-OS)

**File**: `examples/profiles/dc-leaf-evpn.json`

Features:
- VXLAN EVPN
- BGP as underlay/overlay
- vPC (MLAG)
- L2VNI and L3VNI
- Anycast Gateway
- BFD

```bash
python cli_generate.py --vendor nxos --config examples/profiles/dc-leaf-evpn.json --output configs/
```

## 🔧 Basic Configuration Structure

### Minimal OSPF Example

```json
{
  "global": {
    "hostname": "router1",
    "domain_name": "example.com"
  },
  "l3": {
    "interfaces": [
      {
        "interface": "GigabitEthernet0/0",
        "ipv4": [{"address": "10.1.1.1/24"}]
      }
    ],
    "ospf": [{
      "process_id": 10,
      "router_id": "1.1.1.1",
      "areas": [{"id": "0.0.0.0"}],
      "interfaces": [
        {"interface": "GigabitEthernet0/0", "area": "0.0.0.0"}
      ]
    }]
  }
}
```

### VLAN + STP Example

```json
{
  "global": {
    "hostname": "switch1"
  },
  "l2": {
    "vlans": [
      {"id": 10, "name": "DATA"},
      {"id": 20, "name": "VOICE"}
    ],
    "stp": {
      "mode": "rapid-pvst",
      "portfast_default": true,
      "guards": {
        "bpduguard_default": true
      }
    }
  }
}
```

### BGP + EVPN Example (DC)

```json
{
  "global": {
    "hostname": "leaf-01"
  },
  "l3": {
    "bgp": {
      "asn": 65001,
      "router_id": "1.1.1.1",
      "neighbors": [
        {
          "ip": "10.0.0.1",
          "remote_as": 65000,
          "description": "Spine-01"
        }
      ],
      "address_families": {
        "l2vpn_evpn": {
          "enabled": true,
          "neighbors_activate": ["10.0.0.1"],
          "advertise_all_vni": true
        }
      }
    }
  },
  "vxlan": {
    "enabled": true,
    "vtep": {
      "source_interface": "loopback1"
    },
    "l2vnis": [
      {"vni": 10010, "vlan": 10}
    ]
  }
}
```

## 📚 Next Steps

1. **Explore Templates**: Check `config_templates/` to see how configs are generated
2. **Read Schema**: `schemas/network_config_schema.yaml` has the complete data model
3. **Customize**: Modify templates or add new protocols
4. **Validate**: Always use `--validate-only` first to check your JSON
5. **Test**: Run `pytest tests/` to ensure everything works

## 🔍 Validation & Linting

### Validate Before Generating

```bash
python cli_generate.py --validate-only --config myconfig.json
```

**Output:**
```
✅ Validation: PASSED
⚠️  Warnings (2):
  - L2: VLAN 100 has no name
  - L3: Interface Vlan10 references undefined VRF 'PROD'
```

### Lint Existing Config

```bash
python cli_generate.py --lint --file router1.cfg --vendor ios
```

**Output:**
```
✅ Linting: PASSED (142 lines)

⚠️  Linting Warnings (1):
  - Line 45: Duplicate configuration: ip routing
```

## 🌐 Multi-Vendor Generation

Generate configs for multiple vendors from single JSON:

```bash
python cli_generate.py \
  --vendors ios,nxos,eos \
  --config myconfig.json \
  --output configs/

# Creates:
#   configs/router1_ios.cfg
#   configs/router1_nxos.cfg
#   configs/router1_eos.cfg
```

## 💡 Tips

1. **Start with Examples**: Modify existing examples rather than starting from scratch
2. **Use Validation**: Always validate before deploying to production
3. **Check Vendor Support**: Some features aren't available on all platforms
4. **Test in Lab**: Deploy to lab devices first
5. **Version Control**: Store JSON configs in Git for change tracking
6. **CI/CD**: Use CLI tool in pipelines for automated config generation

## 🆘 Troubleshooting

### "Vendor not supported"
- Check spelling: must be lowercase (ios, nxos, eos, junos, frr)

### "Invalid IP address"
- Use CIDR notation: `10.1.1.1/24` not `10.1.1.1 255.255.255.0`

### "Undefined variable in template"
- Enable strict validation: this catches missing required fields
- Check schema for required fields

### "Template not found"
- Ensure `config_templates/<vendor>/` directory exists
- Check template file has `.j2` extension

### Web UI not loading
- Check Flask is running: `python app_modern.py`
- Verify port 5000 is not in use: `lsof -i :5000`
- Try another port: `app.run(port=8080)`

## 📖 Documentation

- **Full README**: `README.md` - Complete feature list
- **API Docs**: `docs/api_spec.md` - REST API reference
- **Schema**: `schemas/network_config_schema.yaml` - Data model
- **Architecture**: `docs/architecture.md` - System design

## 🎓 Learning Resources

1. **Examples Directory**: Start here for real-world configs
2. **Templates**: See how Jinja2 templates work
3. **Tests**: Golden tests show expected outputs
4. **Schema**: Reference for all available fields

---

**Ready to generate some configs? Let's go! 🚀**
