"""Visualization utilities for HPSS voice denoiser."""

from typing import Optional
import numpy as np
from numpy.typing import NDArray

from hpss_denoiser.core.config import DenoiserConfig
from hpss_denoiser.core.pipeline import HPSSDenoiser
from hpss_denoiser.utils.audio import pcm16_to_float


def create_analysis_plot(
    pcm_file: str,
    output_image: str = "hpss_analysis.png",
    config: Optional[DenoiserConfig] = None,
    sample_rate: int = 16000,
) -> None:
    """
    Generate analysis visualization for HPSS denoising.
    
    Creates a multi-panel plot showing:
    - Waveform comparison (original vs processed)
    - Harmonic component (raw vs tightened)
    - Envelope tightening gains
    - Voice context and percussive gain
    - Removed signal
    
    Args:
        pcm_file: Path to input PCM file.
        output_image: Path to output image file.
        config: Denoiser configuration. If None, uses defaults.
        sample_rate: Sample rate for time axis.
    
    Raises:
        ImportError: If matplotlib is not installed.
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install with: pip install hpss-voice-denoiser[visualization]"
        )
    
    # Load audio
    with open(pcm_file, 'rb') as f:
        pcm_data = f.read()
    
    # Process
    denoiser = HPSSDenoiser(config)
    stages = denoiser.process_stages(pcm_data)
    
    # Convert to float for plotting
    original = pcm16_to_float(stages['0_original'])
    harmonic_raw = pcm16_to_float(stages['1_harmonic_raw'])
    harmonic_tight = pcm16_to_float(stages['2_harmonic_tight'])
    final = pcm16_to_float(stages['5_final'])
    
    # Get debug info for gains
    debug = denoiser.process_debug(pcm16_to_float(pcm_data))
    tighten_gains = debug['tighten_gains']
    perc_gain = debug['perc_gain']
    voice_context = debug['voice_context']
    
    # Create plot
    plt.style.use('dark_background')
    fig, axes = plt.subplots(5, 1, figsize=(14, 12))
    
    # Time axes
    time = np.arange(len(original)) / sample_rate
    hop_ms = denoiser.config.hop_size_ms
    frame_time = np.arange(len(tighten_gains)) * hop_ms / 1000
    
    # Panel 1: Waveform comparison
    axes[0].plot(time, original, linewidth=0.5, color='#00ff88', alpha=0.7, label='Original')
    axes[0].plot(time, final, linewidth=0.5, color='#ff00ff', alpha=0.7, label='Processed')
    axes[0].set_title('Waveform Comparison', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Amplitude')
    axes[0].legend(loc='upper right')
    axes[0].set_xlim(0, time[-1])
    
    # Panel 2: Harmonic comparison
    axes[1].plot(time, harmonic_raw, linewidth=0.5, color='#00aaff', alpha=0.7, label='Harmonic Raw')
    axes[1].plot(time, harmonic_tight, linewidth=0.5, color='#ffaa00', alpha=0.7, label='Harmonic Tight')
    axes[1].set_title('Harmonic: Raw vs Tightened (Echo Reduction)', fontsize=12, fontweight='bold')
    axes[1].set_ylabel('Amplitude')
    axes[1].legend(loc='upper right')
    axes[1].set_xlim(0, time[-1])
    
    # Panel 3: Tightening gains
    axes[2].plot(frame_time, tighten_gains, color='#ff8800', linewidth=1)
    axes[2].fill_between(frame_time, 0, tighten_gains, alpha=0.3, color='#ff8800')
    axes[2].set_title('Envelope Tightening Gains', fontsize=12, fontweight='bold')
    axes[2].set_ylabel('Gain')
    axes[2].set_ylim(0, 1.1)
    axes[2].set_xlim(0, frame_time[-1] if len(frame_time) > 0 else 1)
    
    # Panel 4: Voice context and percussive gain
    axes[3].fill_between(frame_time, 0, voice_context, alpha=0.3, color='#00ff88', label='Voice Context')
    axes[3].plot(frame_time, perc_gain, color='#ff00ff', linewidth=1.5, label='Percussive Gain')
    axes[3].axhline(
        denoiser.config.voice_context_perc_gain,
        color='#00ff88', linestyle='--', alpha=0.5,
        label=f'Voice Gain ({denoiser.config.voice_context_perc_gain})'
    )
    axes[3].axhline(
        denoiser.config.no_context_perc_gain,
        color='#ff4444', linestyle='--', alpha=0.5,
        label=f'Silence Gain ({denoiser.config.no_context_perc_gain})'
    )
    axes[3].set_title('Voice Context & Percussive Gain', fontsize=12, fontweight='bold')
    axes[3].set_ylabel('Value')
    axes[3].set_ylim(0, 0.35)
    axes[3].legend(loc='upper right', fontsize=8)
    axes[3].set_xlim(0, frame_time[-1] if len(frame_time) > 0 else 1)
    
    # Panel 5: Removed signal
    min_len = min(len(original), len(final))
    diff = original[:min_len] - final[:min_len]
    axes[4].plot(time[:min_len], diff, linewidth=0.5, color='#ffaa00')
    axes[4].set_title('Removed Signal (Original - Processed)', fontsize=12, fontweight='bold')
    axes[4].set_ylabel('Amplitude')
    axes[4].set_xlabel('Time (s)')
    axes[4].set_xlim(0, time[-1])
    
    plt.tight_layout()
    plt.savefig(output_image, dpi=150, bbox_inches='tight', facecolor='#1a1a1a')
    plt.close()
    
    print(f"Analysis saved to: {output_image}")


def create_spectrogram_comparison(
    original: NDArray[np.floating],
    processed: NDArray[np.floating],
    output_image: str = "spectrogram_comparison.png",
    sample_rate: int = 16000,
) -> None:
    """
    Create spectrogram comparison plot.
    
    Args:
        original: Original audio samples.
        processed: Processed audio samples.
        output_image: Path to output image file.
        sample_rate: Sample rate in Hz.
    """
    try:
        import matplotlib.pyplot as plt
        from scipy import signal as scipy_signal
    except ImportError:
        raise ImportError(
            "matplotlib is required for visualization. "
            "Install with: pip install hpss-voice-denoiser[visualization]"
        )
    
    # Compute spectrograms
    nperseg = 512
    noverlap = 384
    
    f_orig, t_orig, sxx_orig = scipy_signal.spectrogram(
        original, sample_rate, nperseg=nperseg, noverlap=noverlap
    )
    f_proc, t_proc, sxx_proc = scipy_signal.spectrogram(
        processed, sample_rate, nperseg=nperseg, noverlap=noverlap
    )
    
    # Convert to dB
    sxx_orig_db = 10 * np.log10(sxx_orig + 1e-10)
    sxx_proc_db = 10 * np.log10(sxx_proc + 1e-10)
    
    # Difference
    min_t = min(sxx_orig_db.shape[1], sxx_proc_db.shape[1])
    diff_db = sxx_orig_db[:, :min_t] - sxx_proc_db[:, :min_t]
    
    # Create plot
    plt.style.use('dark_background')
    fig, axes = plt.subplots(1, 3, figsize=(15, 4))
    
    vmin, vmax = -80, 0
    
    im0 = axes[0].pcolormesh(t_orig, f_orig / 1000, sxx_orig_db,
                              shading='gouraud', cmap='magma', vmin=vmin, vmax=vmax)
    axes[0].set_title('Original', fontsize=12, fontweight='bold')
    axes[0].set_ylabel('Frequency (kHz)')
    axes[0].set_xlabel('Time (s)')
    axes[0].set_ylim(0, 8)
    
    im1 = axes[1].pcolormesh(t_proc, f_proc / 1000, sxx_proc_db,
                              shading='gouraud', cmap='magma', vmin=vmin, vmax=vmax)
    axes[1].set_title('Processed', fontsize=12, fontweight='bold')
    axes[1].set_xlabel('Time (s)')
    axes[1].set_ylim(0, 8)
    
    im2 = axes[2].pcolormesh(t_orig[:min_t], f_orig / 1000, diff_db,
                              shading='gouraud', cmap='RdYlGn', vmin=-20, vmax=20)
    axes[2].set_title('Difference (green=reduced)', fontsize=12, fontweight='bold')
    axes[2].set_xlabel('Time (s)')
    axes[2].set_ylim(0, 8)
    
    # Colorbars
    plt.colorbar(im0, ax=axes[0], label='dB')
    plt.colorbar(im1, ax=axes[1], label='dB')
    plt.colorbar(im2, ax=axes[2], label='dB')
    
    plt.tight_layout()
    plt.savefig(output_image, dpi=150, bbox_inches='tight', facecolor='#1a1a1a')
    plt.close()
    
    print(f"Spectrogram comparison saved to: {output_image}")
