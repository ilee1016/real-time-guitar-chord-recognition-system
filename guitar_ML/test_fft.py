#!/usr/bin/env python3
"""
FFT Data Receiver and Visualizer
Receives FFT magnitude spectrum from Nucleo board and displays it
"""

import serial
import struct
import numpy as np
import matplotlib.pyplot as plt
import time
import argparse


class FFTReceiver:
    def __init__(self, port, baudrate=115200):
        self.port = port
        self.baudrate = baudrate
        self.ser = None

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=10.0,
                write_timeout=5.0
            )
            print(f"Connected to {port} at {baudrate} baud")
            time.sleep(2)
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            raise

    def read_line(self):
        """Read a line from serial"""
        try:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            return line
        except Exception as e:
            print(f"Error reading line: {e}")
            return ""

    def receive_fft(self):
        """Receive FFT data from Nucleo"""
        # Wait for FFT_START marker
        while True:
            line = self.read_line()
            if not line:
                continue

            print(f"Received: {line}")

            if line == "FFT_START":
                break

        # Read metadata
        metadata = {}
        while True:
            line = self.read_line()
            if not line:
                continue

            print(f"Metadata: {line}")

            if line == "FFT_DATA":
                break

            if '=' in line:
                key, value = line.split('=')
                metadata[key] = int(value)

        # Extract metadata
        fft_size = metadata.get('FFT_SIZE', 2048)
        sample_rate = metadata.get('SAMPLE_RATE', 8000)
        min_bin = metadata.get('MIN_BIN', 0)
        max_bin = metadata.get('MAX_BIN', 512)
        num_bins = metadata.get('NUM_BINS', 512)

        print(f"\nFFT Configuration:")
        print(f"  FFT Size: {fft_size}")
        print(f"  Sample Rate: {sample_rate} Hz")
        print(f"  Frequency Resolution: {sample_rate / fft_size:.2f} Hz/bin")
        print(f"  Bins: {min_bin} to {max_bin} ({num_bins} bins)")
        print(f"  Frequency Range: {min_bin * sample_rate / fft_size:.1f} - {max_bin * sample_rate / fft_size:.1f} Hz")

        # Read magnitude data (float32)
        num_bytes = num_bins * 4  # 4 bytes per float
        print(f"\nReading {num_bytes} bytes ({num_bins} floats)...")

        magnitude_bytes = self.ser.read(num_bytes)

        if len(magnitude_bytes) != num_bytes:
            print(f"Error: Expected {num_bytes} bytes, got {len(magnitude_bytes)}")
            return None

        # Convert bytes to float array
        magnitudes = np.array(struct.unpack(f'<{num_bins}f', magnitude_bytes))

        # Wait for FFT_END marker
        while True:
            line = self.read_line()
            if not line:
                continue

            print(f"Received: {line}")

            if line.startswith("FFT_END") or line.startswith("Peak:"):
                break

        # Create frequency array
        bin_indices = np.arange(min_bin, max_bin + 1)
        frequencies = bin_indices * sample_rate / fft_size

        return {
            'frequencies': frequencies,
            'magnitudes': magnitudes,
            'sample_rate': sample_rate,
            'fft_size': fft_size,
            'min_freq': frequencies[0],
            'max_freq': frequencies[-1]
        }

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Serial port closed")


def plot_fft(fft_data, show_peaks=5):
    """Plot FFT magnitude spectrum"""
    if fft_data is None:
        return

    frequencies = fft_data['frequencies']
    magnitudes = fft_data['magnitudes']

    # Find peaks
    peak_indices = np.argsort(magnitudes)[-show_peaks:][::-1]
    peak_freqs = frequencies[peak_indices]
    peak_mags = magnitudes[peak_indices]

    print("\n" + "="*60)
    print(f"Top {show_peaks} Frequencies:")
    for i, (freq, mag) in enumerate(zip(peak_freqs, peak_mags), 1):
        print(f"  {i}. {freq:7.2f} Hz  (magnitude: {mag:10.0f})")
    print("="*60)

    # Plot
    plt.figure(figsize=(14, 6))

    # Magnitude spectrum
    plt.subplot(1, 2, 1)
    plt.plot(frequencies, magnitudes, 'b-', linewidth=0.8)
    plt.plot(peak_freqs, peak_mags, 'ro', markersize=8, label='Peaks')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude')
    plt.title('FFT Magnitude Spectrum')
    plt.grid(True, alpha=0.3)
    plt.legend()

    # Log scale
    plt.subplot(1, 2, 2)
    magnitudes_db = 20 * np.log10(magnitudes + 1e-10)  # Add small epsilon to avoid log(0)
    plt.plot(frequencies, magnitudes_db, 'b-', linewidth=0.8)
    peak_mags_db = 20 * np.log10(peak_mags + 1e-10)
    plt.plot(peak_freqs, peak_mags_db, 'ro', markersize=8, label='Peaks')
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Magnitude (dB)')
    plt.title('FFT Magnitude Spectrum (dB scale)')
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.tight_layout()
    plt.show()


def main():
    parser = argparse.ArgumentParser(description='Receive and visualize FFT data from Nucleo')
    parser.add_argument('--port', type=str, default='/dev/cu.usbmodem2103',
                        help='Serial port (default: /dev/cu.usbmodem2103)')
    parser.add_argument('--baudrate', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    parser.add_argument('--peaks', type=int, default=10,
                        help='Number of peaks to highlight (default: 10)')
    parser.add_argument('--continuous', action='store_true',
                        help='Continuously receive and plot FFT data')

    args = parser.parse_args()

    print("FFT Data Receiver")
    print("="*60)
    print(f"Port: {args.port}")
    print(f"Baud Rate: {args.baudrate}")
    print("="*60)

    try:
        receiver = FFTReceiver(args.port, args.baudrate)

        if args.continuous:
            print("\nContinuous mode - Press Ctrl+C to stop")
            while True:
                fft_data = receiver.receive_fft()
                if fft_data:
                    plot_fft(fft_data, show_peaks=args.peaks)
        else:
            print("\nWaiting for FFT data...")
            fft_data = receiver.receive_fft()
            if fft_data:
                plot_fft(fft_data, show_peaks=args.peaks)

    except KeyboardInterrupt:
        print("\n\nStopped by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'receiver' in locals():
            receiver.close()


if __name__ == "__main__":
    main()
