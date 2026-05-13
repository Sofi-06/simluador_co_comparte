@echo off
REM Script para ejecutar el Simulador de Latinoamérica Comparte
REM =========================================================

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║   Latinoamérica Comparte - Simulador de Markov        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python no está instalado. Por favor instala Python 3.8+
    pause
    exit /b 1
)

REM Crear ambiente virtual si no existe
if not exist "venv" (
    echo 📦 Creando ambiente virtual...
    python -m venv venv
)

REM Activar ambiente virtual
echo ⚙️  Activando ambiente virtual...
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📚 Instalando dependencias...
pip install -q -r requirements.txt

REM Ejecutar la aplicación
echo.
echo ✅ Iniciando aplicación...
echo 🌐 Accede a: http://localhost:8501
echo.
streamlit run src/app.py

pause
