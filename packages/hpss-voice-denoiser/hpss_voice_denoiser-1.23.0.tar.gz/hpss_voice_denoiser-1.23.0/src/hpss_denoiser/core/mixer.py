"""Context-based percussive mixing module."""

from typing import Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import maximum_filter1d, uniform_filter1d

from hpss_denoiser.core.config import DenoiserConfig


class ContextMixer:
    """
    Context-based mixer for harmonic and percussive components.
    
    This mixer addresses a key challenge with HPSS for voice: consonants
    (like 't', 's', 'k', 'p') are classified as percussive because they
    are transient in nature. Simply removing the percussive component
    would make speech unintelligible.
    
    The solution is to detect voice activity using harmonic energy and
    mix the percussive component accordingly:
    - During speech: include more percussive (preserve consonants)
    - During silence: suppress percussive (remove noise transients)
    
    Attributes:
        config: Denoiser configuration.
    """
    
    def __init__(self, config: DenoiserConfig) -> None:
        """
        Initialize the context mixer.
        
        Args:
            config: Denoiser configuration.
        """
        self.config = config
        
        # Precompute frequency bins for voice band detection
        self._freqs = np.fft.rfftfreq(config.fft_size, 1 / config.sample_rate)
        self._voice_band_mask = (self._freqs >= 200) & (self._freqs <= 4000)
    
    def _compute_voice_context(
        self,
        harmonic_mag: NDArray[np.floating]
    ) -> NDArray[np.floating]:
        """
        Compute voice activity context from harmonic component.
        
        Args:
            harmonic_mag: Harmonic magnitude spectrogram (num_frames, num_bins).
        
        Returns:
            Voice context array (num_frames,) with values in [0, 1].
            1 = voice present, 0 = silence.
        """
        # Sum energy in voice frequency band (200-4000 Hz)
        voice_energy = np.sum(harmonic_mag[:, self._voice_band_mask] ** 2, axis=1)
        
        # Convert to dB relative to maximum
        max_energy = np.max(voice_energy) + 1e-10
        energy_db = 10 * np.log10(voice_energy / max_energy + 1e-10)
        
        # Threshold to binary voice detection
        threshold = self.config.harmonic_threshold_db
        voice_present = (energy_db > threshold).astype(np.float64)
        
        # Extend voice regions to include surrounding frames
        # This helps preserve consonants at word boundaries
        context_window = self.config.context_window
        extended = maximum_filter1d(voice_present, size=context_window * 2 + 1)
        
        # Smooth transitions
        extended = uniform_filter1d(extended, size=self.config.mix_smooth_frames)
        
        return np.clip(extended, 0.0, 1.0)
    
    def compute_percussive_gain(
        self,
        harmonic_mag: NDArray[np.floating],
        _percussive_mag: NDArray[np.floating]
    ) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
        """
        Compute per-frame gain for percussive component.
        
        Args:
            harmonic_mag: Harmonic magnitude spectrogram.
            _percussive_mag: Percussive magnitude spectrogram (unused, for API consistency).
        
        Returns:
            Tuple of (percussive_gain, voice_context):
            - percussive_gain: Per-frame gain (num_frames,)
            - voice_context: Voice activity (num_frames,), for debugging
        """
        voice_context = self._compute_voice_context(harmonic_mag)
        
        # Interpolate between voice and silence gains
        voice_gain = self.config.voice_context_perc_gain
        silence_gain = self.config.no_context_perc_gain
        
        gain = voice_context * voice_gain + (1 - voice_context) * silence_gain
        
        return gain, voice_context
