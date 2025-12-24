@echo off
setlocal enabledelayedexpansion

echo ########################################
echo #   GemShot Ultimate - Windows Setup   #
echo ########################################
echo.

:: 1. Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python no detectado. Intentando instalar via Winget...
    winget install Python.Python.3.11 --silent --accept-package-agreements --accept-source-agreements
    if %errorlevel% neq 0 (
        echo [X] Error: No se pudo instalar Python automaticamente. 
        echo Por favor, instalalo manualmente desde python.org
        pause
        exit /b
    )
    echo [+] Python instalado. Por favor, REINICIA este script.
    pause
    exit /b
)

echo [+] Python detectado.
echo [+] Instalando dependencias (requirements.txt)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

:: Prepare zero‑install distribution
echo Preparing zero‑install distribution...
python prepare_dist.py
if %errorlevel% neq 0 (
    echo [!] Error preparing distribution.
) else (
    echo Distribution ready in dist_zero_install.
)

@echo off
:: After installing dependencies, ask if the user wants to run the app
if %errorlevel% equ 0 (
    echo.
    echo ########################################
    echo #      INSTALACION COMPLETADA          #
    echo ########################################
    echo Puedes ejecutar GemShot ahora.
    set /p run_now="¿Quieres ejecutar GemShot ahora? (S/N): "
    if /I "%run_now%"=="S" (
        start "" "GemShot Launch.bat"
    ) else (
        echo "GemShot no se ejecutará ahora."
    )
) else (
    echo [X] Hubo un error instalando librerias.
)

pause
