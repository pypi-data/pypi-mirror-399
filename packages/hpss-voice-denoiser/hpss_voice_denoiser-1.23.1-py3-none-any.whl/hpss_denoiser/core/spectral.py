"""Low-frequency spectral denoising module."""

import numpy as np
from numpy.typing import NDArray

from hpss_denoiser.core.config import DenoiserConfig


class LowFrequencyDenoiser:
    """
    Spectral subtraction denoiser targeting low frequencies.
    
    Environmental noise often has significant energy in low frequencies
    (below 350 Hz), including room rumble, HVAC noise, and distant traffic.
    This module applies frequency-dependent spectral subtraction:
    - Aggressive below 175 Hz
    - Tapering off up to 350 Hz
    - No effect above 350 Hz (preserve voice)
    
    The noise floor is estimated using a low percentile across all frames,
    which captures the minimum energy level (assumed to be noise).
    
    Reference:
        Boll, S. (1979). Suppression of Acoustic Noise in Speech
        Using Spectral Subtraction.
    
    Attributes:
        config: Denoiser configuration.
    """
    
    def __init__(self, config: DenoiserConfig) -> None:
        """
        Initialize the low-frequency denoiser.
        
        Args:
            config: Denoiser configuration.
        """
        self.config = config
        
        # Precompute frequency bins
        self._freqs = np.fft.rfftfreq(config.fft_size, 1 / config.sample_rate)
        
        # Build frequency-dependent reduction curve
        self._reduction = self._build_reduction_curve()
    
    def _build_reduction_curve(self) -> NDArray[np.floating]:
        """
        Build the frequency-dependent reduction strength curve.
        
        Returns:
            Reduction strength per frequency bin (num_bins,).
        """
        reduction = np.zeros(len(self._freqs))
        max_freq = self.config.noise_reduction_max_freq
        strength = self.config.noise_reduction_strength
        
        for i, freq in enumerate(self._freqs):
            if freq < max_freq * 0.5:
                # Full strength below half the max frequency
                reduction[i] = strength
            elif freq < max_freq:
                # Linear taper from half to max frequency
                t = (freq - max_freq * 0.5) / (max_freq * 0.5)
                reduction[i] = strength * (1 - t)
            else:
                # No reduction above max frequency
                reduction[i] = 0.0
        
        return reduction
    
    def _estimate_noise(self, magnitude: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Estimate noise floor per frequency bin.
        
        Args:
            magnitude: Magnitude spectrogram (num_frames, num_bins).
        
        Returns:
            Estimated noise floor per bin (num_bins,).
        """
        # Use low percentile as noise estimate
        noise = np.percentile(magnitude, self.config.noise_percentile, axis=0)
        
        # Smooth across frequency bins
        kernel = np.array([0.2, 0.6, 0.2])
        noise = np.convolve(noise, kernel, mode='same')
        
        return noise
    
    def compute_gains(self, magnitude: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Compute spectral subtraction gains.
        
        Args:
            magnitude: Magnitude spectrogram (num_frames, num_bins).
        
        Returns:
            Gain matrix (num_frames, num_bins).
        """
        noise = self._estimate_noise(magnitude)
        num_frames = magnitude.shape[0]
        gains = np.ones_like(magnitude)
        floor = self.config.noise_floor
        
        for i in range(num_frames):
            # Compute SNR per bin
            snr = magnitude[i] / (noise + 1e-10)
            
            # Spectral subtraction gain
            # gain = 1 - (reduction_strength / snr)
            gain = 1.0 - self._reduction / (snr + 1e-10)
            
            # Apply floor and ceiling
            gain = np.clip(gain, floor, 1.0)
            gains[i] = gain
        
        return gains
