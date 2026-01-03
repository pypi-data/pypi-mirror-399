"""Envelope tightening module to reduce HPSS echo artifacts."""

import numpy as np
from numpy.typing import NDArray
from scipy.ndimage import maximum_filter1d, uniform_filter1d

from hpss_denoiser.core.config import DenoiserConfig


class EnvelopeTightener:
    """
    Tighten the harmonic component's envelope to reduce echo artifacts.
    
    HPSS median filtering can cause temporal "smearing" of energy, resulting
    in echo-like artifacts where energy lingers after transients. This module
    addresses this by applying an asymmetric envelope follower that:
    - Follows energy increases quickly (fast attack)
    - Decays energy more quickly than the smeared HPSS output (controlled release)
    
    The result is a cleaner harmonic component with tighter transients.
    
    Attributes:
        config: Denoiser configuration.
    """
    
    def __init__(self, config: DenoiserConfig) -> None:
        """
        Initialize the envelope tightener.
        
        Args:
            config: Denoiser configuration.
        """
        self.config = config

    @staticmethod
    def _compute_frame_energy(magnitude: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Compute total energy per frame.

        Args:
            magnitude: Magnitude spectrogram (num_frames, num_bins).

        Returns:
            Energy per frame (num_frames,).
        """
        return np.sum(magnitude ** 2, axis=1)

    def _detect_onsets(self, energy: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Detect energy onsets (sudden increases).
        
        Args:
            energy: Per-frame energy.
        
        Returns:
            Binary onset mask with protection zone extended.
        """
        num_frames = len(energy)
        onsets = np.zeros(num_frames)
        
        ratio_threshold = self.config.onset_ratio
        
        for i in range(1, num_frames):
            ratio = energy[i] / (energy[i - 1] + 1e-10)
            if ratio > ratio_threshold:
                onsets[i] = 1.0
        
        # Extend protection around onsets
        protect = self.config.onset_protection_frames
        if protect > 0:
            onsets = maximum_filter1d(onsets, size=protect * 2 + 1)
        
        return onsets
    
    def _compute_target_envelope(
        self,
        energy: NDArray[np.floating],
        onsets: NDArray[np.floating]
    ) -> NDArray[np.floating]:
        """
        Compute target envelope using asymmetric follower.
        
        Args:
            energy: Per-frame energy.
            onsets: Binary onset mask.
        
        Returns:
            Target envelope (num_frames,).
        """
        num_frames = len(energy)
        target = np.zeros(num_frames)
        
        # Compute filter coefficients
        attack_frames = self.config.envelope_attack_frames
        release_frames = self.config.envelope_release_frames
        
        attack_coef = 1.0 - np.exp(-2.0 / max(1, attack_frames))
        release_coef = 1.0 - np.exp(-2.0 / max(1, release_frames))
        
        # Initialize
        current = energy[0] if len(energy) > 0 else 0.0
        target[0] = current
        
        # Process frames
        for i in range(1, num_frames):
            if onsets[i] > 0.5 or energy[i] > current:
                # Attack: fast rise (or onset protection)
                current = attack_coef * energy[i] + (1 - attack_coef) * current
            else:
                # Release: controlled decay
                decay_target = current * (1 - release_coef)
                current = max(energy[i], decay_target)
            
            target[i] = current
        
        return target
    
    def process(self, harmonic_mag: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Compute tightening gains for harmonic component.
        
        Args:
            harmonic_mag: Harmonic magnitude spectrogram (num_frames, num_bins).
        
        Returns:
            Per-frame tightening gains (num_frames,).
        """
        if not self.config.envelope_tightening:
            return np.ones(harmonic_mag.shape[0])
        
        # Compute energy envelope
        energy = self._compute_frame_energy(harmonic_mag)
        
        # Only process frames above noise floor
        max_energy = np.max(energy) + 1e-10
        energy_db = 10 * np.log10(energy / max_energy + 1e-10)
        threshold_db = self.config.tightening_threshold_db
        
        # Detect onsets for protection
        onsets = self._detect_onsets(energy)
        
        # Compute target envelope
        target = self._compute_target_envelope(energy, onsets)
        
        # Compute gains
        gains = np.ones(len(energy))
        active = energy_db > threshold_db
        
        gains[active] = target[active] / (energy[active] + 1e-10)
        gains = np.clip(gains, self.config.envelope_min_gain, 1.0)
        
        # Smooth gains
        gains = uniform_filter1d(gains, size=2)
        
        return gains
