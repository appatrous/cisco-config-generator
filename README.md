# Cisco Configuration Generator 🚀

> **Advanced network configuration generator for Cisco devices with compliance checking, topology mapping, and educational features.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [New Features](#new-features)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Usage](#usage)
- [Documentation](#documentation)
- [Architecture](#architecture)
- [Contributing](#contributing)
- [Security](#security)
- [License](#license)

## 🎯 Overview

Cisco Configuration Generator is a comprehensive web application that helps network engineers generate, validate, and manage Cisco device configurations. It supports **IOS**, **NX-OS**, and **ASA** platforms with 60+ network protocols and features.

**Perfect for:**
- Network engineers deploying Cisco devices
- Students learning Cisco technologies
- IT teams standardizing configurations
- Organizations requiring compliance validation

## ✨ Key Features

### Core Configuration Generation
- **60+ Supported Protocols**: OSPF, BGP, EIGRP, VLANs, ACLs, NAT, VPNs, and more
- **Multiple Platforms**: Cisco IOS, NX-OS, ASA, IOS-XE, IOS-XR
- **Multiple Output Formats**: CLI commands, JSON, YAML
- **Web UI + REST API**: Interactive forms or programmatic access

### 🆕 New Features

#### 1. **Network Topology Mapper** 🗺️
Automatically visualize your network topology from configurations:
- Extract device connections from configs
- Identify Layer 2 and Layer 3 relationships
- Detect routing protocol adjacencies (OSPF, BGP, EIGRP)
- Generate interactive network diagrams
- Export to JSON, GraphML for use in visualization tools

```python
from services.topology_mapper import TopologyMapper

mapper = TopologyMapper()
mapper.parse_configuration(router_config, "Router1", "ios")
topology_data = mapper.generate_visualization_data()
```

#### 2. **Compliance Checker** ✅
Verify configurations against industry standards:
- **PCI-DSS** (Payment Card Industry)
- **NIST** Cybersecurity Framework
- **CIS** Cisco Benchmarks
- Detailed compliance reports with severity levels
- Remediation recommendations

```python
from services.compliance_checker import ComplianceChecker

checker = ComplianceChecker(platform='ios')
report = checker.check_configuration(config_cli, standards=['pci-dss', 'cis'])
# Returns: compliance score, findings, recommendations
```

**Example Report:**
```json
{
  "summary": {
    "compliance_score": 78.5,
    "risk_level": "MEDIUM",
    "total_checks": 45,
    "passed": 32,
    "failed": 13
  },
  "findings_by_severity": {
    "critical": [...],
    "high": [...],
    "medium": [...]
  }
}
```

#### 3. **Change Impact Analysis** 🔍
Predict the impact of configuration changes before applying them:
- Compare old vs new configurations
- Identify affected components (routing, security, interfaces)
- Risk assessment with impact levels
- Rollback plans and testing procedures
- Pre/post-change checklists

```python
from services.change_impact_analyzer import ChangeImpactAnalyzer

analyzer = ChangeImpactAnalyzer(platform='ios')
impact = analyzer.analyze_changes(old_config, new_config)
# Returns: risk score, affected components, recommendations
```

**Risk Levels:**
- 🔴 **CRITICAL**: Service disruption, network outage
- 🟠 **HIGH**: Significant impact on multiple services
- 🟡 **MEDIUM**: Limited impact on specific services
- 🟢 **LOW**: Minimal impact

#### 4. **Learning Mode** 🎓
Educational explanations for every command:
- Detailed command explanations
- Syntax and parameters
- Best practices and common mistakes
- Related commands and examples
- Interactive tutorials for topics (OSPF, VLANs, ACLs, etc.)

```python
from services.learning_mode import CommandExplainer

explainer = CommandExplainer(platform='ios')
explanation = explainer.explain_command("router ospf 1")
# Returns: purpose, syntax, best practices, examples, protocol info
```

### Additional Features

#### Security Enhancements 🔒
- Environment-based configuration (`.env` files)
- Encrypted password storage (bcrypt)
- Rate limiting for API endpoints
- Input validation and sanitization
- Session management with secure cookies

#### Database & History 💾
- SQLAlchemy ORM with SQLite/PostgreSQL
- Configuration versioning and history
- User management with roles (admin, engineer, viewer)
- API key management
- Configuration templates and sharing

#### Developer Features 🛠️
- Comprehensive logging system
- Error handling and monitoring
- REST API with Swagger documentation
- Docker containerization
- CI/CD ready (GitHub Actions)

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- pip package manager
- (Optional) Docker for containerized deployment

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/appatrous/cisco-config-generator.git
cd cisco-config-generator
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment:**
```bash
cp .env.example .env
# Edit .env file with your settings
nano .env
```

5. **Initialize database:**
```bash
python manage.py init-db
```

6. **Run the application:**
```bash
python app.py
```

7. **Access the application:**
Open browser to `http://localhost:5000`

### Docker Deployment

```bash
# Build Docker image
docker build -t cisco-config-generator .

# Run container
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://user:pass@db/cisco_config \
  cisco-config-generator
```

### Docker Compose (Development)

```bash
docker-compose up -d
```

## 📖 Usage

### Web Interface

1. **Select Device Type:** Choose Router, Switch, or Firewall
2. **Select Platform:** IOS, NX-OS, or ASA
3. **Choose Features:** Click on protocols/features to configure
4. **Fill Forms:** Enter configuration parameters
5. **Generate:** Get CLI, JSON, or YAML output
6. **Validate:** Run compliance checks
7. **Visualize:** Generate topology map

### REST API

#### Generate Configuration
```bash
curl -X POST http://localhost:5000/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "ios",
    "device_type": "router",
    "hostname": "R1",
    "interfaces": [
      {
        "name": "GigabitEthernet0/0",
        "ip_address": "192.168.1.1",
        "subnet_mask": "255.255.255.0"
      }
    ]
  }'
```

#### Check Compliance
```bash
curl -X POST http://localhost:5000/api/compliance/check \
  -H "Content-Type: application/json" \
  -d '{
    "config_cli": "hostname R1\n...",
    "standards": ["pci-dss", "cis"]
  }'
```

#### Analyze Change Impact
```bash
curl -X POST http://localhost:5000/api/impact/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "old_config": "...",
    "new_config": "..."
  }'
```

#### Generate Topology
```bash
curl -X POST http://localhost:5000/api/topology/generate \
  -H "Content-Type: application/json" \
  -d '{
    "devices": [
      {
        "name": "Router1",
        "platform": "ios",
        "config": "..."
      }
    ]
  }'
```

## 📚 Documentation

Comprehensive documentation available in the `/docs` folder:

- **[Architecture](docs/architecture.md)** - System design and components
- **[API Specification](docs/api_spec.md)** - REST API endpoints
- **[Usage Guide](docs/usage.md)** - Detailed usage instructions
- **[Compliance Standards](docs/compliance_standards.md)** - Supported compliance frameworks
- **[Topology Mapping](docs/topology_mapping.md)** - How topology mapper works
- **[Contributing](docs/contributing.md)** - Contribution guidelines

## 🏗️ Architecture

```
cisco-config-generator/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── models.py                   # Database models
├── requirements.txt            # Python dependencies
│
├── services/                   # Business logic modules
│   ├── topology_mapper.py      # Network topology generation
│   ├── compliance_checker.py   # Compliance validation
│   ├── change_impact_analyzer.py  # Change impact analysis
│   └── learning_mode.py        # Educational explanations
│
├── routes/                     # Flask route handlers
│   ├── web_routes.py          # Web UI routes
│   ├── api_routes.py          # REST API routes
│   └── auth_routes.py         # Authentication routes
│
├── utils/                      # Utility modules
│   ├── validators.py          # Input validation
│   ├── logger.py              # Logging configuration
│   ├── config_export.py       # Config rendering
│   └── jinja_helpers.py       # Jinja2 filters
│
├── templates/                  # HTML templates
├── static/                     # CSS, JS, images
├── config_templates/           # Jinja2 config templates
├── tests/                      # Unit and integration tests
└── docs/                       # Documentation
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Ways to contribute:**
- 🐛 Report bugs and issues
- 💡 Suggest new features
- 📝 Improve documentation
- 🔧 Submit pull requests
- ⭐ Star the repository

## 🔒 Security

Security is a top priority. Please review [SECURITY.md](SECURITY.md) for:
- Security best practices
- Vulnerability reporting
- Secure deployment guidelines

**Security Features:**
- Environment-based secrets management
- Password hashing with bcrypt
- Input validation and sanitization
- Rate limiting on API endpoints
- Secure session management
- SQL injection prevention (ORM)

## 📊 Compliance Standards Supported

| Standard | Description | Coverage |
|----------|-------------|----------|
| **PCI-DSS** | Payment Card Industry Data Security Standard | 🟢 Full |
| **NIST CSF** | NIST Cybersecurity Framework | 🟢 Full |
| **CIS Benchmarks** | Center for Internet Security Cisco Benchmarks | 🟢 Full |
| **Custom Policies** | Organization-specific policies | 🟡 Partial |

## 🗺️ Roadmap

### Q1 2025
- [ ] Multi-tenancy support
- [ ] Advanced RBAC (Role-Based Access Control)
- [ ] Integration with NetBox and Nautobot
- [ ] Ansible playbook generation
- [ ] Terraform provider

### Q2 2025
- [ ] Support for Juniper JunOS
- [ ] Support for Arista EOS
- [ ] AI-powered configuration recommendations
- [ ] Automated configuration deployment via SSH/NETCONF

### Q3 2025
- [ ] Cisco ACI fabric configuration
- [ ] SD-WAN (Viptela) support
- [ ] Real-time collaboration features
- [ ] Mobile app (iOS/Android)

## 📈 Statistics

- **60+** Supported network protocols
- **5** Device platforms (IOS, NX-OS, ASA, IOS-XE, IOS-XR)
- **3** Compliance frameworks
- **100+** Validation rules
- **1000+** Lines of test coverage

## 🙏 Acknowledgments

- Cisco Systems for IOS documentation
- Flask community for excellent web framework
- NetworkX for graph algorithms
- All contributors and users

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/appatrous/cisco-config-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/appatrous/cisco-config-generator/discussions)
- **Email**: support@example.com

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ by network engineers, for network engineers**

