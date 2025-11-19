# 🪟 Guide d'Installation Windows

## ⚡ Installation Rapide (5 minutes)

### Étape 1: Installer Python

1. **Télécharger Python 3.10+** depuis https://www.python.org/downloads/
2. **IMPORTANT**: Cocher "Add Python to PATH" lors de l'installation
3. Vérifier l'installation en ouvrant **PowerShell** ou **CMD**:
   ```powershell
   python --version
   ```
   Résultat attendu: `Python 3.10.x` ou supérieur

### Étape 2: Cloner ou Télécharger le Projet

**Option A - Avec Git:**
```powershell
git clone <url-du-repo>
cd cisco-config-generator
```

**Option B - Sans Git:**
1. Télécharger le ZIP du projet
2. Extraire dans un dossier (ex: `C:\cisco-config-generator`)
3. Ouvrir PowerShell dans ce dossier

### Étape 3: Créer un Environnement Virtuel

```powershell
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
.\venv\Scripts\activate

# Vous devriez voir (venv) au début de votre ligne de commande
```

### Étape 4: Installer les Dépendances

```powershell
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances principales (sans dépendances optionnelles)
pip install Flask>=3.0.0 Flask-SQLAlchemy>=3.1.1 Flask-Migrate>=4.0.5
pip install Flask-CORS>=4.0.0 Jinja2>=3.1.0 PyYAML>=6.0
pip install pydantic>=2.5.0 python-dotenv>=1.0.0 markupsafe>=2.1.0

# OU installer TOUTES les dépendances (peut prendre plus de temps)
pip install -r requirements.txt
```

**Note**: Si vous avez des erreurs avec certaines dépendances (PostgreSQL, Redis), ignorez-les pour l'instant. L'application peut fonctionner sans.

### Étape 5: Configuration (Optionnel)

Créer un fichier `.env` à la racine du projet:

```powershell
# Copier le fichier d'exemple
copy .env.example .env
```

Éditer `.env` avec Notepad ou VS Code:
```env
# Configuration de base
SECRET_KEY=votre_cle_secrete_ici_generez_une_cle_aleatoire
FLASK_DEBUG=True
FLASK_ENV=development

# Port d'écoute (par défaut 5000)
FLASK_RUN_PORT=5000
FLASK_RUN_HOST=127.0.0.1
```

**Note**: Si vous ne créez pas de `.env`, l'application générera automatiquement une clé secrète temporaire.

### Étape 6: Lancer l'Application

```powershell
# Activer l'environnement virtuel si ce n'est pas déjà fait
.\venv\Scripts\activate

# Lancer l'application
python app.py
```

**OU avec Flask CLI:**
```powershell
flask run
```

**OU avec mode debug:**
```powershell
python app.py --debug
```

Vous devriez voir:
```
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

### Étape 7: Accéder à l'Application

Ouvrir votre navigateur web et aller à:
```
http://localhost:5000
```

ou
```
http://127.0.0.1:5000
```

🎉 **C'est tout! L'application est maintenant accessible!**

---

## 🚀 Utilisation Quotidienne

### Démarrer l'Application

```powershell
# Naviguer vers le dossier du projet
cd C:\chemin\vers\cisco-config-generator

# Activer l'environnement virtuel
.\venv\Scripts\activate

# Lancer l'application
python app.py
```

### Arrêter l'Application

Appuyer sur **CTRL+C** dans la fenêtre PowerShell

### Désactiver l'Environnement Virtuel

```powershell
deactivate
```

---

## 📋 Protocoles Disponibles (41 protocoles - 100%)

L'application supporte actuellement **41 protocoles Cisco** répartis en catégories:

### Layer 2 (8 protocoles)
- VLAN, VTP, DHCP Snooping, Dynamic ARP Inspection
- IP Source Guard, IGMP Snooping, Private VLAN, Voice VLAN

### Layer 3 Routing (8 protocoles)
- Static Routing, OSPF, EIGRP, BGP, RIP
- Multicast Routing, IGMP, PIM

### High Availability (3 protocoles)
- HSRP, VRRP, GLBP

### NAT (3 protocoles)
- Static NAT, Dynamic NAT, PAT

### Security (5 protocoles)
- ACL, Object Groups, Zone-Based Firewall
- IDS/IPS, SSL/TLS Inspection

### VPN & Tunnels (3 protocoles)
- GRE, SSL VPN, AnyConnect

### Services (9 protocoles)
- AAA, SNMP, Syslog, NTP/PTP
- DHCP Server/Relay, NetFlow, QoS, VRF, GNOC

### ASA Specific (2 protocoles)
- ASA Failover/Clustering

---

## 🔧 Dépannage

### Problème: "python n'est pas reconnu"

**Solution**: Python n'est pas dans le PATH
1. Réinstaller Python en cochant "Add Python to PATH"
2. OU ajouter manuellement Python au PATH:
   - Variables d'environnement → Path → Ajouter `C:\Users\VotreNom\AppData\Local\Programs\Python\Python3XX`

### Problème: "pip install" échoue

**Solutions**:
```powershell
# Mettre à jour pip
python -m pip install --upgrade pip

# Installer setuptools et wheel
pip install setuptools wheel

# Réessayer l'installation
pip install -r requirements.txt
```

### Problème: Erreur avec PostgreSQL/psycopg2

**Solution**: Installer uniquement les dépendances de base
```powershell
# Ne pas installer psycopg2-binary si vous n'utilisez pas PostgreSQL
pip install --no-deps -r requirements.txt
```

### Problème: Port 5000 déjà utilisé

**Solution**: Changer le port
```powershell
# Dans .env, modifier:
FLASK_RUN_PORT=8080

# OU lancer avec:
flask run --port 8080
```

### Problème: "Access Denied" ou permission refusée

**Solution**: Lancer PowerShell en tant qu'Administrateur
1. Clic droit sur PowerShell
2. "Exécuter en tant qu'administrateur"
3. Naviguer vers le dossier du projet
4. Relancer les commandes

### Problème: Erreur d'exécution de scripts PowerShell

**Solution**: Autoriser l'exécution de scripts
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 💡 Astuces

### Accéder depuis un autre PC sur le réseau

Modifier `.env`:
```env
FLASK_RUN_HOST=0.0.0.0
```

Puis accéder via: `http://IP_DE_VOTRE_PC:5000`

### Lancer en arrière-plan

Utiliser **Windows Terminal** ou créer un fichier batch `start.bat`:
```batch
@echo off
cd C:\chemin\vers\cisco-config-generator
call venv\Scripts\activate
python app.py
pause
```

Double-cliquer sur `start.bat` pour lancer l'application.

### Mode Production

```powershell
# Dans .env:
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=generez_une_vraie_cle_secrete_forte

# Lancer avec:
python app.py
```

---

## 📚 Prochaines Étapes

1. **Explorer l'Interface**: Tester la génération de configurations pour différents protocoles
2. **Lire la Documentation**: Consulter `PROTOCOL_STATUS.md` pour voir tous les protocoles disponibles
3. **Personnaliser**: Modifier les templates dans `templates/` selon vos besoins
4. **Contribuer**: Ajouter de nouveaux protocoles ou améliorer l'interface

---

## 🆘 Support

- **Documentation Complète**: Lire `README.md`
- **Statut des Protocoles**: Voir `PROTOCOL_STATUS.md`
- **Problèmes**: Créer un ticket GitHub Issues

---

**Version**: v2.0 ✅ Production Ready
**Dernière mise à jour**: 2025-11-19
**Compatibilité**: Windows 10/11, Python 3.10+
