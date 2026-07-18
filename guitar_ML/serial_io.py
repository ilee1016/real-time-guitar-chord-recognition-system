"""
Serial communication module for Nucleo board.
Handles receiving FFT data and sending chord predictions.
"""

import serial
import struct
import numpy as np
import time


class SerialConnection:
    """
    Manages serial communication with the Nucleo board.

    Protocol:
    - Nucleo sends FFT data as binary float array
    - Host sends predictions as text strings
    """

    def __init__(self, port, baudrate=115200, timeout=1.0):
        """
        Initialize serial connection.

        Args:
            port: Serial port name (e.g., '/dev/ttyACM0', 'COM3')
            baudrate: Baud rate for serial communication
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout
            )
            print(f"Connected to {port} at {baudrate} baud")
            time.sleep(2)  # Wait for connection to stabilize
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            raise

    def receive_fft_data(self):
        """
        Receive FFT magnitude data from Nucleo.

        Expected format:
        1. Start marker: "FFT_START\n"
        2. FFT size (4 bytes, uint32)
        3. FFT data (FFT_size * 4 bytes, float32 array)
        4. End marker: "FFT_END\n"

        Returns:
            numpy array of FFT magnitudes, or None if no valid data
        """
        try:
            # Read until we find the start marker
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()

            if line == "FFT_START":
                # Read FFT size (4 bytes)
                size_bytes = self.ser.read(4)
                if len(size_bytes) != 4:
                    print("Error: Could not read FFT size")
                    return None

                fft_size = struct.unpack('<I', size_bytes)[0]  # Little-endian uint32

                if fft_size == 0 or fft_size > 10000:
                    print(f"Error: Invalid FFT size: {fft_size}")
                    return None

                # Read FFT data (fft_size * 4 bytes)
                num_bytes = fft_size * 4
                fft_bytes = self.ser.read(num_bytes)

                if len(fft_bytes) != num_bytes:
                    print(f"Error: Expected {num_bytes} bytes, got {len(fft_bytes)}")
                    return None

                # Unpack as float32 array
                fft_data = struct.unpack(f'<{fft_size}f', fft_bytes)  # Little-endian floats
                fft_array = np.array(fft_data, dtype=np.float32)

                # Read end marker
                end_line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if end_line != "FFT_END":
                    print(f"Warning: Expected 'FFT_END', got '{end_line}'")

                print(f"Received FFT data: {fft_size} bins")
                return fft_array

        except Exception as e:
            print(f"Error receiving FFT data: {e}")
            return None

        return None

    def send_prediction(self, chord_label, confidence):
        """
        Send chord prediction back to Nucleo.

        Format: "CHORD:<label>,<confidence>\n"
        Example: "CHORD:C,0.95\n"

        Args:
            chord_label: Predicted chord name (string)
            confidence: Confidence score (0.0 to 1.0)
        """
        try:
            message = f"CHORD:{chord_label},{confidence:.2f}\n"
            self.ser.write(message.encode('utf-8'))
            self.ser.flush()
            print(f"Sent: {message.strip()}")

        except Exception as e:
            print(f"Error sending prediction: {e}")

    def send_command(self, command):
        """
        Send a command string to the Nucleo.

        Args:
            command: Command string to send
        """
        try:
            self.ser.write(f"{command}\n".encode('utf-8'))
            self.ser.flush()

        except Exception as e:
            print(f"Error sending command: {e}")

    def receive_line(self):
        """
        Receive a single line of text from Nucleo.

        Returns:
            Decoded line string, or None if timeout
        """
        try:
            line = self.ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                return line
        except Exception as e:
            print(f"Error receiving line: {e}")

        return None

    def close(self):
        """
        Close the serial connection.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"Closed connection to {self.port}")


def list_serial_ports():
    """
    List available serial ports.

    Returns:
        List of available port names
    """
    import serial.tools.list_ports

    ports = serial.tools.list_ports.comports()
    available_ports = []

    print("Available serial ports:")
    for port in ports:
        print(f"  {port.device}: {port.description}")
        available_ports.append(port.device)

    return available_ports


def test_serial_connection(port, baudrate=115200):
    """
    Test serial connection by reading lines from Nucleo.

    Args:
        port: Serial port name
        baudrate: Baud rate
    """
    print(f"Testing serial connection to {port}...")
    ser = SerialConnection(port, baudrate)

    try:
        print("Listening for data (press Ctrl+C to stop)...")
        while True:
            line = ser.receive_line()
            if line:
                print(f"Received: {line}")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nStopping test...")
    finally:
        ser.close()


if __name__ == '__main__':
    """
    Test serial communication.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Test serial communication')
    parser.add_argument('--port', type=str, default=None,
                        help='Serial port (e.g., /dev/ttyACM0 or COM3)')
    parser.add_argument('--baudrate', type=int, default=115200,
                        help='Baud rate')
    parser.add_argument('--list', action='store_true',
                        help='List available serial ports')

    args = parser.parse_args()

    if args.list or args.port is None:
        available = list_serial_ports()
        if not args.list and len(available) > 0:
            print(f"\nUsing first available port: {available[0]}")
            args.port = available[0]
        elif not args.list:
            print("No serial ports found!")
            exit(1)
        else:
            exit(0)

    test_serial_connection(args.port, args.baudrate)
