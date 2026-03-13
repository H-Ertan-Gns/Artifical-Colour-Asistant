# ColorSight – Renk Körlüğü Asistanı

Renk körü kullanıcılar için görüntüleri daha anlaşılır ve ayırt edilebilir hale getiren, etkileşimli bir görüntü işleme aracı.

---

## 1. Problem ve çözüm özeti


| Başlık            | Açıklama                                                                                                                                                                           |
| ----------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Problem           | Renk körü kullanıcılar, özellikle kırmızı–yeşil ve mavi–sarı eksenlerinde, kritik bilgileri (trafik ışığı, uyarılar, haritalar vb.) ayırt etmekte zorlanır.                        |
| ColorSight çözümü | Yüklenen görüntüyü renk körü kullanıcının gözünden simüle eder, ardından o kullanıcı için daha ayırt edilebilir bir versiyonunu üretir ve tasarımcılar için analiz araçları sunar. |


**Ana fikir**:  
“Normal göz bu sahneyi nasıl görür, renk körü kullanıcı nasıl görür ve bizim düzeltmemizle nasıl görebilir?” sorularını tek ekranda yan yana göstermek.

---

## 2. Görsel mimari & akış

### Uygulama akışı (şema)

```mermaid
flowchart LR
    A[Fotoğraf / Kamera] --> B[Renk körlüğü tipi seçimi]
    B --> C[Simülasyon\n(Ben nasıl görüyorum?)]
    B --> D[Daltonization\n(Benim için düzeltilmiş)]
    C --> E[Üçlü karşılaştırma ekranı]
    D --> E
    E --> F[PDF rapor indirme]
```



### Örnek sahne karşılaştırması

Bu depo, uygulama içinde dinamik olarak üretilen aşağıdaki türde sahneleri kullanır:

- Kırmızı, yeşil ve mavi bloklardan oluşan basit bir arka plan,
- Trafik lambasına benzeyen üçlü ışık yapısı,
- Her renk körlüğü tipi için bu sahnenin simülasyonu (Genel bilgilendirme sekmesinde).

---

## 3. Teknik özet

- **Dil ve çerçeve**
  - Python 3.x
  - Streamlit (çok sekmeli web arayüzü)
- **Görüntü işleme**
  - Pillow (PIL) – görüntü okuma/yazma
  - NumPy – matris işlemleri, RGB ↔ LMS dönüşümleri
  - LMS tabanlı simülasyon matrisleri (Protanopia, Deuteranopia, Tritanopia)
- **Raporlama**
  - ReportLab – Türkçe karakter destekli, tek sayfalık PDF rapor (metin + düzeltilmiş görüntü)

---

## 4. Özellikler (sekme bazlı)

### Görüntü dönüştürücü

- Fotoğraf yükle → “Düzelt”:
  - **Orijinal**
  - **Ben nasıl görüyorum?** (tipine göre simülasyon)
  - **Benim için düzeltilmiş** (daltonization)
- İsteğe bağlı:
  - Renk dönüşüm özeti (kırmızı → kahverengi, yeşil → soluk vb.),
  - Tek sayfalık PDF rapor + düzeltilmiş görüntü indirme.

### Renk körlüğü testi (beta)

- 3 soruluk mini test ile algınızın:
  - Protanopia/Protanomaly,
  - Deuteranopia/Deuteranomaly,
  - Tritanopia  
  eksenlerinden hangisine daha yakın olabileceğini yaklaşık olarak tahmin eder.

### Genel bilgilendirme

- Tek bir sahne için:
  - Normal,
  - Protanopia / Deuteranopia / Tritanopia,
  - Protanomaly / Deuteranomaly / Monokromasi  
  simülasyonlarını yan yana gösterir.

### Canlı kamera (beta)

- Kameradan kare yakalar,
- Aynı üçlü görünümü (orijinal / ben nasıl görüyorum / düzeltilmiş) canlı görüntü üzerine uygular.

### Erişilebilirlik & renk paleti

- Metin/arka plan renkleri için kontrast oranı hesabı,
- Girilen hex renk paletinin, seçilen renk körlüğü tipi için nasıl görüneceğini gösteren palet simülasyonu.

---

## 5. Kurulum ve çalışma

```bash
cd "c:\Users\Lenovo\OneDrive\Masaüstü\Görüntü İşleme\chromafix"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m streamlit run app.py
```

---

## 6. Yazarlar

- [Hayri Ertan Güneş](https://github.com/H-Ertan-Gns)
- [Suzan Atmaca](https://github.com/SuzanATMACA/SuzanATMACA)

