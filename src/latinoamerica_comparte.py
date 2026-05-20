import base64
import html as html_lib
import os
import time
from collections import Counter

import networkx as nx
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from streamlit.components.v1 import html
from PIL import Image

# ----- configuracion general -----
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


# ----- helpers de logos -----
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


# ----- estilos y enfoque de pestañas -----
def inject_styles() -> None:
    css_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'styles.css')
    assets_css = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'styles.css')
    try:
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            return
        # fallback to assets/styles.css if present
        with open(assets_css, 'r', encoding='utf-8') as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Minimal fallback to avoid breaking layout
        st.markdown(
            """
            <style>
            .stApp { background: #121212; color: #ffffff; }
            </style>
            """,
            unsafe_allow_html=True,
        )


def focus_active_tab() -> None:
    active_tab = st.session_state.get("active_tab")
    if active_tab != "Simulación":
        return

    html(
        """
        <script>
        const activateTab = () => {
            const parentDoc = window.parent.document;
            const tabs = parentDoc.querySelectorAll('.stTabs [data-baseweb="tab"]');
            const target = Array.from(tabs).find((tab) =>
                tab.textContent && tab.textContent.trim() === 'Simulación'
            );
            if (target) {
                target.click();
            }
        };

        window.addEventListener('load', () => {
            setTimeout(activateTab, 0);
            setTimeout(activateTab, 150);
            setTimeout(activateTab, 400);
        });
        </script>
        """,
        height=0,
    )
    st.session_state.pop("active_tab", None)


# ----- datos del modelo markoviano -----
@st.cache_data
def load_markov_assets() -> dict:
    # ----- recorridos base del modelo -----
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

    # ----- catalogo de estados -----
    estados = [
        "S0","S1","S2","S3","S4","S5","S6","S7","S8",
        "S9","S10","S11","S12","S13","S14","S15","S16",
        "S17","S18","S19","S20","S21","S22","S23","S24",
        "S25","S26","S27","S28","S29","S30","S31","S32",
        "S33","S34","S35","S36",
    ]

    # ----- estados terminales -----
    estados_finales = [
        "S3","S7","S8","S11","S12","S14","S17","S19",
        "S21","S23","S27","S29","S30","S32","S35","S36",
    ]

    # ----- nombres descriptivos -----
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

    # ----- ponderaciones de resultados -----
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

    # ----- clasificaciones del modelo -----
    critical_states    = {"S3","S12","S23","S32","S36","S8"}
    success_states     = set(weighted_success_states.keys())
    error_states       = set(weighted_error_states.keys())
    abandonment_states = set(weighted_abandonment_states.keys())

    # ----- construccion de matrices base -----
    matriz_conteos = pd.DataFrame(0, index=estados, columns=estados)
    for recorrido in recorridos:
        for i in range(len(recorrido) - 1):
            matriz_conteos.loc[recorrido[i], recorrido[i + 1]] += 1

    matriz_probabilidades = matriz_conteos.div(
        matriz_conteos.sum(axis=1), axis=0
    ).fillna(0)

    # ----- estados iniciales permitidos -----
    estados_iniciales_validos = sorted(set(rec[0] for rec in recorridos if rec))

    # ----- paquete final de assets -----
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


# ----- helpers de simulacion -----
def classify_result(result_name: str, assets: dict) -> str:
    if result_name in assets["success_states"]:
        return "Éxito"
    if result_name in assets["error_states"]:
        return "Error"
    if result_name in assets["abandonment_states"]:
        return "Abandono"
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


def build_transition_figure_from_matrix(matriz: pd.DataFrame, assets: dict, title: str = "Grafo de Transiciones", show_codes: bool = False) -> go.Figure:
    # ----- construir grafo desde matriz -----
    G = nx.DiGraph()
    for src in matriz.index:
        for dst in matriz.columns:
            w = float(matriz.loc[src, dst])
            if w > 0:
                G.add_edge(src, dst, weight=w)

    # ----- posicion y aristas -----
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

    # ----- nodos y etiquetas -----
    node_x, node_y, node_text, node_color, node_hover = [], [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        name = assets['nombres_estados'].get(n, n)
        label = n if show_codes else f"{n} - {name}"
        node_text.append(label)
        node_hover.append(f"{n} - {name}")
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
        hovertext=node_hover,
        marker=dict(color=node_color, size=22, line_width=1, line=dict(color='rgba(255,255,255,0.2)', width=1))
    )

    # ----- figura final -----
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False, title=title, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=450, font=dict(color="#d4d4d8"))
    return fig


