import time
from collections import Counter
import os

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image


# Configuración general de la página
st.set_page_config(
    page_title="Latinoamérica Comparte — Simulador",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Obtener la ruta del directorio actual
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))  # src/
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)  # latinoComparte/
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
LOGO_PATH = os.path.join(ASSETS_DIR, "logo.png")


def inject_styles() -> None:
    """Dark mode elegante con paleta púrpura corporativa."""
    st.markdown(
        """
        <style>
        :root {
            --bg-dark: #0a0e27;
            --bg-card: #131829;
            --bg-hover: #1a1f3a;
            --text-primary: #e8eaed;
            --text-secondary: #9ca3af;
            --accent: #a78bfa;
            --accent-light: #d8b4fe;
            --accent-glow: rgba(167, 139, 250, 0.15);
            --accent-dark: #7c3aed;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: rgba(167, 139, 250, 0.2);
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 8px 24px rgba(0, 0, 0, 0.4);
        }

        .stApp {
            background: linear-gradient(135deg, var(--bg-dark) 0%, #1a0f35 100%);
            color: var(--text-primary);
        }

        section[data-testid="stSidebar"] {
            background: var(--bg-dark);
            border-right: 1px solid var(--border);
        }

        .logo-banner {
            text-align: center;
            padding: 16px 0;
            margin-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }

        .logo-image {
            max-width: 120px;
            margin-bottom: 12px;
        }

        .logo-text {
            font-size: 1.3rem;
            font-weight: 900;
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin: 0;
            letter-spacing: -0.02em;
        }

        .logo-subtitle {
            font-size: 0.75rem;
            color: var(--text-secondary);
            margin: 4px 0 0 0;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }

        .hero-banner {
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-hover) 100%);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 32px;
            margin-bottom: 28px;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
        }

        .hero-banner::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 300px;
            height: 300px;
            background: radial-gradient(circle, rgba(167, 139, 250, 0.12) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(100px, -100px);
        }

        .hero-banner::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(124, 58, 237, 0.08) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(-50px, 50px);
        }

        .hero-title {
            font-size: 2rem;
            font-weight: 800;
            color: var(--text-primary);
            margin: 0 0 10px 0;
            letter-spacing: -0.02em;
            position: relative;
            z-index: 1;
        }

        .hero-title::before {
            content: '';
            display: block;
            width: 40px;
            height: 4px;
            background: linear-gradient(90deg, var(--accent) 0%, var(--accent-light) 100%);
            border-radius: 2px;
            margin-bottom: 12px;
        }

        .hero-subtitle {
            color: var(--text-secondary);
            font-size: 0.95rem;
            line-height: 1.7;
            margin: 0;
            position: relative;
            z-index: 1;
        }

        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 14px;
            margin: 24px 0 0 0;
            position: relative;
            z-index: 1;
        }

        .kpi-card {
            background: linear-gradient(135deg, rgba(167, 139, 250, 0.08), rgba(167, 139, 250, 0.03));
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
        }

        .kpi-card::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
        }

        .kpi-card:hover {
            background: linear-gradient(135deg, rgba(167, 139, 250, 0.15), rgba(167, 139, 250, 0.08));
            border-color: var(--accent);
            box-shadow: 0 0 20px rgba(167, 139, 250, 0.2);
            transform: translateY(-2px);
        }

        .kpi-label {
            color: var(--text-secondary);
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .kpi-value {
            color: var(--accent-light);
            font-size: 1.6rem;
            font-weight: 800;
            margin: 0;
        }

        .section-title {
            font-size: 1.35rem;
            font-weight: 800;
            color: var(--text-primary);
            margin: 0 0 4px 0;
            letter-spacing: -0.01em;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .section-title::before {
            content: '';
            width: 3px;
            height: 24px;
            background: linear-gradient(180deg, var(--accent), transparent);
            border-radius: 2px;
        }

        .panel-card {
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-hover) 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
            position: relative;
        }

        .panel-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-light), transparent);
            border-radius: 10px 10px 0 0;
        }

        .panel-card:hover {
            border-color: rgba(167, 139, 250, 0.4);
            box-shadow: 0 0 20px rgba(167, 139, 250, 0.12);
        }

        .section-copy {
            color: var(--text-secondary);
            line-height: 1.8;
            font-size: 0.95rem;
            margin: 0;
        }

        .success-card {
            background: linear-gradient(135deg, rgba(16, 185, 129, 0.08), rgba(16, 185, 129, 0.02));
            border-color: rgba(16, 185, 129, 0.3);
        }

        .warning-card {
            background: linear-gradient(135deg, rgba(245, 158, 11, 0.08), rgba(245, 158, 11, 0.02));
            border-color: rgba(245, 158, 11, 0.3);
        }

        .error-card {
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.08), rgba(239, 68, 68, 0.02));
            border-color: rgba(239, 68, 68, 0.3);
        }

        .success-card::before {
            background: linear-gradient(90deg, transparent, var(--success), transparent) !important;
        }

        .warning-card::before {
            background: linear-gradient(90deg, transparent, var(--warning), transparent) !important;
        }

        .error-card::before {
            background: linear-gradient(90deg, transparent, var(--danger), transparent) !important;
        }

        .alert-title {
            color: var(--text-primary);
            font-weight: 700;
            font-size: 0.95rem;
            margin: 0 0 8px 0;
        }

        .alert-copy {
            color: var(--text-secondary);
            font-size: 0.9rem;
            line-height: 1.8;
            margin: 0;
        }

        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background: transparent;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border);
        }

        .stTabs [data-baseweb="tab"] {
            background: rgba(167, 139, 250, 0.05);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 16px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(167, 139, 250, 0.12);
            border-color: var(--accent);
            color: var(--accent-light);
        }

        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(167, 139, 250, 0.25), rgba(167, 139, 250, 0.12));
            border-color: var(--accent);
            color: var(--accent-light);
        }

        .stButton button {
            background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
            color: #0a0e27;
            border: 0;
            border-radius: 8px;
            font-weight: 700;
            font-size: 0.95rem;
            width: 100%;
            padding: 0.8rem 1.2rem;
            box-shadow: 0 8px 16px rgba(167, 139, 250, 0.25);
            transition: all 0.3s ease;
            font-weight: 600;
        }

        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(167, 139, 250, 0.35);
            background: linear-gradient(135deg, #9370db 0%, #c084fc 100%);
        }

        .metric-highlight {
            color: var(--accent-light);
            font-weight: 700;
        }

        .state-chip {
            display: inline-block;
            background: rgba(167, 139, 250, 0.12);
            border: 1px solid var(--border);
            border-radius: 6px;
            padding: 6px 12px;
            margin: 4px 4px 4px 0;
            color: var(--accent-light);
            font-size: 0.85rem;
            transition: all 0.2s ease;
            font-weight: 500;
        }

        .state-chip:hover {
            background: rgba(167, 139, 250, 0.2);
            border-color: var(--accent);
            box-shadow: 0 0 12px rgba(167, 139, 250, 0.2);
        }

        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-hover) 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            box-shadow: var(--shadow-sm);
        }

        div[data-testid="stMetric"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
            border-radius: 10px 10px 0 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_markov_assets():
    """Carga el modelo base con estados, recorridos y pesos de negocio."""
    recorridos = [
        ["S0", "S28", "S29"],
        ["S0", "S28", "S30"],
        ["S0", "S28", "S31"],
        ["S0", "S28", "S33", "S34", "S35"],
        ["S0", "S28", "S33", "S34", "S36"],
        ["S0", "S28", "S30", "S33", "S34", "S35"],
        ["S0", "S28", "S32", "S0"],
        ["S0", "S28", "S29", "S30", "S28", "S31"],
        ["S0", "S28", "S31", "S32", "S0"],
        ["S0", "S28", "S0"],
        ["S0", "S28", "S30", "S28", "S0"],
        ["S0", "S28", "S33", "S34", "S36", "S33", "S34", "S35"],
        ["S0", "S1", "S2", "S3", "S0"],
        ["S0", "S1", "S2", "S3", "S1", "S2", "S3"],
        ["S0", "S1", "S0"],
        ["S0", "S1", "S2", "S3", "S28", "S33", "S34", "S35"],
        ["S0", "S1", "S2", "S3", "S1", "S2", "S4", "S9"],
        ["S0", "S1", "S2", "S4", "S9"],
        ["S4", "S9", "S10", "S11"],
        ["S4", "S9", "S10", "S12", "S10", "S11"],
        ["S4", "S9", "S10", "S12", "S9"],
        ["S4", "S9", "S13", "S14"],
        ["S4", "S9", "S13", "S9"],
        ["S4", "S9", "S4", "S7", "S0"],
        ["S4", "S28", "S33", "S34", "S35"],
        ["S4", "S9", "S10", "S11", "S7", "S0"],
        ["S0", "S1", "S2", "S5", "S15"],
        ["S5", "S15", "S16", "S17"],
        ["S5", "S15", "S16", "S23", "S0"],
        ["S5", "S15", "S16", "S23", "S16", "S17"],
        ["S5", "S15", "S18", "S17"],
        ["S5", "S15", "S19"],
        ["S5", "S15", "S24", "S15"],
        ["S5", "S25", "S26", "S27"],
        ["S5", "S25", "S26", "S27", "S7", "S0"],
        ["S5", "S28", "S32", "S0"],
        ["S5", "S15", "S16", "S17", "S7", "S0"],
        ["S5", "S28", "S33", "S34", "S35", "S29"],
        ["S5", "S28", "S33", "S34", "S36", "S29"],
        ["S0", "S1", "S2", "S6", "S15"],
        ["S6", "S15", "S22", "S21"],
        ["S6", "S15", "S20", "S21"],
        ["S6", "S15", "S16", "S17"],
        ["S6", "S15", "S18", "S23", "S18", "S17"],
        ["S6", "S15", "S18", "S23", "S15"],
        ["S6", "S15", "S18", "S15", "S0"],
        ["S6", "S28", "S32", "S0"],
        ["S6", "S28", "S33", "S34", "S35", "S29"],
        ["S6", "S15", "S22", "S21", "S7", "S0"],
        ["S0", "S1", "S2", "S6", "S15", "S18", "S17", "S7", "S0"],
        ["S0", "S28", "S30", "S31", "S33", "S34", "S35", "S0"],
        ["S0", "S1", "S2", "S3", "S28", "S29", "S0"],
        ["S5", "S15", "S18", "S15", "S16", "S17"],
        ["S6", "S15", "S20", "S21", "S28", "S31", "S7", "S0"],
        ["S0", "S28", "S29", "S32", "S33", "S34", "S35", "S0"],
        ["S4", "S9", "S10", "S12", "S10", "S11", "S9", "S10", "S11"],
        ["S5", "S25", "S26", "S27", "S15", "S18", "S17"],
        ["S6", "S15", "S16", "S17", "S28", "S30", "S7", "S0"],
        ["S0", "S28", "S33", "S34", "S36", "S0"],
        ["S5", "S15", "S24", "S15", "S18", "S17", "S7", "S0"],
        ["S6", "S15", "S22", "S23", "S22", "S21"],
    ]

    estados = [
        "S0", "S1", "S2", "S3", "S4", "S5", "S6", "S7", "S8",
        "S9", "S10", "S11", "S12", "S13", "S14", "S15", "S16",
        "S17", "S18", "S19", "S20", "S21", "S22", "S23", "S24",
        "S25", "S26", "S27", "S28", "S29", "S30", "S31", "S32",
        "S33", "S34", "S35", "S36",
    ]

    estados_finales = [
        "S3", "S7", "S8", "S11", "S12", "S14", "S17", "S19",
        "S21", "S23", "S27", "S29", "S30", "S32", "S35", "S36",
    ]

    nombres_estados = {
        "S0": "Sesión no iniciada",
        "S1": "Formulario de login visible",
        "S2": "Credenciales en ingreso",
        "S3": "Autenticación fallida",
        "S4": "Sesión activa - Superadmin",
        "S5": "Sesión activa - Admin",
        "S6": "Sesión activa - Editor",
        "S7": "Sesión cerrada manualmente",
        "S8": "Sesión cerrada por inactividad",
        "S9": "Panel de usuarios abierto",
        "S10": "Formulario de usuario en diligenciamiento",
        "S11": "Usuario registrado exitosamente",
        "S12": "Error al registrar usuario",
        "S13": "Formulario de edición de usuario activo",
        "S14": "Usuario modificado exitosamente",
        "S15": "Panel de contenido por país abierto",
        "S16": "Formulario de noticia en diligenciamiento",
        "S17": "Noticia visible públicamente",
        "S18": "Formulario de edición de noticia activo",
        "S19": "Noticia eliminada",
        "S20": "Formulario de testimonio en diligenciamiento",
        "S21": "Testimonio visible públicamente",
        "S22": "Formulario de edición de testimonio activo",
        "S23": "Error al gestionar contenido",
        "S24": "Detalle de noticia visible",
        "S25": "Panel de solicitudes abierto",
        "S26": "Detalle de solicitud visible",
        "S27": "Estado de solicitud actualizado",
        "S28": "Página de inicio cargada",
        "S29": "Contenido general en navegación",
        "S30": "Sección de noticias visible",
        "S31": "Sección de testimonios visible",
        "S32": "Acceso denegado por permisos",
        "S33": "Chatbot iniciado",
        "S34": "Consulta en procesamiento",
        "S35": "Respuesta del chatbot exitosa",
        "S36": "Respuesta del chatbot no disponible",
    }

    weighted_success_states = {
        "Estado de solicitud actualizado": 0.10,
        "Contenido general en navegación": 0.10,
        "Sección de noticias visible": 0.10,
        "Respuesta del chatbot exitosa": 0.15,
        "Noticia visible públicamente": 0.15,
        "Testimonio visible públicamente": 0.15,
        "Usuario registrado exitosamente": 0.10,
        "Usuario modificado exitosamente": 0.05,
        "Noticia eliminada": 0.10,
    }

    weighted_error_states = {
        "Autenticación fallida": 0.40,
        "Acceso denegado por permisos": 0.20,
        "Error al registrar usuario": 0.15,
        "Error al gestionar contenido": 0.15,
        "Respuesta del chatbot no disponible": 0.10,
    }

    weighted_abandonment_states = {
        "Sesión cerrada manualmente": 0.60,
        "Sesión cerrada por inactividad": 0.40,
    }

    critical_states = {"S3", "S12", "S23", "S32", "S36", "S8"}
    success_states = set(weighted_success_states.keys())
    error_states = set(weighted_error_states.keys())
    abandonment_states = set(weighted_abandonment_states.keys())

    matriz_conteos = pd.DataFrame(0, index=estados, columns=estados)
    for recorrido in recorridos:
        for i in range(len(recorrido) - 1):
            matriz_conteos.loc[recorrido[i], recorrido[i + 1]] += 1

    matriz_probabilidades = matriz_conteos.div(matriz_conteos.sum(axis=1), axis=0).fillna(0)

    return {
        "recorridos": recorridos,
        "estados": estados,
        "estados_finales": estados_finales,
        "nombres_estados": nombres_estados,
        "weighted_success_states": weighted_success_states,
        "weighted_error_states": weighted_error_states,
        "weighted_abandonment_states": weighted_abandonment_states,
        "critical_states": critical_states,
        "success_states": success_states,
        "error_states": error_states,
        "abandonment_states": abandonment_states,
        "matriz_conteos": matriz_conteos,
        "matriz_probabilidades": matriz_probabilidades,
    }


def classify_result(result_name: str, assets: dict) -> str:
    if result_name in assets["success_states"]:
        return "Éxito"
    if result_name in assets["error_states"]:
        return "Error"
    if result_name in assets["abandonment_states"]:
        return "Abandono"
    return "Otro"


def simulate_user(matriz_probabilidades: pd.DataFrame, estados_finales: list[str], estado_inicial: str, max_pasos: int) -> list[str]:
    """Ejecuta un recorrido de usuario siguiendo las probabilidades de Markov."""
    estado_actual = estado_inicial
    recorrido = [estado_actual]

    for _ in range(max_pasos):
        if estado_actual in estados_finales:
            break

        probabilidades = matriz_probabilidades.loc[estado_actual]
        if probabilidades.sum() == 0:
            break

        siguiente_estado = np.random.choice(matriz_probabilidades.columns, p=probabilidades.values)
        recorrido.append(siguiente_estado)
        estado_actual = siguiente_estado

    return recorrido


def calculate_weighted_percentages(df_resultados: pd.DataFrame, assets: dict) -> dict:
    """Calcula la distribucion ponderada de exito, error y abandono."""
    def score(states_dict: dict) -> float:
        total = 0.0
        for state_name, weight in states_dict.items():
            total += df_resultados[df_resultados["resultado"] == state_name].shape[0] * weight
        return total

    weighted_success = score(assets["weighted_success_states"])
    weighted_error = score(assets["weighted_error_states"])
    weighted_abandonment = score(assets["weighted_abandonment_states"])
    total_weighted = weighted_success + weighted_error + weighted_abandonment

    if total_weighted == 0:
        return {"Éxito": 0.0, "Error": 0.0, "Abandono": 0.0}

    return {
        "Éxito": weighted_success / total_weighted * 100,
        "Error": weighted_error / total_weighted * 100,
        "Abandono": weighted_abandonment / total_weighted * 100,
    }


def run_simulation(assets: dict, num_usuarios: int, max_pasos: int, estado_inicial: str, seed: int = 42) -> pd.DataFrame:
    """Simula multiples usuarios y produce un dataset analitico."""
    np.random.seed(seed)
    resultados = []

    for i in range(num_usuarios):
        recorrido = simulate_user(
            assets["matriz_probabilidades"],
            assets["estados_finales"],
            estado_inicial=estado_inicial,
            max_pasos=max_pasos,
        )
        estado_final = recorrido[-1]
        resultados.append(
            {
                "usuario": i + 1,
                "recorrido_lista": recorrido,
                "recorrido": " → ".join(recorrido),
                "estado_final": estado_final,
                "estado_final_nombre": assets["nombres_estados"].get(estado_final, estado_final),
                "num_pasos": len(recorrido),
                "truncado": estado_final not in assets["estados_finales"],
            }
        )

    df = pd.DataFrame(resultados)
    df["resultado"] = df["estado_final_nombre"]
    df["categoria_final"] = df["resultado"].apply(lambda name: classify_result(name, assets))

    visitas = []
    for _, row in df.iterrows():
        for orden, estado in enumerate(row["recorrido_lista"], start=1):
            visitas.append(
                {
                    "usuario": row["usuario"],
                    "orden": orden,
                    "estado": estado,
                    "estado_nombre": assets["nombres_estados"][estado],
                    "estado_tipo": state_type(estado, assets),
                }
            )
    visitas_df = pd.DataFrame(visitas)
    return df, visitas_df


def state_type(state_code: str, assets: dict) -> str:
    if state_code in assets["critical_states"]:
        return "Crítico"
    if state_code in assets["estados_finales"]:
        return "Final"
    return "Intermedio"


def compute_summary(df_resultados: pd.DataFrame, df_visitas: pd.DataFrame, assets: dict) -> dict:
    """Resume KPIs e insights clave de la simulacion."""
    result_counts = df_resultados["resultado"].value_counts()
    top_result = result_counts.index[0] if not result_counts.empty else "Sin datos"
    weighted = calculate_weighted_percentages(df_resultados, assets)
    estados_visitados = df_visitas["estado"].value_counts()

    critical_visits = df_visitas[df_visitas["estado"].isin(assets["critical_states"])]["estado_nombre"].value_counts()
    critical_state = critical_visits.index[0] if not critical_visits.empty else "Sin incidencias"

    success_rate = (df_resultados["categoria_final"] == "Éxito").mean() * 100 if not df_resultados.empty else 0
    error_rate = (df_resultados["categoria_final"] == "Error").mean() * 100 if not df_resultados.empty else 0
    abandonment_rate = (df_resultados["categoria_final"] == "Abandono").mean() * 100 if not df_resultados.empty else 0

    return {
        "top_result": top_result,
        "critical_state": critical_state,
        "success_rate": success_rate,
        "error_rate": error_rate,
        "abandonment_rate": abandonment_rate,
        "avg_steps": df_resultados["num_pasos"].mean() if not df_resultados.empty else 0,
        "weighted": weighted,
        "top_states": estados_visitados.head(8),
    }


def generate_recommendations(summary: dict, df_resultados: pd.DataFrame, df_visitas: pd.DataFrame) -> list[dict]:
    """Genera recomendaciones claras y accionables."""
    recommendations = []
    error_rate = summary["error_rate"]
    abandonment_rate = summary["abandonment_rate"]
    success_rate = summary["success_rate"]

    if success_rate >= 50:
        recommendations.append({
            "type": "success",
            "title": "Desempeño sólido",
            "text": f"Tasa de éxito de {success_rate:.0f}%. Considera replicar estos patrones en otras áreas."
        })
    
    if error_rate >= 25:
        recommendations.append({
            "type": "error",
            "title": "Revisar puntos de error",
            "text": f"Errores en {error_rate:.0f}% de casos. Enfócate en validaciones y manejo de excepciones."
        })

    if abandonment_rate >= 20:
        recommendations.append({
            "type": "warning",
            "title": "Reducir abandonos",
            "text": f"Abandono de {abandonment_rate:.0f}%. Simplifica el flujo y mejora el feedback visual."
        })
    
    error_states = df_resultados[df_resultados["categoria_final"] == "Error"]["resultado"].value_counts().head(1)
    if not error_states.empty:
        recommendations.append({
            "type": "error",
            "title": f"Cuello de botella: {error_states.index[0]}",
            "text": f"Este estado aparece {error_states.values[0]} veces en errores. Prioriza su revisión."
        })

    most_visited = df_visitas["estado_nombre"].value_counts().head(1)
    if not most_visited.empty:
        recommendations.append({
            "type": "success",
            "title": f"Zona de alto tráfico detectada",
            "text": f"{most_visited.index[0]} es un buen candidato para mejorar experiencia."
        })

    return recommendations[:4]


def hero_section(summary: dict, assets: dict, usuarios: int) -> None:
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=150)
        else:
            st.markdown("### LC")
    
    kpi_html = f"""
    <div class="hero-banner">
        <div class="hero-title">Latinoamérica Comparte</div>
        <div class="hero-subtitle">
            Simulación predictiva de comportamiento de usuarios basada en Cadenas de Markov
        </div>
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Estados</div>
                <div class="kpi-value">{len(assets["estados"])}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Usuarios</div>
                <div class="kpi-value">{usuarios}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Éxito</div>
                <div class="kpi-value" style="color: #10b981;">{summary['success_rate']:.0f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Error</div>
                <div class="kpi-value" style="color: #ef4444;">{summary['error_rate']:.0f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Promedio Pasos</div>
                <div class="kpi-value" style="color: #f59e0b;">{summary['avg_steps']:.1f}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)


def build_heatmap(matriz_probabilidades: pd.DataFrame) -> go.Figure:
    fig = go.Figure(
        data=go.Heatmap(
            z=matriz_probabilidades.values,
            x=matriz_probabilidades.columns,
            y=matriz_probabilidades.index,
            colorscale=[
                [0.0, "#0a0e27"],
                [0.2, "#3d2a5a"],
                [0.45, "#6c3fa6"],
                [0.7, "#8b5cf6"],
                [1.0, "#a78bfa"],
            ],
            text=(matriz_probabilidades * 100).round(1).astype(str) + "%",
            texttemplate="%{text}",
            hovertemplate="Actual: %{y}<br>Siguiente: %{x}<br>Probabilidad: %{z:.2%}<extra></extra>",
        )
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaed"),
    )
    return fig


def build_state_graph(assets: dict) -> go.Figure:
    """Construye el grafo visual de estados y transiciones."""
    matrix = assets["matriz_probabilidades"]
    graph = nx.DiGraph()

    for state in assets["estados"]:
        graph.add_node(state, label=assets["nombres_estados"][state], kind=state_type(state, assets))

    for source in matrix.index:
        row = matrix.loc[source]
        for target, prob in row[row > 0].items():
            graph.add_edge(source, target, weight=float(prob))

    pos = nx.spring_layout(graph, seed=11, k=0.95)

    edge_traces = []
    for source, target, data in graph.edges(data=True):
        x0, y0 = pos[source]
        x1, y1 = pos[target]
        edge_traces.append(
            go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode="lines",
                line=dict(width=max(data["weight"] * 12, 1.2), color="rgba(96, 165, 250, 0.25)"),
                hoverinfo="text",
                text=f"{source} → {target}<br>{data['weight']:.1%}",
                showlegend=False,
            )
        )

    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []
    palette = {"Intermedio": "#a78bfa", "Final": "#10b981", "Crítico": "#ef4444"}
    size_map = {"Intermedio": 18, "Final": 24, "Crítico": 30}

    for node, attrs in graph.nodes(data=True):
        kind = attrs["kind"]
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(f"{node}<br>{attrs['label']}<br>{kind}")
        node_color.append(palette[kind])
        node_size.append(size_map[kind])

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        text=list(graph.nodes()),
        textposition="top center",
        hovertext=node_text,
        hoverinfo="text",
        marker=dict(size=node_size, color=node_color, line=dict(width=1.5, color="#131829")),
        showlegend=False,
    )

    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        margin=dict(l=10, r=10, t=30, b=10),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        font=dict(color="#e8eaed"),
        height=640,
    )
    return fig


