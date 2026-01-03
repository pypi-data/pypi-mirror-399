"""Harmonic-Percussive Source Separation (HPSS) module."""

from typing import Tuple

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import median_filter

from hpss_denoiser.core.config import DenoiserConfig


class HPSSSeparator:
    """
    Harmonic-Percussive Source Separation using median filtering.
    
    HPSS separates an audio signal into two components:
    - Harmonic: Sustained tonal content (voice fundamentals, vowels)
    - Percussive: Transient content (consonants, noise bursts)
    
    The separation is based on the observation that:
    - Harmonic content appears as horizontal lines in the spectrogram
    - Percussive content appears as vertical lines in the spectrogram
    
    Median filtering along time (horizontal) enhances harmonic content,
    while filtering along frequency (vertical) enhances percussive content.
    
    Reference:
        Fitzgerald, D. (2010). Harmonic/Percussive Separation using Median Filtering.
    
    Attributes:
        config: Denoiser configuration.
    """
    
    def __init__(self, config: DenoiserConfig) -> None:
        """
        Initialize the HPSS separator.
        
        Args:
            config: Denoiser configuration.
        """
        self.config = config
    
    def separate(
        self,
        magnitude: NDArray[np.floating]
    ) -> Tuple[NDArray[np.floating], NDArray[np.floating]]:
        """
        Separate magnitude spectrogram into harmonic and percussive components.
        
        Args:
            magnitude: Magnitude spectrogram of shape (num_frames, num_bins).
        
        Returns:
            Tuple of (harmonic_magnitude, percussive_magnitude), each with
            the same shape as the input.
        """
        # Work with power spectrogram for better separation
        power = magnitude ** 2
        
        # Median filter along time axis (harmonic enhancement)
        # Kernel shape: (time, freq) = (kernel_size, 1)
        harmonic_enhanced = median_filter(
            power,
            size=(self.config.harmonic_kernel, 1),
            mode='reflect'
        )
        
        # Median filter along frequency axis (percussive enhancement)
        # Kernel shape: (time, freq) = (1, kernel_size)
        percussive_enhanced = median_filter(
            power,
            size=(1, self.config.percussive_kernel),
            mode='reflect'
        )
        
        # Compute soft masks using margin-based weighting
        margin = self.config.hpss_margin
        
        h_weight = harmonic_enhanced ** margin
        p_weight = percussive_enhanced ** margin
        total = h_weight + p_weight + 1e-10
        
        harmonic_mask = h_weight / total
        percussive_mask = p_weight / total
        
        # Apply masks to magnitude (not power)
        # Use sqrt because we computed masks on power
        harmonic_mag = magnitude * np.sqrt(harmonic_mask)
        percussive_mag = magnitude * np.sqrt(percussive_mask)
        
        return harmonic_mag, percussive_mag
