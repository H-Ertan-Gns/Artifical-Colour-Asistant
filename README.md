# ColorSight – Renk Körlüğü Asistanı

Renk körü kullanıcılar için görüntüleri daha anlaşılır ve ayırt edilebilir hale getiren, etkileşimli bir görüntü işleme aracı.

---

## Problem tanımı

Renk körlüğü (color vision deficiency), özellikle kırmızı–yeşil ve mavi–sarı eksenlerinde, insanların renkleri algılama biçimini değiştiren kalıtsal bir durumdur.  
Bu durum:

- Trafik işaretleri, haritalar, uyarı metinleri gibi kritik bilgilerin okunmasını zorlaştırabilir,
- Tasarımcılar ve yazılım geliştiriciler için “renk körü kullanıcı bu ekranı nasıl görüyor?” sorusunu önemli hale getirir.

**ColorSight**, bu problemi üç açıdan ele alır:

1. Renk körü kullanıcının bir görüntüyü nasıl gördüğünü simüle eder.  
2. Aynı görüntünün, o kullanıcı için daha ayırt edilebilir bir versiyonunu üretir (daltonization).  
3. Tasarımcılar için renk paleti ve kontrast analiz araçları sunar.

---

## Teknik mimari

- **Dil ve çerçeve**
  - Python 3.x
  - Streamlit (web arayüzü ve etkileşim)
- **Görüntü işleme**
  - Pillow (PIL) – görüntü okuma, yazma ve temel işlemler
  - NumPy – matris işlemleri (renk uzayı dönüşümleri)
  - OpenCV / scikit-image – ileride genişletilebilir ek dönüşümler için
- **Raporlama**
  - ReportLab – tek sayfalık PDF rapor üretimi

Klasör yapısı kısaca:

- `app.py` – tüm Streamlit sayfalarının (sekme yapısı) ve iş akışlarının ana dosyası
- `core/`
  - `cvd_types.py` – renk körlüğü tipleri için enum ve bilgilendirme metinleri
  - `pipeline.py` – simülasyon ve daltonization algoritmalarının merkezi
- `ui/`
  - `upload_panel.py` – yükleme ve önizleme bileşeni
  - `cvd_selector.py` – sol menüdeki tip ve mod seçimleri

---

## Algoritmalar (özet)

### 1. Simülasyon (Ben nasıl görüyorum?)

Her tip için, yaklaşık LMS tabanlı dönüşümler kullanılır:

- RGB → LMS dönüşümü için literatürde kullanılan 3×3 matrisler,
- İlgili koni kanalı (L, M veya S) tipine göre yeniden hesaplanır:
  - Protanopia: L kanalı, M ve S’den tahmin edilir (kırmızı koni eksikliği),
  - Deuteranopia: M kanalı, L ve S’den tahmin edilir (yeşil koni eksikliği),
  - Tritanopia: S kanalı, L ve M’den tahmin edilir (mavi koni eksikliği).
- Son olarak LMS → RGB’ye dönüş yapılır ve 0–1 aralığına kliplenir.

Anomaliler (Protanomaly / Deuteranomaly) için:

- Orijinal görüntü ile ilgili tipin simülasyonu karıştırılır  
  (`sim = 0.6 * orijinal + 0.4 * tam simülasyon`),  
  böylece “tam körlük” yerine zayıflamış algı modellenir.

Monokromasi için:

- Luma tabanlı gri tonlama kullanılır:  
  \( L = 0.2126 R + 0.7152 G + 0.0722 B \)  
  ve üç kanal da \(L\) ile doldurulur.

### 2. Düzeltme (Benim için düzeltilmiş)

Temel fikir:

1. Önce ilgili tip için simülasyon üretilir.  
2. Orijinal ile simülasyon arasındaki hata matrisi hesaplanır:  
   \( \text{error} = \text{orijinal} - \text{simülasyon} \)
