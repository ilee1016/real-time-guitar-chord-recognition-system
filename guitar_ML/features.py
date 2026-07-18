"""
Feature extraction for guitar chord classification.
Extracts pitch intensity features from FFT magnitude data.
"""

import numpy as np

# Standard guitar tuning frequencies (Hz) - open strings
GUITAR_NOTES = {
    'E2': 82.41,   # Low E string
    'A2': 110.00,  # A string
    'D3': 146.83,  # D string
    'G3': 196.00,  # G string
    'B3': 246.94,  # B string
    'E4': 329.63   # High E string
}

# Common notes in guitar chords (including fretted notes)
CHROMATIC_NOTES = {
    'C': 130.81,
    'C#': 138.59,
    'D': 146.83,
    'D#': 155.56,
    'E': 164.81,
    'F': 174.61,
    'F#': 185.00,
    'G': 196.00,
    'G#': 207.65,
    'A': 220.00,
    'A#': 233.08,
    'B': 246.94,
    'C5': 261.63,
    'C#5': 277.18,
    'D5': 293.66,
    'E5': 329.63,
    'F#5': 369.99,
    'G5': 392.00,
}


def get_frequency_bins(fft_size, sample_rate):
    """
    Calculate the frequency corresponding to each FFT bin.

    Args:
        fft_size: Size of the FFT
        sample_rate: Sampling rate in Hz

    Returns:
        Array of frequencies (Hz) for each FFT bin
    """
    return np.fft.rfftfreq(fft_size, 1.0 / sample_rate)


def find_closest_bin(target_freq, freq_bins):
    """
    Find the FFT bin index closest to a target frequency.

    Args:
        target_freq: Target frequency in Hz
        freq_bins: Array of FFT bin frequencies

    Returns:
        Index of the closest frequency bin
    """
    return np.argmin(np.abs(freq_bins - target_freq))


def extract_pitch_features(fft_magnitude, sample_rate, fft_size, bandwidth_hz=10):
    """
    Extract pitch intensity features from FFT magnitude spectrum.

    For each note frequency, this computes the average magnitude in a narrow
    frequency band around that note (to account for tuning variations and
    frequency resolution limits).

    Args:
        fft_magnitude: Magnitude spectrum from FFT (1D numpy array)
        sample_rate: Sampling rate used for audio capture (Hz)
        fft_size: Size of FFT window
        bandwidth_hz: Frequency bandwidth around each note to average (Hz)

    Returns:
        Feature vector as 1D numpy array
    """
    freq_bins = get_frequency_bins(fft_size, sample_rate)
    features = []

    # Extract intensity for each chromatic note
    for note_name, note_freq in sorted(CHROMATIC_NOTES.items(), key=lambda x: x[1]):
        # Find the frequency range around this note
        center_bin = find_closest_bin(note_freq, freq_bins)

        # Calculate bandwidth in bins
        freq_resolution = sample_rate / fft_size
        bin_bandwidth = max(1, int(bandwidth_hz / freq_resolution))

        # Extract average magnitude in the bandwidth
        start_bin = max(0, center_bin - bin_bandwidth // 2)
        end_bin = min(len(fft_magnitude), center_bin + bin_bandwidth // 2 + 1)

        avg_magnitude = np.mean(fft_magnitude[start_bin:end_bin])
        features.append(avg_magnitude)

    # Also add features for the first 3 harmonics of each guitar string
    for string_name, string_freq in sorted(GUITAR_NOTES.items(), key=lambda x: x[1]):
        for harmonic in [2, 3]:  # 2nd and 3rd harmonics
            harmonic_freq = string_freq * harmonic
            if harmonic_freq < sample_rate / 2:  # Nyquist limit
                center_bin = find_closest_bin(harmonic_freq, freq_bins)
                freq_resolution = sample_rate / fft_size
                bin_bandwidth = max(1, int(bandwidth_hz / freq_resolution))

                start_bin = max(0, center_bin - bin_bandwidth // 2)
                end_bin = min(len(fft_magnitude), center_bin + bin_bandwidth // 2 + 1)

                avg_magnitude = np.mean(fft_magnitude[start_bin:end_bin])
                features.append(avg_magnitude)

    return np.array(features)


def normalize_features(features):
    """
    Normalize features to have zero mean and unit variance.
    Useful for ML models like k-NN and logistic regression.

    Args:
        features: Feature vector or matrix (can be 1D or 2D)

    Returns:
        Normalized features
    """
    features = np.array(features)

    # Handle 1D case
    if features.ndim == 1:
        if np.std(features) > 1e-8:
            return (features - np.mean(features)) / np.std(features)
        else:
            return features

    # Handle 2D case (multiple samples)
    normalized = np.zeros_like(features)
    for i in range(features.shape[1]):
        col = features[:, i]
        if np.std(col) > 1e-8:
            normalized[:, i] = (col - np.mean(col)) / np.std(col)
        else:
            normalized[:, i] = col

    return normalized
