"""
Script de diagnostic pour identifier les problèmes de l'application.
Exécutez ce script pour obtenir des informations détaillées sur les erreurs.
"""
import sys
import os

print("="*60)
print("DIAGNOSTIC DE L'APPLICATION CISCO CONFIG GENERATOR")
print("="*60)
print()

# Test 1: Version Python
print("[1/10] Version Python:")
print(f"  Python {sys.version}")
print()

# Test 2: Vérification des imports de base
print("[2/10] Test des imports de base:")
try:
    import flask
    print(f"  ✓ Flask {flask.__version__}")
except ImportError as e:
    print(f"  ✗ Flask: {e}")
    sys.exit(1)

try:
    import pydantic
    print(f"  ✓ Pydantic {pydantic.__version__}")
except ImportError as e:
    print(f"  ✗ Pydantic: {e}")

try:
    import yaml
    print(f"  ✓ PyYAML OK")
except ImportError as e:
    print(f"  ✗ PyYAML: {e}")

try:
    from dotenv import load_dotenv
    print(f"  ✓ python-dotenv OK")
except ImportError as e:
    print(f"  ✗ python-dotenv: {e}")

print()

# Test 3: Fichier .env
print("[3/10] Vérification du fichier .env:")
if os.path.exists('.env'):
    print("  ✓ Fichier .env existe")
    load_dotenv()
    secret_key = os.getenv('SECRET_KEY')
    if secret_key:
        print(f"  ✓ SECRET_KEY définie")
    else:
        print(f"  ✗ SECRET_KEY non définie")
else:
    print("  ✗ Fichier .env manquant")
    print("  → Créer un fichier .env avec:")
    print("     FLASK_ENV=development")
    print("     FLASK_DEBUG=True")
    print("     SECRET_KEY=votre-cle-secrete")
print()

# Test 4: Structure du projet
print("[4/10] Vérification de la structure du projet:")
required_files = ['app.py', 'config.py']
required_dirs = ['routes', 'services', 'templates', 'static']

for file in required_files:
    if os.path.exists(file):
        print(f"  ✓ {file}")
    else:
        print(f"  ✗ {file} manquant")

for dir in required_dirs:
    if os.path.exists(dir):
        print(f"  ✓ {dir}/")
    else:
        print(f"  ⚠ {dir}/ manquant")
print()

# Test 5: Import de config.py
print("[5/10] Test d'import de config.py:")
try:
    import config
    print(f"  ✓ Config importé")
    print(f"  → SECRET_KEY: {'Défini' if hasattr(config, 'SECRET_KEY') and config.SECRET_KEY else 'Non défini'}")
    print(f"  → DEBUG: {getattr(config, 'DEBUG', 'Non défini')}")
except Exception as e:
    print(f"  ✗ Erreur: {e}")
print()

# Test 6: Import des routes
print("[6/10] Test d'import des routes:")
try:
    from routes import register_blueprints
    print(f"  ✓ Routes importées")
except Exception as e:
    print(f"  ✗ Erreur: {e}")
    print(f"  → Détails: {type(e).__name__}")
print()

# Test 7: Import des services
print("[7/10] Test d'import des services:")
try:
    from services.protocol_service import ProtocolService
    print(f"  ✓ ProtocolService importé")
except Exception as e:
    print(f"  ✗ Erreur: {e}")
print()

# Test 8: Création de l'application
print("[8/10] Test de création de l'application Flask:")
try:
    from app import create_app
    app = create_app()
    print(f"  ✓ Application créée avec succès")
    print(f"  → Debug mode: {app.config.get('DEBUG')}")
    print(f"  → Secret key: {'Défini' if app.secret_key else 'Non défini'}")
except Exception as e:
    print(f"  ✗ Erreur lors de la création de l'app: {e}")
    import traceback
    print("\nStack trace complet:")
    traceback.print_exc()
    sys.exit(1)
print()

# Test 9: Liste des blueprints
print("[9/10] Blueprints enregistrés:")
try:
    from app import create_app
    app = create_app()
    for blueprint in app.blueprints:
        print(f"  ✓ {blueprint}")
except Exception as e:
    print(f"  ✗ Erreur: {e}")
print()

# Test 10: Test des routes
print("[10/10] Test des routes principales:")
try:
    from app import create_app
    app = create_app()
    with app.test_client() as client:
        # Test route principale
        response = client.get('/')
        print(f"  → GET /: Status {response.status_code}")

        # Test route protocols
        response = client.get('/protocols')
        print(f"  → GET /protocols: Status {response.status_code}")
except Exception as e:
    print(f"  ✗ Erreur lors du test des routes: {e}")
    import traceback
    traceback.print_exc()
print()

print("="*60)
print("DIAGNOSTIC TERMINÉ")
print("="*60)
print()

# Recommandations
print("RECOMMANDATIONS:")
print()

# Vérifier les erreurs critiques
errors = []

if not os.path.exists('.env'):
    errors.append("Créer un fichier .env avec les paramètres de base")

try:
    import pydantic
except ImportError:
    errors.append("Installer pydantic: pip install pydantic>=2.5.0")

try:
    import yaml
except ImportError:
    errors.append("Installer PyYAML: pip install PyYAML>=6.0")

if errors:
    print("Problèmes détectés:")
    for i, error in enumerate(errors, 1):
        print(f"  {i}. {error}")
else:
    print("✓ Aucun problème critique détecté!")
    print()
    print("L'application devrait fonctionner.")
    print("Pour démarrer: python app.py")

print()
print("="*60)
