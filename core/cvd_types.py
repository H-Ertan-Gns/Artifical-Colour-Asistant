from __future__ import annotations

from enum import Enum, auto


class CVDType(Enum):
    PROTANOPIA = auto()
    DEUTERANOPIA = auto()
    TRITANOPIA = auto()
    PROTANOMALY = auto()
    DEUTERANOMALY = auto()
    MONOCHROMASY = auto()


def from_label(label: str) -> CVDType:
    mapping = {
        "Protanopia (kırmızı-körlük)": CVDType.PROTANOPIA,
        "Deuteranopia (yeşil-körlük)": CVDType.DEUTERANOPIA,
        "Tritanopia (mavi-körlük)": CVDType.TRITANOPIA,
        "Protanomaly (kırmızı zayıf)": CVDType.PROTANOMALY,
        "Deuteranomaly (yeşil zayıf)": CVDType.DEUTERANOMALY,
        "Monokromasi (tam renk körlüğü)": CVDType.MONOCHROMASY,
    }
    return mapping[label]


def info_for_type(cvd_type: CVDType) -> str:
    """
    Her renk körlüğü tipi için kısa bilgilendirme metni döner.
    """
    texts = {
        CVDType.PROTANOPIA: (
            "Protanopia (kırmızı-körlük): Kırmızı tonları büyük ölçüde kaybolur, kırmızı alanlar "
            "daha çok koyu yeşil / kahverengi gibi algılanır. Düzeltme sırasında kırmızı-kanal "
            "bilgisi diğer kanallardan tahmin edilerek güçlendirilir."
        ),
        CVDType.DEUTERANOPIA: (
            "Deuteranopia (yeşil-körlük): Yeşil tonları seçmek zorlaşır, kırmızı ve yeşil birbirine "
            "yakın görünür. Düzeltme, yeşil-kanaldaki kayıp bilgiyi telafi etmeye odaklanır."
        ),
        CVDType.TRITANOPIA: (
            "Tritanopia (mavi-körlük): Mavi ve sarı tonları karışabilir, mavi daha soluk ve "
            "yeşilimsi algılanır. Düzeltme, özellikle mavi-kanalı yeniden dağıtır."
        ),
        CVDType.PROTANOMALY: (
            "Protanomaly (kırmızı zayıf): Kırmızı algısı tamamen kaybolmamıştır ama zayıftır. "
            "Düzeltme, kırmızı-kanalı normalden daha fazla güçlendirerek kontrastı artırır."
        ),
        CVDType.DEUTERANOMALY: (
            "Deuteranomaly (yeşil zayıf): En yaygın renk körlüğü tipidir; yeşil algısı zayıftır. "
            "Düzeltme, yeşil-kanalı güçlendirip kırmızı/yeşil ayrımını netleştirir."
        ),
        CVDType.MONOCHROMASY: (
            "Monokromasi (tam renk körlüğü): Renkler neredeyse tamamen gri tonlar olarak algılanır. "
            "Uygulama, parlaklık bilgisini koruyarak daha okunaklı bir gri-ton görüntü üretir."
        ),
    }
    return texts.get(cvd_type, "")

