# Guide de Migration v1.0 → v2.0

## 📖 Vue d'ensemble

Ce guide vous aidera à migrer de l'ancienne architecture monolithique (`app.py`) vers la nouvelle architecture modulaire v2.0 (`app_refactored.py` + `app_api.py`).

---

## ⚠️ Changements Majeurs

### Architecture

| Composant | v1.0 | v2.0 |
|-----------|------|------|
| **Application principale** | `app.py` (1776 lignes) | `app_refactored.py` (60 lignes) + blueprints |
| **Structure** | Monolithique | Modulaire (routes, services, schemas) |
| **Routage** | Routes dans app.py | Blueprints Flask séparés |
| **Logique métier** | Mélangée avec routes | Service layer séparé |
| **Validation** | Manuelle | Pydantic schemas |

### Données

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **Stockage configurations** | Fichiers texte (`data/*.txt`) | PostgreSQL |
| **Stockage devices** | Aucun | Table `devices` |
| **Utilisateurs** | Aucun | Table `users` avec auth |
| **Historique** | Fichiers | Tables `deployments`, `audit_log` |

### Sécurité

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| **SECRET_KEY** | Hardcodé | Variable d'environnement |
| **Authentification** | Aucune | JWT avec refresh tokens |
| **Autorisation** | Aucune | RBAC (admin/user) |
| **Multi-tenancy** | Aucun | Organisations avec isolation |

---

## 🔄 Stratégie de Migration

### Approche Recommandée : Dual-Run

Exécuter les deux versions en parallèle pendant la transition :

```
┌─────────────────┐
│   v1.0 (port    │ ──▶ Production (lecture seule)
│   5001)         │
└─────────────────┘

┌─────────────────┐
│   v2.0 (port    │ ──▶ Staging → Production
│   5000)         │
└─────────────────┘
```

**Phase 1** : Déployer v2.0 en staging (2 semaines)
**Phase 2** : Tests parallèles v1/v2 (1 semaine)
**Phase 3** : Migration progressive du trafic
**Phase 4** : Décommissionnement v1.0

---

## 📋 Checklist de Migration

### Préparation

- [ ] **Sauvegarder** toutes les données existantes
- [ ] **Documenter** les configurations custom actuelles
- [ ] **Identifier** les intégrations existantes
- [ ] **Planifier** la fenêtre de maintenance
- [ ] **Tester** v2.0 en environnement de staging

### Configuration

- [ ] **Copier** `.env.example` → `.env`
- [ ] **Générer** des secrets sécurisés
- [ ] **Configurer** PostgreSQL et Redis
- [ ] **Migrer** les variables d'environnement
- [ ] **Tester** la connexion aux services

### Migration des Données

- [ ] **Exporter** les configurations existantes
- [ ] **Importer** dans PostgreSQL
- [ ] **Créer** les utilisateurs et organisations
- [ ] **Migrer** l'historique si nécessaire
- [ ] **Valider** l'intégrité des données

### Tests

- [ ] **Tests fonctionnels** de bout en bout
- [ ] **Tests de performance**
- [ ] **Tests de sécurité**
- [ ] **Tests d'intégration** avec systèmes existants
- [ ] **Tests de rollback**

### Mise en Production

- [ ] **Déployer** v2.0 en production
- [ ] **Rediriger** le trafic progressivement
- [ ] **Monitorer** les métriques et logs
- [ ] **Former** les utilisateurs
- [ ] **Documenter** les changements

---

## 🔧 Migration des Composants

### 1. Migration des Configurations Générées

#### Export depuis v1.0

```bash
# Les configurations v1.0 sont dans data/*.txt
ls data/

# Exemple de structure:
# data/router_config.txt
# data/switch_config.txt
# data/firewall_config.txt
```

#### Import vers v2.0

```python
# Script de migration des configurations
import os
import json
from datetime import datetime

# Lire les anciennes configurations
data_dir = 'data'
configs = {}

for filename in os.listdir(data_dir):
    if filename.endswith('_config.txt'):
        device_type = filename.replace('_config.txt', '')
        with open(os.path.join(data_dir, filename), 'r') as f:
            configs[device_type] = f.read()

# Importer dans PostgreSQL via API v2.0
import requests

API_URL = 'http://localhost:5000/api'
TOKEN = 'your_jwt_token'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

for device_type, config_text in configs.items():
    # Créer le device
    device_data = {
        'hostname': f'{device_type}-1',
        'ip_address': '192.168.1.1',  # À adapter
        'platform': 'ios',  # À adapter
        'device_type': device_type
    }

    response = requests.post(
        f'{API_URL}/devices',
        headers=headers,
        json=device_data
    )
    device_id = response.json()['id']

    # Créer la configuration
    config_data = {
        'device_id': device_id,
        'config_text': config_text,
        'description': f'Migrated from v1.0 - {datetime.now()}'
    }

    requests.post(
        f'{API_URL}/configs',
        headers=headers,
        json=config_data
    )

print("Migration completed!")
```

### 2. Migration des Routes

