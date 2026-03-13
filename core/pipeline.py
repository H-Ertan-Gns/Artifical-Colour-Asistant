from __future__ import annotations

from typing import Optional

import numpy as np
from PIL import Image

from .cvd_types import CVDType


def _to_float_rgb(image: Image.Image) -> np.ndarray:
    arr = np.asarray(image).astype("float32") / 255.0
    return np.clip(arr, 0.0, 1.0)


def _from_float_rgb(arr: np.ndarray) -> Image.Image:
    arr_u8 = np.clip(arr * 255.0, 0, 255).astype("uint8")
    return Image.fromarray(arr_u8)


def _simulate_protanopia(rgb: np.ndarray) -> np.ndarray:
    """
    Basit LMS tabanlı Protanopia simülasyonu (sadece L konisinin yokluğu).
    Literatürdeki Brettel/Viénot matrislerinin sadeleştirilmiş bir versiyonudur.
    """
    # sRGB -> LMS yaklaşık dönüşüm
    M_RGB2LMS = np.array(
        [
            [0.31399022, 0.63951294, 0.04649755],
            [0.15537241, 0.75789446, 0.08670142],
            [0.01775239, 0.10944209, 0.87256922],
        ],
        dtype=np.float32,
    )
    M_LMS2RGB = np.linalg.inv(M_RGB2LMS).astype(np.float32)

    flat = rgb.reshape(-1, 3)
    lms = flat @ M_RGB2LMS.T

    L, M, S = lms[:, 0], lms[:, 1], lms[:, 2]

    # Protanopia: L kanalı, M ve S kanallarından tahmin edilir
    L_sim = 0.0 * L + 1.05118294 * M - 0.05116099 * S

    lms_sim = np.stack([L_sim, M, S], axis=1)
    rgb_sim = lms_sim @ M_LMS2RGB.T

    rgb_sim = rgb_sim.reshape(rgb.shape)
    return np.clip(rgb_sim, 0.0, 1.0)


def _simulate_deuteranopia(rgb: np.ndarray) -> np.ndarray:
    M_RGB2LMS = np.array(
        [
            [0.31399022, 0.63951294, 0.04649755],
            [0.15537241, 0.75789446, 0.08670142],
            [0.01775239, 0.10944209, 0.87256922],
        ],
        dtype=np.float32,
    )
    M_LMS2RGB = np.linalg.inv(M_RGB2LMS).astype(np.float32)

    flat = rgb.reshape(-1, 3)
    lms = flat @ M_RGB2LMS.T

    L, M, S = lms[:, 0], lms[:, 1], lms[:, 2]

    M_sim = 0.0 * M + 0.9513092 * L + 0.04866992 * S

    lms_sim = np.stack([L, M_sim, S], axis=1)
    rgb_sim = lms_sim @ M_LMS2RGB.T
    rgb_sim = rgb_sim.reshape(rgb.shape)
    return np.clip(rgb_sim, 0.0, 1.0)


def _simulate_tritanopia(rgb: np.ndarray) -> np.ndarray:
    M_RGB2LMS = np.array(
        [
            [0.31399022, 0.63951294, 0.04649755],
            [0.15537241, 0.75789446, 0.08670142],
            [0.01775239, 0.10944209, 0.87256922],
        ],
        dtype=np.float32,
    )
    M_LMS2RGB = np.linalg.inv(M_RGB2LMS).astype(np.float32)

    flat = rgb.reshape(-1, 3)
    lms = flat @ M_RGB2LMS.T

    L, M, S = lms[:, 0], lms[:, 1], lms[:, 2]

    S_sim = 0.0 * S + 0.86744736 * L + 0.13255264 * M

    lms_sim = np.stack([L, M, S_sim], axis=1)
    rgb_sim = lms_sim @ M_LMS2RGB.T
    rgb_sim = rgb_sim.reshape(rgb.shape)
    return np.clip(rgb_sim, 0.0, 1.0)


