@echo off
REM ============================================================================
REM Cisco Config Generator - Script de Diagnostic
REM ============================================================================

echo.
echo ========================================
echo  Diagnostic de l'Application
echo ========================================
echo.

REM Activer l'environnement virtuel
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

echo [1/8] Verification de Python...
python --version
if errorlevel 1 (
    echo [ERREUR] Python non trouve
    pause
    exit /b 1
)
echo.

echo [2/8] Verification des imports Flask...
python -c "import flask; print('Flask version:', flask.__version__)" 2>nul
if errorlevel 1 (
    echo [ERREUR] Flask n'est pas installe
    echo Installation de Flask...
    pip install Flask>=3.0.0
)
echo.

echo [3/8] Verification des dependances critiques...
python -c "import pydantic; print('Pydantic OK')" 2>nul
if errorlevel 1 (
    echo [WARNING] Pydantic manquant, installation...
    pip install pydantic>=2.5.0
)

python -c "import yaml; print('PyYAML OK')" 2>nul
if errorlevel 1 (
    echo [WARNING] PyYAML manquant, installation...
    pip install PyYAML>=6.0
)

python -c "from dotenv import load_dotenv; print('python-dotenv OK')" 2>nul
if errorlevel 1 (
    echo [WARNING] python-dotenv manquant, installation...
    pip install python-dotenv>=1.0.0
)
echo.

echo [4/8] Verification du fichier .env...
if exist ".env" (
    echo [OK] Fichier .env existe
    type .env | findstr "SECRET_KEY" >nul
    if errorlevel 1 (
        echo [WARNING] SECRET_KEY non trouve dans .env
    )
) else (
    echo [WARNING] Fichier .env manquant
    echo Creation d'un fichier .env minimal...
    (
        echo FLASK_ENV=development
        echo FLASK_DEBUG=True
        echo SECRET_KEY=dev-secret-key-auto-generated
        echo FLASK_RUN_PORT=5000
    ) > .env
    echo [OK] Fichier .env cree
)
echo.

echo [5/8] Verification de la structure du projet...
if exist "app.py" (
    echo [OK] app.py existe
) else (
    echo [ERREUR] app.py non trouve
)

if exist "routes" (
    echo [OK] Dossier routes existe
) else (
    echo [WARNING] Dossier routes manquant
)

if exist "services" (
    echo [OK] Dossier services existe
) else (
    echo [WARNING] Dossier services manquant
)

if exist "templates" (
    echo [OK] Dossier templates existe
) else (
    echo [WARNING] Dossier templates manquant
)
echo.

echo [6/8] Test d'import de l'application...
python -c "from app import create_app; print('Import app OK')" 2>test_import_error.txt
if errorlevel 1 (
    echo [ERREUR] Impossible d'importer l'application
    echo Erreur detaillee:
    type test_import_error.txt
    del test_import_error.txt
    echo.
    echo Solutions possibles:
    echo 1. Verifier que toutes les dependances sont installees
    echo 2. Verifier la syntaxe Python dans app.py
    echo 3. Installer les dependances manquantes
    pause
    exit /b 1
) else (
    echo [OK] Application importee avec succes
    if exist "test_import_error.txt" del test_import_error.txt
)
echo.

echo [7/8] Verification du port 5000...
netstat -ano | findstr :5000 >nul
if errorlevel 1 (
    echo [OK] Port 5000 disponible
) else (
    echo [WARNING] Port 5000 deja utilise
    echo Processus utilisant le port 5000:
    netstat -ano | findstr :5000
    echo.
    echo Solution: Changer le port dans .env
    echo Exemple: FLASK_RUN_PORT=8080
)
echo.

echo [8/8] Creation des dossiers necessaires...
if not exist "uploads" mkdir uploads && echo [OK] Dossier uploads cree
if not exist "logs" mkdir logs && echo [OK] Dossier logs cree
if not exist "config_templates" mkdir config_templates && echo [OK] Dossier config_templates cree
echo.

echo ========================================
echo  Diagnostic Termine
echo ========================================
echo.
echo Voulez-vous essayer de lancer l'application maintenant? (O/N)
set /p launch=

if /i "%launch%"=="O" (
    echo.
    echo Lancement de l'application en mode debug...
    echo.
    python app.py
)

pause