#### Ancien Code (v1.0)

```python
# app.py
@app.route('/protocol/<slug>', methods=['GET', 'POST'])
def protocol_page(slug: str):
    # 200+ lignes de logique mélangée
    if request.method == 'POST':
        # Traitement formulaire
        form_data = request.form.to_dict(flat=False)

        # Génération configuration
        if slug == 'ospf':
            config = generate_ospf_config(form_data)
        elif slug == 'vlan':
            config = generate_vlan_config(form_data)
        # ... 50+ protocoles

        # Écriture fichier
        with open('data/config.txt', 'a') as f:
            f.write(config)

    return render_template(f'protocol_{slug}.html')
```

#### Nouveau Code (v2.0)

```python
# routes/protocols.py
from flask import Blueprint
from services.protocol_service import ProtocolService

protocols_bp = Blueprint('protocols', __name__)

@protocols_bp.route('/protocol/<slug>', methods=['GET', 'POST'])
def protocol_page(slug: str):
    if request.method == 'POST':
        form_data = request.form.to_dict(flat=False)

        # Service layer gère la logique
        config = ProtocolService.generate_config(slug, form_data)

        # Persistance en DB via API
        save_config_to_database(config, device_id)

    template_name = ProtocolService.get_template_name(slug)
    return render_template(template_name, slug=slug)
```

### 3. Migration de la Logique Métier

#### Ancien (v1.0) - Logique dans les routes

```python
# app.py
@app.route('/generate', methods=['POST'])
def generate():
    form_data = request.form.to_dict(flat=False)

    # Validation manuelle
    if not form_data.get('hostname'):
        return "Error: Hostname required", 400

    # Génération CLI
    cli_output = "hostname " + form_data['hostname'][0] + "\n"

    # ... beaucoup plus de code

    return render_template('result.html', config=cli_output)
```

#### Nouveau (v2.0) - Service Layer + Validation Pydantic

```python
# routes/main.py
from schemas.config_schemas import ConfigGenerationRequest
from pydantic import ValidationError

@main_bp.route('/generate', methods=['POST'])
def generate():
    try:
        # Validation automatique
        request_data = ConfigGenerationRequest(**request.form)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400

    # Service layer
    config = ConfigService.generate(request_data)

    return render_template('result.html', config=config)
```

### 4. Migration des Templates

#### Changements dans les URLs

| v1.0 | v2.0 | Notes |
|------|------|-------|
| `/protocol/ospf` | `/protocol/ospf` | ✅ Compatible |
| `/generated-config/router` | `/generated-config/router` | ✅ Compatible |
| `/download-config/router` | `/download-config/router` | ✅ Compatible |

Les templates Jinja2 existants sont **compatibles** avec v2.0 !

---

## 🔐 Migration de la Sécurité

### 1. Externalisation des Secrets

#### Avant (v1.0)

```python
# config.py
SECRET_KEY = 'change-me-to-a-random-secret-key'  # ⚠️ Hardcodé
```

#### Après (v2.0)

```python
# config.py
import os
import sys

SECRET_KEY = os.getenv('SECRET_KEY')

if not SECRET_KEY and os.getenv('FLASK_ENV') == 'production':
    print("ERROR: SECRET_KEY required in production!")
    sys.exit(1)
```

```bash
# .env
SECRET_KEY=$(python utils/generate_secrets.py)
JWT_SECRET_KEY=$(python utils/generate_secrets.py)
```

### 2. Ajout de l'Authentification

#### Créer le Premier Utilisateur Admin

```bash
# Via API
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@company.com",
    "username": "admin",
    "password": "SecurePassword123!",
    "first_name": "Admin",
    "last_name": "User",
    "organization_name": "My Company"
  }'
```

#### Obtenir un Token JWT

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "SecurePassword123!"
  }'

# Response:
# {
#   "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
#   "user": {
#     "id": 1,
#     "username": "admin",
#     "email": "admin@company.com"
#   }
# }
```

#### Utiliser le Token

```bash
# Toutes les requêtes API nécessitent le token
curl -X GET http://localhost:5000/api/devices \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..."
```

---

## 🚀 Déploiement

### Option 1: Docker Compose (Recommandé)

```bash
# 1. Configurer l'environnement
cp .env.example .env
nano .env  # Éditer les secrets

# 2. Démarrer les services
docker-compose up -d

# 3. Vérifier les logs
docker-compose logs -f api

# 4. Initialiser la BD
docker-compose exec api python init_db.py
```

### Option 2: Déploiement Manuel

```bash
# 1. Démarrer PostgreSQL
sudo systemctl start postgresql

# 2. Démarrer Redis
sudo systemctl start redis

# 3. Activer l'environnement virtuel
source venv/bin/activate

# 4. Initialiser la BD
python init_db.py

# 5. Démarrer l'API
gunicorn -w 4 -b 0.0.0.0:5000 app_api:app