def build_transition_matrices_from_visits(df_visitas: pd.DataFrame, assets: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    # ----- estructura vacia de matrices -----
    estados = assets["estados"]
    matriz_conteos = pd.DataFrame(0, index=estados, columns=estados)

    if df_visitas.empty:
        matriz_probabilidades = matriz_conteos.astype(float)
        return matriz_conteos, matriz_probabilidades

    # ----- conteo de transiciones observadas -----
    df_visits_sorted = df_visitas.sort_values(["usuario", "orden"])
    for _, group in df_visits_sorted.groupby("usuario"):
        seq = list(group["estado"])
        for i in range(len(seq) - 1):
            src = seq[i]
            dst = seq[i + 1]
            if src in matriz_conteos.index and dst in matriz_conteos.columns:
                matriz_conteos.loc[src, dst] += 1

    # ----- normalizacion a probabilidades -----
    matriz_probabilidades = matriz_conteos.div(matriz_conteos.sum(axis=1), axis=0).fillna(0)
    return matriz_conteos, matriz_probabilidades


def build_transition_figure_from_visits(df_visitas: pd.DataFrame, assets: dict, title: str = "Grafo de Recorridos Observados", show_codes: bool = False) -> go.Figure:
    # ----- conteo de transiciones observadas -----
    df_visits_sorted = df_visitas.sort_values(['usuario','orden'])
    edges = Counter()
    for uid, group in df_visits_sorted.groupby('usuario'):
        seq = list(group['estado'])
        for i in range(len(seq)-1):
            edges[(seq[i], seq[i+1])] += 1

    # ----- construir grafo observado -----
    G = nx.DiGraph()
    for (u,v), w in edges.items():
        G.add_edge(u, v, weight=w)

    if len(G.nodes) == 0:
        return go.Figure()

    # ----- posicion y aristas -----
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

    # ----- nodos y etiquetas -----
    node_x, node_y, node_text, node_color, node_hover = [], [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        name = assets['nombres_estados'].get(n, n)
        label = n if show_codes else f"{n} - {name}"
        node_text.append(label)
        node_hover.append(f"{n} - {name}")
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
        hovertext=node_hover,
        marker=dict(color=node_color, size=20, line_width=1, line=dict(color='rgba(255,255,255,0.2)', width=1))
    )

    # ----- figura final -----
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False, title=title, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=500, font=dict(color="#d4d4d8"))
    return fig


def build_path_figure(recorrido: list[str], assets: dict, title: str = "Grafo del Recorrido Seleccionado", show_codes: bool = False) -> go.Figure:
    # ----- construir recorrido seleccionado -----
    G = nx.DiGraph()
    for i in range(len(recorrido) - 1):
        src = recorrido[i]
        dst = recorrido[i + 1]
        if G.has_edge(src, dst):
            G[src][dst]["weight"] += 1
        else:
            G.add_edge(src, dst, weight=1)

    if recorrido and recorrido[0] not in G.nodes:
        G.add_node(recorrido[0])

    if len(G.nodes) == 0:
        return go.Figure()

    # ----- posicion secuencial del recorrido -----
    pos = {}
    total = max(len(recorrido), 1)
    for idx, state in enumerate(recorrido):
        if state not in pos:
            pos[state] = (idx, -(idx % 2) * 0.15)

    edge_x, edge_y = [], []
    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=2, color="#f72585"),
        hoverinfo='none',
        mode='lines'
    )

    # ----- nodos y etiquetas -----
    node_x, node_y, node_text, node_color, node_hover = [], [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        name = assets['nombres_estados'].get(n, n)
        label = n if show_codes else f"{n} - {name}"
        node_text.append(label)
        node_hover.append(f"{n} - {name}")
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
        hovertext=node_hover,
        marker=dict(color=node_color, size=22, line_width=1, line=dict(color='rgba(255,255,255,0.2)', width=1))
    )

    # ----- figura final -----
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        title=title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=450,
        font=dict(color="#d4d4d8"),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
    )
    return fig


