@echo off
REM ============================================================================
REM Cisco Config Generator - Windows Startup Script
REM ============================================================================
REM
REM Ce script lance automatiquement l'application Flask sur Windows
REM Double-cliquez sur ce fichier pour demarrer l'application
REM
REM ============================================================================

echo.
echo ========================================
echo  Cisco Config Generator v2.0
echo  Demarrage de l'application...
echo ========================================
echo.

REM Verifier si Python est installe
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou n'est pas dans le PATH
    echo.
    echo Telecharger Python depuis: https://www.python.org/downloads/
    echo N'oubliez pas de cocher "Add Python to PATH" lors de l'installation
    echo.
    pause
    exit /b 1
)

REM Verifier si l'environnement virtuel existe
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel
        pause
        exit /b 1
    )
    echo [OK] Environnement virtuel cree
    echo.
)

REM Activer l'environnement virtuel
echo [INFO] Activation de l'environnement virtuel...
call venv\Scripts\activate.bat

REM Verifier si Flask est installe
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installation des dependances (premiere utilisation)...
    echo Cela peut prendre quelques minutes...
    echo.

    REM Mettre a jour pip
    python -m pip install --upgrade pip --quiet

    REM Installer les dependances de base
    pip install Flask>=3.0.0 Flask-SQLAlchemy>=3.1.1 Flask-Migrate>=4.0.5 --quiet
    pip install Flask-CORS>=4.0.0 Jinja2>=3.1.0 PyYAML>=6.0 --quiet
    pip install pydantic>=2.5.0 python-dotenv>=1.0.0 markupsafe>=2.1.0 --quiet

    if errorlevel 1 (
        echo [ERREUR] Echec de l'installation des dependances
        pause
        exit /b 1
    )
    echo [OK] Dependances installees avec succes
    echo.
)

REM Verifier si le fichier .env existe
if not exist ".env" (
    echo [INFO] Creation du fichier .env depuis .env.example...
    if exist ".env.example" (
        copy .env.example .env >nul
        echo [OK] Fichier .env cree
    ) else (
        echo [WARNING] Fichier .env.example non trouve
        echo L'application utilisera les valeurs par defaut
    )
    echo.
)

REM Lancer l'application
echo ========================================
echo  Demarrage du serveur Flask...
echo ========================================
echo.
echo L'application sera accessible a:
echo.
echo    http://localhost:5000
echo    http://127.0.0.1:5000
echo.
echo Appuyez sur CTRL+C pour arreter le serveur
echo.
echo ========================================
echo.

REM Lancer l'application avec Flask
python app.py

REM Si erreur, afficher le message
if errorlevel 1 (
    echo.
    echo ========================================
    echo [ERREUR] L'application a rencontre une erreur
    echo ========================================
    echo.
)

REM Desactiver l'environnement virtuel
deactivate

echo.
echo ========================================
echo Application arretee
echo ========================================
echo.
pause
