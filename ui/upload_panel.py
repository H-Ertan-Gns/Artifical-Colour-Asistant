from __future__ import annotations

from typing import Optional

import streamlit as st
from PIL import Image


def render_upload_panel() -> Optional[Image.Image]:
    st.subheader("1. Görselini yükle")
    uploaded_file = st.file_uploader(
        "Bir görüntü dosyası seç (PNG, JPG, JPEG)",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
    )

    if uploaded_file is None:
        return None

    try:
        image = Image.open(uploaded_file).convert("RGB")
    except Exception:
        st.error("Görsel yüklenirken bir hata oluştu. Lütfen geçerli bir resim dosyası yükleyin.")
        return None

    st.subheader("2. Önizleme")
    # Genişlik parametresi vermeyerek görüntüyü doğal çözünürlüğünde gösteriyoruz.
    st.image(image, caption="Yüklenen orijinal görüntü")

    return image