def run_simulation(
    assets: dict, num_usuarios: int, max_pasos: int,
    estado_inicial: str, seed: int = 42,
):
    # ----- configuracion de ejecucion -----
    np.random.seed(seed)
    resultados, visitas = [], []

    # ----- simulacion usuario por usuario -----
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
        # ----- detalle de visitas por recorrido -----
        for orden, estado in enumerate(recorrido, start=1):
            visitas.append({
                "usuario":       i + 1,
                "orden":         orden,
                "estado":        estado,
                "estado_nombre": assets["nombres_estados"][estado],
                "estado_tipo":   state_type(estado, assets),
            })
    return pd.DataFrame(resultados), pd.DataFrame(visitas)


# ----- metricas y recomendaciones -----
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
    # ----- resumen de resultados finales -----
    result_counts = df_resultados["resultado"].value_counts()
    top_result    = result_counts.index[0] if not result_counts.empty else "Sin datos"
    weighted      = calculate_weighted_percentages(df_resultados, assets)

    # ----- identificacion de estado critico -----
    critical_visits = (
        df_visitas[df_visitas["estado"].isin(assets["critical_states"])]["estado_nombre"]
        .value_counts()
    )
    critical_state = critical_visits.index[0] if not critical_visits.empty else "Sin incidencias"

    # ----- tasas globales -----
    success_rate     = (df_resultados["categoria_final"] == "Éxito").mean()    * 100
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
    # ----- reglas de recomendacion -----
    recs = []
    sr, er, ar = summary["success_rate"], summary["error_rate"], summary["abandonment_rate"]
    if sr >= 50:
        recs.append({"type":"success","title":"Desempeño sólido",
            "text": "La tasa de éxito es de " + str(int(sr)) + "%. Conviene identificar qué pasos funcionan bien y repetir esas mismas condiciones en otras partes del proceso."})
    if er >= 25:
        recs.append({"type":"error","title":"Revisar puntos de error",
            "text": "Se presentan errores en " + str(int(er)) + "% de los casos. Conviene revisar qué dato, acción o pantalla está fallando y mostrar instrucciones claras para que la persona pueda corregirlo."})
    if ar >= 20:
        recs.append({"type":"warning","title":"Reducir abandonos",
            "text": "El " + str(int(ar)) + "% de los usuarios abandona el proceso. Se recomienda acortar pasos, hacer más claras las instrucciones y confirmar visualmente que cada avance fue guardado."})
    # ----- hallazgos puntuales -----
    error_top = df_resultados[df_resultados["categoria_final"]=="Error"]["resultado"].value_counts().head(1)
    if not error_top.empty:
        recs.append({"type":"error","title":"Cuello de botella: " + error_top.index[0],
            "text": "Este problema aparece " + str(error_top.values[0]) + " veces dentro de los errores. Es un buen punto para intervenir primero porque está frenando una parte importante del recorrido."})
    most_visited = df_visitas["estado_nombre"].value_counts().head(1)
    if not most_visited.empty:
        recs.append({"type":"success","title":"Zona de alto tráfico detectada",
            "text": most_visited.index[0] + " es una etapa por la que pasa mucha gente. Si se mejora esa parte, el impacto puede notarse en una gran cantidad de usuarios."})
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
            f"({affected_pct:.1f}% del total). Se recomienda verificar credenciales, roles "
            "y permisos antes de enviar al usuario a este punto; mostrar mensajes claros "
            "que indiquen si el problema es usuario, contraseña o autorización; y ofrecer "
            "una salida visible para recuperar contraseña, reintentar o contactar soporte. "
            "Esto ayuda a reducir abandonos tempranos y recuperar usuarios dentro del flujo."
        )
    elif crit_name in {"Error al registrar usuario", "Error al gestionar contenido", "Respuesta del chatbot no disponible"}:
        title = "Reducir fricción en el flujo crítico"
        text = (
            f"El estado {crit_code} - {crit_name} aparece en {visits_crit.shape[0]} recorridos. "
            "Se recomienda revisar qué dato o acción dispara el fallo, avisar con claridad qué "
            "debe corregirse y permitir que la persona continúe o reintente sin empezar todo "
            "de nuevo."
        )
    elif crit_name in {"Sesión cerrada manualmente", "Sesión cerrada por inactividad"}:
        title = "Disminuir abandono de sesión"
        text = (
            f"El estado {crit_code} - {crit_name} indica salida del flujo en {affected_pct:.1f}% de los usuarios. "
            "Se recomienda reducir pasos innecesarios, guardar el avance automáticamente y avisar "
            "antes de que la sesión termine para que la persona no pierda su progreso."
        )
    else:
        title = "Atender el punto crítico detectado"
        text = (
            f"El estado {crit_code} - {crit_name} concentra {affected_users} usuarios afectados. "
            "Se recomienda revisar qué ocurre justo antes de este punto, explicar mejor qué debe "
            "hacer el usuario y ofrecer una salida clara para evitar que abandone el proceso."
        )

    return {
        "type": "warning",
        "title": title,
        "text": text,
    }


