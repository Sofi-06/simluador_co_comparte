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
from PIL import Image

# ── Configuración general ─────────────────────────────────────────────────────
# ── Configuración general ─────────────────────────────────────────────────────
LOGO_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..", "assets", "logo.png"
)

favicon = Image.open(LOGO_PATH) if os.path.exists(LOGO_PATH) else "📊"

st.set_page_config(
    page_title="Latinoamérica Comparte — Simulador",
    page_icon=favicon,
    layout="wide",
    initial_sidebar_state="expanded",
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


def get_analytics_logo_html(max_width: int = 70) -> str:
    """Devuelve analytics.png en base64 solo para el banner."""
    analytics_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "assets", "analiticas.png"
    )
    if os.path.exists(analytics_path):
        ext = os.path.splitext(analytics_path)[1].lower().lstrip(".")
        mime = "svg+xml" if ext == "svg" else ext
        with open(analytics_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return (
            f'<img src="data:image/{mime};base64,{b64}" '
            f'style="max-width:{max_width}px;display:block;" />'
        )
    return ""


# ── Estilos ───────────────────────────────────────────────────────────────────
def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-dark: #121212;
            --bg-card: rgba(30, 30, 30, 0.6);
            --bg-hover: rgba(45, 45, 45, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #a1a1aa;
            --accent: #4cc9f0; /* Cyan */
            --accent-light: #f72585; /* Pink/Red */
            --accent-glow: rgba(76, 201, 240, 0.2);
            --accent-dark: #3a0ca3; /* Deep Blue */
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --border: rgba(255, 255, 255, 0.08);
            --shadow-sm: 0 4px 12px rgba(0, 0, 0, 0.4);
            --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.5);
        }
        .stApp {
            background: radial-gradient(circle at 80% 0%, rgba(247, 37, 133, 0.05) 0%, transparent 40%), 
                        radial-gradient(circle at 20% 100%, rgba(76, 201, 240, 0.05) 0%, transparent 40%),
                        #121212;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
        }
        section[data-testid="stSidebar"] {
            background: #18181b;
            border-right: 1px solid var(--border);
        }
        section[data-testid="stSidebar"] * {
            color: #d4d4d8 !important;
        }
        .logo-banner {
            text-align: center;
            padding: 16px 0;
            margin-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }
        .hero-banner {
            background: var(--bg-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 12px 16px;
            margin-bottom: 16px;
            box-shadow: var(--shadow-md);
            position: relative;
            overflow: hidden;
        }
        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            color: #ffffff;
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
            font-weight: 400;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 16px;
            margin: 24px 0 0 0;
            position: relative;
            z-index: 1;
        }
        .kpi-card {
            background: rgba(40, 40, 40, 0.4);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 10px 12px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
        }
        .kpi-card:hover {
            background: rgba(60, 60, 60, 0.5);
            border-color: rgba(255, 255, 255, 0.15);
            transform: translateY(-4px);
            box-shadow: 0 10px 24px rgba(0,0,0,0.4);
        }
        .kpi-label {
            color: var(--text-secondary);
            font-size: 0.65rem;
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-bottom: 4px;
            font-weight: 600;
        }
        .kpi-value {
            color: #ffffff;
            font-size: 1.3rem;
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
            background: var(--bg-card);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 24px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
            position: relative;
        }
        .panel-card:hover {
            box-shadow: var(--shadow-md);
            border-color: rgba(255, 255, 255, 0.12);
        }
        .section-copy {
            color: var(--text-secondary);
            line-height: 1.8;
            font-size: 0.95rem;
            margin: 0;
        }
        .success-card { border-left: 4px solid var(--success); }
        .warning-card { border-left: 4px solid var(--warning); }
        .error-card { border-left: 4px solid var(--danger); }
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
            background: transparent;
            border: none;
            border-bottom: 2px solid transparent;
            border-radius: 0;
            padding: 12px 20px;
            color: var(--text-secondary);
            font-size: 0.95rem;
            transition: all 0.2s ease;
            font-weight: 600;
        }
        .stTabs [data-baseweb="tab"]:hover {
            color: var(--text-primary);
            background: transparent;
        }
        .stTabs [aria-selected="true"] {
            background: transparent;
            border-bottom: 2px solid var(--accent);
            color: var(--text-primary);
        }
        .stButton button {
            background: linear-gradient(135deg, #18181b 0%, #27272a 100%);
            color: #ffffff;
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            width: 100%;
            padding: 0.8rem 1.2rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
        }
        .stButton button:hover {
            transform: translateY(-2px);
            border-color: var(--accent);
            box-shadow: 0 8px 20px rgba(76, 201, 240, 0.2);
            background: linear-gradient(135deg, #27272a 0%, #3f3f46 100%);
        }
        div[data-testid="stMetric"] {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 16px;
            box-shadow: var(--shadow-sm);
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #ffffff;
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
        "S0":  "Sesión no iniciada",
        "S1":  "Formulario de login visible",
        "S2":  "Credenciales en ingreso",
        "S3":  "Autenticación fallida",
        "S4":  "Sesión activa - Superadmin",
        "S5":  "Sesión activa - Admin",
        "S6":  "Sesión activa - Editor",
        "S7":  "Sesión cerrada manualmente",
        "S8":  "Sesión cerrada por inactividad",
        "S9":  "Panel de usuarios abierto",
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
        "Estado de solicitud actualizado":  0.10,
        "Contenido general en navegación":  0.10,
        "Sección de noticias visible":      0.10,
        "Respuesta del chatbot exitosa":    0.15,
        "Noticia visible públicamente":     0.15,
        "Testimonio visible públicamente":  0.15,
        "Usuario registrado exitosamente":  0.10,
        "Usuario modificado exitosamente":  0.05,
        "Noticia eliminada":                0.10,
    }
    weighted_error_states = {
        "Autenticación fallida":                    0.40,
        "Acceso denegado por permisos":             0.20,
        "Error al registrar usuario":               0.15,
        "Error al gestionar contenido":             0.15,
        "Respuesta del chatbot no disponible":      0.10,
    }
    weighted_abandonment_states = {
        "Sesión cerrada manualmente":       0.60,
        "Sesión cerrada por inactividad":   0.40,
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

    # Extraer estados iniciales válidos (primeros estados de cada recorrido)
    estados_iniciales_validos = sorted(set(rec[0] for rec in recorridos if rec))

    return {
        "recorridos":                recorridos,
        "estados":                   estados,
        "estados_iniciales_validos": estados_iniciales_validos,
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


# ── Helpers de simulación ─────────────────────────────────────────────────────
def classify_result(result_name: str, assets: dict) -> str:
    if result_name in assets["success_states"]:    return "Éxito"
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
    if state_code in assets["critical_states"]:  return "Crítico"
    if state_code in assets["estados_finales"]:  return "Final"
    return "Intermedio"


def build_transition_figure_from_matrix(matriz: pd.DataFrame, assets: dict, title: str = "Grafo de Transiciones") -> go.Figure:
    G = nx.DiGraph()
    for src in matriz.index:
        for dst in matriz.columns:
            w = float(matriz.loc[src, dst])
            if w > 0:
                G.add_edge(src, dst, weight=w)

    pos = nx.spring_layout(G, seed=42)
    edge_x, edge_y = [], []
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="#3a0ca3"),
        hoverinfo='none',
        mode='lines'
    )

    node_x, node_y, node_text, node_color = [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        name = assets['nombres_estados'].get(n, n)
        node_text.append(f"{n} - {name}")
        if n in assets['critical_states']:
            node_color.append('#f72585')
        elif n in assets['estados_finales']:
            node_color.append('#10b981')
        else:
            node_color.append('#4cc9f0')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        textposition='top center',
        text=node_text,
        marker=dict(color=node_color, size=22, line_width=1, line=dict(color='rgba(255,255,255,0.2)', width=1))
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False, title=title, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, font=dict(color="#d4d4d8"))
    return fig


def build_transition_figure_from_visits(df_visitas: pd.DataFrame, assets: dict, title: str = "Grafo de Recorridos Observados") -> go.Figure:
    # Build counts of transitions from visits
    df_visits_sorted = df_visitas.sort_values(['usuario','orden'])
    edges = Counter()
    for uid, group in df_visits_sorted.groupby('usuario'):
        seq = list(group['estado'])
        for i in range(len(seq)-1):
            edges[(seq[i], seq[i+1])] += 1

    G = nx.DiGraph()
    for (u,v), w in edges.items():
        G.add_edge(u, v, weight=w)

    if len(G.nodes) == 0:
        return go.Figure()

    pos = nx.spring_layout(G, seed=42)
    edge_x, edge_y = [], []
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="#f72585"),
        hoverinfo='text',
        mode='lines'
    )

    node_x, node_y, node_text, node_color = [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        name = assets['nombres_estados'].get(n, n)
        node_text.append(f"{n} - {name}")
        if n in assets['critical_states']:
            node_color.append('#f72585')
        elif n in assets['estados_finales']:
            node_color.append('#10b981')
        else:
            node_color.append('#4cc9f0')

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        hoverinfo='text',
        textposition='top center',
        text=node_text,
        marker=dict(color=node_color, size=20, line_width=1, line=dict(color='rgba(255,255,255,0.2)', width=1))
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False, title=title, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500, font=dict(color="#d4d4d8"))
    return fig


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
        return {"Éxito": 0.0, "Error": 0.0, "Abandono": 0.0}
    return {"Éxito": ws/total*100, "Error": we/total*100, "Abandono": wa/total*100}


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


