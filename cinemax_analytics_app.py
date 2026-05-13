import base64
import os
import time
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ── Configuración general ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="Latinoamérica Comparte — Simulador",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

LOGO_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "assets", "logo.png"
)


# ── Logo helper ───────────────────────────────────────────────────────────────
def get_logo_html(max_width: int = 120) -> str:
    """Devuelve <img> en base64 si existe el archivo, o texto fallback."""
    if os.path.exists(LOGO_PATH):
        ext = os.path.splitext(LOGO_PATH)[1].lower().lstrip(".")
        mime = "svg+xml" if ext == "svg" else ext
        with open(LOGO_PATH, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (
            f'<img src="data:image/{mime};base64,{b64}" '
            f'style="max-width:{max_width}px;display:block;margin:0 auto 8px auto;" />'
        )
    return '<div class="logo-text">&#9670; LC</div>'


# ── Estilos ───────────────────────────────────────────────────────────────────
def inject_styles() -> None:
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
        .logo-text {
            font-size: 2rem;
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
            top: 0; right: 0;
            width: 300px; height: 300px;
            background: radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 70%);
            border-radius: 50%;
            transform: translate(100px, -100px);
        }
        .hero-banner::after {
            content: '';
            position: absolute;
            bottom: 0; left: 0;
            width: 200px; height: 200px;
            background: radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%);
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
            width: 40px; height: 4px;
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
            background: linear-gradient(135deg, rgba(167,139,250,0.08), rgba(167,139,250,0.03));
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
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent), transparent);
        }
        .kpi-card:hover {
            background: linear-gradient(135deg, rgba(167,139,250,0.15), rgba(167,139,250,0.08));
            border-color: var(--accent);
            box-shadow: 0 0 20px rgba(167,139,250,0.2);
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
            width: 3px; height: 24px;
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
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--accent-light), transparent);
            border-radius: 10px 10px 0 0;
        }
        .panel-card:hover {
            border-color: rgba(167,139,250,0.4);
            box-shadow: 0 0 20px rgba(167,139,250,0.12);
        }
        .section-copy {
            color: var(--text-secondary);
            line-height: 1.8;
            font-size: 0.95rem;
            margin: 0;
        }
        .success-card {
            background: linear-gradient(135deg, rgba(16,185,129,0.08), rgba(16,185,129,0.02));
            border-color: rgba(16,185,129,0.3);
        }
        .warning-card {
            background: linear-gradient(135deg, rgba(245,158,11,0.08), rgba(245,158,11,0.02));
            border-color: rgba(245,158,11,0.3);
        }
        .error-card {
            background: linear-gradient(135deg, rgba(239,68,68,0.08), rgba(239,68,68,0.02));
            border-color: rgba(239,68,68,0.3);
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
            background: rgba(167,139,250,0.05);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 10px 16px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            transition: all 0.2s ease;
            font-weight: 500;
        }
        .stTabs [data-baseweb="tab"]:hover {
            background: rgba(167,139,250,0.12);
            border-color: var(--accent);
            color: var(--accent-light);
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(135deg, rgba(167,139,250,0.25), rgba(167,139,250,0.12));
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
            box-shadow: 0 8px 16px rgba(167,139,250,0.25);
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(167,139,250,0.35);
            background: linear-gradient(135deg, #9370db 0%, #c084fc 100%);
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(135deg, var(--bg-card) 0%, var(--bg-hover) 100%);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 16px;
            box-shadow: var(--shadow-sm);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ── Datos del modelo ──────────────────────────────────────────────────────────
@st.cache_data
def load_markov_assets() -> dict:
    recorridos = [
        ["S0","S28","S29"],
        ["S0","S28","S30"],
        ["S0","S28","S31"],
        ["S0","S28","S33","S34","S35"],
        ["S0","S28","S33","S34","S36"],
        ["S0","S28","S30","S33","S34","S35"],
        ["S0","S28","S32","S0"],
        ["S0","S28","S29","S30","S28","S31"],
        ["S0","S28","S31","S32","S0"],
        ["S0","S28","S0"],
        ["S0","S28","S30","S28","S0"],
        ["S0","S28","S33","S34","S36","S33","S34","S35"],
        ["S0","S1","S2","S3","S0"],
        ["S0","S1","S2","S3","S1","S2","S3"],
        ["S0","S1","S0"],
        ["S0","S1","S2","S3","S28","S33","S34","S35"],
        ["S0","S1","S2","S3","S1","S2","S4","S9"],
        ["S0","S1","S2","S4","S9"],
        ["S4","S9","S10","S11"],
        ["S4","S9","S10","S12","S10","S11"],
        ["S4","S9","S10","S12","S9"],
        ["S4","S9","S13","S14"],
        ["S4","S9","S13","S9"],
        ["S4","S9","S4","S7","S0"],
        ["S4","S28","S33","S34","S35"],
        ["S4","S9","S10","S11","S7","S0"],
        ["S0","S1","S2","S5","S15"],
        ["S5","S15","S16","S17"],
        ["S5","S15","S16","S23","S0"],
        ["S5","S15","S16","S23","S16","S17"],
        ["S5","S15","S18","S17"],
        ["S5","S15","S19"],
        ["S5","S15","S24","S15"],
        ["S5","S25","S26","S27"],
        ["S5","S25","S26","S27","S7","S0"],
        ["S5","S28","S32","S0"],
        ["S5","S15","S16","S17","S7","S0"],
        ["S5","S28","S33","S34","S35","S29"],
        ["S5","S28","S33","S34","S36","S29"],
        ["S0","S1","S2","S6","S15"],
        ["S6","S15","S22","S21"],
        ["S6","S15","S20","S21"],
        ["S6","S15","S16","S17"],
        ["S6","S15","S18","S23","S18","S17"],
        ["S6","S15","S18","S23","S15"],
        ["S6","S15","S18","S15","S0"],
        ["S6","S28","S32","S0"],
        ["S6","S28","S33","S34","S35","S29"],
        ["S6","S15","S22","S21","S7","S0"],
        ["S0","S1","S2","S6","S15","S18","S17","S7","S0"],
        ["S0","S28","S30","S31","S33","S34","S35","S0"],
        ["S0","S1","S2","S3","S28","S29","S0"],
        ["S5","S15","S18","S15","S16","S17"],
        ["S6","S15","S20","S21","S28","S31","S7","S0"],
        ["S0","S28","S29","S32","S33","S34","S35","S0"],
        ["S4","S9","S10","S12","S10","S11","S9","S10","S11"],
        ["S5","S25","S26","S27","S15","S18","S17"],
        ["S6","S15","S16","S17","S28","S30","S7","S0"],
        ["S0","S28","S33","S34","S36","S0"],
        ["S5","S15","S24","S15","S18","S17","S7","S0"],
        ["S6","S15","S22","S23","S22","S21"],
    ]

    estados = [
        "S0","S1","S2","S3","S4","S5","S6","S7","S8",
        "S9","S10","S11","S12","S13","S14","S15","S16",
        "S17","S18","S19","S20","S21","S22","S23","S24",
        "S25","S26","S27","S28","S29","S30","S31","S32",
        "S33","S34","S35","S36",
    ]

    estados_finales = [
        "S3","S7","S8","S11","S12","S14","S17","S19",
        "S21","S23","S27","S29","S30","S32","S35","S36",
    ]

    nombres_estados = {
        "S0":  "Sesion no iniciada",
        "S1":  "Formulario de login visible",
        "S2":  "Credenciales en ingreso",
        "S3":  "Autenticacion fallida",
        "S4":  "Sesion activa - Superadmin",
        "S5":  "Sesion activa - Admin",
        "S6":  "Sesion activa - Editor",
        "S7":  "Sesion cerrada manualmente",
        "S8":  "Sesion cerrada por inactividad",
        "S9":  "Panel de usuarios abierto",
        "S10": "Formulario de usuario en diligenciamiento",
        "S11": "Usuario registrado exitosamente",
        "S12": "Error al registrar usuario",
        "S13": "Formulario de edicion de usuario activo",
        "S14": "Usuario modificado exitosamente",
        "S15": "Panel de contenido por pais abierto",
        "S16": "Formulario de noticia en diligenciamiento",
        "S17": "Noticia visible publicamente",
        "S18": "Formulario de edicion de noticia activo",
        "S19": "Noticia eliminada",
        "S20": "Formulario de testimonio en diligenciamiento",
        "S21": "Testimonio visible publicamente",
        "S22": "Formulario de edicion de testimonio activo",
        "S23": "Error al gestionar contenido",
        "S24": "Detalle de noticia visible",
        "S25": "Panel de solicitudes abierto",
        "S26": "Detalle de solicitud visible",
        "S27": "Estado de solicitud actualizado",
        "S28": "Pagina de inicio cargada",
        "S29": "Contenido general en navegacion",
        "S30": "Seccion de noticias visible",
        "S31": "Seccion de testimonios visible",
        "S32": "Acceso denegado por permisos",
        "S33": "Chatbot iniciado",
        "S34": "Consulta en procesamiento",
        "S35": "Respuesta del chatbot exitosa",
        "S36": "Respuesta del chatbot no disponible",
    }

    weighted_success_states = {
        "Estado de solicitud actualizado":  0.10,
        "Contenido general en navegacion":  0.10,
        "Seccion de noticias visible":      0.10,
        "Respuesta del chatbot exitosa":    0.15,
        "Noticia visible publicamente":     0.15,
        "Testimonio visible publicamente":  0.15,
        "Usuario registrado exitosamente":  0.10,
        "Usuario modificado exitosamente":  0.05,
        "Noticia eliminada":                0.10,
    }
    weighted_error_states = {
        "Autenticacion fallida":                    0.40,
        "Acceso denegado por permisos":             0.20,
        "Error al registrar usuario":               0.15,
        "Error al gestionar contenido":             0.15,
        "Respuesta del chatbot no disponible":      0.10,
    }
    weighted_abandonment_states = {
        "Sesion cerrada manualmente":       0.60,
        "Sesion cerrada por inactividad":   0.40,
    }

    critical_states    = {"S3","S12","S23","S32","S36","S8"}
    success_states     = set(weighted_success_states.keys())
    error_states       = set(weighted_error_states.keys())
    abandonment_states = set(weighted_abandonment_states.keys())

    matriz_conteos = pd.DataFrame(0, index=estados, columns=estados)
    for recorrido in recorridos:
        for i in range(len(recorrido) - 1):
            matriz_conteos.loc[recorrido[i], recorrido[i + 1]] += 1

    matriz_probabilidades = matriz_conteos.div(
        matriz_conteos.sum(axis=1), axis=0
    ).fillna(0)

    return {
        "recorridos":                recorridos,
        "estados":                   estados,
        "estados_finales":           estados_finales,
        "nombres_estados":           nombres_estados,
        "weighted_success_states":   weighted_success_states,
        "weighted_error_states":     weighted_error_states,
        "weighted_abandonment_states": weighted_abandonment_states,
        "critical_states":           critical_states,
        "success_states":            success_states,
        "error_states":              error_states,
        "abandonment_states":        abandonment_states,
        "matriz_conteos":            matriz_conteos,
        "matriz_probabilidades":     matriz_probabilidades,
    }


# ── Helpers de simulacion ─────────────────────────────────────────────────────
def classify_result(result_name: str, assets: dict) -> str:
    if result_name in assets["success_states"]:    return "Exito"
    if result_name in assets["error_states"]:      return "Error"
    if result_name in assets["abandonment_states"]:return "Abandono"
    return "Otro"


def simulate_user(
    matriz_probabilidades: pd.DataFrame,
    estados_finales: list,
    estado_inicial: str,
    max_pasos: int,
) -> list:
    estado_actual = estado_inicial
    recorrido = [estado_actual]
    for _ in range(max_pasos):
        if estado_actual in estados_finales:
            break
        probs = matriz_probabilidades.loc[estado_actual]
        if probs.sum() == 0:
            break
        estado_actual = np.random.choice(matriz_probabilidades.columns, p=probs.values)
        recorrido.append(estado_actual)
    return recorrido


def state_type(state_code: str, assets: dict) -> str:
    if state_code in assets["critical_states"]:  return "Critico"
    if state_code in assets["estados_finales"]:  return "Final"
    return "Intermedio"


def run_simulation(
    assets: dict, num_usuarios: int, max_pasos: int,
    estado_inicial: str, seed: int = 42,
):
    np.random.seed(seed)
    resultados, visitas = [], []
    for i in range(num_usuarios):
        recorrido    = simulate_user(assets["matriz_probabilidades"], assets["estados_finales"], estado_inicial, max_pasos)
        estado_final = recorrido[-1]
        result_name  = assets["nombres_estados"].get(estado_final, estado_final)
        resultados.append({
            "usuario":             i + 1,
            "recorrido_lista":     recorrido,
            "recorrido":           " -> ".join(recorrido),
            "estado_final":        estado_final,
            "estado_final_nombre": result_name,
            "num_pasos":           len(recorrido),
            "truncado":            estado_final not in assets["estados_finales"],
            "resultado":           result_name,
            "categoria_final":     classify_result(result_name, assets),
        })
        for orden, estado in enumerate(recorrido, start=1):
            visitas.append({
                "usuario":       i + 1,
                "orden":         orden,
                "estado":        estado,
                "estado_nombre": assets["nombres_estados"][estado],
                "estado_tipo":   state_type(estado, assets),
            })
    return pd.DataFrame(resultados), pd.DataFrame(visitas)


# ── KPIs ──────────────────────────────────────────────────────────────────────
def calculate_weighted_percentages(df_resultados: pd.DataFrame, assets: dict) -> dict:
    def score(states_dict):
        return sum(
            df_resultados[df_resultados["resultado"] == name].shape[0] * w
            for name, w in states_dict.items()
        )
    ws = score(assets["weighted_success_states"])
    we = score(assets["weighted_error_states"])
    wa = score(assets["weighted_abandonment_states"])
    total = ws + we + wa
    if total == 0:
        return {"Exito": 0.0, "Error": 0.0, "Abandono": 0.0}
    return {"Exito": ws/total*100, "Error": we/total*100, "Abandono": wa/total*100}


def compute_summary(df_resultados: pd.DataFrame, df_visitas: pd.DataFrame, assets: dict) -> dict:
    result_counts = df_resultados["resultado"].value_counts()
    top_result    = result_counts.index[0] if not result_counts.empty else "Sin datos"
    weighted      = calculate_weighted_percentages(df_resultados, assets)

    critical_visits = (
        df_visitas[df_visitas["estado"].isin(assets["critical_states"])]["estado_nombre"]
        .value_counts()
    )
    critical_state = critical_visits.index[0] if not critical_visits.empty else "Sin incidencias"

    success_rate     = (df_resultados["categoria_final"] == "Exito").mean()    * 100
    error_rate       = (df_resultados["categoria_final"] == "Error").mean()    * 100
    abandonment_rate = (df_resultados["categoria_final"] == "Abandono").mean() * 100

    return {
        "top_result":       top_result,
        "critical_state":   critical_state,
        "success_rate":     success_rate,
        "error_rate":       error_rate,
        "abandonment_rate": abandonment_rate,
        "avg_steps":        df_resultados["num_pasos"].mean(),
        "weighted":         weighted,
        "top_states":       df_visitas["estado"].value_counts().head(8),
    }


def generate_recommendations(summary: dict, df_resultados: pd.DataFrame, df_visitas: pd.DataFrame) -> list:
    recs = []
    sr, er, ar = summary["success_rate"], summary["error_rate"], summary["abandonment_rate"]
    if sr >= 50:
        recs.append({"type":"success","title":"Desempeno solido",
            "text": "Tasa de exito de " + str(int(sr)) + "%. Considera replicar estos patrones en otras areas."})
    if er >= 25:
        recs.append({"type":"error","title":"Revisar puntos de error",
            "text": "Errores en " + str(int(er)) + "% de casos. Enfocate en validaciones y manejo de excepciones."})
    if ar >= 20:
        recs.append({"type":"warning","title":"Reducir abandonos",
            "text": "Abandono de " + str(int(ar)) + "%. Simplifica el flujo y mejora el feedback visual."})
    error_top = df_resultados[df_resultados["categoria_final"]=="Error"]["resultado"].value_counts().head(1)
    if not error_top.empty:
        recs.append({"type":"error","title":"Cuello de botella: " + error_top.index[0],
            "text": "Este estado aparece " + str(error_top.values[0]) + " veces en errores. Prioriza su revision."})
    most_visited = df_visitas["estado_nombre"].value_counts().head(1)
    if not most_visited.empty:
        recs.append({"type":"success","title":"Zona de alto trafico detectada",
            "text": most_visited.index[0] + " es un buen candidato para mejorar la experiencia."})
    return recs[:4]


# ── Hero banner ───────────────────────────────────────────────────────────────
def hero_section(summary: dict, assets: dict, usuarios: int) -> None:
    num_estados  = len(assets["estados"])
    success_rate = summary["success_rate"]
    error_rate   = summary["error_rate"]
    avg_steps    = summary["avg_steps"]
    logo_html    = get_logo_html(max_width=80)

    kpi_html = f"""
    <div class="hero-banner">
        <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;position:relative;z-index:2;">
            {logo_html}
            <div>
                <div class="hero-title" style="margin-bottom:0;">Latinoamerica Comparte</div>
                <div style="font-size:0.65rem;color:#9ca3af;letter-spacing:0.05em;">SIMULATOR</div>
            </div>
        </div>
        <div class="hero-subtitle">
            Simulacion predictiva de comportamiento de usuarios basada en Cadenas de Markov
        </div>
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-label">Estados</div>
                <div class="kpi-value">{num_estados}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Usuarios</div>
                <div class="kpi-value">{usuarios}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Exito</div>
                <div class="kpi-value" style="color:#10b981;">{success_rate:.0f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Error</div>
                <div class="kpi-value" style="color:#ef4444;">{error_rate:.0f}%</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-label">Promedio Pasos</div>
                <div class="kpi-value" style="color:#f59e0b;">{avg_steps:.1f}</div>
            </div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
def render_sidebar(assets: dict) -> tuple:
    logo_html = get_logo_html(max_width=100)
    with st.sidebar:
        st.markdown(
            f"""
            <div class="logo-banner">
                {logo_html}
                <div class="logo-subtitle">Latinoamerica Comparte</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Simulador basado en Cadenas de Markov")
        st.markdown("---")

        num_usuarios   = st.slider("Usuarios a simular", min_value=5,  max_value=100, value=25, step=5)
        max_pasos      = st.slider("Maximo de pasos",    min_value=5,  max_value=100, value=20, step=5)
        estado_inicial = st.selectbox(
            "Estado inicial",
            assets["estados"],
            index=assets["estados"].index("S0"),
            format_func=lambda s: f"{s} - {assets['nombres_estados'][s]}",
        )

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            iniciar  = st.button("Simular", use_container_width=True, type="primary")
        with c2:
            resetear = st.button("Limpiar", use_container_width=True)

        if resetear:
            for key in ("df_resultados","df_visitas","sim_params","sim_before"):
                st.session_state.pop(key, None)
            st.rerun()

    return num_usuarios, max_pasos, estado_inicial, iniciar


# ── Simulacion con progreso ───────────────────────────────────────────────────
def perform_simulation(assets: dict, num_usuarios: int, max_pasos: int, estado_inicial: str) -> None:
    progress = st.sidebar.progress(0, text="Preparando...")
    live_box = st.sidebar.empty()
    results, visitas = [], []
    chunk = max(5, num_usuarios // 20)
    np.random.seed(42)

    for i in range(num_usuarios):
        recorrido    = simulate_user(assets["matriz_probabilidades"], assets["estados_finales"], estado_inicial, max_pasos)
        estado_final = recorrido[-1]
        result_name  = assets["nombres_estados"].get(estado_final, estado_final)
        results.append({
            "usuario":             i + 1,
            "recorrido_lista":     recorrido,
            "recorrido":           " -> ".join(recorrido),
            "estado_final":        estado_final,
            "estado_final_nombre": result_name,
            "num_pasos":           len(recorrido),
            "truncado":            estado_final not in assets["estados_finales"],
            "resultado":           result_name,
            "categoria_final":     classify_result(result_name, assets),
        })
        for orden, estado in enumerate(recorrido, start=1):
            visitas.append({
                "usuario":       i + 1,
                "orden":         orden,
                "estado":        estado,
                "estado_nombre": assets["nombres_estados"][estado],
                "estado_tipo":   state_type(estado, assets),
            })

        if (i + 1) % chunk == 0 or i + 1 == num_usuarios:
            parcial    = pd.DataFrame(results)
            categorias = parcial["categoria_final"].value_counts(normalize=True).mul(100).round(1)
            ex = categorias.get("Exito",   0)
            er = categorias.get("Error",   0)
            ab = categorias.get("Abandono",0)
            live_box.markdown(
                f"""
                <div class="panel-card">
                    <div class="section-title" style="font-size:1rem;">Progreso</div>
                    <div class="section-copy">
                        <strong>{i+1}/{num_usuarios}</strong> usuarios<br>
                        OK {ex:.1f}% | ERR {er:.1f}% | ABA {ab:.1f}%
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            progress.progress(int((i+1)/num_usuarios*100), text=f"Usuario {i+1} de {num_usuarios}")
            time.sleep(0.02)

    progress.empty()
    live_box.empty()
    st.session_state["df_resultados"] = pd.DataFrame(results)
    st.session_state["df_visitas"]    = pd.DataFrame(visitas)
    st.session_state["sim_params"]    = {
        "usuarios": num_usuarios, "max_pasos": max_pasos, "estado_inicial": estado_inicial,
    }


# ── Estado inicial automatico ─────────────────────────────────────────────────
def initial_state(assets: dict) -> None:
    if "df_resultados" not in st.session_state:
        df_r, df_v = run_simulation(assets, 1200, 12, "S0")
        st.session_state["df_resultados"] = df_r
        st.session_state["df_visitas"]    = df_v
        st.session_state["sim_params"]    = {"usuarios":1200,"max_pasos":12,"estado_inicial":"S0"}


# ── Dashboard ─────────────────────────────────────────────────────────────────
def render_dashboard(
    assets: dict,
    df_resultados: pd.DataFrame,
    df_visitas: pd.DataFrame,
    sim_params: dict,
) -> None:
    summary = compute_summary(df_resultados, df_visitas, assets)
    hero_section(summary, assets, sim_params["usuarios"])

    tabs = st.tabs([
        "Resumen Ejecutivo", "Estados", "Matriz Conteo",
        "Matriz Probabilidades", "Recorridos", "Resultados",
        "Diagnostico", "Simulador de Mejoras", "Comparacion",
    ])

    # ── TAB 0 ─────────────────────────────────────────────────────────────────
    with tabs[0]:
        col1, col2 = st.columns([1.4, 0.6])
        with col1:
            st.markdown(
                """
                <div class="panel-card">
                    <div class="section-title">Acerca de esta Simulacion</div>
                    <div class="section-copy">
                        Modelado de transiciones entre estados usando Cadenas de Markov.
                        Cada recorrido representa una sesion de usuario en el sistema.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            cm1, cm2, cm3 = st.columns(3)
            cm1.metric("Exito",    f"{summary['success_rate']:.0f}%")
            cm2.metric("Error",    f"{summary['error_rate']:.0f}%")
            cm3.metric("Abandono", f"{summary['abandonment_rate']:.0f}%")

            weighted_df = pd.DataFrame({
                "Categoria": list(summary["weighted"].keys()),
                "Porcentaje": list(summary["weighted"].values()),
            })
            fig_w = px.bar(
                weighted_df, x="Categoria", y="Porcentaje", color="Categoria",
                color_discrete_map={"Exito":"#10b981","Error":"#ef4444","Abandono":"#f59e0b"},
                text_auto=".1f", title="Distribucion Ponderada de Resultados",
            )
            fig_w.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaed",size=11), showlegend=False,
                title_font_size=12, height=320,
            )
            st.plotly_chart(fig_w, use_container_width=True)

        with col2:
            top_r  = summary["top_result"]
            crit_s = summary["critical_state"]
            avg_s  = summary["avg_steps"]
            suc_w  = summary["weighted"]["Exito"]
            e_ini  = sim_params["estado_inicial"]
            u_n    = sim_params["usuarios"]
            st.markdown(
                f"""
                <div class="panel-card" style="margin-bottom:14px;">
                    <div class="section-title">Resultado Dominante</div>
                    <div class="kpi-value" style="font-size:1.4rem;color:#f59e0b;">{top_r}</div>
                </div>
                <div class="panel-card" style="margin-bottom:14px;">
                    <div class="section-title">Punto Critico</div>
                    <div class="kpi-value" style="font-size:1.2rem;color:#ef4444;">{crit_s}</div>
                </div>
                <div class="panel-card" style="margin-bottom:14px;">
                    <div class="section-title">Promedio Pasos</div>
                    <div class="kpi-value" style="font-size:1.4rem;color:#60a5fa;">{avg_s:.1f}</div>
                </div>
                <div class="panel-card success-card">
                    <div class="alert-title">Parametros de Simulacion</div>
                    <div class="alert-copy">
                        <strong>Estado Inicial:</strong> {e_ini}<br>
                        <strong>Usuarios:</strong> {u_n}<br>
                        Exito ponderado: <strong>{suc_w:.1f}%</strong>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── TAB 1 ─────────────────────────────────────────────────────────────────
    with tabs[1]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Catalogo de Estados del Sistema</div>
                <div class="section-copy">Inventario completo de todos los estados del modelo Markoviano.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        rows = [
            {
                "Codigo": s,
                "Descripcion": assets["nombres_estados"][s],
                "Tipo": state_type(s, assets),
                "Final":   "Si" if s in assets["estados_finales"] else "No",
                "Critico": "Si" if s in assets["critical_states"] else "No",
            }
            for s in assets["estados"]
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # ── TAB 2 ─────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Matriz de Frecuencias de Transicion</div>
                <div class="section-copy">Conteo absoluto de transiciones observadas entre estados.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        fig_c = go.Figure(data=go.Heatmap(
            z=assets["matriz_conteos"].values,
            x=assets["matriz_conteos"].columns,
            y=assets["matriz_conteos"].index,
            colorscale=[[0,"#0a0e27"],[0.2,"#3d2a5a"],[0.45,"#6c3fa6"],[0.7,"#8b5cf6"],[1,"#a78bfa"]],
            text=assets["matriz_conteos"].astype(int).values,
            texttemplate="%{text}",
            hovertemplate="Desde: %{y}<br>Hacia: %{x}<br>Frecuencia: %{z}<extra></extra>",
        ))
        fig_c.update_layout(
            title="Matriz de Conteo de Transiciones",
            margin=dict(l=80,r=20,t=60,b=80),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaed",size=10), height=700,
        )
        st.plotly_chart(fig_c, use_container_width=True)
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Total Transiciones",  int(assets["matriz_conteos"].sum().sum()))
        cc2.metric("Transiciones Unicas", int((assets["matriz_conteos"] > 0).sum().sum()))
        cc3.metric("Maxima Frecuencia",   int(assets["matriz_conteos"].max().max()))

    # ── TAB 3 ─────────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Matriz de Probabilidades de Markov</div>
                <div class="section-copy">Probabilidades normalizadas de transicion (suma por fila = 100%).</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        fig_p = go.Figure(data=go.Heatmap(
            z=(assets["matriz_probabilidades"].values * 100).round(2),
            x=assets["matriz_probabilidades"].columns,
            y=assets["matriz_probabilidades"].index,
            colorscale=[[0,"#0f1435"],[0.2,"#1e3a5f"],[0.45,"#2d5a9f"],[0.7,"#3b7bd8"],[1,"#60a5fa"]],
            text=np.round(assets["matriz_probabilidades"].values * 100, 1),
            texttemplate="%{text:.1f}%",
            hovertemplate="Desde: %{y}<br>Hacia: %{x}<br>Prob: %{z:.1f}%<extra></extra>",
        ))
        fig_p.update_layout(
            title="Matriz de Probabilidades de Markov",
            margin=dict(l=80,r=20,t=60,b=80),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaed",size=10), height=700,
        )
        st.plotly_chart(fig_p, use_container_width=True)

    # ── TAB 4 ─────────────────────────────────────────────────────────────────
    with tabs[4]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Rutas de Usuarios Simulados</div>
                <div class="section-copy">Exploracion de secuencias generadas por la cadena markoviana.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        rf1, rf2, rf3, rf4 = st.columns(4)
        rf1.metric("Total",    len(df_resultados))
        rf2.metric("Exito",   (df_resultados["categoria_final"]=="Exito").sum())
        rf3.metric("Error",   (df_resultados["categoria_final"]=="Error").sum())
        rf4.metric("Abandono",(df_resultados["categoria_final"]=="Abandono").sum())
        st.markdown("")

        cf1, cf2 = st.columns(2)
        with cf1:
            cat_filtro = st.multiselect(
                "Filtrar por categoria",
                ["Exito","Error","Abandono"],
                default=["Exito","Error","Abandono"],
            )
        with cf2:
            res_filtro = st.multiselect(
                "Filtrar por estado final",
                df_resultados["resultado"].unique(),
                default=list(df_resultados["resultado"].unique()[:5]),
            )

        df_f = df_resultados[
            df_resultados["categoria_final"].isin(cat_filtro) &
            df_resultados["resultado"].isin(res_filtro)
        ]
        st.dataframe(
            df_f[["usuario","recorrido","estado_final","resultado","num_pasos","categoria_final"]].head(50),
            use_container_width=True, hide_index=True,
        )

        usuario_sel = st.selectbox("Ver detalle de usuario", df_resultados["usuario"].head(100))
        sel = df_resultados[df_resultados["usuario"]==usuario_sel].iloc[0]
        rd1, rd2 = st.columns([2,1])
        with rd1:
            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="section-title">Usuario #{int(sel["usuario"])}</div>
                    <div class="section-copy">
                        <strong>Recorrido:</strong> {sel["recorrido"]}<br>
                        <strong>Estado Final:</strong> {sel["estado_final_nombre"]}<br>
                        <strong>Pasos:</strong> {sel["num_pasos"]}<br>
                        <strong>Resultado:</strong> {sel["resultado"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rd2:
            st.metric("Categoria", sel["categoria_final"])

    # ── TAB 5 ─────────────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Distribucion de Resultados Finales</div>
                <div class="section-copy">Analisis estadistico de estados terminales alcanzados.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        rr1, rr2 = st.columns(2)
        with rr1:
            fd = df_resultados["resultado"].value_counts().reset_index()
            fd.columns = ["Resultado","Usuarios"]
            fig_r = px.bar(
                fd.head(12), x="Usuarios", y="Resultado", orientation="h",
                color="Usuarios",
                color_continuous_scale=["#3d2a5a","#6c3fa6","#8b5cf6","#a78bfa"],
                text_auto=True, title="Estados Finales Mas Frecuentes",
            )
            fig_r.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e8eaed",size=11), coloraxis_showscale=False,
                height=400, showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)
        with rr2:
            cd = df_resultados["categoria_final"].value_counts().reset_index()
            cd.columns = ["Categoria","Usuarios"]
            fig_d = px.pie(
                cd, names="Categoria", values="Usuarios", hole=0.5,
                color="Categoria",
                color_discrete_map={"Exito":"#10b981","Error":"#ef4444","Abandono":"#f59e0b","Otro":"#6b7280"},
                title="Distribucion General de Categorias",
            )
            fig_d.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#e8eaed",size=11), height=400,
            )
            st.plotly_chart(fig_d, use_container_width=True)

        top_df = summary["top_states"].reset_index()
        top_df.columns = ["Estado","Visitas"]
        top_df["Nombre"] = top_df["Estado"].map(assets["nombres_estados"])
        fig_v = px.bar(
            top_df, x="Visitas", y="Nombre", orientation="h",
            color="Visitas",
            color_continuous_scale=["#3d2a5a","#6c3fa6","#8b5cf6","#a78bfa"],
            text_auto=True, title="Estados Mas Visitados",
        )
        fig_v.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaed",size=10), coloraxis_showscale=False, height=350,
        )
        st.plotly_chart(fig_v, use_container_width=True)

    # ── TAB 6 ─────────────────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Recomendaciones Inteligentes</div>
                <div class="section-copy">
                    Analisis automatico de cuellos de botella y oportunidades de mejora.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        for rec in generate_recommendations(summary, df_resultados, df_visitas):
            css = {"success":"success-card","warning":"warning-card"}.get(rec["type"],"error-card")
            st.markdown(
                f"""
                <div class="panel-card {css}">
                    <div class="alert-title">{rec["title"]}</div>
                    <div class="alert-copy">{rec["text"]}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── TAB 7 ─────────────────────────────────────────────────────────────────
    with tabs[7]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Simulador de Mejoras</div>
                <div class="section-copy">
                    Ajusta probabilidades de transicion manualmente para ver el impacto.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")

        estado_origen = st.selectbox(
            "Estado de origen",
            assets["estados"],
            format_func=lambda x: f"{x} - {assets['nombres_estados'][x]}",
        )

        sm1, sm2 = st.columns(2)
        prob_ajustes = {}
        with sm1:
            st.markdown("**Ajustes de Probabilidad (primeros 10 destinos)**")
            for estado_dest in assets["estados"][:10]:
                prob_orig = float(assets["matriz_probabilidades"].loc[estado_origen, estado_dest])
                prob_ajustes[estado_dest] = st.slider(
                    f"{estado_dest} - {assets['nombres_estados'][estado_dest][:25]}",
                    min_value=0.0, max_value=1.0, value=prob_orig, step=0.05,
                )
        with sm2:
            st.markdown("**Impacto de Cambios**")
            cambios_rows = []
            for est, p_nueva in prob_ajustes.items():
                p_vieja = float(assets["matriz_probabilidades"].loc[estado_origen, est])
                delta   = p_nueva - p_vieja
                if abs(delta) > 0.001:
                    cambios_rows.append({
                        "Estado":  est,
                        "Antes":   f"{p_vieja:.1%}",
                        "Despues": f"{p_nueva:.1%}",
                        "Cambio":  f"{delta:+.1%}",
                    })
            if cambios_rows:
                st.dataframe(pd.DataFrame(cambios_rows), use_container_width=True, hide_index=True)
            else:
                st.info("Sin cambios detectados.")

        if st.button("Simular con Cambios", type="primary", use_container_width=True):
            st.info("Funcionalidad disponible en la proxima version.")

    # ── TAB 8 ─────────────────────────────────────────────────────────────────
    with tabs[8]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Comparacion: Antes vs Despues</div>
                <div class="section-copy">Visualiza el impacto proyectado de mejoras propuestas.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")

        sr = summary["success_rate"]
        er = summary["error_rate"]
        ar = summary["abandonment_rate"]

        cp1, cp2 = st.columns(2)
        with cp1:
            fig_g = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=min(100, sr * 1.15),
                delta={"reference": sr, "position":"top"},
                title={"text":"Exito Proyectado"},
                domain={"x":[0,1],"y":[0,1]},
                gauge={
                    "axis":{"range":[0,100]},
                    "bar":{"color":"#4cb850"},
                    "steps":[
                        {"range":[0,25],"color":"#e8678a"},
                        {"range":[25,50],"color":"#ff9a56"},
                        {"range":[50,100],"color":"#4cb850"},
                    ],
                },
            ))
            fig_g.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f5f5f5"), height=300,
            )
            st.plotly_chart(fig_g, use_container_width=True)

        with cp2:
            av = summary["avg_steps"]
            comp_data = {
                "Metrica":  ["Exito","Error","Abandono","Prom. Pasos"],
                "Antes":    [f"{sr:.1f}", f"{er:.1f}", f"{ar:.1f}", f"{av:.1f}"],
                "Despues":  [
                    f"{min(100,sr*1.15):.1f}",
                    f"{max(0,er*0.85):.1f}",
                    f"{max(0,ar*0.90):.1f}",
                    f"{max(1,av*0.95):.1f}",
                ],
            }
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

        fig_cb = go.Figure()
        fig_cb.add_trace(go.Bar(
            x=["Exito","Error","Abandono"], y=[sr,er,ar],
            name="Actual", marker_color="#b0a8bf",
            text=[f"{sr:.0f}%",f"{er:.0f}%",f"{ar:.0f}%"],
            textposition="outside",
        ))
        fig_cb.add_trace(go.Bar(
            x=["Exito","Error","Abandono"],
            y=[min(100,sr*1.15), max(0,er*0.85), max(0,ar*0.90)],
            name="Proyectado", marker_color="#ff9a56",
            text=[f"{min(100,sr*1.15):.0f}%",f"{max(0,er*0.85):.0f}%",f"{max(0,ar*0.90):.0f}%"],
            textposition="outside",
        ))
        fig_cb.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#f5f5f5"), barmode="group", height=400,
            title="Comparativa de Metricas: Antes vs Despues",
        )
        st.plotly_chart(fig_cb, use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    inject_styles()
    assets = load_markov_assets()
    initial_state(assets)

    num_usuarios, max_pasos, estado_inicial, iniciar = render_sidebar(assets)

    if iniciar:
        with st.spinner("Ejecutando simulacion..."):
            perform_simulation(assets, num_usuarios, max_pasos, estado_inicial)
        st.success(f"Simulacion completada: {num_usuarios} usuarios procesados")
        st.rerun()

    df_resultados = st.session_state["df_resultados"]
    df_visitas    = st.session_state["df_visitas"]
    sim_params    = st.session_state["sim_params"]
    render_dashboard(assets, df_resultados, df_visitas, sim_params)


if __name__ == "__main__":
    main()