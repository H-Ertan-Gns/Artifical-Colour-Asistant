from __future__ import annotations

from typing import Tuple

import streamlit as st


def render_cvd_selector(key_prefix: str = "") -> Tuple[str, bool]:
    st.sidebar.header("Ayarlar")
    cvd_type = st.sidebar.selectbox(
        "Renk körlüğü tipi",
        [
            "Protanopia (kırmızı-körlük)",
            "Deuteranopia (yeşil-körlük)",
            "Tritanopia (mavi-körlük)",
            "Protanomaly (kırmızı zayıf)",
            "Deuteranomaly (yeşil zayıf)",
            "Monokromasi (tam renk körlüğü)",
        ],
        key=f"{key_prefix}cvd_type_select",
    )
    enable_simulation = st.sidebar.checkbox(
        "Ben nasıl görüyorum",
        value=False,
        key=f"{key_prefix}cvd_sim_checkbox",
    )
    return cvd_type, enable_simulation