def find_state_code_by_name(name: str, assets: dict) -> str | None:
    for code, nm in assets.get('nombres_estados', {}).items():
        if nm == name:
            return code
    return None


def generate_recommendations(summary: dict, df_resultados: pd.DataFrame, df_visitas: pd.DataFrame) -> list:
    recs = []
    sr, er, ar = summary["success_rate"], summary["error_rate"], summary["abandonment_rate"]
    if sr >= 50:
        recs.append({"type":"success","title":"Desempeño sólido",
            "text": "Tasa de éxito de " + str(int(sr)) + "%. Considera replicar estos patrones en otras áreas."})
    if er >= 25:
        recs.append({"type":"error","title":"Revisar puntos de error",
            "text": "Errores en " + str(int(er)) + "% de casos. Enfócate en validaciones y manejo de excepciones."})
    if ar >= 20:
        recs.append({"type":"warning","title":"Reducir abandonos",
            "text": "Abandono de " + str(int(ar)) + "%. Simplifica el flujo y mejora el feedback visual."})
    error_top = df_resultados[df_resultados["categoria_final"]=="Error"]["resultado"].value_counts().head(1)
    if not error_top.empty:
        recs.append({"type":"error","title":"Cuello de botella: " + error_top.index[0],
            "text": "Este estado aparece " + str(error_top.values[0]) + " veces en errores. Prioriza su revisión."})
    most_visited = df_visitas["estado_nombre"].value_counts().head(1)
    if not most_visited.empty:
        recs.append({"type":"success","title":"Zona de alto tráfico detectada",
            "text": most_visited.index[0] + " es un buen candidato para mejorar la experiencia."})
    return recs[:4]


