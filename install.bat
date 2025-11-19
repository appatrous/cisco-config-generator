@echo off
REM ============================================================================
REM Cisco Config Generator - Windows Installation Script
REM ============================================================================
REM
REM Ce script installe toutes les dependances necessaires
REM Executez ce fichier UNE SEULE FOIS lors de la premiere installation
REM
REM ============================================================================

echo.
echo ========================================
echo  Cisco Config Generator v2.0
echo  Script d'Installation Windows
echo ========================================
echo.

REM Verifier si Python est installe
echo [1/6] Verification de Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Veuillez installer Python 3.10 ou superieur depuis:
    echo https://www.python.org/downloads/
    echo.
    echo N'oubliez pas de cocher "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

python --version
echo [OK] Python detecte
echo.

REM Creer l'environnement virtuel
echo [2/6] Creation de l'environnement virtuel...
if exist "venv" (
    echo [WARNING] L'environnement virtuel existe deja
    echo Voulez-vous le recreer? (O/N)
    set /p recreate=
    if /i "%recreate%"=="O" (
        echo Suppression de l'ancien environnement virtuel...
        rmdir /s /q venv
        python -m venv venv
    )
) else (
    python -m venv venv
)

if errorlevel 1 (
    echo [ERREUR] Impossible de creer l'environnement virtuel
    pause
    exit /b 1
)
echo [OK] Environnement virtuel cree
echo.

REM Activer l'environnement virtuel
echo [3/6] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat
echo [OK] Environnement virtuel active
echo.

REM Mettre a jour pip
echo [4/6] Mise a jour de pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo [WARNING] La mise a jour de pip a echoue, continuation...
)
echo [OK] pip mis a jour
echo.

REM Installer les dependances
echo [5/6] Installation des dependances...
echo Cela peut prendre quelques minutes...
echo.

REM Choix d'installation
echo Choisissez le type d'installation:
echo.
echo 1. Installation BASIQUE (recommandee - rapide)
echo    - Toutes les fonctionnalites principales
echo    - Pas de base de donnees externe
echo    - Pas de task queue
echo.
echo 2. Installation COMPLETE (avancee - lente)
echo    - Toutes les dependances
echo    - Support PostgreSQL et Redis
echo    - Outils de developpement
echo.
set /p install_type="Votre choix (1 ou 2): "

if "%install_type%"=="2" (
    echo.
    echo Installation COMPLETE en cours...
    pip install -r requirements.txt
) else (
    echo.
    echo Installation BASIQUE en cours...
    pip install Flask>=3.0.0 Flask-SQLAlchemy>=3.1.1 Flask-Migrate>=4.0.5
    pip install Flask-CORS>=4.0.0 Jinja2>=3.1.0 PyYAML>=6.0
    pip install pydantic>=2.5.0 python-dotenv>=1.0.0 markupsafe>=2.1.0
    pip install click>=8.1.0 email-validator>=2.1.0
)

if errorlevel 1 (
    echo [ERREUR] L'installation des dependances a echoue
    echo.
    echo Solutions possibles:
    echo 1. Verifiez votre connexion internet
    echo 2. Executez PowerShell en tant qu'Administrateur
    echo 3. Essayez: pip install --upgrade setuptools wheel
    echo.
    pause
    exit /b 1
)
echo [OK] Dependances installees avec succes
echo.

REM Creer le fichier .env
echo [6/6] Configuration de l'environnement...
if not exist ".env" (
    if exist ".env.example" (
        copy .env.example .env
        echo [OK] Fichier .env cree depuis .env.example
    ) else (
        echo [WARNING] .env.example non trouve
        echo Creation d'un fichier .env minimal...
        (
            echo # Cisco Config Generator - Configuration
            echo FLASK_ENV=development
            echo FLASK_DEBUG=True
            echo SECRET_KEY=dev_secret_key_change_in_production
        ) > .env
        echo [OK] Fichier .env minimal cree
    )
) else (
    echo [INFO] Fichier .env existe deja
)
echo.

REM Creer les dossiers necessaires
if not exist "uploads" mkdir uploads
if not exist "config_templates" mkdir config_templates
if not exist "logs" mkdir logs

echo ========================================
echo  Installation Terminee avec Succes!
echo ========================================
echo.
echo Prochaines etapes:
echo.
echo 1. Double-cliquez sur start.bat pour lancer l'application
echo    OU executez: python app.py
echo.
echo 2. Ouvrez votre navigateur a: http://localhost:5000
echo.
echo 3. Consultez INSTALLATION_WINDOWS.md pour plus d'informations
echo.
echo 4. Pour arreter l'application: Appuyez sur CTRL+C
echo.
echo ========================================
echo.

REM Desactiver l'environnement virtuel
deactivate

echo Appuyez sur une touche pour quitter...
pause >nul
