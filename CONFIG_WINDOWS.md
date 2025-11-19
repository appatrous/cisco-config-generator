# 🔧 Configuration pour Windows - Guide Simple

## 📁 Fichiers de Configuration Disponibles

Vous avez **3 options** de fichier `.env` selon vos besoins:

### ✅ Option 1: Configuration MINIMALE (Recommandée pour débuter)

**Fichier**: `.env.minimal`

**Utilisation**:
```powershell
# Copier le fichier minimal
copy .env.minimal .env
```

**Contenu**:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=ma-cle-secrete-ultra-secrete-2025
FLASK_RUN_PORT=5000
```

**Avantages**:
- ✅ 4 lignes seulement
- ✅ Rapide à configurer
- ✅ Aucune dépendance externe
- ✅ Parfait pour tester l'application

---

### ⭐ Option 2: Configuration WINDOWS (Recommandée pour utilisation régulière)

**Fichier**: `.env.windows`

**Utilisation**:
```powershell
# Copier le fichier Windows
copy .env.windows .env
```

**Contenu**: Configuration complète avec commentaires en français

**Avantages**:
- ✅ Tous les paramètres expliqués en français
- ✅ Optimisé pour Windows
- ✅ Sans dépendances Docker/PostgreSQL/Redis
- ✅ Prêt pour personnalisation

---

### 🚀 Option 3: Configuration COMPLÈTE (Pour utilisateurs avancés)

**Fichier**: `.env.example`

**Utilisation**:
```powershell
# Copier le fichier complet
copy .env.example .env
```

**Avantages**:
- ✅ Toutes les fonctionnalités disponibles
- ✅ Support PostgreSQL, Redis, Celery
- ✅ Multi-tenancy
- ✅ JWT Authentication

**Inconvénients**:
- ⚠️ Nécessite l'installation de PostgreSQL
- ⚠️ Nécessite l'installation de Redis
- ⚠️ Configuration plus complexe

---

## 🎯 Quelle Option Choisir?

### Vous êtes DÉBUTANT ou voulez TESTER l'application?
→ **Utilisez `.env.minimal`** (4 lignes, ultra simple)

### Vous utilisez l'application RÉGULIÈREMENT sur Windows?
→ **Utilisez `.env.windows`** (optimisé Windows, sans Docker)

### Vous êtes DÉVELOPPEUR et voulez TOUTES les fonctionnalités?
→ **Utilisez `.env.example`** (complet avec PostgreSQL/Redis)

---

## 📝 Guide d'Installation Étape par Étape

### Méthode 1: Configuration Minimale (La Plus Simple)

```powershell
# 1. Naviguer vers le projet
cd C:\cisco-config-generator

# 2. Copier le fichier minimal
copy .env.minimal .env

# 3. (Optionnel) Éditer le fichier
notepad .env

# 4. Modifier UNIQUEMENT la SECRET_KEY:
#    SECRET_KEY=votre_nouvelle_cle_aleatoire

# 5. Sauvegarder et fermer

# 6. C'est prêt!
```

### Méthode 2: Configuration Windows (Recommandée)

```powershell
# 1. Naviguer vers le projet
cd C:\cisco-config-generator

# 2. Copier le fichier Windows
copy .env.windows .env

# 3. Éditer le fichier
notepad .env

# 4. Modifier les valeurs importantes:
#    - SECRET_KEY: Générer une clé unique
#    - FLASK_RUN_PORT: Changer si 5000 est occupé
#    - FLASK_RUN_HOST: Mettre 0.0.0.0 pour accès réseau

# 5. Sauvegarder et fermer
```

---

## 🔐 Générer une Clé Secrète Sécurisée

### Méthode Python (Recommandée):

```powershell
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Résultat exemple**:
```
xK9mP2vN8qR5wT7yU3jL6hF4sD1aG0bC5vM8nQ2wE7rT9yU4iO6pA3sD
```

Copiez ce résultat dans votre `.env`:
```env
SECRET_KEY=xK9mP2vN8qR5wT7yU3jL6hF4sD1aG0bC5vM8nQ2wE7rT9yU4iO6pA3sD
```

### Méthode Manuelle (Simple mais moins sécurisée):

Inventez une longue phrase aléatoire:
```env
SECRET_KEY=MonSuperMotDePasse2025AvecDesChiffres123456!
```

---

## ⚙️ Paramètres Importants Expliqués

### FLASK_ENV
```env
# development = Mode développement (affiche les erreurs)
# production = Mode production (masque les erreurs)
FLASK_ENV=development
```

### FLASK_DEBUG
```env
# True = Affiche les erreurs détaillées (utile pour déboguer)
# False = Masque les erreurs (utiliser en production)
FLASK_DEBUG=True
```