3. Bu hata, kayıp bilginin en çok gerektiği kanalları güçlendirmek için kullanılır:
   - Protanopia: kırmızı kanal ve bir miktar yeşil kanal güçlendirilir,
   - Deuteranopia: yeşil kanal ve bir miktar kırmızı kanal güçlendirilir,
   - Tritanopia: mavi kanal ve bir miktar yeşil kanal güçlendirilir.

Anomalilerde (kırmızı/yeşil zayıf):

- Orijinal görüntü ile ilgili tipin daltonize edilmiş hali karıştırılır  
  (örneğin `0.6 * orijinal + 0.4 * daltonize`),  
  böylece agresif olmayan ama ayırt ediciliği artıran bir düzeltme sağlanır.

---

## Uygulama akışı (sekme bazlı)

### 1. Görüntü dönüştürücü

- Sol menüden:
  - Renk körlüğü tipi seçilir (ör. *Protanopia – kırmızı-körlük*),
  - “Ben nasıl görüyorum” kutusu istenirse işaretlenir,
  - İsteğe bağlı olarak “Renk dönüşüm özetini göster” ve “Kısa rapor göster” açılır.
- Kullanıcı bir fotoğraf yükler ve **“Düzelt”** butonuna basar.
- Ekranda üçlü karşılaştırma gösterilir:
  - Orijinal,
  - Ben nasıl görüyorum? (simülasyon),
  - Benim için düzeltilmiş (daltonization).
- İstenirse:
  - Renk dönüşüm özeti maddeler halinde gösterilir,
  - Seçilen tip ve işlemlerin kısa raporu,
  - Tek sayfalık PDF (rapor + düzeltilmiş görüntü) indirilebilir.

### 2. Renk körlüğü testi (beta)

- 3 soruluk basit bir test (kırmızı/yeşil, mavi/sarı, trafik ışığı ve yazı okunabilirliği) ile:
  - Protanopia/Protanomaly,
  - Deuteranopia/Deuteranomaly,
  - Tritanopia  
  eksenlerinden hangisine daha yakın olduğunuzu yaklaşık olarak tahmin eder.

### 3. Genel bilgilendirme

- Kırmızı–yeşil–mavi bloklardan ve trafik lambasına benzeyen bir sahneden oluşan örnek görüntü:
  - Normal,
  - Protanopia / Deuteranopia / Tritanopia,
  - Protanomaly / Deuteranomaly / Monokromasi  
  için simüle edilerek yan yana gösterilir.

### 4. Canlı kamera (beta)

- `st.camera_input` ile kameradan kare yakalanır.
- Seçilen tipe göre:
  - Orijinal (kamera),
  - Ben nasıl görüyorum?,
  - Benim için düzeltilmiş  
  üçlü görünüm gösterilir.

### 5. Erişilebilirlik & palet araçları

- **Kontrast aracı**:  
  İki renk seçilerek WCAG’e benzer kontrast oranı hesaplanır.
- **Renk paleti dönüştürücü**:  
  Girilen hex kodlarıyla bir palet görseli oluşturulur ve seçilen tip için simülasyonu gösterilir.

---

## Kurulum ve çalışma

1. Proje klasörüne geç:

```bash
cd "c:\Users\Lenovo\OneDrive\Masaüstü\Görüntü İşleme\chromafix"
```

2. (Önerilen) Sanal ortam oluştur ve etkinleştir:

```bash
python -m venv .venv
.venv\Scripts\activate
```

3. Bağımlılıkları kur:

```bash
pip install -r requirements.txt
```

4. Uygulamayı çalıştır:

```bash
python -m streamlit run app.py
```

---

## Yazarlar

- [Hayri Ertan Güneş](https://github.com/H-Ertan-Gns)
- Arkadaşın (örnek): `[İsim Soyisim](https://github.com/kullanici-adi)`

Arkadaşını eklemek için yukarıdaki ikinci satırı kendi ismi ve GitHub profiliyle değiştirebilirsin.


