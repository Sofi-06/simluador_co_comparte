#!/bin/bash
# Script para ejecutar el Simulador de Latinoamérica Comparte
# ===========================================================

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Latinoamérica Comparte - Simulador de Markov        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python no está instalado. Por favor instala Python 3.8+"
    exit 1
fi

# Crear ambiente virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando ambiente virtual..."
    python3 -m venv venv
fi

# Activar ambiente virtual
echo "⚙️  Activando ambiente virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -q -r requirements.txt

# Ejecutar la aplicación
echo ""
echo "✅ Iniciando aplicación..."
echo "🌐 Accede a: http://localhost:8501"
echo ""
streamlit run src/app.py