def render_sidebar(assets: dict) -> tuple[int, int, str, bool]:
    with st.sidebar:
        # Logo de la empresa - Mostrar imagen
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=100)
            else:
                st.markdown("**LC**")
        
        st.markdown(
            """
            <div style="text-align: center; margin: 12px 0;">
                <div style="font-size: 1rem; font-weight: 900; background: linear-gradient(135deg, #a78bfa 0%, #d8b4fe 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                    Latinoamérica Comparte
                </div>
                <div style="font-size: 0.7rem; color: #9ca3af; letter-spacing: 0.05em; margin-top: 4px;">
                    Simulador de Markov
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Cadenas de Markov · Análisis Predictivo")
        st.markdown("---")

        num_usuarios = st.slider(
            "Usuarios a simular", 
            min_value=5, 
            max_value=100, 
            value=25, 
            step=5
        )
        
        max_pasos = st.slider(
            "Máximo de pasos", 
            min_value=5, 
            max_value=100, 
            value=20, 
            step=5
        )
        
        estado_inicial = st.selectbox(
            "Estado inicial",
            assets["estados"],
            index=assets["estados"].index("S0"),
            format_func=lambda state: f"{state} · {assets['nombres_estados'][state]}"
        )

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            iniciar = st.button("Simular", use_container_width=True, type="primary")
        with col2:
            resetear = st.button("Limpiar", use_container_width=True)
        
        if resetear:
            if "df_resultados" in st.session_state:
                del st.session_state["df_resultados"]
            if "df_visitas" in st.session_state:
                del st.session_state["df_visitas"]
            if "sim_before" in st.session_state:
                del st.session_state["sim_before"]
            st.rerun()
            
    return num_usuarios, max_pasos, estado_inicial, iniciar


def perform_simulation(assets: dict, num_usuarios: int, max_pasos: int, estado_inicial: str) -> None:
    """Ejecuta la simulación con progreso y métricas en vivo."""
    progress = st.sidebar.progress(0, text="Preparando...")
    live_box = st.sidebar.empty()
    results = []
    visitas = []
    chunk = max(25, num_usuarios // 20)
    np.random.seed(42)

    for i in range(num_usuarios):
        recorrido = simulate_user(assets["matriz_probabilidades"], assets["estados_finales"], estado_inicial, max_pasos)
        estado_final = recorrido[-1]
        result_name = assets["nombres_estados"].get(estado_final, estado_final)
        results.append(
            {
                "usuario": i + 1,
                "recorrido_lista": recorrido,
                "recorrido": " → ".join(recorrido),
                "estado_final": estado_final,
                "estado_final_nombre": result_name,
                "num_pasos": len(recorrido),
                "truncado": estado_final not in assets["estados_finales"],
                "resultado": result_name,
                "categoria_final": classify_result(result_name, assets),
            }
        )

        for orden, estado in enumerate(recorrido, start=1):
            visitas.append(
                {
                    "usuario": i + 1,
                    "orden": orden,
                    "estado": estado,
                    "estado_nombre": assets["nombres_estados"][estado],
                    "estado_tipo": state_type(estado, assets),
                }
            )

        if (i + 1) % chunk == 0 or i + 1 == num_usuarios:
            parcial = pd.DataFrame(results)
            categorias = parcial["categoria_final"].value_counts(normalize=True).mul(100).round(1)
            live_box.markdown(
                f"""
                <div class="panel-card">
                    <div class="section-title" style="font-size: 1rem;">Progreso</div>
                    <div class="section-copy">
                        <strong>{i + 1}/{num_usuarios}</strong> usuarios<br>
                        ✅ {categorias.get("Éxito", 0):.1f}% | ❌ {categorias.get("Error", 0):.1f}% | 🚪 {categorias.get("Abandono", 0):.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            progress.progress(int((i + 1) / num_usuarios * 100), text=f"Usuario {i + 1} de {num_usuarios}")
            time.sleep(0.02)

    progress.empty()
    live_box.empty()
    st.session_state["df_resultados"] = pd.DataFrame(results)
    st.session_state["df_visitas"] = pd.DataFrame(visitas)
    st.session_state["sim_params"] = {
        "usuarios": num_usuarios,
        "max_pasos": max_pasos,
        "estado_inicial": estado_inicial,
    }


def main():
    inject_styles()
    assets = load_markov_assets()
    
    num_usuarios, max_pasos, estado_inicial, iniciar = render_sidebar(assets)
    
    if iniciar:
        perform_simulation(assets, num_usuarios, max_pasos, estado_inicial)
    
    if "df_resultados" not in st.session_state:
        st.session_state["df_resultados"] = pd.DataFrame()
        st.session_state["df_visitas"] = pd.DataFrame()
    
    df_resultados = st.session_state.get("df_resultados", pd.DataFrame())
    df_visitas = st.session_state.get("df_visitas", pd.DataFrame())
    
    if df_resultados.empty:
        summary = {
            "top_result": "Sin simulación",
            "success_rate": 0,
            "error_rate": 0,
            "abandonment_rate": 0,
            "avg_steps": 0,
        }
    else:
        summary = compute_summary(df_resultados, df_visitas, assets)
    
    hero_section(summary, assets, num_usuarios)
    
    if not df_resultados.empty:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Análisis", "🔄 Transiciones", "🗺️ Recorridos", "⚠️ Críticos", "💡 Recomendaciones"])
        
        with tab1:
            st.subheader("Métricas Agregadas")
            col1, col2, col3 = st.columns(3)
            col1.metric("Tasa de Éxito", f"{summary['success_rate']:.1f}%", delta=f"({int(df_resultados[df_resultados['categoria_final'] == 'Éxito'].shape[0])} usuarios)")
            col2.metric("Tasa de Error", f"{summary['error_rate']:.1f}%", delta=f"({int(df_resultados[df_resultados['categoria_final'] == 'Error'].shape[0])} usuarios)")
            col3.metric("Abandono", f"{summary['abandonment_rate']:.1f}%", delta=f"({int(df_resultados[df_resultados['categoria_final'] == 'Abandono'].shape[0])} usuarios)")
        
        with tab2:
            st.subheader("Matriz de Probabilidades")
            st.plotly_chart(build_heatmap(assets["matriz_probabilidades"]), use_container_width=True)
        
        with tab3:
            st.subheader("Grafo de Estados")
            st.plotly_chart(build_state_graph(assets), use_container_width=True)
        
        with tab4:
            critical = df_visitas[df_visitas["estado_tipo"] == "Crítico"]["estado_nombre"].value_counts()
            if not critical.empty:
                st.bar_chart(critical)
            else:
                st.info("Sin estados críticos detectados")
        
        with tab5:
            recommendations = generate_recommendations(summary, df_resultados, df_visitas)
            for rec in recommendations:
                card_class = f"{rec['type']}-card"
                st.markdown(
                    f"""
                    <div class="panel-card {card_class}">
                        <div class="alert-title">{rec['title']}</div>
                        <div class="alert-copy">{rec['text']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


if __name__ == "__main__":
    main()
