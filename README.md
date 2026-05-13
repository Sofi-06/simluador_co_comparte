# 🌎 Latinoamérica Comparte — Simulador de Markov

Simulación predictiva interactiva de comportamiento de usuarios basada en Cadenas de Markov para la plataforma **Latinoamérica Comparte**.

## 🎯 Características

- **Simulación de Markov**: Modelado de comportamiento de usuarios con cadenas de Markov
- **Análisis Predictivo**: KPIs en tiempo real (tasa de éxito, error, abandono)
- **Visualizaciones Interactivas**: Gráficos con Plotly para exploración de datos
- **Matriz de Transiciones**: Heatmap de probabilidades entre estados
- **Grafo de Estados**: Visualización de red de transiciones
- **Recomendaciones**: Insights accionables basados en análisis
- **Diseño Corporativo**: Identidad visual con colores púrpura de la marca

## 📦 Estructura del Proyecto

```
latinoComparte/
├── src/
│   └── app.py                    # Aplicación principal Streamlit
├── assets/
│   └── logo.png                  # Logo de Latinoamérica Comparte
├── notebooks/
│   └── simulator.ipynb           # Notebook de análisis
├── .streamlit/
│   └── config.toml              # Configuración de Streamlit
├── requirements.txt             # Dependencias del proyecto
├── .gitignore                   # Archivos a ignorar en Git
└── README.md                    # Este archivo
```

## 🚀 Instalación

### Requisitos
- Python 3.8+
- pip (gestor de paquetes de Python)

### Pasos

1. **Clonar o descargar el proyecto**
   ```bash
   cd latinoComparte
   ```

2. **Crear un ambiente virtual** (opcional pero recomendado)
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Uso

### Ejecutar la aplicación
```bash
streamlit run src/app.py
```

La aplicación se abrirá en `http://localhost:8501` en tu navegador.

### Controles Principales
- **Usuarios a simular**: Ajusta el número de usuarios (5-100)
- **Máximo de pasos**: Define la profundidad de recorridos (5-100)
- **Estado inicial**: Selecciona el estado de partida
- **Simular**: Ejecuta la simulación
- **Limpiar**: Reinicia los resultados

### Tabs de Análisis
- **📊 Análisis**: Métricas agregadas y KPIs
- **🔄 Transiciones**: Matriz de probabilidades
- **🗺️ Recorridos**: Grafo interactivo de estados
- **⚠️ Críticos**: Estados críticos detectados
- **💡 Recomendaciones**: Insights y mejoras sugeridas

## 📊 Análisis Disponible

### KPIs Principales
- **Tasa de Éxito**: Porcentaje de usuarios con resultados exitosos
- **Tasa de Error**: Porcentaje de usuarios que encuentran errores
- **Tasa de Abandono**: Porcentaje de usuarios que abandonan el flujo
- **Promedio de Pasos**: Media de transiciones por usuario

### Estados del Sistema
- **36 Estados**: Modelado completo del flujo de usuario
- **Estados Críticos**: Puntos donde se concentran errores
- **Estados Finales**: Salidas del sistema
- **Estados Intermedios**: Transiciones normales

### Tipos de Resultado
- ✅ **Éxito**: Usuarios que alcanzan objetivos
- ❌ **Error**: Usuarios que encuentran problemas
- 🚪 **Abandono**: Usuarios que dejan la plataforma

## 🎨 Diseño Visual

- **Tema**: Dark mode elegante con identidad corporativa
- **Colores Principales**: Púrpura (#a78bfa) - Corporativo
- **Paleta Complementaria**: Verdes (#10b981), Rojos (#ef4444), Ámbar (#f59e0b)
- **Logo**: Marca Latinoamérica Comparte integrada

## 📝 Dependencias

```
streamlit==1.39.0       # Framework web interactivo
pandas==2.2.3           # Análisis de datos
numpy==1.26.4           # Cálculos numéricos
plotly==5.24.1          # Gráficos interactivos
networkx==3.3           # Análisis de grafos
pillow==10.4.0          # Procesamiento de imágenes
```

## 🔧 Configuración

### Archivo `config.toml`
```toml
[theme]
primaryColor = "#a78bfa"        # Púrpura corporativo
backgroundColor = "#0a0e27"     # Dark background
secondaryBackgroundColor = "#131829"  # Cards
textColor = "#e8eaed"           # Light gray text

[server]
headless = true                 # No UI de servidor
runOnSave = true                # Recargar en cambios
```

## 📈 Ejemplo de Uso

1. Abre la aplicación
2. En el sidebar, configura:
   - Usuarios: 50
   - Máximo de pasos: 25
   - Estado inicial: S0 (Sesión no iniciada)
3. Haz clic en **Simular**
4. Explora los tabs para ver análisis

## 🤝 Contribuciones

Para mejorar el simulador:
1. Sugiere nuevos estados o transiciones
2. Propone mejoras visuales
3. Reporta problemas o bugs

## 📞 Contacto

Proyecto desarrollado para **Latinoamérica Comparte**

## 📄 Licencia

Desarrollado para uso interno de Latinoamérica Comparte.

---

**Versión**: 2.0  
**Última actualización**: Mayo 2026  
**Autor**: Equipo de Desarrollo