# 6. Démarrer Celery Worker (terminal séparé)
celery -A celery_app worker --loglevel=info
```

---

## 🔄 Migration Progressive

### Étape 1: Dual-Run (Semaines 1-2)

```nginx
# nginx.conf - Router le trafic
upstream app_v1 {
    server localhost:5001;  # v1.0 (ancien)
}

upstream app_v2 {
    server localhost:5000;  # v2.0 (nouveau)
}

server {
    listen 80;

    # Rediriger /api vers v2.0
    location /api/ {
        proxy_pass http://app_v2;
    }

    # Reste du trafic vers v1.0
    location / {
        proxy_pass http://app_v1;
    }
}
```

### Étape 2: Canary Deployment (Semaine 3)

```nginx
# Rediriger 10% du trafic vers v2.0
upstream app {
    server localhost:5001 weight=9;  # v1.0 - 90%
    server localhost:5000 weight=1;  # v2.0 - 10%
}
```

### Étape 3: Migration Complète (Semaine 4)

```nginx
# Tout le trafic vers v2.0
upstream app {
    server localhost:5000;  # v2.0 only
}
```

---

## 🐛 Problèmes Courants

### Problème 1: Configurations Manquantes après Migration

**Symptôme**: Les anciennes configurations ne s'affichent pas dans v2.0

**Solution**:
```bash
# Vérifier que les configs sont dans la BD
docker-compose exec postgres psql -U netconfig -d cisco_config_generator

\dt
SELECT COUNT(*) FROM configurations;

# Si vide, réexécuter le script de migration
python scripts/migrate_configs.py
```

### Problème 2: Erreur "SECRET_KEY not set"

**Symptôme**: Application refuse de démarrer

**Solution**:
```bash
# Générer et définir SECRET_KEY
python utils/generate_secrets.py --env > .env
source .env  # Linux/Mac
# ou
set -a; source .env; set +a  # Linux/Mac
```

### Problème 3: Erreur de connexion PostgreSQL

**Symptôme**: "Connection refused" ou "Could not connect"

**Solution**:
```bash
# Vérifier que PostgreSQL est démarré
docker-compose ps postgres

# Vérifier les logs
docker-compose logs postgres

# Tester la connexion
psql -h localhost -U netconfig -d cisco_config_generator
```

### Problème 4: JWT Token Invalide

**Symptôme**: 401 Unauthorized sur les requêtes API

**Solution**:
```bash
# 1. Vérifier que JWT_SECRET_KEY est défini
env | grep JWT_SECRET_KEY

# 2. Re-login pour obtenir un nouveau token
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'

# 3. Utiliser le nouveau token
```

---

## 📊 Vérification Post-Migration

### Checklist de Validation

```bash
# 1. Health Check
curl http://localhost:5000/api/health
# ✅ Attendu: {"status": "healthy"}

# 2. Authentification
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "your_password"}'
# ✅ Attendu: access_token + refresh_token

# 3. Devices
TOKEN="your_access_token"
curl http://localhost:5000/api/devices \
  -H "Authorization: Bearer $TOKEN"
# ✅ Attendu: Liste des devices

# 4. Génération de configuration
curl -X POST http://localhost:5000/api/configs/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"platform": "ios", "hostname": "test-router"}'
# ✅ Attendu: Configuration générée

# 5. Tests automatisés
pytest tests/
# ✅ Attendu: All tests passed
```

---

## 🔙 Rollback

Si des problèmes critiques surviennent :

### Rollback Rapide

```bash
# 1. Arrêter v2.0
docker-compose down

# 2. Redémarrer v1.0
cd v1.0/
python app.py

# 3. Mettre à jour le reverse proxy
sudo systemctl reload nginx
```

### Rollback avec Restauration des Données

```bash
# 1. Restaurer la sauvegarde PostgreSQL
docker-compose exec postgres psql -U netconfig \
  -d cisco_config_generator < backup.sql

# 2. Vérifier l'intégrité
docker-compose exec postgres psql -U netconfig \
  -d cisco_config_generator -c "SELECT COUNT(*) FROM devices;"
```

---

## 📚 Ressources

### Documentation

- **[README.md](README.md)** - Vue d'ensemble du projet
- **[DEVELOPMENT.md](DEVELOPMENT.md)** - Guide de développement
- **[SECURITY.md](SECURITY.md)** - Best practices de sécurité
- **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Configuration backend
- **[FRONTEND_SETUP.md](FRONTEND_SETUP.md)** - Configuration frontend

### Scripts de Migration

```bash
# Scripts utiles (à créer si nécessaire)
scripts/
├── migrate_configs.py      # Migrer configurations
├── migrate_devices.py      # Migrer devices
├── create_admin.py         # Créer utilisateur admin
└── validate_migration.py   # Valider la migration
```

---

## 🆘 Support

### Besoin d'Aide ?

- **Issues GitHub**: [Créer une issue](https://github.com/yourusername/cisco-config-generator/issues)
- **Email**: support@yourcompany.com
- **Documentation**: Consultez les guides ci-dessus

### Migration Assistée

Pour une migration assistée ou des questions spécifiques, contactez l'équipe de support.

---

**✅ Bonne migration vers v2.0 !**