def generate_critical_state_recommendation(
    crit_code: str,
    crit_name: str,
    df_resultados: pd.DataFrame,
    df_visitas: pd.DataFrame,
    assets: dict,
) -> dict:
    visits_crit = df_visitas[df_visitas["estado"] == crit_code]
    affected_users = visits_crit["usuario"].nunique()
    total_users = max(1, df_resultados["usuario"].nunique())
    affected_pct = affected_users / total_users * 100

    if crit_name in {"Autenticación fallida", "Acceso denegado por permisos"}:
        title = "Reforzar autenticación y permisos"
        text = (
            f"El estado {crit_code} - {crit_name} afecta a {affected_users} usuarios "
            f"({affected_pct:.1f}% del total). Conviene revisar validaciones de acceso, "
            "mensajes de error y rutas de recuperación para evitar abandonos tempranos."
        )
    elif crit_name in {"Error al registrar usuario", "Error al gestionar contenido", "Respuesta del chatbot no disponible"}:
        title = "Reducir fricción en el flujo crítico"
        text = (
            f"El estado {crit_code} - {crit_name} aparece en {visits_crit.shape[0]} recorridos. "
            "Prioriza validaciones de formulario, manejo de excepciones y retroalimentación "
            "clara para que el usuario pueda continuar sin bloquearse."
        )
    elif crit_name in {"Sesión cerrada manualmente", "Sesión cerrada por inactividad"}:
        title = "Disminuir abandono de sesión"
        text = (
            f"El estado {crit_code} - {crit_name} indica salida del flujo en {affected_pct:.1f}% de los usuarios. "
            "Reduce pasos innecesarios, mejora el guardado automático y refuerza los avisos de actividad."
        )
    else:
        title = "Atender el punto crítico detectado"
        text = (
            f"El estado {crit_code} - {crit_name} concentra {affected_users} usuarios afectados. "
            "Revisa transiciones previas, mensajes de guía y controles de salida para reducir su impacto."
        )

    return {
        "type": "warning",
        "title": title,
        "text": text,
    }


