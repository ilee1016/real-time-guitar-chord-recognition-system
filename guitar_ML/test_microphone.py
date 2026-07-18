"""
Test script for microphone audio capture.
Receives audio samples from Nucleo and visualizes/plays them.
"""

import serial
import struct
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import time
import argparse


class MicrophoneTester:
    """
    Test microphone by receiving and visualizing audio data.
    """

    def __init__(self, port, baudrate=115200, sample_rate=8000):
        """
        Initialize serial connection.

        Args:
            port: Serial port name (e.g., '/dev/ttyACM0', 'COM3')
            baudrate: Baud rate for serial communication
            sample_rate: Expected sample rate in Hz
        """
        self.port = port
        self.baudrate = baudrate
        self.sample_rate = sample_rate
        self.ser = None

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=10.0,
                write_timeout=5.0
            )
            print(f"Connected to {port} at {baudrate} baud")
            time.sleep(2)  # Wait for connection to stabilize
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            raise

    def receive_audio_data(self):
        """
        Receive audio data from Nucleo.

        Expected format:
        1. Start marker: "AUDIO_START\n"
        2. Buffer size (4 bytes, uint32)
        3. Audio data (size * 2 bytes, uint16 array)
        4. End marker: "AUDIO_END\n"

        Returns:
            numpy array of audio samples (uint16), or None if no valid data
        """
        try:
            # Read until we find the start marker
            while True:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Received: {line}")

                if line == "AUDIO_START":
                    break

            # Read buffer size (4 bytes)
            size_bytes = self.ser.read(4)
            if len(size_bytes) != 4:
                print("Error: Could not read buffer size")
                return None

            buffer_size = struct.unpack('<I', size_bytes)[0]  # Little-endian uint32

            if buffer_size == 0 or buffer_size > 50000:
                print(f"Error: Invalid buffer size: {buffer_size}")
                return None

            print(f"Reading {buffer_size} samples...")

            # Read audio data (buffer_size * 2 bytes)
            num_bytes = buffer_size * 2
            audio_bytes = self.ser.read(num_bytes)

            if len(audio_bytes) != num_bytes:
                print(f"Error: Expected {num_bytes} bytes, got {len(audio_bytes)}")
                return None

            # Unpack as uint16 array
            audio_data = struct.unpack(f'<{buffer_size}H', audio_bytes)  # Little-endian uint16
            audio_array = np.array(audio_data, dtype=np.uint16)

            # Read end marker and any debug messages
            for _ in range(3):
                if self.ser.in_waiting:
                    line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    print(f"Received: {line}")

            return audio_array

        except Exception as e:
            print(f"Error receiving audio data: {e}")
            return None

    def plot_audio(self, audio_data):
        """
        Plot audio waveform.

        Args:
            audio_data: numpy array of audio samples
        """
        if audio_data is None:
            return

        # Convert to time axis
        duration = len(audio_data) / self.sample_rate
        time_axis = np.linspace(0, duration * 1000, len(audio_data))  # milliseconds

        # Create figure with subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

        # Plot waveform
        ax1.plot(time_axis, audio_data, linewidth=0.5)
        ax1.set_xlabel('Time (ms)')
        ax1.set_ylabel('ADC Value (0-65535)')
        ax1.set_title(f'Audio Waveform - {len(audio_data)} samples at {self.sample_rate} Hz')
        ax1.grid(True, alpha=0.3)

        # Calculate statistics
        mean_val = np.mean(audio_data)
        std_val = np.std(audio_data)
        min_val = np.min(audio_data)
        max_val = np.max(audio_data)
        peak_to_peak = max_val - min_val

        # Add statistics text
        stats_text = (
            f'Mean: {mean_val:.1f}\n'
            f'Std Dev: {std_val:.1f}\n'
            f'Min: {min_val}\n'
            f'Max: {max_val}\n'
            f'Peak-to-Peak: {peak_to_peak}\n'
            f'Duration: {duration*1000:.1f} ms'
        )
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        # Plot histogram
        ax2.hist(audio_data, bins=100, edgecolor='black', alpha=0.7)
        ax2.set_xlabel('ADC Value')
        ax2.set_ylabel('Count')
        ax2.set_title('Distribution of ADC Values')
        ax2.axvline(mean_val, color='red', linestyle='--', label=f'Mean: {mean_val:.1f}')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def play_audio(self, audio_data):
        """
        Play audio through speakers (requires pyaudio).

        Args:
            audio_data: numpy array of audio samples (uint16)
        """
        try:
            import pyaudio

            # Convert uint16 to normalized float32 for playback
            audio_float = (audio_data.astype(np.float32) - 32768) / 32768.0

            # Initialize PyAudio
            p = pyaudio.PyAudio()

            # Open stream
            stream = p.open(
                format=pyaudio.paFloat32,
                channels=1,
                rate=self.sample_rate,
                output=True
            )

            print("\nPlaying audio...")
            stream.write(audio_float.tobytes())

            # Cleanup
            stream.stop_stream()
            stream.close()
            p.terminate()

            print("Playback complete.")

        except ImportError:
            print("PyAudio not installed. Install with: pip install pyaudio")
        except Exception as e:
            print(f"Error playing audio: {e}")

    def save_audio(self, audio_data, filename='captured_audio.npy'):
        """
        Save audio data to file.

        Args:
            audio_data: numpy array of audio samples
            filename: Output filename
        """
        np.save(filename, audio_data)
        print(f"Saved audio data to {filename}")

    def run_continuous_plot(self):
        """
        Continuously receive and plot audio data in real-time.
        """
        print("\n=== Continuous Audio Monitoring ===")
        print("Press Ctrl+C to stop\n")

        # Setup plot
        fig, ax = plt.subplots(figsize=(12, 6))
        line, = ax.plot([], [], linewidth=0.5)
        ax.set_xlabel('Sample Index')
        ax.set_ylabel('ADC Value (0-65535)')
        ax.set_title('Real-time Audio Waveform')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 65535)

        text_box = ax.text(0.02, 0.98, '', transform=ax.transAxes,
                          verticalalignment='top',
                          bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        try:
            while True:
                audio_data = self.receive_audio_data()

                if audio_data is not None:
                    # Update plot
                    line.set_data(range(len(audio_data)), audio_data)
                    ax.set_xlim(0, len(audio_data))

                    # Update statistics
                    mean_val = np.mean(audio_data)
                    std_val = np.std(audio_data)
                    peak_to_peak = np.max(audio_data) - np.min(audio_data)

                    stats_text = (
                        f'Mean: {mean_val:.1f}\n'
                        f'Std Dev: {std_val:.1f}\n'
                        f'P2P: {peak_to_peak}\n'
                        f'Samples: {len(audio_data)}'
                    )
                    text_box.set_text(stats_text)

                    plt.pause(0.01)

        except KeyboardInterrupt:
            print("\nStopped monitoring")
        finally:
            plt.close()

    def close(self):
        """
        Close the serial connection.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Closed connection to {self.port}")


def main():
    """
    Main function for microphone testing.
    """
    parser = argparse.ArgumentParser(
        description='Test microphone audio capture from Nucleo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Capture and plot one sample
  python test_microphone.py --port /dev/cu.usbmodem103

  # Continuous monitoring
  python test_microphone.py --port /dev/cu.usbmodem103 --continuous

  # Capture and play audio
  python test_microphone.py --port /dev/cu.usbmodem103 --play

  # Save captured audio
  python test_microphone.py --port /dev/cu.usbmodem103 --save audio.npy
        """
    )

    parser.add_argument('--port', type=str, default='/dev/cu.usbmodem103',
                        help='Serial port (e.g., /dev/ttyACM0 or COM3)')
    parser.add_argument('--baudrate', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    parser.add_argument('--sample-rate', type=int, default=8000,
                        help='Sample rate in Hz (default: 8000)')
    parser.add_argument('--continuous', action='store_true',
                        help='Continuous monitoring mode')
    parser.add_argument('--play', action='store_true',
                        help='Play captured audio through speakers')
    parser.add_argument('--save', type=str, default=None,
                        help='Save captured audio to file')

    args = parser.parse_args()

    # Create tester instance
    try:
        tester = MicrophoneTester(args.port, args.baudrate, args.sample_rate)

        if args.continuous:
            # Continuous monitoring with real-time plot
            tester.run_continuous_plot()
        else:
            # Single capture
            print("Waiting for audio data...")
            audio_data = tester.receive_audio_data()

            if audio_data is not None:
                print(f"\nReceived {len(audio_data)} samples")

                # Plot
                tester.plot_audio(audio_data)

                # Play if requested
                if args.play:
                    tester.play_audio(audio_data)

                # Save if requested
                if args.save:
                    tester.save_audio(audio_data, args.save)

        tester.close()

    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