# ----- banner principal -----
def hero_section(summary: dict, assets: dict, usuarios: int) -> None:
    num_estados  = len(assets["estados"])
    # Mostrar métricas ponderadas en el banner principal
    weighted = summary.get("weighted", {"Éxito": 0.0, "Error": 0.0, "Abandono": 0.0})
    success_rate = weighted.get("Éxito", 0.0)
    error_rate   = weighted.get("Error", 0.0)
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
                        <div class="kpi-label" style="color:#10b981;">Éxito (Ponderado)</div>
                            <div class="kpi-value" style="color:#10b981;">{success_rate:.1f}%</div>
                    </div>
                    <div class="kpi-card" style="flex:1;min-width:100px;">
                        <div class="kpi-label" style="color:#ef4444;">Error (Ponderado)</div>
                        <div class="kpi-value" style="color:#ef4444;">{error_rate:.1f}%</div>
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


# ----- sidebar y controles -----
def render_sidebar(assets: dict) -> tuple:
    logo_html = get_logo_html(max_width=100)
    with st.sidebar:
        # ----- identidad y contexto -----
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

        # ----- parametros de simulacion -----
        num_usuarios   = st.slider("Usuarios a simular", min_value=5,  max_value=5000, value=100, step=5)
        max_pasos      = st.slider("Máximo de pasos",    min_value=5,  max_value=100, value=20, step=5)
        estado_inicial = st.selectbox(
            "Estado inicial",
            assets["estados_iniciales_validos"],
            index=0,
            format_func=lambda s: f"{s} - {assets['nombres_estados'][s]}",
        )

        st.markdown("---")
        # ----- acciones principales -----
        c1, c2 = st.columns(2)
        with c1:
            iniciar  = st.button("Simular", use_container_width=True, type="primary")
        with c2:
            resetear = st.button("Limpiar", use_container_width=True)

        # ----- opciones de previsualizacion -----
        previsualizar = st.button("Previsualizar", use_container_width=True)
        show_codes = st.checkbox("Mostrar solo códigos en grafos", value=True)

        if previsualizar:
            preview_count = min(200, max(5, int(num_usuarios)))
            df_r, df_v = run_simulation(assets, preview_count, max_pasos, estado_inicial, seed=int(time.time()) % 100000)
            st.session_state["df_resultados_preview"] = df_r
            st.session_state["df_visitas_preview"] = df_v
            st.session_state["sim_preview_params"] = {"usuarios": preview_count, "max_pasos": max_pasos, "estado_inicial": estado_inicial}
            # activar preview como vista en dashboard y mover al tab "Simulación"
            st.session_state['use_preview_for_dashboard'] = True
            st.session_state['active_tab'] = 'Simulación'
            st.rerun()

        if resetear:
            for key in ("df_resultados","df_visitas","sim_params","sim_before","df_resultados_preview","df_visitas_preview","sim_preview_params","use_preview_for_dashboard"):
                st.session_state.pop(key, None)
            st.rerun()

    return num_usuarios, max_pasos, estado_inicial, iniciar, previsualizar, show_codes