# ── Hero banner ───────────────────────────────────────────────────────────────
def hero_section(summary: dict, assets: dict, usuarios: int) -> None:
    num_estados  = len(assets["estados"])
    success_rate = summary["success_rate"]
    error_rate   = summary["error_rate"]
    avg_steps    = summary["avg_steps"]
    analytics_logo = get_analytics_logo_html(max_width=70)

    kpi_html = f"""
    <div class="hero-banner">
        <div style="display:flex;align-items:center;gap:16px;position:relative;z-index:2;justify-content:space-between;">
            <div style="flex:1;">
                <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    <div class="kpi-card" style="flex:1;min-width:100px;">
                        <div class="kpi-label">Estados</div>
                        <div class="kpi-value">{num_estados}</div>
                    </div>
                    <div class="kpi-card" style="flex:1;min-width:100px;">
                        <div class="kpi-label">Usuarios</div>
                        <div class="kpi-value">{usuarios}</div>
                    </div>
                    <div class="kpi-card" style="flex:1;min-width:100px;">
                        <div class="kpi-label" style="color:#10b981;">Éxito</div>
                        <div class="kpi-value" style="color:#10b981;">{success_rate:.0f}%</div>
                    </div>
                    <div class="kpi-card" style="flex:1;min-width:100px;">
                        <div class="kpi-label" style="color:#ef4444;">Error</div>
                        <div class="kpi-value" style="color:#ef4444;">{error_rate:.0f}%</div>
                    </div>
                    <div class="kpi-card" style="flex:1;min-width:100px;">
                        <div class="kpi-label" style="color:#4cc9f0;">Prom. Pasos</div>
                        <div class="kpi-value" style="color:#4cc9f0;">{avg_steps:.1f}</div>
                    </div>
                </div>
            </div>
            <div style="flex:0 0 auto;text-align:center;">
                {analytics_logo}
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
                <div class="logo-subtitle">Latinoamérica Comparte</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.caption("Simulador basado en Cadenas de Márkov")
        st.markdown("---")

        num_usuarios   = st.slider("Usuarios a simular", min_value=5,  max_value=5000, value=100, step=5)
        max_pasos      = st.slider("Máximo de pasos",    min_value=5,  max_value=1000, value=20, step=5)
        estado_inicial = st.selectbox(
            "Estado inicial",
            assets["estados_iniciales_validos"],
            index=0,
            format_func=lambda s: f"{s} - {assets['nombres_estados'][s]}",
        )

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            iniciar  = st.button("Simular", use_container_width=True, type="primary")
        with c2:
            resetear = st.button("Limpiar", use_container_width=True)

        # Previsualizacion rápida
        previsualizar = st.button("Previsualizar", use_container_width=True)
        use_preview = st.checkbox("Usar previsualización en dashboard", value=False)

        if previsualizar:
            preview_count = min(200, max(5, int(num_usuarios)))
            df_r, df_v = run_simulation(assets, preview_count, max_pasos, estado_inicial, seed=int(time.time()) % 100000)
            st.session_state["df_resultados_preview"] = df_r
            st.session_state["df_visitas_preview"] = df_v
            st.session_state["sim_preview_params"] = {"usuarios": preview_count, "max_pasos": max_pasos, "estado_inicial": estado_inicial}
            st.info(f"Previsualización generada: {preview_count} usuarios")

        if resetear:
            for key in ("df_resultados","df_visitas","sim_params","sim_before","df_resultados_preview","df_visitas_preview","sim_preview_params"):
                st.session_state.pop(key, None)
            st.rerun()

    return num_usuarios, max_pasos, estado_inicial, iniciar, previsualizar, use_preview


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
        "Simulación", "Simulador de Mejoras", "Comparación",
    ])

    # ── TAB 0 ─────────────────────────────────────────────────────────────────
    with tabs[0]:
        col1, col2 = st.columns([1.4, 0.6])
        with col1:
            st.markdown(
                """
                <div class="panel-card">
                    <div class="section-title">Acerca de esta Simulación</div>
                    <div class="section-copy">
                        Modelado de transiciones entre estados usando Cadenas de Márkov.
                        Cada recorrido representa una sesión de usuario en el sistema.
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            cm1, cm2, cm3 = st.columns(3)
            cm1.metric("Éxito",    f"{summary['success_rate']:.0f}%")
            cm2.metric("Error",    f"{summary['error_rate']:.0f}%")
            cm3.metric("Abandono", f"{summary['abandonment_rate']:.0f}%")

            weighted_df = pd.DataFrame({
                "Categoría": list(summary["weighted"].keys()),
                "Porcentaje": list(summary["weighted"].values()),
            })
            fig_w = px.bar(
                weighted_df, x="Categoría", y="Porcentaje", color="Categoría",
                color_discrete_map={"Éxito":"#10b981","Error":"#f72585","Abandono":"#f59e0b"},
                text_auto=".1f", title="Distribución Ponderada de Resultados",
            )
            fig_w.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#d4d4d8",size=11), showlegend=False,
                title_font_size=12, height=320,
            )
            st.plotly_chart(fig_w, use_container_width=True)

        with col2:
            top_r  = summary["top_result"]
            crit_s = summary["critical_state"]
            avg_s  = summary["avg_steps"]
            suc_w  = summary["weighted"]["Éxito"]
            e_ini  = sim_params["estado_inicial"]
            u_n    = sim_params["usuarios"]
            st.markdown(
                f"""
                <div class="panel-card" style="margin-bottom:14px;">
                    <div class="section-title">Resultado Dominante</div>
                    <div class="kpi-value" style="font-size:1.4rem;color:#f59e0b;">{top_r}</div>
                </div>
                <div class="panel-card" style="margin-bottom:14px;">
                    <div class="section-title">Punto Crítico</div>
                    <div class="kpi-value" style="font-size:1.2rem;color:#ef4444;">{crit_s}</div>
                </div>
                <div class="panel-card" style="margin-bottom:14px;">
                    <div class="section-title">Promedio Pasos</div>
                    <div class="kpi-value" style="font-size:1.4rem;color:#60a5fa;">{avg_s:.1f}</div>
                </div>
                <div class="panel-card success-card">
                    <div class="alert-title">Parámetros de Simulación</div>
                    <div class="alert-copy">
                        <strong>Estado Inicial:</strong> {e_ini}<br>
                        <strong>Usuarios:</strong> {u_n}<br>
                        Éxito ponderado: <strong>{suc_w:.1f}%</strong>
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
                <div class="section-title">Catálogo de Estados del Sistema</div>
                <div class="section-copy">Inventario completo de todos los estados del modelo Markoviano.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        rows = [
            {
                "Código": s,
                "Descripción": assets["nombres_estados"][s],
                "Tipo": state_type(s, assets),
                "Final":   "Sí" if s in assets["estados_finales"] else "No",
                "Crítico": "Sí" if s in assets["critical_states"] else "No",
            }
            for s in assets["estados"]
        ]
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown("")
        st.markdown("**Grafo de Estados (probabilidades de transición)**")
        fig_states = build_transition_figure_from_matrix(assets["matriz_probabilidades"], assets, title="Grafo de Probabilidades")
        st.plotly_chart(fig_states, use_container_width=True)

        st.markdown("")
        estado_sel = st.selectbox("Ver probabilidades de salida", assets["estados"], format_func=lambda s: f"{s} - {assets['nombres_estados'][s]}")
        probs = assets["matriz_probabilidades"].loc[estado_sel]
        probs_df = probs[probs > 0].reset_index()
        probs_df.columns = ["Destino","Probabilidad"]
        st.dataframe(probs_df, use_container_width=True, hide_index=True)
        if not probs_df.empty:
            fig_out = px.bar(probs_df, x="Probabilidad", y="Destino", orientation='h', title=f"Probabilidades de salida desde {estado_sel}")
            fig_out.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#d4d4d8'))
            st.plotly_chart(fig_out, use_container_width=True)

    # ── TAB 2 ─────────────────────────────────────────────────────────────────
    with tabs[2]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Matriz de Frecuencias de Transición</div>
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
            colorscale=[[0,"#1e1e2d"],[0.2,"#27293d"],[0.45,"#5e0075"],[0.7,"#bc00dd"],[1,"#ff007f"]],
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
        cc2.metric("Transiciones Únicas", int((assets["matriz_conteos"] > 0).sum().sum()))
        cc3.metric("Máxima Frecuencia",   int(assets["matriz_conteos"].max().max()))

    # ── TAB 3 ─────────────────────────────────────────────────────────────────
    with tabs[3]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Matriz de Probabilidades de Márkov</div>
                <div class="section-copy">Probabilidades normalizadas de transición (suma por fila = 100%).</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        fig_p = go.Figure(data=go.Heatmap(
            z=(assets["matriz_probabilidades"].values * 100).round(2),
            x=assets["matriz_probabilidades"].columns,
            y=assets["matriz_probabilidades"].index,
            colorscale=[[0,"#1e1e2d"],[0.2,"#27293d"],[0.45,"#5e0075"],[0.7,"#bc00dd"],[1,"#ff007f"]],
            text=np.round(assets["matriz_probabilidades"].values * 100, 1),
            texttemplate="%{text:.1f}%",
            hovertemplate="Desde: %{y}<br>Hacia: %{x}<br>Prob: %{z:.1f}%<extra></extra>",
        ))
        fig_p.update_layout(
            title="Matriz de Probabilidades de Márkov",
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
                <div class="section-copy">Exploración de secuencias generadas por la cadena markoviana.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        # Mostrar rutas definidas en el modelo (recorridos del conjunto de activos)
        rf1, rf2, rf3, rf4 = st.columns(4)
        rf1.metric("Total recorridos del modelo", len(assets.get('recorridos', [])))
        rf2.metric("Estados definidos", len(assets.get('estados', [])))
        rf3.metric("Estados finales", len(assets.get('estados_finales', [])))
        rf4.metric("Estados críticos", len(assets.get('critical_states', [])))
        st.markdown("")

        # Construir dataframe de recorridos del modelo con traducciones
        model_rows = []
        for i, rec in enumerate(assets.get('recorridos', []), start=1):
            codigo = " -> ".join(rec)
            nombres = " -> ".join([assets['nombres_estados'].get(s, s) for s in rec])
            model_rows.append({"id": i, "recorrido_codigos": codigo, "recorrido_nombres": nombres, "longitud": len(rec)})
        df_model_rec = pd.DataFrame(model_rows)

        length_filter = st.slider('Filtrar por longitud de recorrido', min_value=1, max_value=max(df_model_rec['longitud'].max(),1), value=(1, max(df_model_rec['longitud'].max(),1)))
        df_model_filtered = df_model_rec[df_model_rec['longitud'].between(length_filter[0], length_filter[1])]
        st.dataframe(df_model_filtered[['id','recorrido_codigos','recorrido_nombres','longitud']], use_container_width=True, hide_index=True)

        if st.button("Ver grafos de recorridos", use_container_width=True):
            fig_g = build_transition_figure_from_visits(df_visitas, assets, title="Grafo: Recorridos Observados")
            with st.expander("Grafo de Recorridos", expanded=True):
                if fig_g and getattr(fig_g, 'data', None):
                    st.plotly_chart(fig_g, use_container_width=True)
                else:
                    st.info("No hay suficientes datos para generar el grafo.")

    # ── TAB 5 ─────────────────────────────────────────────────────────────────
    with tabs[5]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Distribución de Resultados Finales</div>
                <div class="section-copy">Análisis estadístico de estados terminales alcanzados.</div>
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
                color_continuous_scale=["#3a0ca3","#4cc9f0","#f72585"],
                text_auto=True, title="Estados Finales Más Frecuentes",
            )
            fig_r.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#d4d4d8",size=11), coloraxis_showscale=False,
                height=400, showlegend=False,
            )
            st.plotly_chart(fig_r, use_container_width=True)
        with rr2:
            cd = df_resultados["categoria_final"].value_counts().reset_index()
            cd.columns = ["Categoría","Usuarios"]
            fig_d = px.pie(
                cd, names="Categoría", values="Usuarios", hole=0.5,
                color="Categoría",
                color_discrete_map={"Éxito":"#10b981","Error":"#f43f5e","Abandono":"#f59e0b","Otro":"#6366f1"},
                title="Distribución General de Categorías",
            )
            fig_d.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#d4d4d8",size=11), height=400,
            )
            st.plotly_chart(fig_d, use_container_width=True)

        top_df = summary["top_states"].reset_index()
        top_df.columns = ["Estado","Visitas"]
        top_df["Nombre"] = top_df["Estado"].map(assets["nombres_estados"])
        fig_v = px.bar(
            top_df, x="Visitas", y="Nombre", orientation="h",
            color="Visitas",
            color_continuous_scale=["#27293d","#5e0075","#bc00dd","#ff007f"],
            text_auto=True, title="Estados Más Visitados",
        )
        fig_v.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d4d4d8",size=10), coloraxis_showscale=False, height=350,
        )
        st.plotly_chart(fig_v, use_container_width=True)

    # ── TAB 6 ─────────────────────────────────────────────────────────────────
    with tabs[6]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Simulación Ejecutada</div>
                <div class="section-copy">
                    Métricas y distribución basadas en la última simulación (real).
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        col_a, col_b = st.columns([1.2, 0.8])
        with col_a:
            st.metric("Usuarios simulados", int(sim_params.get('usuarios', 0)))
            st.metric("Pasos máximos", int(sim_params.get('max_pasos', 0)))
            st.metric("Estado inicial", sim_params.get('estado_inicial', ''))

            visits = df_visitas['estado_nombre'].value_counts().reset_index()
            visits.columns = ['Estado','Visitas']
            fig_states = px.bar(visits.head(20), x='Visitas', y='Estado', orientation='h',
                                color='Visitas', title='Estados más visitados (observado)')
            fig_states.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#d4d4d8'))
            st.plotly_chart(fig_states, use_container_width=True)

        with col_b:
            sr = summary['success_rate']
            er = summary['error_rate']
            ar = summary['abandonment_rate']
            st.metric('Éxito', f"{sr:.1f}%")
            st.metric('Error', f"{er:.1f}%")
            st.metric('Abandono', f"{ar:.1f}%")

            df_cat = df_resultados['categoria_final'].value_counts().reset_index()
            df_cat.columns = ['Categoría','Usuarios']
            fig_pie = px.pie(df_cat, names='Categoría', values='Usuarios', hole=0.5,
                             color_discrete_map={"Éxito":"#10b981","Error":"#f72585","Abandono":"#f59e0b","Otro":"#3a0ca3"})
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#d4d4d8'))
            st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")

        # Mostrar tabla de recorridos simulados (detallada) con traducción de códigos
        st.markdown("**Recorridos Simulados (detallados)**")
        # añadir columna traducida si no existe
        if 'recorrido_nombres' not in df_resultados.columns:
            df_resultados['recorrido_nombres'] = df_resultados['recorrido_lista'].apply(lambda lst: ' -> '.join([assets['nombres_estados'].get(s, s) for s in lst]))

        cf1, cf2 = st.columns(2)
        with cf1:
            cat_filtro = st.multiselect(
                "Filtrar por categoría",
                ["Éxito","Error","Abandono","Otro"],
                default=["Éxito","Error","Abandono"],
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
            df_f[["usuario","recorrido","recorrido_nombres","estado_final","resultado","num_pasos","categoria_final"]].head(100),
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
                        <strong>Recorrido (códigos):</strong> {sel["recorrido"]}<br>
                        <strong>Recorrido (nombres):</strong> {sel["recorrido_nombres"]}<br>
                        <strong>Estado Final:</strong> {sel["estado_final_nombre"]}<br>
                        <strong>Pasos:</strong> {sel["num_pasos"]}<br>
                        <strong>Resultado:</strong> {sel["resultado"]}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with rd2:
            st.metric("Categoría", sel["categoria_final"]) 

        st.markdown("---")
        st.markdown("**Recomendaciones automáticas (análisis rápido)**")
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
                    Identifica el estado crítico, muestra por qué y permite ajustar sus probabilidades.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")

        # Detectar estado crítico actual (nombre) y buscar su código
        crit_name = summary.get('critical_state', None)
        crit_code = find_state_code_by_name(crit_name, assets) if crit_name else None

        if crit_name is None or crit_name == 'Sin incidencias' or crit_code is None:
            st.info('No se detectó un estado crítico automáticamente. Selecciona uno manualmente.')
            crit_code = st.selectbox('Seleccionar estado crítico (código)', assets['estados'], format_func=lambda s: f"{s} - {assets['nombres_estados'][s]}")
            crit_name = assets['nombres_estados'][crit_code]
        else:
            st.markdown(f"**Estado crítico detectado:** <strong>{crit_code} - {crit_name}</strong>", unsafe_allow_html=True)

        if crit_code is not None and crit_name is not None and crit_name != 'Sin incidencias':
            rec_crit = generate_critical_state_recommendation(crit_code, crit_name, df_resultados, df_visitas, assets)
            st.markdown(
                f"""
                <div class="panel-card warning-card">
                    <div class="alert-title">{rec_crit['title']}</div>
                    <div class="alert-copy">{rec_crit['text']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Mostrar por qué es crítico
        st.markdown("**Por qué es crítico**")
        visits_crit = df_visitas[df_visitas['estado'] == crit_code]
        cnt_users = visits_crit['usuario'].nunique()
        cnt_visits = visits_crit.shape[0]
        pct_users = cnt_users / df_resultados['usuario'].nunique() * 100 if df_resultados['usuario'].nunique() > 0 else 0
        st.markdown(f"- Usuarios afectados: **{cnt_users}** ({pct_users:.1f}% del total)")
        st.markdown(f"- Apariciones totales en recorridos: **{cnt_visits}**")
        # mostrar ejemplos de recorridos que llegan al crítico
        sample_rows = df_resultados[df_resultados['recorrido'].str.contains(crit_code)].head(6)
        if not sample_rows.empty:
            st.markdown('Ejemplos de recorridos que contienen el estado crítico:')
            st.dataframe(sample_rows[['usuario','recorrido','num_pasos','estado_final','categoria_final']], use_container_width=True)

        st.markdown('---')
        st.markdown('**Ajustar probabilidades de salida del estado crítico**')
        row_probs = assets['matriz_probabilidades'].loc[crit_code]
        # consider destinations with prob > 0 or top 8
        nonzero = row_probs[row_probs > 0]
        if nonzero.empty:
            st.info('El estado crítico no tiene transiciones salientes registradas.')
        else:
            dests = nonzero.sort_values(ascending=False).index.tolist()[:12]
            sliders = {}
            for d in dests:
                p = float(row_probs.loc[d])
                sliders[d] = st.slider(f"{d} - {assets['nombres_estados'][d]}", 0.0, 1.0, value=p, step=0.01)

            if st.button('Aplicar mejora y recalcular (antes/después)', use_container_width=True, type='primary'):
                # build modified assets copy
                assets_mod = assets.copy()
                assets_mod['matriz_probabilidades'] = assets['matriz_probabilidades'].copy()
                # set new row values for displayed destinations, keep other destinations as-is
                for d in dests:
                    assets_mod['matriz_probabilidades'].loc[crit_code, d] = float(sliders[d])
                # normalize row
                row_sum = assets_mod['matriz_probabilidades'].loc[crit_code].sum()
                if row_sum > 0:
                    assets_mod['matriz_probabilidades'].loc[crit_code] = assets_mod['matriz_probabilidades'].loc[crit_code] / row_sum

                # run simulation with modified matrix (use smaller sample for speed option)
                usuarios_run = int(sim_params.get('usuarios', 50))
                max_pasos_run = int(sim_params.get('max_pasos', 20))
                estado_init = sim_params.get('estado_inicial', 'S0')
                with st.spinner('Recalculando simulación con mejoras...'):
                    df_r_opt, df_v_opt = run_simulation(assets_mod, usuarios_run, max_pasos_run, estado_init, seed=123)
                st.session_state['df_resultados_opt'] = df_r_opt
                st.session_state['df_visitas_opt'] = df_v_opt
                st.session_state['assets_mod'] = assets_mod
                st.success('Simulación con mejora completada (guardada en sesión).')

        # Si hay resultado optimizado, mostrar comparación básica
        if 'df_resultados_opt' in st.session_state:
            st.markdown('---')
            st.markdown('**Comparación Rápida: Antes vs Después (simulación actual)**')
            df_before = df_resultados
            df_after = st.session_state['df_resultados_opt']
            before_summary = compute_summary(df_before, df_visitas, assets)
            after_summary = compute_summary(df_after, st.session_state['df_visitas_opt'], st.session_state.get('assets_mod', assets))
            c1, c2, c3 = st.columns(3)
            c1.metric('Éxito antes', f"{before_summary['success_rate']:.1f}%", delta=f"{after_summary['success_rate'] - before_summary['success_rate']:.1f}%")
            c2.metric('Error antes', f"{before_summary['error_rate']:.1f}%", delta=f"{after_summary['error_rate'] - before_summary['error_rate']:.1f}%")
            c3.metric('Abandono antes', f"{before_summary['abandonment_rate']:.1f}%", delta=f"{after_summary['abandonment_rate'] - before_summary['abandonment_rate']:.1f}%")
            # plot side by side bars
            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Bar(x=['Éxito','Error','Abandono'], y=[before_summary['success_rate'], before_summary['error_rate'], before_summary['abandonment_rate']], name='Antes', marker_color='#b0a8bf'))
            fig_cmp.add_trace(go.Bar(x=['Éxito','Error','Abandono'], y=[after_summary['success_rate'], after_summary['error_rate'], after_summary['abandonment_rate']], name='Después', marker_color='#ff9a56'))
            fig_cmp.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#d4d4d8'))
            st.plotly_chart(fig_cmp, use_container_width=True)

    # ── TAB 8 ─────────────────────────────────────────────────────────────────
    with tabs[8]:
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Comparación: Antes vs Después</div>
                <div class="section-copy">Visualiza el impacto proyectado de mejoras propuestas.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")

        # If an optimized simulation exists in session, prefer real before/after comparison
        if 'df_resultados_opt' in st.session_state and 'df_visitas_opt' in st.session_state:
            df_before = df_resultados
            df_vis_before = df_visitas
            df_after = st.session_state['df_resultados_opt']
            df_vis_after = st.session_state['df_visitas_opt']
            summary_before = compute_summary(df_before, df_vis_before, assets)
            summary_after = compute_summary(df_after, df_vis_after, st.session_state.get('assets_mod', assets))
            sr = summary_before['success_rate']
            er = summary_before['error_rate']
            ar = summary_before['abandonment_rate']
            sr_after = summary_after['success_rate']
            er_after = summary_after['error_rate']
            ar_after = summary_after['abandonment_rate']
        else:
            sr = summary["success_rate"]
            er = summary["error_rate"]
            ar = summary["abandonment_rate"]

        cp1, cp2 = st.columns(2)
        with cp1:
            # Use actual after values if available
            value_for_gauge = None
            if 'df_resultados_opt' in st.session_state:
                value_for_gauge = min(100, sr_after)
                delta_ref = sr
            else:
                value_for_gauge = min(100, sr * 1.15)
                delta_ref = sr

            fig_g = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=value_for_gauge,
                delta={"reference": delta_ref, "position":"top"},
                title={"text":"Éxito Proyectado"},
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
                paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#d4d4d8"), height=300,
            )
            st.plotly_chart(fig_g, use_container_width=True)

        with cp2:
            av = summary["avg_steps"]
            if 'df_resultados_opt' in st.session_state:
                comp_data = {
                    "Métrica": ["Éxito","Error","Abandono","Prom. Pasos"],
                    "Antes": [f"{sr:.1f}", f"{er:.1f}", f"{ar:.1f}", f"{av:.1f}"],
                    "Después": [f"{sr_after:.1f}", f"{er_after:.1f}", f"{ar_after:.1f}", f"{st.session_state['df_resultados_opt']['num_pasos'].mean():.1f}"],
                }
            else:
                comp_data = {
                    "Métrica":  ["Éxito","Error","Abandono","Prom. Pasos"],
                    "Antes":    [f"{sr:.1f}", f"{er:.1f}", f"{ar:.1f}", f"{av:.1f}"],
                    "Después":  [
                        f"{min(100,sr*1.15):.1f}",
                        f"{max(0,er*0.85):.1f}",
                        f"{max(0,ar*0.90):.1f}",
                        f"{max(1,av*0.95):.1f}",
                    ],
                }
            st.dataframe(pd.DataFrame(comp_data), use_container_width=True, hide_index=True)

        fig_cb = go.Figure()
        if 'df_resultados_opt' in st.session_state:
            fig_cb.add_trace(go.Bar(x=["Éxito","Error","Abandono"], y=[sr,er,ar], name="Antes", marker_color="#b0a8bf", text=[f"{sr:.0f}%",f"{er:.0f}%",f"{ar:.0f}%"], textposition="outside"))
            fig_cb.add_trace(go.Bar(x=["Éxito","Error","Abandono"], y=[sr_after,er_after,ar_after], name="Después", marker_color="#ff9a56", text=[f"{sr_after:.0f}%",f"{er_after:.0f}%",f"{ar_after:.0f}%"], textposition="outside"))
        else:
            fig_cb.add_trace(go.Bar(
                x=["Éxito","Error","Abandono"], y=[sr,er,ar],
                name="Actual", marker_color="#b0a8bf",
                text=[f"{sr:.0f}%",f"{er:.0f}%",f"{ar:.0f}%"],
                textposition="outside",
            ))
            fig_cb.add_trace(go.Bar(
                x=["Éxito","Error","Abandono"],
                y=[min(100,sr*1.15), max(0,er*0.85), max(0,ar*0.90)],
                name="Proyectado", marker_color="#ff9a56",
                text=[f"{min(100,sr*1.15):.0f}%",f"{max(0,er*0.85):.0f}%",f"{max(0,ar*0.90):.0f}%"],
                textposition="outside",
            ))
        fig_cb.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#d4d4d8"), barmode="group", height=400,
            title="Comparativa de Métricas: Antes vs Después",
        )
        st.plotly_chart(fig_cb, use_container_width=True)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    inject_styles()
    assets = load_markov_assets()
    initial_state(assets)

    num_usuarios, max_pasos, estado_inicial, iniciar, previsualizar, use_preview = render_sidebar(assets)

    if iniciar:
        with st.spinner("Ejecutando simulación..."):
            perform_simulation(assets, num_usuarios, max_pasos, estado_inicial)
        st.success(f"Simulación completada: {num_usuarios} usuarios procesados")
        st.rerun()

    # Decide whether to use preview results or the full simulation
    if use_preview and "df_resultados_preview" in st.session_state:
        df_resultados = st.session_state["df_resultados_preview"]
        df_visitas    = st.session_state["df_visitas_preview"]
        sim_params    = st.session_state.get("sim_preview_params", {})
    else:
        df_resultados = st.session_state["df_resultados"]
        df_visitas    = st.session_state["df_visitas"]
        sim_params    = st.session_state["sim_params"]
    render_dashboard(assets, df_resultados, df_visitas, sim_params)


if __name__ == "__main__":
    main()
