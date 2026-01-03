"""Command-line interface for HPSS voice denoiser."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from hpss_denoiser import __version__
from hpss_denoiser.core.config import DenoiserConfig
from hpss_denoiser.core.pipeline import HPSSDenoiser
from hpss_denoiser.utils.audio import pcm16_to_float, linear_to_db
import numpy as np


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog='hpss-denoise',
        description='HPSS-based voice denoiser optimized for ASR preprocessing.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  hpss-denoise input.pcm output.pcm

  # Process with intermediate stages
  hpss-denoise input.pcm output.pcm --stages

  # Generate analysis visualization
  hpss-denoise input.pcm --analyze

  # Custom parameters
  hpss-denoise input.pcm output.pcm --voice-gain 0.25 --silence-gain 0.02

Audio Format:
  Input/output is raw PCM: 16-bit signed integer, mono, little-endian.
  Default sample rate is 16000 Hz.
  
  Convert with ffmpeg:
    ffmpeg -i input.wav -f s16le -ar 16000 -ac 1 input.pcm
    ffmpeg -f s16le -ar 16000 -ac 1 -i output.pcm output.wav
""",
    )
    
    parser.add_argument(
        'input',
        type=str,
        help='Input PCM file path',
    )
    
    parser.add_argument(
        'output',
        type=str,
        nargs='?',
        default=None,
        help='Output PCM file path (required unless --analyze)',
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}',
    )
    
    # Processing modes
    mode_group = parser.add_argument_group('Processing modes')
    mode_group.add_argument(
        '--stages',
        action='store_true',
        help='Save all intermediate processing stages',
    )
    mode_group.add_argument(
        '--analyze',
        action='store_true',
        help='Generate analysis visualization (requires matplotlib)',
    )
    
    # Audio parameters
    audio_group = parser.add_argument_group('Audio parameters')
    audio_group.add_argument(
        '--sample-rate', '-r',
        type=int,
        default=16000,
        metavar='HZ',
        help='Sample rate in Hz (default: 16000)',
    )
    
    # HPSS parameters
    hpss_group = parser.add_argument_group('HPSS parameters')
    hpss_group.add_argument(
        '--harmonic-kernel',
        type=int,
        default=9,
        metavar='N',
        help='Harmonic median filter kernel size (default: 9)',
    )
    hpss_group.add_argument(
        '--percussive-kernel',
        type=int,
        default=9,
        metavar='N',
        help='Percussive median filter kernel size (default: 9)',
    )
    hpss_group.add_argument(
        '--hpss-margin',
        type=float,
        default=2.5,
        metavar='M',
        help='HPSS separation margin (default: 2.5)',
    )
    
    # Mixing parameters
    mix_group = parser.add_argument_group('Mixing parameters')
    mix_group.add_argument(
        '--voice-gain',
        type=float,
        default=0.20,
        metavar='G',
        help='Percussive gain during voice (0-1, default: 0.20)',
    )
    mix_group.add_argument(
        '--silence-gain',
        type=float,
        default=0.04,
        metavar='G',
        help='Percussive gain during silence (0-1, default: 0.04)',
    )
    mix_group.add_argument(
        '--context-window',
        type=int,
        default=10,
        metavar='N',
        help='Voice context extension frames (default: 10)',
    )
    
    # Envelope parameters
    env_group = parser.add_argument_group('Envelope tightening')
    env_group.add_argument(
        '--no-tightening',
        action='store_true',
        help='Disable envelope tightening',
    )
    env_group.add_argument(
        '--release-frames',
        type=int,
        default=3,
        metavar='N',
        help='Envelope release frames (default: 3)',
    )
    
    # Denoising parameters
    denoise_group = parser.add_argument_group('Spectral denoising')
    denoise_group.add_argument(
        '--noise-strength',
        type=float,
        default=0.8,
        metavar='S',
        help='Low-freq noise reduction strength (0-1, default: 0.8)',
    )
    denoise_group.add_argument(
        '--noise-max-freq',
        type=float,
        default=350.0,
        metavar='HZ',
        help='Max frequency for noise reduction (default: 350)',
    )
    
    # Output options
    output_group = parser.add_argument_group('Output options')
    output_group.add_argument(
        '--output-image',
        type=str,
        default=None,
        metavar='PATH',
        help='Output path for analysis image (default: based on input)',
    )
    output_group.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress informational output',
    )
    
    return parser


