"""
Data collection script for recording guitar chord training data.
Receives FFT data from Nucleo and saves it with labels.
"""

import numpy as np
import serial_io
import os
from pathlib import Path
import time


CHORD_LABELS = ['C', 'G', 'D', 'A', 'E']


def create_data_directories(base_dir='data'):
    """
    Create directory structure for training data.

    Args:
        base_dir: Base directory for data storage
    """
    base_path = Path(base_dir)
    base_path.mkdir(exist_ok=True)

    for chord in CHORD_LABELS:
        chord_dir = base_path / chord
        chord_dir.mkdir(exist_ok=True)

    print(f"Created data directories in {base_dir}/")


def get_next_sample_number(chord_label, base_dir='data'):
    """
    Get the next available sample number for a chord.

    Args:
        chord_label: Chord name (e.g., 'C', 'G')
        base_dir: Base directory for data storage

    Returns:
        Next sample number (int)
    """
    chord_dir = Path(base_dir) / chord_label
    existing_files = list(chord_dir.glob('sample_*.npy'))

    if not existing_files:
        return 0

    # Extract numbers from filenames
    numbers = []
    for f in existing_files:
        try:
            num = int(f.stem.split('_')[1])
            numbers.append(num)
        except:
            pass

    return max(numbers) + 1 if numbers else 0


def save_fft_sample(fft_data, chord_label, sample_rate, fft_size, base_dir='data'):
    """
    Save FFT data with metadata.

    Args:
        fft_data: FFT magnitude array
        chord_label: Chord name
        sample_rate: Sampling rate (Hz)
        fft_size: FFT window size
        base_dir: Base directory for data storage

    Returns:
        Path to saved file
    """
    sample_num = get_next_sample_number(chord_label, base_dir)
    filename = f"sample_{sample_num}.npy"
    filepath = Path(base_dir) / chord_label / filename

    # Save as dictionary with metadata
    data = {
        'fft': fft_data,
        'sample_rate': sample_rate,
        'fft_size': fft_size,
        'chord': chord_label
    }

    np.save(filepath, data)
    print(f"Saved {filepath}")

    return filepath


def collect_training_data(serial_port, baudrate=115200, sample_rate=8000, fft_size=512):
    """
    Interactive data collection loop.

    Args:
        serial_port: Serial port for Nucleo
        baudrate: Serial baud rate
        sample_rate: Audio sampling rate (Hz)
        fft_size: FFT window size
    """
    print("="*60)
    print("Guitar Chord Data Collection")
    print("="*60)

    # Create directories
    create_data_directories()

    # Connect to Nucleo
    print(f"\nConnecting to {serial_port}...")
    ser = serial_io.SerialConnection(serial_port, baudrate)

    print("\n" + "="*60)
    print("INSTRUCTIONS:")
    print("="*60)
    print("1. Play a chord on your guitar")
    print("2. Wait for FFT data to be received")
    print("3. Enter the chord name when prompted (C, G, D, A, E)")
    print("4. Type 'skip' to discard the sample")
    print("5. Type 'quit' to exit")
    print("="*60)

    try:
        while True:
            # Wait for FFT data
            print("\n[Waiting for FFT data from Nucleo...]")
            print("(Play a chord now)")

            fft_data = None
            while fft_data is None:
                fft_data = ser.receive_fft_data()
                time.sleep(0.1)

            # Prompt user for label
            print("\n" + "-"*60)
            label = input(f"Enter chord label ({'/'.join(CHORD_LABELS)}) or 'skip'/'quit': ").strip().upper()

            if label == 'QUIT':
                print("Exiting data collection...")
                break

            if label == 'SKIP':
                print("Sample discarded.")
                continue

            if label not in CHORD_LABELS:
                print(f"Invalid label '{label}'. Sample discarded.")
                continue

            # Save the sample
            save_fft_sample(fft_data, label, sample_rate, fft_size)

            # Show statistics
            print("\nCurrent dataset:")
            for chord in CHORD_LABELS:
                count = len(list((Path('data') / chord).glob('sample_*.npy')))
                print(f"  {chord}: {count} samples")

    except KeyboardInterrupt:
        print("\n\nData collection interrupted by user.")

    finally:
        ser.close()

    print("\nData collection complete!")


def collect_batch_samples(serial_port, chord_label, num_samples, baudrate=115200,
                         sample_rate=8000, fft_size=512, delay=2.0):
    """
    Collect multiple samples for a single chord with automatic timing.

    Args:
        serial_port: Serial port for Nucleo
        chord_label: Chord to record
        num_samples: Number of samples to collect
        baudrate: Serial baud rate
        sample_rate: Audio sampling rate (Hz)
        fft_size: FFT window size
        delay: Delay between samples (seconds)
    """
    print("="*60)
    print(f"Batch Data Collection: {chord_label} chord")
    print(f"Collecting {num_samples} samples with {delay}s delay between each")
    print("="*60)

    # Create directories
    create_data_directories()

    # Connect to Nucleo
    print(f"\nConnecting to {serial_port}...")
    ser = serial_io.SerialConnection(serial_port, baudrate)

    print("\nStarting in 3 seconds...")
    time.sleep(3)

    try:
        for i in range(num_samples):
            print(f"\n{'='*60}")
            print(f"Sample {i+1}/{num_samples}")
            print(f"{'='*60}")
            print("Play the chord NOW!")

            # Wait for FFT data
            fft_data = None
            timeout = 0
            while fft_data is None and timeout < 50:  # 5 second timeout
                fft_data = ser.receive_fft_data()
                time.sleep(0.1)
                timeout += 1

            if fft_data is None:
                print("ERROR: No FFT data received. Skipping...")
                continue

            # Save the sample
            save_fft_sample(fft_data, chord_label, sample_rate, fft_size)

            # Wait before next sample
            if i < num_samples - 1:
                print(f"\nWaiting {delay}s before next sample...")
                time.sleep(delay)

    except KeyboardInterrupt:
        print("\n\nBatch collection interrupted by user.")

    finally:
        ser.close()

    print(f"\nCollected batch for {chord_label} chord!")


def main():
    """
    Main entry point for data collection.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Collect training data for chord classification')
    parser.add_argument('--port', type=str, default='/dev/ttyACM0',
                        help='Serial port for Nucleo')
    parser.add_argument('--baudrate', type=int, default=115200,
                        help='Serial baud rate')
    parser.add_argument('--sample-rate', type=int, default=8000,
                        help='Audio sampling rate (Hz)')
    parser.add_argument('--fft-size', type=int, default=512,
                        help='FFT window size')
    parser.add_argument('--batch', action='store_true',
                        help='Batch mode: collect multiple samples of one chord')
    parser.add_argument('--chord', type=str, default=None,
                        help='Chord label for batch mode (C, G, D, A, or E)')
    parser.add_argument('--num-samples', type=int, default=10,
                        help='Number of samples to collect in batch mode')
    parser.add_argument('--delay', type=float, default=2.0,
                        help='Delay between samples in batch mode (seconds)')

    args = parser.parse_args()

    if args.batch:
        if args.chord is None:
            print("Error: --chord required for batch mode")
            exit(1)

        chord = args.chord.upper()
        if chord not in CHORD_LABELS:
            print(f"Error: Invalid chord '{chord}'. Must be one of {CHORD_LABELS}")
            exit(1)

        collect_batch_samples(
            args.port, chord, args.num_samples,
            args.baudrate, args.sample_rate, args.fft_size, args.delay
        )
    else:
        collect_training_data(
            args.port, args.baudrate, args.sample_rate, args.fft_size
        )


if __name__ == '__main__':
    main()
