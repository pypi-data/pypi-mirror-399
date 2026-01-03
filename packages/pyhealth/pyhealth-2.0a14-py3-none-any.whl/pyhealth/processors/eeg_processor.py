"""EEG signal processor for filtering, resampling, and montage conversion."""

from typing import Any, Dict, List, Optional, Tuple, Union
from pathlib import Path

import numpy as np
import torch

from . import register_processor
from .base_processor import FeatureProcessor


@register_processor("eeg")
class EEGProcessor(FeatureProcessor):
    """Feature processor for EEG signals with filtering and montage conversion.

    This processor handles common EEG preprocessing steps:
    - Bandpass filtering
    - Notch filtering (for line noise removal)
    - Resampling to target sample rate
    - Bipolar montage conversion (optional)

    The processor can accept either:
    - A numpy array of shape (channels, samples)
    - A tuple of (signal_array, sample_rate) for signals with known sample rate
    - A path to an EDF file (if mne is available)

    Args:
        sample_rate: Target sample rate after resampling. If None, keeps original.
            Defaults to 256.
        lowcut: Low cutoff frequency for bandpass filter (Hz). Defaults to 0.1.
        highcut: High cutoff frequency for bandpass filter (Hz). Defaults to 75.0.
        notch_freq: Notch filter frequency (Hz) for line noise removal.
            If None, no notch filter is applied. Defaults to 50.0.
        apply_bipolar: Whether to convert to bipolar montage. Defaults to False.
        bipolar_pairs: List of channel name pairs for bipolar montage.
            Each pair is (anode, cathode). If None, uses standard 10-20 TCP montage.
        dtype: Output torch dtype. Defaults to torch.float32.

    Examples:
        >>> processor = EEGProcessor(sample_rate=256, lowcut=0.1, highcut=75.0)
        >>> # Process a numpy array
        >>> signal = np.random.randn(19, 2560)  # 19 channels, 10 seconds at 256 Hz
        >>> processed = processor.process((signal, 256))
        >>> print(processed.shape)
        torch.Size([19, 2560])

        >>> # Process with bipolar montage
        >>> processor = EEGProcessor(sample_rate=256, apply_bipolar=True)
        >>> processed = processor.process((signal, 256))
    """

    # Standard 10-20 TCP (Temporal Central Parasagittal) bipolar montage
    # Used in Temple University EEG datasets
    STANDARD_BIPOLAR_PAIRS: List[Tuple[str, str]] = [
        ("EEG FP1-REF", "EEG F7-REF"),
        ("EEG F7-REF", "EEG T3-REF"),
        ("EEG T3-REF", "EEG T5-REF"),
        ("EEG T5-REF", "EEG O1-REF"),
        ("EEG FP2-REF", "EEG F8-REF"),
        ("EEG F8-REF", "EEG T4-REF"),
        ("EEG T4-REF", "EEG T6-REF"),
        ("EEG T6-REF", "EEG O2-REF"),
        ("EEG FP1-REF", "EEG F3-REF"),
        ("EEG F3-REF", "EEG C3-REF"),
        ("EEG C3-REF", "EEG P3-REF"),
        ("EEG P3-REF", "EEG O1-REF"),
        ("EEG FP2-REF", "EEG F4-REF"),
        ("EEG F4-REF", "EEG C4-REF"),
        ("EEG C4-REF", "EEG P4-REF"),
        ("EEG P4-REF", "EEG O2-REF"),
    ]

    def __init__(
        self,
        sample_rate: Optional[int] = 256,
        lowcut: Optional[float] = 0.1,
        highcut: Optional[float] = 75.0,
        notch_freq: Optional[float] = 50.0,
        apply_bipolar: bool = False,
        bipolar_pairs: Optional[List[Tuple[str, str]]] = None,
        channel_names: Optional[List[str]] = None,
        dtype: torch.dtype = torch.float32,
    ) -> None:
        self.sample_rate = sample_rate
        self.lowcut = lowcut
        self.highcut = highcut
        self.notch_freq = notch_freq
        self.apply_bipolar = apply_bipolar
        self.bipolar_pairs = bipolar_pairs or self.STANDARD_BIPOLAR_PAIRS
        self.channel_names = channel_names
        self.dtype = dtype

    def _bandpass_filter(
        self,
        signal: np.ndarray,
        fs: float,
        lowcut: float,
        highcut: float,
        order: int = 4,
    ) -> np.ndarray:
        """Apply Butterworth bandpass filter.

        Args:
            signal: Input signal of shape (channels, samples)
            fs: Sampling frequency
            lowcut: Low cutoff frequency
            highcut: High cutoff frequency
            order: Filter order

        Returns:
            Filtered signal
        """
        from scipy.signal import butter, filtfilt

        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype="band")
        return filtfilt(b, a, signal, axis=-1)

    def _notch_filter(
        self,
        signal: np.ndarray,
        fs: float,
        freq: float,
        quality: float = 30.0,
    ) -> np.ndarray:
        """Apply notch filter to remove line noise.

        Args:
            signal: Input signal of shape (channels, samples)
            fs: Sampling frequency
            freq: Frequency to notch out
            quality: Quality factor (higher = narrower notch)

        Returns:
            Filtered signal
        """
        from scipy.signal import iirnotch, filtfilt

        b, a = iirnotch(freq, quality, fs)
        return filtfilt(b, a, signal, axis=-1)

    def _resample(
        self,
        signal: np.ndarray,
        orig_fs: float,
        target_fs: float,
    ) -> np.ndarray:
        """Resample signal to target sample rate.

        Args:
            signal: Input signal of shape (channels, samples)
            orig_fs: Original sampling frequency
            target_fs: Target sampling frequency

        Returns:
            Resampled signal
        """
        from scipy.signal import resample

        if orig_fs == target_fs:
            return signal

        num_samples = int(signal.shape[-1] * target_fs / orig_fs)
        return resample(signal, num_samples, axis=-1)

    def _apply_bipolar_montage(
        self,
        signal: np.ndarray,
        channel_names: List[str],
    ) -> np.ndarray:
        """Convert referential montage to bipolar montage.

        Args:
            signal: Input signal of shape (channels, samples)
            channel_names: List of channel names corresponding to signal rows

        Returns:
            Bipolar signal of shape (num_pairs, samples)
        """
        channel_map = {name: idx for idx, name in enumerate(channel_names)}

        bipolar_signals = []
        for anode, cathode in self.bipolar_pairs:
            if anode not in channel_map or cathode not in channel_map:
                raise ValueError(
                    f"Bipolar pair ({anode}, {cathode}) not found in channels. "
                    f"Available: {channel_names}"
                )
            anode_idx = channel_map[anode]
            cathode_idx = channel_map[cathode]
            bipolar_signals.append(signal[anode_idx] - signal[cathode_idx])

        return np.vstack(bipolar_signals)

    def process(
        self,
        value: Union[
            np.ndarray,
            Tuple[np.ndarray, float],
            Tuple[np.ndarray, float, List[str]],
            Dict[str, Any],
        ],
    ) -> torch.Tensor:
        """Process EEG signal with filtering and optional montage conversion.

        Args:
            value: Input can be one of:
                - np.ndarray: Signal array (channels, samples). Assumes sample_rate
                  is already at target or uses processor's sample_rate.
                - Tuple[np.ndarray, float]: (signal, original_sample_rate)
                - Tuple[np.ndarray, float, List[str]]: (signal, sample_rate, channel_names)
                - Dict with keys 'signal', 'sample_rate', and optionally 'channel_names'

        Returns:
            Processed signal as torch.Tensor
        """
        # Parse input
        if isinstance(value, dict):
            signal = value["signal"]
            orig_fs = value.get("sample_rate", self.sample_rate)
            channel_names = value.get("channel_names", self.channel_names)
        elif isinstance(value, tuple):
            if len(value) == 2:
                signal, orig_fs = value
                channel_names = self.channel_names
            else:
                signal, orig_fs, channel_names = value
        else:
            signal = value
            orig_fs = self.sample_rate
            channel_names = self.channel_names

        # Ensure numpy array
        if isinstance(signal, torch.Tensor):
            signal = signal.numpy()

        # Apply bandpass filter
        if self.lowcut is not None and self.highcut is not None:
            signal = self._bandpass_filter(signal, orig_fs, self.lowcut, self.highcut)

        # Apply notch filter
        if self.notch_freq is not None:
            signal = self._notch_filter(signal, orig_fs, self.notch_freq)

        # Resample
        if self.sample_rate is not None and orig_fs != self.sample_rate:
            signal = self._resample(signal, orig_fs, self.sample_rate)

        # Apply bipolar montage
        if self.apply_bipolar and channel_names is not None:
            signal = self._apply_bipolar_montage(signal, channel_names)

        return torch.tensor(signal, dtype=self.dtype)

    def __repr__(self) -> str:
        return (
            f"EEGProcessor(sample_rate={self.sample_rate}, "
            f"lowcut={self.lowcut}, highcut={self.highcut}, "
            f"notch_freq={self.notch_freq}, apply_bipolar={self.apply_bipolar})"
        )


