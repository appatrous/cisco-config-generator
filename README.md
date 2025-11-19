# 🌐 Cisco Configuration Generator v2.0

**Enterprise-Grade Network Configuration Management Platform**

[![CI/CD](https://github.com/yourusername/cisco-config-generator/workflows/CI%2FCD%20Pipeline/badge.svg)](https://github.com/yourusername/cisco-config-generator/actions)
[![Code Coverage](https://codecov.io/gh/yourusername/cisco-config-generator/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/cisco-config-generator)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Une plateforme complète de gestion et génération de configurations réseau avec interface web moderne, API REST, authentification JWT, base de données PostgreSQL, et déploiement automatisé.

---

## ✨ Nouveautés Version 2.0

🎉 **Architecture Refactorisée** - Code modulaire et maintenable
🔐 **Sécurité Renforcée** - Secrets externalisés, validation Pydantic, JWT auth
💾 **Base de Données** - PostgreSQL avec SQLAlchemy ORM
⚡ **Tâches Asynchrones** - Celery + Redis pour déploiements en arrière-plan
📊 **WebSockets** - Mises à jour temps réel des déploiements
🧪 **Tests Complets** - >50% de couverture, CI/CD automatisé
🎨 **Frontend React** - Interface moderne avec Ant Design
🏢 **Multi-tenant** - Support des organisations multiples

---

## 📋 Table des Matières

- [Fonctionnalités](#-fonctionnalités)
- [Architecture](#-architecture)
- [Installation](#-installation)
- [Démarrage Rapide](#-démarrage-rapide)
- [Documentation](#-documentation)
- [Tests](#-tests)
- [Contribution](#-contribution)
- [Migration](#-migration-depuis-v1)

---

## 🚀 Fonctionnalités

### Multi-Vendor Support
- **Cisco IOS/IOS-XE** - Routeurs et switches campus/edge
- **Cisco NX-OS** - Switches data center (Nexus 9K/7K)
- **Cisco ASA** - Pare-feu et sécurité
- **Arista EOS** - Switches data center et campus
- **Juniper Junos** - Switches EX/QFX

### Protocoles Supportés

#### 🔌 Layer 2
- VLANs & Trunking (802.1Q)
- Spanning Tree (STP, RSTP, MSTP, PVST+)
- Link Aggregation (LACP)
- Port Security, DHCP Snooping
- Dynamic ARP Inspection
- IP Source Guard
- CDP / LLDP

#### 🌐 Layer 3
- **Routing**: OSPF, EIGRP, BGP, RIP, Static
- **FHRP**: HSRP, VRRP, GLBP
- **VRF/VRF-Lite** - Isolation des tables de routage
- **Multicast**: PIM, IGMP/MLD
- **NAT**: Static, Dynamic, PAT

#### 🎯 Avancé
- **VXLAN/EVPN** - Data center fabric
- **QoS** - Classification, marking, policing
- **NTP, SNMP, Syslog** - Monitoring
- **AAA** - TACACS+, RADIUS authentication

### Backend API (Nouveau v2.0)

#### 🔐 Authentification & Autorisation
- JWT (JSON Web Tokens) avec refresh tokens
- Authentification basée sur les rôles (admin/user)
- Multi-tenant avec isolation par organisation
- Sessions sécurisées avec expiration

#### 💾 Gestion des Périphériques
- CRUD complet des devices
- Import/Export CSV bulk
- Gestion des credentials chiffrés
- Health checks et monitoring
- Historique des configurations

#### ⚙️ Déploiement Automatisé
- Déploiement asynchrone via Celery
- WebSocket notifications en temps réel
- Rollback automatique en cas d'échec
- Logs détaillés de déploiement
- Validation pré-déploiement

#### 📊 Validation & Comparaison
- Validation syntaxique avancée
- Comparaison de configurations (diff)
- Détection des changements risqués
- Analyse de conformité
- Suggestions d'optimisation

### Frontend React (Nouveau v2.0)

#### 🎨 Interface Moderne
- **Dashboard** - Vue d'ensemble avec statistiques
- **Inventaire** - Gestion des devices avec filtres
- **Déploiement** - Wizard en 3 étapes
- **Diff Viewer** - Comparaison side-by-side
- **Timeline** - Historique interactif

#### ⚡ Fonctionnalités
- Auto-refresh (30s)
- Import CSV bulk
- Export configurations
- Recherche et filtres avancés
- Notifications temps réel

---

## 🏗️ Architecture

### Structure Modulaire

```
cisco-config-generator/
├── 🎯 Applications
│   ├── app.py                     # [Legacy] Application monolithique
│   ├── app_refactored.py         # ✨ [v2.0] Application modulaire
│   └── app_api.py                # ✨ [v2.0] API REST avec JWT
│
├── 🔀 Routes (Blueprints Flask)
│   ├── routes/
│   │   ├── main.py               # Routes UI principales
│   │   ├── devices.py            # Pages devices
│   │   ├── protocols.py          # Configuration protocoles
│   │   ├── configs.py            # Gestion configurations
│   │   └── troubleshoot.py       # Troubleshooting
│
├── 🔧 Services (Business Logic)
│   └── services/
│       └── protocol_service.py   # Génération configurations
│
├── 📝 Schemas (Validation Pydantic)
│   ├── schemas/
│   │   ├── config_schemas.py     # Validation configs
│   │   └── device_schemas.py     # Validation devices
│
├── 💾 Models (SQLAlchemy ORM)
│   └── models/
│       └── __init__.py           # Organization, User, Device, etc.
│
├── ⚡ Tasks (Celery Background Jobs)
│   └── tasks/
│       └── deployment_tasks.py   # Déploiements asynchrones
│
├── 🛠️ Utils (Helpers)
│   ├── utils/
│   │   ├── troubleshoot.py       # Commandes troubleshooting
│   │   ├── config_export.py      # Export configurations
│   │   └── generate_secrets.py   # Génération secrets sécurisés
│
├── 🧪 Tests (>50% Coverage)
│   ├── tests/
│   │   ├── conftest.py           # Fixtures pytest
│   │   ├── unit/                 # Tests unitaires
│   │   │   ├── test_models.py
│   │   │   └── test_services.py
│   │   └── integration/          # Tests intégration
│   │       ├── test_api_auth.py
│   │       ├── test_api_devices.py
│   │       └── test_api_validation.py
│
├── 🎨 Frontend React
│   └── frontend/
│       └── src/
│           ├── components/       # Composants React
│           ├── services/         # API client
│           └── App.jsx           # Application principale
│
├── 📄 Templates & Config
│   ├── config_templates/         # Templates Jinja2
│   ├── templates/                # Templates HTML
│   ├── static/                   # Assets statiques
│   └── migrations/               # Migrations DB
│
└── 📚 Documentation
    ├── README.md                 # Ce fichier
    ├── DEVELOPMENT.md            # Guide développement
    ├── SECURITY.md               # Guide sécurité
    ├── MIGRATION.md              # Guide migration v1→v2
    ├── BACKEND_SETUP.md          # Setup backend
    └── FRONTEND_SETUP.md         # Setup frontend
```

### Stack Technologique

#### Backend
- **Framework**: Flask 3.0+
- **ORM**: SQLAlchemy 2.0+ avec Flask-Migrate
- **Auth**: Flask-JWT-Extended (JWT tokens)
- **Validation**: Pydantic 2.5+
- **Queue**: Celery 5.3+ avec Redis
- **WebSocket**: Flask-SocketIO avec Eventlet
- **Database**: PostgreSQL 15+
- **Cache**: Redis 7+

#### Frontend
- **Framework**: React 18.3+
- **UI Library**: Ant Design 5.14+
- **Routing**: React Router 6+
- **State**: React Query 3.39+
- **HTTP**: Axios
- **WebSocket**: Socket.IO Client
- **Build**: Vite 5.1+

#### DevOps
- **Containerization**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **Testing**: Pytest avec coverage
- **Linting**: Black, Flake8, isort, mypy
- **Security**: Bandit, detect-secrets
- **Pre-commit**: Hooks automatiques

---

## 📦 Installation

### Prérequis

- **Python** 3.11+
- **PostgreSQL** 15+
- **Redis** 7+
- **Node.js** 18+ (pour le frontend)
- **Docker** & Docker Compose (optionnel mais recommandé)

### Option 1: Installation avec Docker (Recommandé)

```bash
# 1. Cloner le repository
git clone <repository-url>
cd cisco-config-generator

# 2. Copier et configurer les variables d'environnement
cp .env.example .env
nano .env  # Modifier les secrets

# 3. Générer des secrets sécurisés
python utils/generate_secrets.py --env >> .env

# 4. Démarrer tous les services
docker-compose up -d

# 5. Initialiser la base de données
docker-compose exec api python init_db.py

# 6. Vérifier les services
docker-compose ps
```

Les services seront disponibles sur :
- **API Backend**: http://localhost:5000
- **Frontend React**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Option 2: Installation Manuelle

#### Backend

```bash
# 1. Créer un environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 3. Configurer l'environnement
cp .env.example .env
python utils/generate_secrets.py --env  # Copier dans .env

# 4. Démarrer PostgreSQL et Redis
# (ou utiliser Docker Compose pour ces services uniquement)
docker-compose up -d postgres redis

# 5. Initialiser la base de données
python init_db.py

# 6. Démarrer l'application
python app_api.py  # API Backend

# Dans un autre terminal
celery -A celery_app worker --loglevel=info  # Worker Celery
```

#### Frontend

```bash
# 1. Aller dans le répertoire frontend
cd frontend

# 2. Installer les dépendances
npm install

# 3. Démarrer le serveur de développement
npm run dev
```

---

## 🚀 Démarrage Rapide

### Script de Démarrage Rapide

```bash
# Utiliser le script de démarrage
chmod +x start_dev.sh
./start_dev.sh
```

### Premiers Pas

#### 1. Créer un Compte Administrateur

```bash
# Via l'API
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "username": "admin",
    "password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "organization_name": "My Organization"
  }'
```

#### 2. Se Connecter

```bash
# Obtenir un token JWT
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecurePassword123!"
  }'

# Response:
# {
#   "access_token": "eyJ0eXAi...",
#   "refresh_token": "eyJ0eXAi...",
#   "user": {...}
# }
```

#### 3. Ajouter un Device

```bash
curl -X POST http://localhost:5000/api/devices \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "hostname": "router1",
    "ip_address": "192.168.1.1",
    "platform": "ios",
    "device_type": "router",
    "location": "Data Center 1",
    "username": "admin",
    "password": "cisco123"
  }'
```

#### 4. Générer une Configuration

```bash
curl -X POST http://localhost:5000/api/configs/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "platform": "ios",
    "hostname": "router1",
    "static_routes": [
      {
        "network": "192.168.1.0",
        "mask": "255.255.255.0",
        "next_hop": "10.0.0.1"
      }
    ],
    "vlans": [
      {"vlan_id": 10, "name": "VLAN_10"}
    ]
  }'
```

### Interface Web

Ouvrez http://localhost:3000 dans votre navigateur :

1. **Dashboard** - Vue d'ensemble des devices
2. **Devices** - Ajouter/Modifier devices
3. **Deployment** - Déployer des configurations
4. **History** - Consulter l'historique

---

## 📚 Documentation

### Guides Complets

- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guide de développement complet
- **[SECURITY.md](SECURITY.md)** - Best practices de sécurité
- **[MIGRATION.md](MIGRATION.md)** - Migration v1 → v2
- **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Configuration backend détaillée
- **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - Configuration frontend détaillée

### API Reference

#### Endpoints Principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/health` | GET | Health check |
| `/api/auth/register` | POST | Enregistrement utilisateur |
| `/api/auth/login` | POST | Connexion |
| `/api/auth/refresh` | POST | Refresh token |
| `/api/devices` | GET/POST | Liste/Créer devices |
| `/api/devices/{id}` | GET/PUT/DELETE | Device spécifique |
| `/api/devices/{id}/ping` | POST | Ping device |
| `/api/configs` | GET/POST | Configurations |
| `/api/configs/generate` | POST | Générer config |
| `/api/configs/compare` | POST | Comparer configs |
| `/api/validate/config` | POST | Valider config |
| `/api/deployments` | GET/POST | Déploiements |

Documentation complète : http://localhost:5000/api/docs (quand l'app est lancée)

---

## 🧪 Tests

### Exécuter les Tests

```bash
# Tous les tests
pytest

# Tests unitaires uniquement
pytest tests/unit -v

# Tests d'intégration uniquement
pytest tests/integration -v

# Avec coverage
pytest --cov --cov-report=html --cov-report=term-missing

# Ouvrir le rapport HTML
open htmlcov/index.html
```

### Pre-commit Hooks

```bash
# Installer les hooks
pre-commit install

# Exécuter manuellement
pre-commit run --all-files
```

### CI/CD

Les tests sont automatiquement exécutés sur chaque push et PR via GitHub Actions :
- ✅ Linting (black, flake8, isort, mypy)
- ✅ Security scan (bandit, trivy)
- ✅ Unit tests (>50% coverage)
- ✅ Integration tests
- ✅ Docker build

---

## 🤝 Contribution

Les contributions sont les bienvenues ! Veuillez :

1. **Fork** le repository
2. **Créer** une branche feature (`git checkout -b feature/ma-feature`)
3. **Ajouter** des tests pour vos modifications
4. **Vérifier** que tous les tests passent (`pytest`)
5. **Commit** vos changements (`git commit -m 'feat: ajouter ma feature'`)
6. **Push** vers la branche (`git push origin feature/ma-feature`)
7. **Créer** une Pull Request

### Format des Commits

Suivre [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nouvelle fonctionnalité
fix: correction de bug
docs: documentation
test: ajout de tests
refactor: refactoring du code
style: formatage du code
chore: tâches de maintenance
```

---

## 🔄 Migration depuis v1

Si vous utilisez l'ancienne version monolithique (`app.py`), consultez **[MIGRATION.md](MIGRATION.md)** pour migrer vers v2.0.

### Différences Principales

| Aspect | v1.0 (Legacy) | v2.0 (Nouveau) |
|--------|---------------|----------------|
| **Architecture** | Monolithique (1776 lignes) | Modulaire (35+ fichiers) |
| **Base de données** | Fichiers/mémoire | PostgreSQL |
| **Auth** | Aucune | JWT avec multi-tenant |
| **Déploiement** | Synchrone | Asynchrone (Celery) |
| **Monitoring** | Aucun | WebSocket temps réel |
| **Frontend** | Templates Jinja2 | React moderne |
| **Tests** | Minimaux | >50% coverage |
| **CI/CD** | Aucun | GitHub Actions |
| **Sécurité** | Secrets hardcodés | Variables d'environnement |

---

## 🛡️ Sécurité

### Bonnes Pratiques

✅ **Secrets externalisés** - Jamais de secrets dans le code
✅ **Validation stricte** - Pydantic pour toutes les entrées
✅ **JWT sécurisés** - Tokens avec expiration
✅ **Mots de passe hashés** - Bcrypt pour tous les passwords
✅ **HTTPS recommandé** - Utiliser un reverse proxy en production
✅ **CORS configuré** - Origines autorisées définies
✅ **Rate limiting** - Protection contre les abus

### Rapport de Vulnérabilité

Pour signaler une vulnérabilité de sécurité :
- **NE PAS** créer une issue publique
- Envoyer un email à : security@yourcompany.com
- Voir [SECURITY.md](SECURITY.md) pour plus de détails

---

## 📄 License

[MIT License](LICENSE) - Copyright (c) 2025

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/cisco-config-generator/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cisco-config-generator/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/cisco-config-generator/wiki)
- **Email**: support@yourcompany.com

---

## 🎯 Roadmap

### v2.1 (Q2 2025)
- [ ] Swagger/OpenAPI documentation complète
- [ ] Webhooks pour notifications externes
- [ ] Export/Import de configurations en masse
- [ ] Dashboard avec métriques Prometheus

### v2.2 (Q3 2025)
- [ ] Terraform provider
- [ ] Ansible collection
- [ ] GitOps workflow natif
- [ ] Compliance as Code

### v3.0 (Q4 2025)
- [ ] AI-assisted configuration generation
- [ ] Prédiction de problèmes réseau
- [ ] Optimisation automatique de configs
- [ ] Network Digital Twin

---

## 🙏 Remerciements

Construit avec ❤️ pour les Network Engineers

- Flask & SQLAlchemy teams
- React & Ant Design teams
- Celery & Redis teams
- La communauté open source

---

**⭐ N'oubliez pas de mettre une étoile si ce projet vous est utile !**