def build_config(args: argparse.Namespace) -> DenoiserConfig:
    """Build configuration from command-line arguments."""
    return DenoiserConfig(
        sample_rate=args.sample_rate,
        harmonic_kernel=args.harmonic_kernel,
        percussive_kernel=args.percussive_kernel,
        hpss_margin=args.hpss_margin,
        voice_context_perc_gain=args.voice_gain,
        no_context_perc_gain=args.silence_gain,
        context_window=args.context_window,
        envelope_tightening=not args.no_tightening,
        envelope_release_frames=args.release_frames,
        noise_reduction_strength=args.noise_strength,
        noise_reduction_max_freq=args.noise_max_freq,
    )


def process_file(
    input_path: str,
    output_path: str,
    config: DenoiserConfig,
    save_stages: bool = False,
    quiet: bool = False,
) -> None:
    """Process a single PCM file."""
    # Load input
    with open(input_path, 'rb') as f:
        pcm_data = f.read()
    
    if not quiet:
        duration = len(pcm_data) / 2 / config.sample_rate
        print(f"Input: {input_path} ({duration:.2f}s)")
    
    # Create denoiser
    denoiser = HPSSDenoiser(config)
    
    if save_stages:
        # Process with stages
        stages = denoiser.process_stages(pcm_data)
        
        # Save each stage
        base = Path(output_path).stem
        output_dir = Path(output_path).parent
        
        for name, data in stages.items():
            stage_path = output_dir / f"{base}_{name}.pcm"
            with open(stage_path, 'wb') as f:
                f.write(data)
            if not quiet:
                print(f"Saved: {stage_path}")
    else:
        # Process normally
        processed = denoiser.process(pcm_data)
        
        with open(output_path, 'wb') as f:
            f.write(processed)
        
        if not quiet:
            # Compute statistics
            orig = pcm16_to_float(pcm_data)
            proc = pcm16_to_float(processed)
            
            orig_rms = linear_to_db(float(np.sqrt(np.mean(orig ** 2))))
            proc_rms = linear_to_db(float(np.sqrt(np.mean(proc ** 2))))
            
            print(f"Output: {output_path}")
            print(f"RMS: {orig_rms:.1f} dB → {proc_rms:.1f} dB")


def analyze_file(
    input_path: str,
    output_image: Optional[str],
    config: DenoiserConfig,
    quiet: bool = False,
) -> None:
    """Generate analysis visualization."""
    try:
        # noinspection PyUnusedImports
        from hpss_denoiser.utils.visualization import create_analysis_plot
    except ImportError:
        print("Error: matplotlib is required for analysis.")
        print("Install with: pip install hpss-voice-denoiser[visualization]")
        sys.exit(1)
    
    # Default output image path
    if output_image is None:
        output_image = str(Path(input_path).with_suffix('.png'))
    
    if not quiet:
        print(f"Analyzing: {input_path}")
    
    create_analysis_plot(
        input_path,
        output_image,
        config,
        config.sample_rate,
    )
    
    if not quiet:
        print(f"Analysis saved: {output_image}")


def main(argv: Optional[list] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Validate arguments
    if not args.analyze and args.output is None:
        parser.error("output is required unless --analyze is specified")
    
    # Check input exists
    if not Path(args.input).exists():
        print(f"Error: Input file not found: {args.input}")
        return 1
    
    try:
        # Build configuration
        config = build_config(args)
        config.validate()
        
        if args.analyze:
            # Analysis mode
            analyze_file(
                args.input,
                args.output_image,
                config,
                args.quiet,
            )
        else:
            # Processing mode
            process_file(
                args.input,
                args.output,
                config,
                args.stages,
                args.quiet,
            )
        
        return 0
    
    except ValueError as e:
        print(f"Configuration error: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
