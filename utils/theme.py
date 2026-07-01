"""
Thème visuel central de POLITIQUE | Command Center.

Toutes les pages importent `inject_theme()` pour appliquer le même habillage
(palette Material 3 dark, glassmorphism, typographies Inter / JetBrains Mono)
que la maquette Stitch fournie comme référence.
"""

import streamlit as st

# --- Tokens de couleur (repris 1:1 du HTML Stitch) -------------------------
COLORS = {
    "background": "#0b1326",
    "surface": "#0b1326",
    "surface_container_lowest": "#060e20",
    "surface_container_low": "#131b2e",
    "surface_container": "#171f33",
    "surface_container_high": "#222a3d",
    "surface_container_highest": "#2d3449",
    "surface_variant": "#2d3449",
    "surface_bright": "#31394d",
    "on_surface": "#dae2fd",
    "on_surface_variant": "#c2c6d6",
    "outline": "#8c909f",
    "outline_variant": "#424754",
    "primary": "#adc6ff",
    "primary_container": "#4d8eff",
    "on_primary": "#002e6a",
    "on_primary_container": "#00285d",
    "secondary": "#ffb3ad",
    "secondary_container": "#a40217",
    "on_secondary": "#68000a",
    "on_secondary_container": "#ffaea8",
    "tertiary": "#bcc7de",
    "tertiary_container": "#8691a7",
    "error": "#ffb4ab",
    "error_container": "#93000a",
}

PARTY_COLORS = {
    "Extrême gauche - Gauche": COLORS["on_secondary_container"],
    "Centre - Majorité": COLORS["primary"],
    "Droite - Républicains": COLORS["tertiary_container"],
    "Extrême droite": COLORS["secondary_container"],
}


def inject_theme():
    """Injecte le CSS global Material3-dark + masque le chrome Streamlit par défaut."""
    c = COLORS
    st.markdown(
        f"""
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet">

        <style>
        /* ---------- Reset / base ---------- */
        html, body, [class*="css"]  {{
            font-family: 'Inter', sans-serif;
        }}
        .stApp {{
            background-color: {c['background']};
            color: {c['on_surface']};
        }}
        section[data-testid="stSidebar"] {{
            background-color: {c['surface_container']};
            border-right: 1px solid {c['outline_variant']}1a;
        }}
        section[data-testid="stSidebar"] * {{
            color: {c['on_surface_variant']};
        }}
        #MainMenu, header[data-testid="stHeader"], footer {{
            visibility: hidden;
            height: 0;
        }}
        .block-container {{
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1440px;
        }}

        /* ---------- Typo utilitaires ---------- */
        .label-caps {{
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            letter-spacing: 0.05em;
            font-weight: 500;
            text-transform: uppercase;
            color: {c['on_surface_variant']};
            opacity: 0.75;
        }}
        .data-num {{
            font-family: 'JetBrains Mono', monospace;
            font-weight: 600;
        }}
        .headline {{
            font-weight: 600;
            letter-spacing: -0.01em;
            color: {c['on_surface']};
        }}
        .display {{
            font-weight: 800;
            letter-spacing: -0.02em;
            color: {c['on_surface']};
        }}

        /* ---------- Cartes en verre ---------- */
        .glass-card {{
            background: rgba(30, 41, 59, 0.55);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            padding: 20px 22px;
            transition: transform 0.25s cubic-bezier(.34,1.56,.64,1), border-color 0.25s;
        }}
        .glass-card:hover {{
            transform: translateY(-2px);
            border-color: rgba(173,198,255,0.3);
        }}
        .glass-card-high {{
            background: rgba(23, 31, 51, 0.85);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 12px;
            box-shadow: 0 32px 64px -12px rgba(0,0,0,0.45);
            padding: 20px 22px;
        }}

        /* ---------- KPI ---------- */
        .kpi-card {{
            border-left: 4px solid var(--accent, {c['primary']});
        }}
        .kpi-label {{
            display:flex; justify-content:space-between; align-items:flex-start;
            margin-bottom: 10px;
        }}
        .kpi-value {{
            font-family:'JetBrains Mono', monospace;
            font-size: 40px;
            line-height: 1.05;
            font-weight: 700;
            letter-spacing: -0.02em;
            color: {c['on_surface']};
        }}
        .kpi-sub {{
            font-size: 12px;
            color: {c['on_surface_variant']};
            opacity: 0.7;
            margin-top: 6px;
        }}
        .kpi-delta-up {{ color: {c['primary']}; font-weight:700; font-size:12px; }}
        .kpi-delta-flag {{ color: {c['secondary']}; font-weight:700; font-size:12px; }}

        /* ---------- Pills / badges ---------- */
        .pill {{
            display:inline-block;
            padding: 2px 9px;
            border-radius: 999px;
            font-size: 10px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }}
        .pill-primary {{ background: rgba(173,198,255,0.12); color: {c['primary']}; }}
        .pill-secondary {{ background: rgba(255,179,173,0.12); color: {c['secondary']}; }}
        .pill-neutral {{ background: {c['surface_container_highest']}; color: {c['on_surface_variant']}; }}

        /* ---------- Divers ---------- */
        hr {{
            border-color: {c['outline_variant']}33;
        }}
        a {{ color: {c['primary']}; }}

        ::-webkit-scrollbar {{ width: 6px; }}
        ::-webkit-scrollbar-thumb {{ background: rgba(173,198,255,0.25); border-radius: 10px; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def material_icon(name: str, size: int = 20, color: str | None = None) -> str:
    """Retourne le HTML d'une icône Material Symbols Outlined inline."""
    col = f"color:{color};" if color else ""
    return (
        f'<span class="material-symbols-outlined" '
        f'style="font-size:{size}px;{col}font-variation-settings:\'FILL\' 0,\'wght\' 400;">'
        f"{name}</span>"
    )