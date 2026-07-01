import streamlit as st
from utils.theme import inject_theme

st.set_page_config(page_title="POLITIQUE | Segmentation", page_icon="🗳️", layout="wide")
inject_theme()

st.markdown('<div class="display" style="font-size:30px;">Segmentation</div>', unsafe_allow_html=True)
st.markdown('<div class="label-caps">Page à construire — prochaine étape</div>', unsafe_allow_html=True)
st.info("Cette page sera construite à la suite de la home page, selon le plan défini.")