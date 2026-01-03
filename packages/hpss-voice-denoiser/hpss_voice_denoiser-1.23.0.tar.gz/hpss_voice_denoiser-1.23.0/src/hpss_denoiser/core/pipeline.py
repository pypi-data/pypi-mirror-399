"""Main HPSS voice denoiser pipeline."""

from typing import Dict, Optional, Any

import numpy as np
from numpy.typing import NDArray
from scipy import signal as scipy_signal

from hpss_denoiser.core.config import DenoiserConfig
from hpss_denoiser.core.hpss import HPSSSeparator
from hpss_denoiser.core.mixer import ContextMixer
from hpss_denoiser.core.envelope import EnvelopeTightener
from hpss_denoiser.core.spectral import LowFrequencyDenoiser
from hpss_denoiser.utils.audio import pcm16_to_float, float_to_pcm16


class HPSSDenoiser:
    """
    HPSS-based voice denoiser optimized for ASR preprocessing.
    
    This denoiser uses Harmonic-Percussive Source Separation (HPSS) with
    context-aware mixing to preserve voice quality while removing
    environmental noise.
    
    Key features:
    - Preserves consonants (t, s, k, p, etc.) through context-aware mixing
    - Reduces low-frequency noise through spectral subtraction
    - Removes HPSS echo artifacts through envelope tightening
    - Stateless processing: each chunk is processed independently
    
    Pipeline:
    1. High-pass filter (80 Hz) - remove DC and rumble
    2. STFT analysis
    3. HPSS separation - split into harmonic and percussive
    4. Envelope tightening - reduce echo in harmonic component
    5. Context mixing - intelligently mix percussive based on voice activity
    6. Spectral denoising - reduce low-frequency noise
    7. ISTFT synthesis
    8. Fade in/out - smooth edges
    
    Example:
        >>> from hpss_denoiser import HPSSDenoiser
        >>> 
        >>> # Create denoiser
        >>> denoiser = HPSSDenoiser()
        >>> 
        >>> # Process PCM data
        >>> with open("input.pcm", "rb") as f:
        ...     pcm_data = f.read()
        >>> cleaned_pcm = denoiser.process(pcm_data)
        >>> 
        >>> # Or process numpy array
        >>> audio = np.random.randn(16000) * 0.1
        >>> cleaned_array = denoiser.process_array(audio)
    
    Attributes:
        config: Denoiser configuration.
    """
    
    def __init__(self, config: Optional[DenoiserConfig] = None) -> None:
        """
        Initialize the HPSS denoiser.
        
        Args:
            config: Denoiser configuration. If None, uses default settings.
        
        Raises:
            ValueError: If configuration is invalid.
        """
        self.config = config or DenoiserConfig()
        self.config.validate()
        
        # Initialize analysis window
        self._window = np.hanning(self.config.frame_size).astype(np.float64)
        
        # Initialize processing components
        self._hpss = HPSSSeparator(self.config)
        self._tightener = EnvelopeTightener(self.config)
        self._mixer = ContextMixer(self.config)
        self._denoiser = LowFrequencyDenoiser(self.config)
        
        # Initialize high-pass filter (80 Hz cutoff)
        nyquist = self.config.sample_rate / 2
        # noinspection PyTupleAssignmentBalance
        self._hp_b, self._hp_a = scipy_signal.butter(3, 80 / nyquist, btype='high')
    
    def _stft(self, audio: NDArray[np.floating]) -> tuple:
        """
        Compute Short-Time Fourier Transform.
        
        Args:
            audio: Input audio samples.
        
        Returns:
            Tuple of (spectrogram, total_padded_length, padding_amount).
        """
        frame_size = self.config.frame_size
        hop_size = self.config.hop_size
        fft_size = self.config.fft_size
        
        # Pad audio for edge handling
        pad = frame_size
        audio_padded = np.concatenate([np.zeros(pad), audio, np.zeros(pad)])
        
        # Compute number of frames
        num_frames = (len(audio_padded) - frame_size) // hop_size + 1
        
        # Allocate spectrogram
        spec = np.zeros((num_frames, fft_size // 2 + 1), dtype=np.complex128)
        
        # Compute STFT
        for i in range(num_frames):
            start = i * hop_size
            frame = audio_padded[start:start + frame_size] * self._window
            
            # Zero-pad to FFT size
            padded_frame = np.zeros(fft_size)
            padded_frame[:frame_size] = frame
            
            spec[i] = np.fft.rfft(padded_frame)
        
        return spec, len(audio_padded), pad
    
    def _istft(
        self,
        spec: NDArray[np.complexfloating],
        total_len: int,
        pad: int,
        orig_len: int
    ) -> NDArray[np.floating]:
        """
        Compute Inverse Short-Time Fourier Transform.
        
        Args:
            spec: Complex spectrogram.
            total_len: Total padded length.
            pad: Padding amount.
            orig_len: Original audio length.
        
        Returns:
            Reconstructed audio samples.
        """
        num_frames = spec.shape[0]
        frame_size = self.config.frame_size
        hop_size = self.config.hop_size
        fft_size = self.config.fft_size
        
        # Allocate output with overlap-add buffers
        output = np.zeros(total_len)
        window_sum = np.zeros(total_len)
        
        # Overlap-add synthesis
        for i in range(num_frames):
            frame = np.fft.irfft(spec[i], fft_size)[:frame_size]
            start = i * hop_size
            
            output[start:start + frame_size] += frame * self._window
            window_sum[start:start + frame_size] += self._window ** 2
        
        # Normalize by window sum
        window_sum = np.maximum(window_sum, 1e-8)
        output /= window_sum
        
        # Remove padding and return original length
        return output[pad:pad + orig_len]
    
    def _apply_fades(self, audio: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Apply fade in/out to avoid edge clicks.
        
        Args:
            audio: Input audio.
        
        Returns:
            Audio with fades applied.
        """
        fade = self.config.fade_samples
        
        if len(audio) < fade * 2:
            return audio
        
        output = audio.copy()
        
        # Quadratic fade curve
        curve = np.linspace(0, 1, fade) ** 2
        
        output[:fade] *= curve
        output[-fade:] *= curve[::-1]
        
        return output
    
    def process_array(self, audio: NDArray[np.floating]) -> NDArray[np.floating]:
        """
        Process audio as numpy array.
        
        Args:
            audio: Input audio samples (float64, range [-1, 1]).
        
        Returns:
            Denoised audio samples.
        """
        if len(audio) == 0:
            return audio.copy()
        
        # Ensure float64
        audio = audio.astype(np.float64)
        
        # High-pass filter
        audio = scipy_signal.filtfilt(self._hp_b, self._hp_a, audio)
        
        orig_len = len(audio)
        
        # STFT analysis
        spec, total_len, pad = self._stft(audio)
        magnitude = np.abs(spec)
        phase = np.angle(spec)
        
        # HPSS separation
        harmonic_mag, percussive_mag = self._hpss.separate(magnitude)
        
        # Envelope tightening
        tighten_gains = self._tightener.process(harmonic_mag)
        tighten_gains_2d = tighten_gains[:, np.newaxis]
        harmonic_mag_tight = harmonic_mag * tighten_gains_2d
        
        # Context-based mixing
        perc_gain, _ = self._mixer.compute_percussive_gain(
            harmonic_mag_tight, percussive_mag
        )
        perc_gain_2d = perc_gain[:, np.newaxis]
        mixed_mag = harmonic_mag_tight + perc_gain_2d * percussive_mag
        
        # Spectral denoising
        denoise_gains = self._denoiser.compute_gains(mixed_mag)
        mixed_mag = mixed_mag * denoise_gains
        
        # Reconstruct complex spectrogram
        processed_spec = mixed_mag * np.exp(1j * phase)
        
        # ISTFT synthesis
        audio = self._istft(processed_spec, total_len, pad, orig_len)
        
        # Apply fades
        audio = self._apply_fades(audio)
        
        return audio
    
    def process(self, pcm_data: bytes) -> bytes:
        """
        Process PCM audio data.
        
        Args:
            pcm_data: Input PCM data (16-bit signed integer, mono).
        
        Returns:
            Denoised PCM data.
        """
        if len(pcm_data) == 0:
            return pcm_data
        
        # Convert to float
        audio = pcm16_to_float(pcm_data)
        
        # Process
        audio = self.process_array(audio)
        
        # Convert back to PCM
        return float_to_pcm16(audio)
    
    def process_debug(self, audio: NDArray[np.floating]) -> Dict[str, Any]:
        """
        Process audio with debug outputs for all intermediate stages.
        
        Useful for visualization and debugging.
        
        Args:
            audio: Input audio samples.
        
        Returns:
            Dictionary containing:
            - 'harmonic_raw': Raw harmonic component
            - 'harmonic_tight': Harmonic after envelope tightening
            - 'percussive': Percussive component
            - 'mixed': Mixed before denoising
            - 'final': Final output
            - 'tighten_gains': Envelope tightening gains
            - 'perc_gain': Percussive mixing gains
            - 'voice_context': Voice activity detection
        """
        audio = audio.astype(np.float64)
        audio = scipy_signal.filtfilt(self._hp_b, self._hp_a, audio)
        
        orig_len = len(audio)
        
        spec, total_len, pad = self._stft(audio)
        magnitude = np.abs(spec)
        phase = np.angle(spec)
        
        harmonic_mag, percussive_mag = self._hpss.separate(magnitude)
        
        debug: Dict[str, Any] = {
            'harmonic_raw': self._istft(
                harmonic_mag * np.exp(1j * phase), total_len, pad, orig_len
            ),
            'percussive': self._istft(
                percussive_mag * np.exp(1j * phase), total_len, pad, orig_len
            ),
        }
        
        tighten_gains = self._tightener.process(harmonic_mag)
        debug['tighten_gains'] = tighten_gains
        
        tighten_gains_2d = tighten_gains[:, np.newaxis]
        harmonic_mag_tight = harmonic_mag * tighten_gains_2d
        
        debug['harmonic_tight'] = self._istft(
            harmonic_mag_tight * np.exp(1j * phase), total_len, pad, orig_len
        )
        
        perc_gain, voice_context = self._mixer.compute_percussive_gain(
            harmonic_mag_tight, percussive_mag
        )
        debug['perc_gain'] = perc_gain
        debug['voice_context'] = voice_context
        
        perc_gain_2d = perc_gain[:, np.newaxis]
        mixed_mag = harmonic_mag_tight + perc_gain_2d * percussive_mag
        
        debug['mixed'] = self._istft(
            mixed_mag * np.exp(1j * phase), total_len, pad, orig_len
        )
        
        denoise_gains = self._denoiser.compute_gains(mixed_mag)
        final_mag = mixed_mag * denoise_gains
        
        processed = self._istft(final_mag * np.exp(1j * phase), total_len, pad, orig_len)
        debug['final'] = self._apply_fades(processed)
        
        return debug
    
    def process_stages(self, pcm_data: bytes) -> Dict[str, bytes]:
        """
        Process PCM data and return all intermediate stages as PCM.
        
        Useful for A/B comparison and debugging.
        
        Args:
            pcm_data: Input PCM data.
        
        Returns:
            Dictionary containing PCM data for each stage:
            - '0_original': Original input
            - '1_harmonic_raw': Raw harmonic component
            - '2_harmonic_tight': Harmonic after tightening
            - '3_percussive': Percussive component
            - '4_mixed': Mixed before denoising
            - '5_final': Final output
        """
        audio = pcm16_to_float(pcm_data)
        
        stages: Dict[str, bytes] = {
            '0_original': pcm_data,
        }
        
        debug = self.process_debug(audio)
        
        stages['1_harmonic_raw'] = float_to_pcm16(debug['harmonic_raw'])
        stages['2_harmonic_tight'] = float_to_pcm16(debug['harmonic_tight'])
        stages['3_percussive'] = float_to_pcm16(debug['percussive'])
        stages['4_mixed'] = float_to_pcm16(debug['mixed'])
        stages['5_final'] = float_to_pcm16(debug['final'])
        
        return stages