def _daltonize_protanopia(rgb: np.ndarray) -> np.ndarray:
    """
    Protanopia için basit daltonization:
    1. Protanopia simülasyonu üret.
    2. Orijinal - simülasyon hatasını hesapla.
    3. Bu hatayı özellikle kırmızı kanal üzerinde güçlendirerek geri ekle.
    """
    sim = _simulate_protanopia(rgb)
    error = rgb - sim

    # Kırmızı kanal vurgusu: hatayı R kanalına daha çok yansıt
    corrected = rgb.copy()
    corrected[..., 0] = corrected[..., 0] + 1.0 * error[..., 0]
    corrected[..., 1] = corrected[..., 1] + 0.4 * error[..., 0]

    return np.clip(corrected, 0.0, 1.0)


def _daltonize_deuteranopia(rgb: np.ndarray) -> np.ndarray:
    sim = _simulate_deuteranopia(rgb)
    error = rgb - sim

    corrected = rgb.copy()
    corrected[..., 1] = corrected[..., 1] + 1.0 * error[..., 1]
    corrected[..., 0] = corrected[..., 0] + 0.4 * error[..., 1]

    return np.clip(corrected, 0.0, 1.0)


def _daltonize_tritanopia(rgb: np.ndarray) -> np.ndarray:
    sim = _simulate_tritanopia(rgb)
    error = rgb - sim

    corrected = rgb.copy()
    corrected[..., 2] = corrected[..., 2] + 1.0 * error[..., 2]
    corrected[..., 1] = corrected[..., 1] + 0.3 * error[..., 2]

    return np.clip(corrected, 0.0, 1.0)


def apply_cvd_correction(image: Image.Image, cvd_type: CVDType) -> Image.Image:
    """
    Kullanıcının seçtiği CVD tipine göre düzeltme uygular.
    """
    rgb = _to_float_rgb(image)

    if cvd_type == CVDType.PROTANOPIA:
        corrected = _daltonize_protanopia(rgb)
    elif cvd_type == CVDType.DEUTERANOPIA:
        corrected = _daltonize_deuteranopia(rgb)
    elif cvd_type == CVDType.TRITANOPIA:
        corrected = _daltonize_tritanopia(rgb)
    elif cvd_type == CVDType.PROTANOMALY:
        corrected = 0.6 * rgb + 0.4 * _daltonize_protanopia(rgb)
    elif cvd_type == CVDType.DEUTERANOMALY:
        corrected = 0.6 * rgb + 0.4 * _daltonize_deuteranopia(rgb)
    elif cvd_type == CVDType.MONOCHROMASY:
        # Luma tabanlı gri tonlama
        luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        corrected = np.stack([luma, luma, luma], axis=-1)
    else:
        corrected = rgb

    return _from_float_rgb(corrected)


def apply_cvd_simulation(image: Image.Image, cvd_type: CVDType) -> Optional[Image.Image]:
    """
    Renk körlüğü simülasyonu.
    """
    rgb = _to_float_rgb(image)

    if cvd_type == CVDType.PROTANOPIA:
        sim = _simulate_protanopia(rgb)
    elif cvd_type == CVDType.DEUTERANOPIA:
        sim = _simulate_deuteranopia(rgb)
    elif cvd_type == CVDType.TRITANOPIA:
        sim = _simulate_tritanopia(rgb)
    elif cvd_type == CVDType.PROTANOMALY:
        sim = 0.6 * rgb + 0.4 * _simulate_protanopia(rgb)
    elif cvd_type == CVDType.DEUTERANOMALY:
        sim = 0.6 * rgb + 0.4 * _simulate_deuteranopia(rgb)
    elif cvd_type == CVDType.MONOCHROMASY:
        luma = 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]
        sim = np.stack([luma, luma, luma], axis=-1)
    else:
        return None

    return _from_float_rgb(sim)


