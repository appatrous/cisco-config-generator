# 🔧 Guide de Dépannage - Internal Server Error

## ❌ Erreur Rencontrée

```
Internal Server Error
The server encountered an internal error and was unable to complete your request.
```

Cette erreur signifie que l'application Flask a rencontré une exception lors du démarrage ou de l'exécution.

---

## 🚀 Solution Rapide (90% des cas)

### **Méthode 1: Script de Diagnostic Automatique**

```powershell
# Lancer le diagnostic
.\diagnostic.bat
```

Ce script va:
- ✓ Vérifier toutes les dépendances
- ✓ Créer le fichier .env si manquant
- ✓ Installer les packages manquants
- ✓ Vérifier la structure du projet
- ✓ Tester l'application

### **Méthode 2: Diagnostic Python**

```powershell
python diagnostic.py
```

Affiche un rapport détaillé avec toutes les erreurs.

---

## 🔍 Diagnostic Manuel

### **Étape 1: Vérifier les Logs d'Erreur**

Lancer l'application en mode debug pour voir l'erreur exacte:

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\activate

# Lancer en mode debug
python app.py
```

Regardez attentivement le message d'erreur qui s'affiche.

---

### **Étape 2: Erreurs Courantes et Solutions**

#### **Erreur: "No module named 'pydantic'"**

**Solution:**
```powershell
pip install pydantic>=2.5.0
```

#### **Erreur: "No module named 'yaml'"**

**Solution:**
```powershell
pip install PyYAML>=6.0
```

#### **Erreur: "No module named 'dotenv'"**

**Solution:**
```powershell
pip install python-dotenv>=1.0.0
```

#### **Erreur: "SECRET_KEY not set"**

**Solution:** Créer un fichier `.env`:
```powershell
copy .env.minimal .env
```

Ou créer manuellement:
```env
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=ma-cle-secrete-unique
FLASK_RUN_PORT=5000
```

#### **Erreur: "Address already in use" ou "Port 5000 already in use"**

**Solution:** Changer le port dans `.env`:
```env
FLASK_RUN_PORT=8080
```

Ou lancer directement:
```powershell
flask run --port 8080
```

#### **Erreur: "ModuleNotFoundError: No module named 'routes'"**

**Solution:** Vérifier que le dossier `routes` existe:
```powershell
dir routes
```

Si absent, vous êtes dans le mauvais dossier. Naviguez vers le bon dossier:
```powershell
cd C:\chemin\vers\cisco-config-generator
```

#### **Erreur: "ImportError: cannot import name 'register_blueprints'"**

**Solution:** Vérifier le fichier `routes/__init__.py`:
```powershell
type routes\__init__.py
```

#### **Erreur: PostgreSQL ou Redis**

**Solution:** L'application essaie de se connecter à PostgreSQL/Redis qui ne sont pas installés.

Modifier `.env`:
```env
# Commenter ou supprimer ces lignes:
# DATABASE_URL=postgresql://...
# REDIS_URL=redis://...
# CELERY_BROKER_URL=redis://...
```

Ou utiliser `.env.minimal`:
```powershell
copy .env.minimal .env
```

---

### **Étape 3: Réinstaller les Dépendances**

Si le problème persiste, réinstaller toutes les dépendances:

```powershell
# Activer l'environnement virtuel
.\venv\Scripts\activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances de base
pip install Flask>=3.0.0 Flask-SQLAlchemy>=3.1.1 Flask-CORS>=4.0.0
pip install Jinja2>=3.1.0 PyYAML>=6.0 pydantic>=2.5.0
pip install python-dotenv>=1.0.0 markupsafe>=2.1.0 click>=8.1.0
```

---

### **Étape 4: Vérifier la Structure du Projet**

Assurez-vous d'avoir cette structure:

```
cisco-config-generator/
├── app.py
├── config.py
├── .env
├── routes/
│   ├── __init__.py
│   └── config_routes.py
├── services/
│   └── protocol_service.py
├── templates/
│   └── (fichiers HTML)
├── static/
└── venv/
```

Vérifier:
```powershell
dir /b
# Doit afficher: app.py, config.py, routes, services, templates, etc.
```

---

### **Étape 5: Tester l'Import**

Tester si l'application peut être importée:

```powershell
python -c "from app import create_app; app = create_app(); print('OK')"
```

Si erreur, elle s'affichera ici.

---

## 🛠️ Solutions Complètes par Scénario

### **Scénario 1: Première Installation**

```powershell
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. Activer
.\venv\Scripts\activate

