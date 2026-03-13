import io
from datetime import datetime
import textwrap

from PIL import Image, ImageDraw
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from ui.upload_panel import render_upload_panel
from ui.cvd_selector import render_cvd_selector
from core.cvd_types import from_label, info_for_type, CVDType
from core.pipeline import apply_cvd_correction, apply_cvd_simulation


PAGE_TITLE = "ColorSight – Renk Körlüğü Asistanı"
PAGE_SUBTITLE = "Renk körü kullanıcılar için görüntüleri daha anlaşılır ve ayırt edilebilir hale getiren etkileşimli bir araç."


def main() -> None:
    st.set_page_config(page_title="ColorSight", layout="wide")

    st.title(PAGE_TITLE)
    st.caption(PAGE_SUBTITLE)

    # Sidebar ayarları (tüm sekmeler için ortak)
    cvd_label, enable_simulation = render_cvd_selector("main_")
    st.sidebar.markdown("---")
    show_legend = st.sidebar.checkbox("Renk dönüşüm özetini göster", value=False, key="legend_main")
    show_report = st.sidebar.checkbox("Kısa rapor göster", value=False, key="report_main")

    tabs = st.tabs(
        [
            "Görüntü dönüştürücü",
            "Renk körlüğü testi (beta)",
            "Genel bilgilendirme",
            "Canlı kamera",
            "Erişilebilirlik & palet",
        ]
    )

    with tabs[0]:
        image = render_upload_panel()

        if image is None:
            st.info("Başlamak için bir görüntü yükleyip soldan renk körlüğü tipini seçebilirsin.")
            return

        st.subheader("3. İşlem")
        if st.button("Düzelt"):
            cvd_type = from_label(cvd_label)

            corrected_image = apply_cvd_correction(image, cvd_type)
            sim_image = apply_cvd_simulation(image, cvd_type) if enable_simulation else None

            # Üçlü karşılaştırma: Orijinal / Ben nasıl görüyorum? / Düzeltilmiş
            cols = st.columns(3)
            with cols[0]:
                st.markdown("**Orijinal**")
                st.image(image)

            with cols[1]:
                st.markdown("**Ben nasıl görüyorum?**")
                if enable_simulation and sim_image is not None:
                    st.image(sim_image)
                elif enable_simulation and sim_image is None:
                    st.warning("Bu tip için simülasyon henüz uygulanmadı.")
                else:
                    st.info("Bu alanı görmek için sol menüden \"Ben nasıl görüyorum\" kutusunu işaretle.")

            with cols[2]:
                st.markdown("**Benim için düzeltilmiş**")
                st.image(corrected_image)

            if enable_simulation:
                info_text = info_for_type(cvd_type)
                if info_text:
                    st.info(info_text)

            if show_legend:
                st.markdown("### Renk dönüşüm özeti")
                if cvd_label.startswith("Protanopia"):
                    st.markdown("- **Kırmızı**: Koyu yeşil / kahverengi tonlarına kayma eğiliminde.\n- **Yeşil**: Kırmızıya yaklaşarak ayrımı zorlaştırır.")
                elif cvd_label.startswith("Deuteranopia"):
                    st.markdown("- **Yeşil**: Soluk ve kırmızıya yakın görünür.\n- **Kırmızı**: Yeşille karışarak nötr tonlara kayar.")
                elif cvd_label.startswith("Tritanopia"):
                    st.markdown("- **Mavi**: Yeşilimsi veya soluk tonlara kayar.\n- **Sarı**: Açık pembe / gri tonlarıyla karışabilir.")
                elif cvd_label.startswith("Monokromasi"):
                    st.markdown("- **Tüm renkler**: Farklı parlaklıklarda gri tonları olarak algılanır.")
                else:
                    st.markdown("- **Anomaliler**: İlgili ana rengin (kırmızı/yeşil) doygunluğu düşer, daltonization bu kanalı güçlendirir.")

            if show_report:
                st.markdown("### Kısa rapor")
                st.write(f"- Seçilen tip: **{cvd_label}**")
                st.write(
                    "- Uygulanan işlemler: Simülasyon + daltonization + tipine göre gri-tonlama / kanal güçlendirme."
                )

            # İndirilebilir rapor + görsel paketi
            processed_at = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
            rapor_satirlari = [
                "ColorSight – Dönüştürme Raporu",
                f"Tarih / Saat: {processed_at}",
                "",
                f"Seçilen renk körlüğü tipi: {cvd_label}",
                f"Giriş görüntüsü boyutu: {image.width}x{image.height} piksel",
                "",
                "Uygulanan işlemler:",
                "- Orijinal görüntü temel alınarak seçilen tipe özel daltonization uygulandı.",
                "- İlgili koni (kırmızı/yeşil/mavi) bilgisindeki kayıp, diğer kanallardan tahmin edilerek güçlendirildi.",
            ]

            if enable_simulation:
                rapor_satirlari.append("- Seçilen tip için ek olarak 'Ben nasıl görüyorum?' simülasyonu üretildi.")

            if show_legend:
                rapor_satirlari.append("")
                rapor_satirlari.append("Renk dönüşüm özeti:")
                if cvd_label.startswith("Protanopia"):
                    rapor_satirlari.append("• Kırmızı, daha koyu yeşil / kahverengi tonlarına yaklaşır.")
                    rapor_satirlari.append("• Yeşil, kırmızıya yaklaşarak ayrımı zorlaştırır.")
                elif cvd_label.startswith("Deuteranopia"):
                    rapor_satirlari.append("• Yeşil, soluk ve kırmızıya yakın görünür.")
                    rapor_satirlari.append("• Kırmızı, yeşille karışarak daha nötr tonlara kayar.")
                elif cvd_label.startswith("Tritanopia"):
                    rapor_satirlari.append("• Mavi, yeşilimsi veya soluk tonlara kayar.")
                    rapor_satirlari.append("• Sarı, açık pembe / gri tonlarına karışabilir.")
                elif cvd_label.startswith("Monokromasi"):
                    rapor_satirlari.append("• Tüm renkler, farklı parlaklıklarda gri tonları olarak algılanır.")
                else:
                    rapor_satirlari.append(
                        "• İlgili ana rengin (kırmızı/yeşil) doygunluğu düşer, düzeltme bu kanalı güçlendirmeye odaklanır."
                    )

            info_text = info_for_type(cvd_type)
            if info_text:
                rapor_satirlari.append("")
                rapor_satirlari.append("Tip hakkında kısa bilgi:")
                rapor_satirlari.append(info_text)

            rapor_metin = "\n".join(rapor_satirlari)

            # PDF oluştur
            pdf_buffer = io.BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4

            # Türkçe karakterleri destekleyen bir font kaydet (Windows varsayılan yolu üzerinden)
            font_name = "Arial"
            try:
                pdfmetrics.getFont(font_name)
            except KeyError:
                try:
                    pdfmetrics.registerFont(TTFont(font_name, "C:/Windows/Fonts/arial.ttf"))
                except Exception:
                    font_name = "Helvetica"

            text_object = c.beginText(40, height - 60)
            text_object.setFont(font_name, 11)
            text_object.setLeading(15)

            # Metni sayfa genişliğine göre sar
            max_chars = 90
            for line in rapor_satirlari:
                wrapped = textwrap.wrap(line, width=max_chars) or [""]
                for sub in wrapped:
                    text_object.textLine(sub)

            c.drawText(text_object)

            # Düzeltilmiş görüntüyü sayfanın alt kısmına yerleştir
            img_width, img_height = corrected_image.size
            max_img_width = width - 80
            max_img_height = height / 3
            scale = min(max_img_width / img_width, max_img_height / img_height, 1.0)
            render_width = img_width * scale
            render_height = img_height * scale
            x = (width - render_width) / 2
            y = 60

            # ReportLab, dosya yolu veya ImageReader bekler
            img_buffer = io.BytesIO()
            corrected_image.save(img_buffer, format="PNG")
            img_buffer.seek(0)
            image_reader = ImageReader(img_buffer)

            c.drawImage(image_reader, x, y, width=render_width, height=render_height, preserveAspectRatio=True, mask="auto")

            c.showPage()
            c.save()
            pdf_buffer.seek(0)

            st.download_button(
                label="Düzeltilmiş görüntü + raporu PDF olarak indir",
                data=pdf_buffer,
                file_name=f"colorsight_rapor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
            )

    with tabs[1]:
        st.subheader("Hızlı renk körlüğü testi (yaklaşık tahmin)")

        q1 = st.radio(
            "1) Aşağıdaki renk çiftlerinden hangisini ayırt etmek senin için en zor?",
            ["Kırmızı / Yeşil", "Mavi / Sarı", "Kırmızı / Mavi", "Hepsi benzer zorlukta değil"],
        )
        q2 = st.radio(
            "2) Trafik ışıklarını düşün:",
            [
                "Üstteki (kırmızı) ile ortadaki (sarı/yeşil) bazen karışıyor",
                "Alttaki (yeşil) ile ortadaki (sarı) bazen karışıyor",
                "Genelde net görüyorum",
            ],
        )
        q3 = st.radio(
            "3) Renkli yazıları okurken en çok hangisi sorun?",
            [
                "Kırmızı yazı yeşil zemin üzerinde",
                "Mavi yazı sarı zemin üzerinde",
                "Genel olarak hepsi okunabilir",
            ],
        )

        if st.button("Test sonucumu göster"):
            score = {"Protanopia / Protanomaly": 0, "Deuteranopia / Deuteranomaly": 0, "Tritanopia": 0}

            if q1 == "Kırmızı / Yeşil":
                score["Protanopia / Protanomaly"] += 1
                score["Deuteranopia / Deuteranomaly"] += 1
            elif q1 == "Mavi / Sarı":
                score["Tritanopia"] += 2

            if q2.startswith("Üstteki"):
                score["Protanopia / Protanomaly"] += 1
            elif q2.startswith("Alttaki"):
                score["Deuteranopia / Deuteranomaly"] += 1

            if q3.startswith("Kırmızı yazı"):
                score["Protanopia / Protanomaly"] += 1
            elif q3.startswith("Mavi yazı"):
                score["Tritanopia"] += 1

            likely = max(score, key=score.get)

            st.success(f"Sonuç: Cevaplarına göre **{likely}** tipine yakın bir algın olabilir.")
            st.info(
                "ColorSight içinde, sol menüden bu tipe en yakın seçeneği işaretleyip kendi görsellerin üzerinde "
                "‘Ben nasıl görüyorum?’ ve ‘Benim için düzeltilmiş’ karşılaştırmalarını deneyebilirsin."
            )

    with tabs[2]:
        st.subheader("Renk körlüğü tiplerine göre örnek görseller")
        st.caption("Aşağıdaki görseller, aynı sahnenin farklı renk körlüğü tipleri için yaklaşık olarak nasıl göründüğünü gösterir.")

        # Basit ama renkli bir demo sahnesi oluştur (kırmızı, yeşil, mavi alanlar + trafik ışığı benzeri şekiller)
        width, height = 600, 400
        base = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(base)

        # Arka plan blokları
        draw.rectangle((0, 0, width // 3, height // 2), fill=(220, 20, 60))   # kırmızı alan
        draw.rectangle((width // 3, 0, 2 * width // 3, height // 2), fill=(50, 205, 50))  # yeşil alan
        draw.rectangle((2 * width // 3, 0, width, height // 2), fill=(30, 144, 255))  # mavi alan

        # Trafik ışığı stili
        cx = width // 2
        top = height // 2 + 20
        r = 35
        draw.rectangle((cx - 60, top - 20, cx + 60, top + 3 * r * 2 + 40), fill=(30, 30, 30))
        draw.ellipse((cx - r, top, cx + r, top + 2 * r), fill=(220, 20, 60))  # kırmızı
        draw.ellipse((cx - r, top + 2 * r + 10, cx + r, top + 4 * r + 10), fill=(255, 215, 0))  # sarı
        draw.ellipse((cx - r, top + 4 * r + 20, cx + r, top + 6 * r + 20), fill=(50, 205, 50))  # yeşil

        # Normal + simülasyonlar
        st.markdown("#### Normal görüş")
        st.image(base, caption="Normal (renk körlüğü yok)")

        sim_cols = st.columns(3)
        sim_types = [
            (CVDType.PROTANOPIA, "Protanopia (kırmızı-körlük)"),
            (CVDType.DEUTERANOPIA, "Deuteranopia (yeşil-körlük)"),
            (CVDType.TRITANOPIA, "Tritanopia (mavi-körlük)"),
        ]

        for col, (cvd_type, label) in zip(sim_cols, sim_types):
            with col:
                sim_img = apply_cvd_simulation(base, cvd_type)
                if sim_img is not None:
                    st.image(sim_img, caption=label)

        sim_cols2 = st.columns(3)
        sim_types2 = [
            (CVDType.PROTANOMALY, "Protanomaly (kırmızı zayıf)"),
            (CVDType.DEUTERANOMALY, "Deuteranomaly (yeşil zayıf)"),
            (CVDType.MONOCHROMASY, "Monokromasi (tam renk körlüğü)"),
        ]

        for col, (cvd_type, label) in zip(sim_cols2, sim_types2):
            with col:
                sim_img = apply_cvd_simulation(base, cvd_type)
                if sim_img is not None:
                    st.image(sim_img, caption=label)

    with tabs[3]:
        st.subheader("Canlı kamera (beta)")
        st.caption("Kamerandan bir kare yakalayıp seçilen renk körlüğü tipine göre görüntüyü dönüştürebilirsin.")

        cam_image = st.camera_input("Kameradan görüntü yakala")

        if cam_image is not None:
            image_cam = Image.open(cam_image).convert("RGB")
            cvd_type_cam = from_label(cvd_label)

            corrected_cam = apply_cvd_correction(image_cam, cvd_type_cam)
            sim_cam = apply_cvd_simulation(image_cam, cvd_type_cam) if enable_simulation else None

            cols_cam = st.columns(3)
            with cols_cam[0]:
                st.markdown("**Orijinal (kamera)**")
                st.image(image_cam)

            with cols_cam[1]:
                st.markdown("**Ben nasıl görüyorum?**")
                if enable_simulation and sim_cam is not None:
                    st.image(sim_cam)
                elif enable_simulation:
                    st.info("Bu tip için simülasyon henüz uygulanmadı.")
                else:
                    st.info("Bu alanı görmek için sol menüden \"Ben nasıl görüyorum\" kutusunu işaretle.")

            with cols_cam[2]:
                st.markdown("**Benim için düzeltilmiş**")
                st.image(corrected_cam)

    with tabs[4]:
        st.subheader("Erişilebilirlik denetleyicisi ve renk paleti dönüştürücü")

        # Kontrast aracı
        st.markdown("### Metin / arka plan kontrastı")
        col_a, col_b = st.columns(2)
        with col_a:
            fg = st.color_picker("Metin rengi", "#FFFFFF")
        with col_b:
            bg = st.color_picker("Arka plan rengi", "#0066CC")

        def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
            hex_color = hex_color.lstrip("#")
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return r, g, b

        def _rel_luminance(rgb: tuple[float, float, float]) -> float:
            def f(c: float) -> float:
                return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

            r, g, b = rgb
            return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)

        fg_lum = _rel_luminance(_hex_to_rgb(fg))
        bg_lum = _rel_luminance(_hex_to_rgb(bg))
        lighter = max(fg_lum, bg_lum)
        darker = min(fg_lum, bg_lum)
        contrast_ratio = (lighter + 0.05) / (darker + 0.05)

        st.write(f"Kontrast oranı: **{contrast_ratio:.2f}:1**")

        # Palet dönüştürücü
        st.markdown("### Renk paleti dönüştürücü")
        st.caption("Altıya kadar hex kodu gir (örnek: #FF0000, #00FF00, #0000FF) ve seçilen tip için paletin nasıl değiştiğini gör.")
        palette_text = st.text_area(
            "Renk paleti (virgülle veya boşlukla ayrılmış hex kodları)",
            "#FF0000, #00FF00, #0000FF, #FFFF00",
        )

        if st.button("Paleti dönüştür"):
            parts = [p.strip() for p in palette_text.replace("\n", " ").split(",")]
            colors = []
            for part in parts:
                if not part:
                    continue
                c = part.strip()
                if " " in c:
                    c = c.split()[0]
                if not c.startswith("#"):
                    continue
                if len(c) == 7:
                    colors.append(c)

            if not colors:
                st.warning("Geçerli en az bir renk kodu gir.")
            else:
                n = len(colors)
                w, h = 80 * n, 80
                base_pal = Image.new("RGB", (w, h), "white")
                draw_pal = ImageDraw.Draw(base_pal)
                for i, hex_c in enumerate(colors):
                    r = int(hex_c[1:3], 16)
                    g = int(hex_c[3:5], 16)
                    b = int(hex_c[5:7], 16)
                    draw_pal.rectangle((i * 80, 0, (i + 1) * 80, h), fill=(r, g, b))

                cvd_type_pal = from_label(cvd_label)
                sim_pal = apply_cvd_simulation(base_pal, cvd_type_pal)
                if sim_pal is None:
                    st.warning("Bu tip için palet simülasyonu henüz uygulanmadı.")
                else:
                    col_p1, col_p2 = st.columns(2)
                    with col_p1:
                        st.markdown("**Orijinal palet**")
                        st.image(base_pal)
                    with col_p2:
                        st.markdown("**Benim gözümden palet**")
                        st.image(sim_pal)


if __name__ == "__main__":
    main()


