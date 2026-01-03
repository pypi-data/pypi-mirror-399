"""Audio utility functions."""

import numpy as np
from numpy.typing import NDArray


def db_to_linear(db: float) -> float:
    """
    Convert decibels to linear amplitude.
    
    Args:
        db: Value in decibels.
    
    Returns:
        Linear amplitude.
    
    Example:
        >>> db_to_linear(0)
        1.0
        >>> db_to_linear(-6)  # doctest: +ELLIPSIS
        0.501...
        >>> db_to_linear(-20)
        0.1
    """
    return 10.0 ** (db / 20.0)


def linear_to_db(linear: float) -> float:
    """
    Convert linear amplitude to decibels.
    
    Args:
        linear: Linear amplitude (must be positive).
    
    Returns:
        Value in decibels. Returns -120 dB for zero or negative input.
    
    Example:
        >>> linear_to_db(1.0)
        0.0
        >>> linear_to_db(0.1)
        -20.0
        >>> linear_to_db(0)
        -120.0
    """
    if linear <= 0:
        return -120.0
    return 20.0 * np.log10(linear)


def pcm16_to_float(pcm_data: bytes) -> NDArray[np.float64]:
    """
    Convert 16-bit PCM data to float64 array.
    
    Args:
        pcm_data: Raw PCM bytes (16-bit signed integer, little-endian).
    
    Returns:
        Float64 array with values in range [-1.0, 1.0].
    
    Example:
        >>> pcm = b'\\x00\\x00'  # silence
        >>> pcm16_to_float(pcm)
        array([0.])
        >>> pcm = b'\\xff\\x7f'  # max positive
        >>> pcm16_to_float(pcm)[0]  # doctest: +ELLIPSIS
        0.999...
    """
    return np.frombuffer(pcm_data, dtype=np.int16).astype(np.float64) / 32768.0


def float_to_pcm16(audio: NDArray[np.floating]) -> bytes:
    """
    Convert float array to 16-bit PCM data.
    
    Args:
        audio: Float array with values in range [-1.0, 1.0].
    
    Returns:
        Raw PCM bytes (16-bit signed integer, little-endian).
    
    Example:
        >>> audio_arr = np.array([0.0])
        >>> float_to_pcm16(audio_arr)
        b'\\x00\\x00'
    """
    # Clip to valid range and scale
    clipped = np.clip(audio, -1.0, 1.0)
    scaled = np.round(clipped * 32767).astype(np.int16)
    return scaled.tobytes()


def compute_rms(audio: NDArray[np.floating]) -> float:
    """
    Compute RMS (Root Mean Square) level.
    
    Args:
        audio: Audio samples.
    
    Returns:
        RMS level.
    
    Example:
        >>> audio_arr = np.array([1.0, -1.0, 1.0, -1.0])
        >>> compute_rms(audio_arr)
        1.0
    """
    return float(np.sqrt(np.mean(audio ** 2)))


def compute_rms_db(audio: NDArray[np.floating]) -> float:
    """
    Compute RMS level in decibels.
    
    Args:
        audio: Audio samples.
    
    Returns:
        RMS level in dB.
    """
    return linear_to_db(compute_rms(audio))


def normalize_rms(
    audio: NDArray[np.floating],
    target_db: float = -20.0
) -> NDArray[np.floating]:
    """
    Normalize audio to target RMS level.
    
    Args:
        audio: Input audio.
        target_db: Target RMS level in dB.
    
    Returns:
        Normalized audio.
    """
    current_rms = compute_rms(audio)
    
    if current_rms < 1e-10:
        return audio.copy()
    
    target_rms = db_to_linear(target_db)
    gain = target_rms / current_rms
    
    # Limit gain to avoid amplifying noise too much
    gain = min(gain, 10.0)  # Max +20 dB
    gain = max(gain, 0.1)   # Max -20 dB
    
    return audio * gain