# ----- simulacion con progreso -----
def perform_simulation(assets: dict, num_usuarios: int, max_pasos: int, estado_inicial: str) -> None:
    # ----- inicializacion del progreso -----
    progress = st.sidebar.progress(0, text="Preparando...")
    live_box = st.sidebar.empty()
    results, visitas = [], []
    chunk = max(5, num_usuarios // 20)
    np.random.seed(42)

    # ----- procesamiento por usuario -----
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

        # ----- actualizacion visual del progreso -----
        if (i + 1) % chunk == 0 or i + 1 == num_usuarios:
            parcial    = pd.DataFrame(results)
            categorias = parcial["categoria_final"].value_counts(normalize=True).mul(100).round(1)
            ex = categorias.get("Éxito",   0)
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

    # ----- persistencia de resultados -----
    progress.empty()
    live_box.empty()
    st.session_state["df_resultados"] = pd.DataFrame(results)
    st.session_state["df_visitas"]    = pd.DataFrame(visitas)
    st.session_state["sim_params"]    = {
        "usuarios": num_usuarios, "max_pasos": max_pasos, "estado_inicial": estado_inicial,
    }


# ----- estado inicial automatico -----
def initial_state(assets: dict) -> None:
    # ----- simulacion inicial por defecto -----
    if "df_resultados" not in st.session_state:
        df_r, df_v = run_simulation(assets, 1200, 12, "S0")
        st.session_state["df_resultados"] = df_r
        st.session_state["df_visitas"]    = df_v
        st.session_state["sim_params"]    = {"usuarios":1200,"max_pasos":12,"estado_inicial":"S0"}


# ----- dashboard principal -----
def render_dashboard(
    assets: dict,
    df_resultados: pd.DataFrame,
    df_visitas: pd.DataFrame,
    sim_params: dict,
    show_codes: bool = True,
) -> None:
    # ----- resumen y matrices observadas -----
    summary = compute_summary(df_resultados, df_visitas, assets)
    matrix_counts, matrix_probabilities = build_transition_matrices_from_visits(df_visitas, assets)
    if matrix_counts.values.sum() == 0:
        matrix_counts = assets["matriz_conteos"]
        matrix_probabilities = assets["matriz_probabilidades"]
    hero_section(summary, assets, sim_params["usuarios"])

    # ----- estructura de navegacion -----
    tabs = st.tabs([
        "Resumen Ejecutivo", "Estados", "Matriz Conteo",
        "Matriz Probabilidades", "Recorridos", "Resultados",
        "Simulación", "Simulador de Mejoras", "Comparación",
    ])
    focus_active_tab()

    # ----- resumen ejecutivo -----
    with tabs[0]:
        # ----- bloque narrativo y metricas -----
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
            # Mostrar KPIs alineados a la distribución ponderada
            w = summary.get("weighted", {"Éxito": 0.0, "Error": 0.0, "Abandono": 0.0})
            cm1.metric("Éxito (Ponderado)",    f"{w['Éxito']:.1f}%")
            cm2.metric("Error (Ponderado)",    f"{w['Error']:.1f}%")
            cm3.metric("Abandono (Ponderado)", f"{w['Abandono']:.1f}%")

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
            # ----- tarjetas de hallazgos clave -----
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

    # ----- catalogo de estados -----
    with tabs[1]:
        # ----- tabla general de estados -----
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
        # ----- grafo general del sistema -----
        st.markdown("**Grafo de Estados Observados (simulación actual)**")
        fig_states = build_transition_figure_from_matrix(matrix_probabilities, assets, title="Grafo de Probabilidades Observadas", show_codes=show_codes)
        st.plotly_chart(fig_states, use_container_width=True)

        st.markdown("")
        # ----- detalle de salidas por estado -----
        estado_sel = st.selectbox("Ver probabilidades de salida", assets["estados"], format_func=lambda s: f"{s} - {assets['nombres_estados'][s]}")
        probs = matrix_probabilities.loc[estado_sel]
        probs_df = probs[probs > 0].reset_index()
        probs_df.columns = ["Destino","Probabilidad"]
        st.dataframe(probs_df, use_container_width=True, hide_index=True)
        if not probs_df.empty:
            fig_out = px.bar(probs_df, x="Probabilidad", y="Destino", orientation='h', title=f"Probabilidades de salida desde {estado_sel}")
            fig_out.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#d4d4d8'))
            st.plotly_chart(fig_out, use_container_width=True)

    # ----- matriz de conteo -----
    with tabs[2]:
        # ----- mapa de calor de frecuencias -----
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Matriz de Frecuencias de Transición</div>
                <div class="section-copy">Conteo absoluto de transiciones observadas en la simulación activa.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        fig_c = go.Figure(data=go.Heatmap(
            z=matrix_counts.values,
            x=matrix_counts.columns,
            y=matrix_counts.index,
            colorscale=[[0,"#1e1e2d"],[0.2,"#27293d"],[0.45,"#5e0075"],[0.7,"#bc00dd"],[1,"#ff007f"]],
            text=matrix_counts.astype(int).values,
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
        # ----- metricas de densidad de transiciones -----
        cc1, cc2, cc3 = st.columns(3)
        cc1.metric("Total Transiciones",  int(matrix_counts.sum().sum()))
        cc2.metric("Transiciones Únicas", int((matrix_counts > 0).sum().sum()))
        cc3.metric("Máxima Frecuencia",   int(matrix_counts.max().max()))

    # ----- matriz de probabilidades -----
    with tabs[3]:
        # ----- mapa de calor probabilistico -----
        st.markdown(
            """
            <div class="panel-card">
                <div class="section-title">Matriz de Probabilidades de Márkov</div>
                <div class="section-copy">Probabilidades normalizadas de transición de la simulación activa.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        fig_p = go.Figure(data=go.Heatmap(
            z=(matrix_probabilities.values * 100).round(2),
            x=matrix_probabilities.columns,
            y=matrix_probabilities.index,
            colorscale=[[0,"#1e1e2d"],[0.2,"#27293d"],[0.45,"#5e0075"],[0.7,"#bc00dd"],[1,"#ff007f"]],
            text=np.round(matrix_probabilities.values * 100, 1),
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

    # ----- recorridos del modelo -----
    with tabs[4]:
        # ----- indicadores del catalogo de recorridos -----
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

        # ----- tabla filtrable de recorridos -----
        model_rows = []
        for i, rec in enumerate(assets.get('recorridos', []), start=1):
            codigo = " -> ".join(rec)
            nombres = " -> ".join([assets['nombres_estados'].get(s, s) for s in rec])
            model_rows.append({"id": i, "recorrido_codigos": codigo, "recorrido_nombres": nombres, "longitud": len(rec)})
        df_model_rec = pd.DataFrame(model_rows)

        length_filter = st.slider('Filtrar por longitud de recorrido', min_value=1, max_value=max(df_model_rec['longitud'].max(),1), value=(1, max(df_model_rec['longitud'].max(),1)))
        df_model_filtered = df_model_rec[df_model_rec['longitud'].between(length_filter[0], length_filter[1])]
        st.dataframe(df_model_filtered[['id','recorrido_codigos','recorrido_nombres','longitud']], use_container_width=True, hide_index=True)

        # ----- seleccion y grafo del recorrido -----
        if not df_model_filtered.empty:
            recorrido_modelo_sel = st.selectbox(
                "Seleccionar recorrido del modelo",
                df_model_filtered["id"].tolist(),
                format_func=lambda rid: f"Recorrido {rid}",
            )
            rec_modelo = df_model_filtered[df_model_filtered["id"] == recorrido_modelo_sel].iloc[0]
            st.markdown(f"**Recorrido seleccionado:** `{rec_modelo['recorrido_codigos']}`")
            fig_g = build_path_figure(
                rec_modelo["recorrido_codigos"].split(" -> "),
                assets,
                title="Grafo: Recorrido del Modelo Seleccionado",
                show_codes=show_codes,
            )
            st.plotly_chart(fig_g, use_container_width=True)
        else:
            st.info("No hay recorridos del modelo con ese filtro.")

    # ----- resultados finales -----
    with tabs[5]:
        # ----- distribucion de cierres y categorias -----
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

        # ----- ranking de estados mas visitados -----
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

    # ----- simulacion ejecutada -----
    with tabs[6]:
        # ----- resumen visual de la corrida actual -----
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
        # ----- metricas principales y composicion final -----
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
            # Mostrar KPIs ponderados en la vista de simulación ejecutada
            w = summary.get('weighted', {"Éxito": 0.0, "Error": 0.0, "Abandono": 0.0})
            st.metric('Éxito (Ponderado)', f"{w['Éxito']:.1f}%")
            st.metric('Error (Ponderado)', f"{w['Error']:.1f}%")
            st.metric('Abandono (Ponderado)', f"{w['Abandono']:.1f}%")

            df_cat = df_resultados['categoria_final'].value_counts().reset_index()
            df_cat.columns = ['Categoría','Usuarios']
            fig_pie = px.pie(df_cat, names='Categoría', values='Usuarios', hole=0.5,
                             color_discrete_map={"Éxito":"#10b981","Error":"#f72585","Abandono":"#f59e0b","Otro":"#3a0ca3"})
            fig_pie.update_layout(paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#d4d4d8'))
            st.plotly_chart(fig_pie, use_container_width=True)

        # ----- detalle exploratorio de recorridos -----
        st.markdown("---")

        # ----- tabla de recorridos simulados -----
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

        # ----- inspeccion individual de usuarios -----
        usuarios_filtrados = df_f["usuario"].head(100).tolist()
        if usuarios_filtrados:
            usuario_sel = st.selectbox("Ver detalle de usuario", usuarios_filtrados)
            sel = df_resultados[df_resultados["usuario"] == usuario_sel].iloc[0]
            recorrido_codigos = html_lib.escape(str(sel["recorrido"]))
            recorrido_nombres = html_lib.escape(str(sel["recorrido_nombres"]))
            estado_final_nombre = html_lib.escape(str(sel["estado_final_nombre"]))
            resultado = html_lib.escape(str(sel["resultado"]))
            rd1, rd2 = st.columns([2,1])
            with rd1:
                st.markdown(
                    f"""
                    <div class="panel-card">
                        <div class="section-title">Usuario #{int(sel["usuario"])}</div>
                        <div class="section-copy">
                            <strong>Recorrido (codigos):</strong> {recorrido_codigos}<br>
                            <strong>Recorrido (nombres):</strong> {recorrido_nombres}<br>
                            <strong>Estado final:</strong> {estado_final_nombre}<br>
                            <strong>Pasos:</strong> {sel["num_pasos"]}<br>
                            <strong>Resultado:</strong> {resultado}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with rd2:
                st.metric("Categoria", sel["categoria_final"])

            fig_usuario = build_path_figure(
                sel["recorrido_lista"],
                assets,
                title=f"Grafo del recorrido del usuario {int(sel['usuario'])}",
                show_codes=show_codes,
            )
            st.plotly_chart(fig_usuario, use_container_width=True)
        else:
            st.info("No hay usuarios que coincidan con los filtros seleccionados.")
        # ----- recomendaciones generadas automaticamente -----
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

    # ----- simulador de mejoras -----
    with tabs[7]:
        # ----- contexto del simulador de mejoras -----
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

        # ----- deteccion del estado critico -----
        crit_name = summary.get('critical_state', None)
        crit_code = find_state_code_by_name(crit_name, assets) if crit_name else None

        if crit_name is None or crit_name == 'Sin incidencias' or crit_code is None:
            st.info('No se detectó un estado crítico automáticamente. Selecciona uno manualmente.')
            crit_code = st.selectbox('Seleccionar estado crítico (código)', assets['estados'], format_func=lambda s: f"{s} - {assets['nombres_estados'][s]}")
            crit_name = assets['nombres_estados'][crit_code]
        else:
            st.markdown(f"**Estado crítico detectado:** <strong>{crit_code} - {crit_name}</strong>", unsafe_allow_html=True)

        # ----- recomendacion asociada al punto critico -----
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

        # ----- analisis del estado critico -----
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

        # ----- ajuste manual de probabilidades -----
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

            if crit_code in assets['estados_finales']:
                st.info(
                    'Este estado crítico también está marcado como final en el modelo base. '
                    'Si aplicas nuevas salidas, la simulación mejorada lo tratará como recuperable '
                    'para que esos cambios sí tengan efecto.'
                )

            if st.button('Aplicar mejora y recalcular (antes/después)', use_container_width=True, type='primary'):
                # build modified assets copy
                assets_mod = assets.copy()
                assets_mod['matriz_probabilidades'] = assets['matriz_probabilidades'].copy()
                assets_mod['estados_finales'] = list(assets['estados_finales'])
                # set new row values for displayed destinations, keep other destinations as-is
                for d in dests:
                    assets_mod['matriz_probabilidades'].loc[crit_code, d] = float(sliders[d])
                # normalize row
                row_sum = assets_mod['matriz_probabilidades'].loc[crit_code].sum()
                if row_sum > 0:
                    assets_mod['matriz_probabilidades'].loc[crit_code] = assets_mod['matriz_probabilidades'].loc[crit_code] / row_sum
                    if crit_code in assets_mod['estados_finales']:
                        assets_mod['estados_finales'].remove(crit_code)
                elif crit_code in assets_mod['estados_finales']:
                    # Si no se definieron salidas, mantiene el comportamiento terminal original.
                    assets_mod['estados_finales'] = list(assets['estados_finales'])

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
        # ----- comparacion rapida tras la mejora -----
        if 'df_resultados_opt' in st.session_state:
            st.markdown('---')
            st.markdown('**Comparación Rápida: Antes vs Después (simulación actual)**')
            df_before = df_resultados
            df_after = st.session_state['df_resultados_opt']
            before_summary = compute_summary(df_before, df_visitas, assets)
            after_summary = compute_summary(df_after, st.session_state['df_visitas_opt'], st.session_state.get('assets_mod', assets))
            c1, c2, c3 = st.columns(3)
            c1.metric(
                'Éxito después',
                f"{after_summary['success_rate']:.1f}%",
                delta=f"{after_summary['success_rate'] - before_summary['success_rate']:.1f}% vs antes",
                delta_color="normal",
            )
            c2.metric(
                'Error después',
                f"{after_summary['error_rate']:.1f}%",
                delta=f"{after_summary['error_rate'] - before_summary['error_rate']:.1f}% vs antes",
                delta_color="inverse",
            )
            c3.metric(
                'Abandono después',
                f"{after_summary['abandonment_rate']:.1f}%",
                delta=f"{after_summary['abandonment_rate'] - before_summary['abandonment_rate']:.1f}% vs antes",
                delta_color="inverse",
            )
            # plot side by side bars
            fig_cmp = go.Figure()
            fig_cmp.add_trace(go.Bar(x=['Éxito','Error','Abandono'], y=[before_summary['success_rate'], before_summary['error_rate'], before_summary['abandonment_rate']], name='Antes', marker_color='#b0a8bf'))
            fig_cmp.add_trace(go.Bar(x=['Éxito','Error','Abandono'], y=[after_summary['success_rate'], after_summary['error_rate'], after_summary['abandonment_rate']], name='Después', marker_color='#ff9a56'))
            fig_cmp.update_layout(barmode='group', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#d4d4d8'))
            st.plotly_chart(fig_cmp, use_container_width=True)

    # ----- comparacion antes vs despues -----
    with tabs[8]:
        # ----- contexto comparativo -----
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

        # ----- comparacion usando simulacion optimizada -----
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

        # ----- gauge y tabla comparativa -----
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
                title={"text":"Éxito Proyectado"},
                domain={"x":[0.08,0.92],"y":[0.12,0.82]},
                number={"font":{"size":48}},
                delta={"reference": delta_ref, "position":"bottom", "font":{"size":18}},
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
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#d4d4d8"),
                height=360,
                margin=dict(l=24, r=24, t=72, b=36),
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

        # ----- barras comparativas finales -----
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


# ----- flujo principal -----
def main() -> None:
    # ----- carga inicial de recursos -----
    inject_styles()
    assets = load_markov_assets()
    initial_state(assets)

    num_usuarios, max_pasos, estado_inicial, iniciar, _, show_codes = render_sidebar(assets)

    # ----- ejecucion manual desde sidebar -----
    if iniciar:
        with st.spinner("Ejecutando simulación..."):
            perform_simulation(assets, num_usuarios, max_pasos, estado_inicial)
        st.success(f"Simulación completada: {num_usuarios} usuarios procesados")
        st.rerun()

    # ----- seleccion de fuente de datos para el dashboard -----
    if st.session_state.get('use_preview_for_dashboard') and "df_resultados_preview" in st.session_state:
        df_resultados = st.session_state["df_resultados_preview"]
        df_visitas    = st.session_state["df_visitas_preview"]
        sim_params    = st.session_state.get("sim_preview_params", {})
    else:
        df_resultados = st.session_state["df_resultados"]
        df_visitas    = st.session_state["df_visitas"]
        sim_params    = st.session_state["sim_params"]
    render_dashboard(assets, df_resultados, df_visitas, sim_params, show_codes=show_codes)


if __name__ == "__main__":
    main()
