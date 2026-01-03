"""
HPSS Voice Denoiser - Production-ready audio denoising for ASR preprocessing.

A Harmonic-Percussive Source Separation (HPSS) based denoiser optimized for
Speech-to-Text, Speaker Diarization, and Voice Embedding applications.

Example:
    >>> from hpss_denoiser import HPSSDenoiser
    >>> denoiser = HPSSDenoiser()
    >>> cleaned_pcm = denoiser.process(noisy_pcm)

"""

from hpss_denoiser.core.config import DenoiserConfig
from hpss_denoiser.core.pipeline import HPSSDenoiser
from hpss_denoiser.utils.audio import (
    pcm16_to_float,
    float_to_pcm16,
    db_to_linear,
    linear_to_db,
)

__version__ = "1.23.1"
__author__ = "Atomys"
__email__ = "contact@atomys.io"

__all__ = [
    # Main API
    "HPSSDenoiser",
    "DenoiserConfig",
    # Utilities
    "pcm16_to_float",
    "float_to_pcm16",
    "db_to_linear",
    "linear_to_db",
    # Metadata
    "__version__",
]