# 3. Installer les dépendances de base
pip install Flask>=3.0.0 pydantic>=2.5.0 PyYAML>=6.0 python-dotenv>=1.0.0

# 4. Créer le fichier .env
copy .env.minimal .env

# 5. Créer les dossiers
mkdir uploads
mkdir logs
mkdir config_templates

# 6. Lancer
python app.py
```

### **Scénario 2: Erreur après Mise à Jour**

```powershell
# 1. Activer l'environnement virtuel
.\venv\Scripts\activate

# 2. Mettre à jour toutes les dépendances
pip install --upgrade -r requirements.txt

# 3. Relancer
python app.py
```

### **Scénario 3: Réinstallation Complète**

```powershell
# 1. Supprimer l'ancien environnement virtuel
rmdir /s /q venv

# 2. Recréer
python -m venv venv

# 3. Activer
.\venv\Scripts\activate

# 4. Réinstaller
.\install.bat
```

---

## 📊 Commandes de Diagnostic

### **Vérifier Python:**
```powershell
python --version
where python
```

### **Vérifier pip:**
```powershell
pip --version
pip list
```

### **Vérifier Flask:**
```powershell
python -c "import flask; print(flask.__version__)"
```

### **Vérifier toutes les dépendances:**
```powershell
python -c "import flask, pydantic, yaml; print('Toutes les dépendances OK')"
```

### **Vérifier le fichier .env:**
```powershell
type .env
```

### **Vérifier le port 5000:**
```powershell
netstat -ano | findstr :5000
```

---

## 🚨 Erreurs Spécifiques

### **Erreur: "RuntimeError: Working outside of application context"**

**Cause:** Tentative d'accès à une ressource Flask hors contexte.

**Solution:** Vérifier que `create_app()` est bien appelé dans `app.py`.

### **Erreur: "jinja2.exceptions.TemplateNotFound"**

**Cause:** Fichier template HTML manquant.

**Solution:** Vérifier que le dossier `templates/` existe et contient les fichiers HTML.

### **Erreur: "sqlalchemy.exc.OperationalError"**

**Cause:** Tentative de connexion à PostgreSQL qui n'est pas installé.

**Solution:** Utiliser `.env.minimal` qui n'utilise pas de base de données:
```powershell
copy .env.minimal .env
```

---

## 💡 Conseils de Dépannage

### **1. Toujours activer l'environnement virtuel**
```powershell
.\venv\Scripts\activate
```

### **2. Lire les messages d'erreur complets**
Ne pas fermer la fenêtre immédiatement, lire toute l'erreur.

### **3. Vérifier le fichier .env**
S'assurer qu'il existe et contient au minimum:
```env
FLASK_DEBUG=True
SECRET_KEY=une-cle-quelconque
```

### **4. Tester étape par étape**
```powershell
# Test 1
python -c "import flask"

# Test 2
python -c "from app import create_app"

# Test 3
python app.py
```

### **5. Logs détaillés**
Activer les logs en mode DEBUG dans `.env`:
```env
FLASK_DEBUG=True
LOG_LEVEL=DEBUG
```

---

## 📞 Obtenir de l'Aide

Si le problème persiste après avoir essayé toutes ces solutions:

1. **Exécuter le diagnostic complet:**
   ```powershell
   python diagnostic.py > diagnostic_report.txt
   type diagnostic_report.txt
   ```

2. **Noter l'erreur exacte** affichée dans la console

3. **Vérifier les versions:**
   ```powershell
   python --version
   pip list > versions.txt
   type versions.txt
   ```

4. **Consulter les fichiers:**
   - `INSTALLATION_WINDOWS.md` - Guide d'installation
   - `CONFIG_WINDOWS.md` - Guide de configuration
   - `README.md` - Documentation complète

---

## ✅ Checklist de Vérification

Avant de demander de l'aide, vérifier:

- [ ] Python 3.10+ installé
- [ ] Environnement virtuel créé et activé
- [ ] Dépendances installées (`pip list`)
- [ ] Fichier `.env` existe et contient `SECRET_KEY`
- [ ] Dossiers `routes/`, `services/`, `templates/` existent
- [ ] Port 5000 disponible
- [ ] Lancé depuis le bon dossier
- [ ] `diagnostic.py` exécuté sans erreur

---

**Avec ces solutions, 99% des problèmes sont résolus!** 🚀
