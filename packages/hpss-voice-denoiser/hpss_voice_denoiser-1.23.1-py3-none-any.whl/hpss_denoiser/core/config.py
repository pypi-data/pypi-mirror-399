"""Configuration for the HPSS voice denoiser."""

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class DenoiserConfig:
    """
    Configuration for the HPSS voice denoiser.
    
    This configuration has been optimized for ASR preprocessing tasks
    including Speech-to-Text, Speaker Diarization, and Voice Embedding.
    
    Attributes:
        sample_rate: Audio sample rate in Hz. Default 16000 (standard for ASR).
        frame_size_ms: STFT frame size in milliseconds.
        hop_size_ms: STFT hop size in milliseconds.
        harmonic_kernel: Median filter kernel size for harmonic separation.
            Smaller values reduce echo but may affect separation quality.
        percussive_kernel: Median filter kernel size for percussive separation.
        hpss_margin: Separation margin. Higher values create harder separation.
        context_window: Number of frames to extend voice context.
            Helps preserve consonants at word boundaries.
        harmonic_threshold_db: Threshold for voice activity detection (relative dB).
        mix_smooth_frames: Smoothing window for percussive gain transitions.
        voice_context_perc_gain: Percussive gain when voice is detected (0.0-1.0).
            Higher values preserve more consonants but also more noise.
        no_context_perc_gain: Percussive gain during silence (0.0-1.0).
            Lower values provide more aggressive noise suppression.
        envelope_tightening: Enable envelope tightening to reduce HPSS echo.
        envelope_attack_frames: Attack time for envelope follower.
        envelope_release_frames: Release time for envelope follower.
        envelope_min_gain: Minimum gain for envelope tightening.
        tightening_threshold_db: Threshold below which tightening is not applied.
        onset_ratio: Energy ratio threshold for onset detection.
        onset_protection_frames: Frames to protect around detected onsets.
        noise_reduction_strength: Spectral subtraction strength for low frequencies.
        noise_percentile: Percentile for noise floor estimation.
        noise_floor: Minimum gain floor for spectral subtraction.
        noise_reduction_max_freq: Maximum frequency for low-freq denoising.
        fade_ms: Fade in/out duration in milliseconds.
    
    Example:
        >>> config = DenoiserConfig(
        ...     sample_rate=16000,
        ...     voice_context_perc_gain=0.25,  # More consonants
        ... )
        >>> denoiser = HPSSDenoiser(config)
    """
    
    # ===========================================
    # AUDIO PARAMETERS
    # ===========================================
    sample_rate: int = 16000
    
    # ===========================================
    # STFT PARAMETERS
    # ===========================================
    frame_size_ms: int = 25
    hop_size_ms: int = 6
    
    # ===========================================
    # HPSS PARAMETERS
    # ===========================================
    harmonic_kernel: int = 9
    percussive_kernel: int = 9
    hpss_margin: float = 2.5
    
    # ===========================================
    # CONTEXT-BASED MIXING
    # ===========================================
    context_window: int = 10
    harmonic_threshold_db: float = -20.0
    mix_smooth_frames: int = 3
    voice_context_perc_gain: float = 0.20
    no_context_perc_gain: float = 0.04
    
    # ===========================================
    # ENVELOPE TIGHTENING
    # ===========================================
    envelope_tightening: bool = True
    envelope_attack_frames: int = 2
    envelope_release_frames: int = 3
    envelope_min_gain: float = 0.15
    tightening_threshold_db: float = -35.0
    onset_ratio: float = 1.5
    onset_protection_frames: int = 2
    
    # ===========================================
    # LOW-FREQUENCY NOISE REDUCTION
    # ===========================================
    noise_reduction_strength: float = 0.8
    noise_percentile: float = 10.0
    noise_floor: float = 0.12
    noise_reduction_max_freq: float = 350.0
    
    # ===========================================
    # OUTPUT
    # ===========================================
    fade_ms: float = 5.0
    
    @property
    def frame_size(self) -> int:
        """Frame size in samples."""
        return int(self.sample_rate * self.frame_size_ms / 1000)
    
    @property
    def hop_size(self) -> int:
        """Hop size in samples."""
        return int(self.sample_rate * self.hop_size_ms / 1000)
    
    @property
    def fft_size(self) -> int:
        """FFT size (next power of 2 >= frame_size)."""
        return 2 ** int(np.ceil(np.log2(self.frame_size)))
    
    @property
    def fade_samples(self) -> int:
        """Fade duration in samples."""
        return int(self.sample_rate * self.fade_ms / 1000)
    
    @property
    def num_fft_bins(self) -> int:
        """Number of FFT bins (fft_size // 2 + 1)."""
        return self.fft_size // 2 + 1
    
    def validate(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If any parameter is invalid.
        """
        if self.sample_rate <= 0:
            raise ValueError(f"sample_rate must be positive, got {self.sample_rate}")
        
        if self.frame_size_ms <= 0:
            raise ValueError(f"frame_size_ms must be positive, got {self.frame_size_ms}")
        
        if self.hop_size_ms <= 0:
            raise ValueError(f"hop_size_ms must be positive, got {self.hop_size_ms}")
        
        if self.hop_size_ms > self.frame_size_ms:
            raise ValueError(
                f"hop_size_ms ({self.hop_size_ms}) must be <= frame_size_ms ({self.frame_size_ms})"
            )
        
        if self.harmonic_kernel < 1 or self.harmonic_kernel % 2 == 0:
            raise ValueError(f"harmonic_kernel must be odd and >= 1, got {self.harmonic_kernel}")
        
        if self.percussive_kernel < 1 or self.percussive_kernel % 2 == 0:
            raise ValueError(f"percussive_kernel must be odd and >= 1, got {self.percussive_kernel}")
        
        if self.hpss_margin <= 0:
            raise ValueError(f"hpss_margin must be positive, got {self.hpss_margin}")
        
        if not 0 <= self.voice_context_perc_gain <= 1:
            raise ValueError(
                f"voice_context_perc_gain must be in [0, 1], got {self.voice_context_perc_gain}"
            )
        
        if not 0 <= self.no_context_perc_gain <= 1:
            raise ValueError(
                f"no_context_perc_gain must be in [0, 1], got {self.no_context_perc_gain}"
            )
        
        if not 0 <= self.noise_floor <= 1:
            raise ValueError(f"noise_floor must be in [0, 1], got {self.noise_floor}")


# Preset configurations for common use cases
PRESET_DEFAULT = DenoiserConfig()

PRESET_AGGRESSIVE = DenoiserConfig(
    no_context_perc_gain=0.02,
    noise_reduction_strength=0.9,
    envelope_min_gain=0.10,
)

PRESET_GENTLE = DenoiserConfig(
    voice_context_perc_gain=0.30,
    no_context_perc_gain=0.08,
    noise_reduction_strength=0.6,
)

PRESET_STREAMING = DenoiserConfig(
    frame_size_ms=20,
    hop_size_ms=5,
    context_window=8,
)
