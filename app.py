import streamlit as st

from utils.theme import inject_theme, material_icon, COLORS, PARTY_COLORS
from utils.data import (
    get_home_kpis,
    get_participation_trend,
    get_political_distribution,
    get_home_highlights,
)

st.set_page_config(
    page_title="POLITIQUE | Command Center",
    page_icon="🗳️",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_theme()

kpis = get_home_kpis()
trend = get_participation_trend()
distribution = get_political_distribution()
highlights = get_home_highlights()

# ---------------------------------------------------------------------------
# Sidebar — identité du projet (reprend le bloc "Command Center" de la maquette)
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        f"""
        <div style="padding: 4px 4px 18px 4px;">
            <div class="display" style="font-size:24px;">POLITIQUE</div>
            <div class="label-caps">Data Intelligence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("app.py", label="Home", icon="🏠")
    st.markdown(
        "Utilisez le menu ci-dessus pour naviguer entre la carte municipale, "
        "les analyses nationales, la segmentation et le module de prédiction."
    )
    st.markdown("---")
    st.markdown(
        f"""
        <div class="glass-card" style="padding:12px 14px;">
            <div style="font-weight:700;">Command Center</div>
            <div class="label-caps" style="font-size:10px; opacity:0.6;">ADMIN_ACCESS_V4</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="padding: 8px 0 28px 0;">
        <div class="label-caps" style="margin-bottom:10px;">
            {material_icon('bar_chart', 16, COLORS['primary'])} &nbsp;ANALYSE ÉLECTORALE & INSEE · 2001 – 2026
        </div>
        <div class="display" style="font-size:46px; line-height:1.05; max-width:780px;">
            Comprendre 25 ans d'élections municipales, commune par commune.
        </div>
        <div style="max-width:680px; color:{COLORS['on_surface_variant']}; font-size:17px; line-height:1.6; margin-top:14px;">
            Ce projet croise les résultats des scrutins municipaux (2001 à 2020) avec les données
            socio-démographiques de l'INSEE pour cartographier les dynamiques politiques locales,
            et propose un modèle de prédiction pour le scrutin de 2026.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# KPI cards
# ---------------------------------------------------------------------------
kpi_cols = st.columns(4, gap="medium")

kpi_specs = [
    {
        "label": "Communes analysées",
        "value": f"{kpis.communes_analysees:,}".replace(",", " "),
        "icon": "location_city",
        "accent": COLORS["primary"],
        "sub": "Couverture nationale",
    },
    {
        "label": "Participation moyenne",
        "value": f"{kpis.participation_moyenne:.1f}%",
        "icon": "how_to_reg",
        "accent": COLORS["secondary"],
        "sub": None,
        "bar": kpis.participation_moyenne,
    },
    {
        "label": "Listes recensées",
        "value": f"{kpis.total_listes:,}".replace(",", " "),
        "icon": "format_list_bulleted",
        "accent": COLORS["tertiary"],
        "sub": "Jeux de données vérifiés",
    },
    {
        "label": "Période d'analyse",
        "value": f"{kpis.periode_min} – {kpis.periode_max}",
        "icon": "calendar_month",
        "accent": COLORS["outline"],
        "sub": "Projections incluses",
    },
]

for col, spec in zip(kpi_cols, kpi_specs):
    with col:
        bar_html = ""
        if "bar" in spec:
            bar_html = f"""
            <div style="width:100%; background:{COLORS['surface_container_highest']};
                        height:6px; border-radius:999px; margin-top:14px;">
                <div style="background:{spec['accent']}; height:100%; width:{spec['bar']}%;
                            border-radius:999px;"></div>
            </div>
            """
        sub_html = f'<div class="kpi-sub">{spec["sub"]}</div>' if spec.get("sub") else ""
        st.markdown(
            f"""
            <div class="glass-card kpi-card" style="--accent:{spec['accent']};">
                <div class="kpi-label">
                    <span class="label-caps">{spec['label']}</span>
                    {material_icon(spec['icon'], 20, spec['accent'])}
                </div>
                <div class="kpi-value">{spec['value']}</div>
                {bar_html}
                {sub_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tendance participation + distribution politique
# ---------------------------------------------------------------------------
left, right = st.columns([7, 5], gap="medium")

with left:
    st.markdown(
        f"""
        <div class="glass-card" style="min-height:340px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                <div>
                    <div class="headline" style="font-size:20px;">Tendance de participation</div>
                    <div class="label-caps">Évolution nationale 2001 – 2026</div>
                </div>
                {material_icon('show_chart', 22, COLORS['on_surface_variant'])}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    chart_years = [str(p["annee"]) for p in trend]
    chart_vals = {"Participation (%)": [p["participation"] for p in trend]}
    st.line_chart(
        {"Année": chart_years, **chart_vals},
        x="Année",
        y="Participation (%)",
        height=260,
        color=COLORS["primary"],
    )

with right:
    st.markdown(
        f"""
        <div class="glass-card" style="min-height:340px;">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:18px;">
                <div>
                    <div class="headline" style="font-size:20px;">Répartition politique</div>
                    <div class="label-caps">Moyenne nationale, dernier scrutin connu</div>
                </div>
                {material_icon('bar_chart', 22, COLORS['on_surface_variant'])}
            </div>
        """,
        unsafe_allow_html=True,
    )
    for bloc in distribution:
        color = PARTY_COLORS.get(bloc["bloc"], COLORS["primary"])
        st.markdown(
            f"""
            <div style="margin-bottom:12px;">
                <div style="display:flex; justify-content:space-between; font-size:11px;
                            font-family:'JetBrains Mono',monospace; margin-bottom:5px;
                            color:{COLORS['on_surface_variant']};">
                    <span style="text-transform:uppercase;">{bloc['bloc']}</span>
                    <span class="data-num" style="color:{COLORS['on_surface']};">{bloc['valeur']}%</span>
                </div>
                <div style="width:100%; background:{COLORS['surface_container_highest']};
                            height:14px; border-radius:3px; overflow:hidden;">
                    <div style="background:{color}; height:100%; width:{bloc['valeur']}%;"></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='height:32px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Aperçu des modules de l'app
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div style="margin-bottom:18px;">
        <div class="headline" style="font-size:22px;">Explorer le projet</div>
        <div class="label-caps">Trois entrées pour démarrer l'analyse</div>
    </div>
    """,
    unsafe_allow_html=True,
)

hl_cols = st.columns(3, gap="medium")
for col, hl in zip(hl_cols, highlights):
    with col:
        st.markdown(
            f"""
            <div class="glass-card" style="min-height:190px;">
                <div style="display:flex; align-items:center; gap:10px; margin-bottom:14px;">
                    <div style="background:rgba(173,198,255,0.1); border-radius:8px; padding:8px;
                                display:flex; align-items:center;">
                        {material_icon(hl['icon'], 22, COLORS['primary'])}
                    </div>
                    <div class="headline" style="font-size:16px;">{hl['title']}</div>
                </div>
                <div style="color:{COLORS['on_surface_variant']}; font-size:14px; line-height:1.55;">
                    {hl['text']}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
st.caption(
    "Source : résultats officiels des élections municipales (ministère de l'Intérieur) "
    "et données INSEE. Les chiffres 2026 sont des projections issues du modèle prédictif."
)