### FLASK_RUN_PORT
```env
# Port par défaut: 5000
# Si occupé, essayer: 8080, 8000, 3000
FLASK_RUN_PORT=5000
```

### FLASK_RUN_HOST
```env
# 127.0.0.1 = Accès UNIQUEMENT depuis votre PC
# 0.0.0.0 = Accès depuis TOUT le réseau local
FLASK_RUN_HOST=127.0.0.1
```

---

## 🌐 Accéder depuis un Autre PC du Réseau

**Étape 1**: Modifier `.env`
```env
FLASK_RUN_HOST=0.0.0.0
FLASK_RUN_PORT=5000
```

**Étape 2**: Trouver votre adresse IP
```powershell
ipconfig
# Chercher "IPv4 Address" (exemple: 192.168.1.100)
```

**Étape 3**: Autoriser dans le pare-feu Windows
```
Panneau de configuration → Pare-feu Windows
→ Paramètres avancés → Règles de trafic entrant
→ Nouvelle règle → Port TCP 5000 → Autoriser
```

**Étape 4**: Accéder depuis un autre PC
```
http://192.168.1.100:5000
```

---

## 🔧 Personnalisation Avancée

### Changer le Port

**Dans `.env`**:
```env
FLASK_RUN_PORT=8080
```

**OU en ligne de commande**:
```powershell
flask run --port 8080
```

### Augmenter la Taille des Fichiers Uploadés

**Dans `.env`**:
```env
# 50 MB = 52428800 bytes
MAX_UPLOAD_SIZE=52428800
```

### Changer le Dossier d'Upload

**Dans `.env`**:
```env
UPLOAD_FOLDER=mes_fichiers
```

### Activer les Logs Détaillés

**Dans `.env`**:
```env
LOG_LEVEL=DEBUG
```

---

## ✅ Vérifier la Configuration

### Vérifier que le fichier .env existe:
```powershell
dir .env
# Vous devez voir le fichier
```

### Vérifier le contenu:
```powershell
type .env
# Affiche le contenu du fichier
```

### Tester l'application:
```powershell
python app.py
# Devrait démarrer sans erreur
```

### Vérifier les variables d'environnement chargées:
```powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('SECRET_KEY:', os.getenv('SECRET_KEY'))"
```

---

## 🚨 Dépannage

### Problème: "No module named 'dotenv'"

**Solution**:
```powershell
pip install python-dotenv
```

### Problème: Le fichier .env n'est pas chargé

**Solution**: Vérifier que le fichier s'appelle bien `.env` (pas `.env.txt`)
```powershell
# Renommer si nécessaire
ren .env.txt .env
```

### Problème: SECRET_KEY non définie

**Solution**: Ajouter une ligne dans `.env`:
```env
SECRET_KEY=ma-cle-secrete-changez-moi
```

### Problème: Port déjà utilisé

**Solution**: Changer le port dans `.env`:
```env
FLASK_RUN_PORT=8080
```

---

## 📋 Template de Fichier .env Complet

Voici un template complet prêt à copier-coller:

```env
# Configuration Flask de Base
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=CHANGEZ_CETTE_CLE_PAR_UNE_VALEUR_ALEATOIRE_UNIQUE
SESSION_LIFETIME=3600
MAX_UPLOAD_SIZE=16777216

# Configuration du Serveur
FLASK_RUN_PORT=5000
FLASK_RUN_HOST=127.0.0.1

# Dossiers
UPLOAD_FOLDER=uploads
CONFIG_TEMPLATE_DIR=config_templates

# Logging
LOG_LEVEL=INFO

# API
API_RATE_LIMIT=100/hour
ITEMS_PER_PAGE=50
CORS_ORIGINS=http://localhost:3000,http://localhost:5000

# Multi-tenancy (désactivé par défaut)
MULTI_TENANT_ENABLED=False
```

---

## 💡 Conseils de Sécurité

### ✅ À FAIRE:
- Générer une SECRET_KEY unique et aléatoire
- Ne JAMAIS partager votre fichier `.env`
- Mettre FLASK_DEBUG=False en production
- Changer ADMIN_PASSWORD par défaut

### ❌ À NE PAS FAIRE:
- Ne jamais commiter `.env` dans Git
- Ne jamais utiliser "password123" ou "admin"
- Ne jamais exposer votre application sur Internet sans sécurité
- Ne jamais laisser FLASK_DEBUG=True en production

---

**Vous êtes maintenant prêt à configurer l'application!** 🚀

Pour toute question, consultez:
- `INSTALLATION_WINDOWS.md` - Guide d'installation
- `README.md` - Documentation complète
- `PROTOCOL_STATUS.md` - Liste des protocoles
