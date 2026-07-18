"""
Test script for OLED display without microphone hardware.
Simulates chord predictions and sends them to the Nucleo board.
"""

import serial
import time
import argparse
from serial_io import list_serial_ports


class OLEDTester:
    """
    Test the OLED display by sending simulated chord predictions.
    """

    # Common guitar chords to test
    TEST_CHORDS = ['C', 'D', 'E', 'F', 'G', 'A', 'B',
                   'CM', 'DM', 'EM', 'FM', 'GM', 'AM', 'BM']

    def __init__(self, port, baudrate=115200):
        """
        Initialize connection to Nucleo board.

        Args:
            port: Serial port name (e.g., '/dev/ttyACM0', 'COM3')
            baudrate: Baud rate for serial communication
        """
        self.port = port
        self.baudrate = baudrate
        self.ser = None

        try:
            self.ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=1.0,
                write_timeout=1.0
            )
            print(f"Connected to {port} at {baudrate} baud")
            time.sleep(2)  # Wait for connection to stabilize
            self.ser.reset_input_buffer()
            self.ser.reset_output_buffer()

        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            raise

    def send_chord(self, chord_label, confidence):
        """
        Send a chord prediction to the OLED display.

        Args:
            chord_label: Chord name (e.g., 'C', 'GM', 'D')
            confidence: Confidence score (0.0 to 1.0)
        """
        try:
            message = f"CHORD:{chord_label},{confidence:.2f}\n"
            self.ser.write(message.encode('utf-8'))
            self.ser.flush()
            print(f"Sent: {message.strip()}")

            # Wait for acknowledgment
            time.sleep(0.1)
            if self.ser.in_waiting:
                response = self.ser.readline().decode('utf-8', errors='ignore').strip()
                print(f"Response: {response}")

        except Exception as e:
            print(f"Error sending chord: {e}")

    def run_automated_test(self, delay=4.0):
        """
        Run automated test cycling through different chords.

        Args:
            delay: Delay between chord changes (seconds)
        """
        print("\n=== Starting Automated OLED Test ===")
        print(f"Cycling through chords with {delay}s delay...\n")

        try:
            # Test different confidence levels
            test_cases = [
                # High confidence chords (green)
                ('C', 0.95),
                ('G', 0.88),
                ('AM', 0.92),

                # Medium confidence chords (yellow)
                ('D', 0.65),
                ('EM', 0.58),

                # Low confidence chords (red)
                ('F', 0.42),
                ('BM', 0.35),

                # More high confidence
                ('E', 0.97),
                ('DM', 0.91),
                ('A', 0.86),
            ]

            for chord, confidence in test_cases:
                print(f"\nTesting: {chord} at {confidence*100:.0f}% confidence")
                self.send_chord(chord, confidence)
                time.sleep(delay)

            print("\n=== Automated test complete ===")

        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")

    def run_cycle_test(self, delay=3.0, cycles=2):
        """
        Cycle through all available chords multiple times.

        Args:
            delay: Delay between chords (seconds)
            cycles: Number of times to cycle through all chords
        """
        print(f"\n=== Cycling through {len(self.TEST_CHORDS)} chords ===")
        print(f"Cycles: {cycles}, Delay: {delay}s\n")

        try:
            for cycle in range(cycles):
                print(f"\n--- Cycle {cycle + 1}/{cycles} ---")

                for chord in self.TEST_CHORDS:
                    # Vary confidence slightly for realism
                    confidence = 0.75 + (hash(chord + str(cycle)) % 25) / 100.0

                    print(f"Chord: {chord} ({confidence*100:.0f}%)")
                    self.send_chord(chord, confidence)
                    time.sleep(delay)

            print("\n=== Cycle test complete ===")

        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")

    def run_interactive_test(self):
        """
        Run interactive test where user can send custom chords.
        """
        print("\n=== Interactive OLED Test ===")
        print("Enter chord predictions to send to the OLED.")
        print("Format: <chord> <confidence>")
        print("Example: C 0.95")
        print("Type 'quit' to exit\n")

        try:
            while True:
                user_input = input("Enter chord and confidence: ").strip()

                if user_input.lower() in ['quit', 'exit', 'q']:
                    break

                if not user_input:
                    continue

                parts = user_input.split()

                if len(parts) != 2:
                    print("Invalid format. Use: <chord> <confidence>")
                    print("Example: C 0.95")
                    continue

                chord = parts[0].upper()

                try:
                    confidence = float(parts[1])
                    if confidence < 0.0 or confidence > 1.0:
                        print("Confidence must be between 0.0 and 1.0")
                        continue

                except ValueError:
                    print("Invalid confidence value. Must be a number between 0.0 and 1.0")
                    continue

                self.send_chord(chord, confidence)
                time.sleep(0.5)  # Brief delay for display update

        except KeyboardInterrupt:
            print("\n\nInteractive test stopped")

    def run_confidence_gradient_test(self, chord='C', steps=10, delay=2.0):
        """
        Test a single chord with varying confidence levels.
        Shows the color changes (green -> yellow -> red).

        Args:
            chord: Chord to test
            steps: Number of confidence steps
            delay: Delay between each step (seconds)
        """
        print(f"\n=== Confidence Gradient Test for '{chord}' ===")
        print(f"Testing {steps} confidence levels from high to low\n")

        try:
            for i in range(steps):
                confidence = 1.0 - (i / (steps - 1))  # From 1.0 to 0.0

                color = "GREEN"
                if confidence < 0.5:
                    color = "RED"
                elif confidence < 0.7:
                    color = "YELLOW"

                print(f"Step {i+1}/{steps}: {confidence*100:.0f}% ({color})")
                self.send_chord(chord, confidence)
                time.sleep(delay)

            print("\n=== Gradient test complete ===")

        except KeyboardInterrupt:
            print("\n\nTest interrupted by user")

    def close(self):
        """
        Close the serial connection.
        """
        if self.ser and self.ser.is_open:
            self.ser.close()
            print(f"\nClosed connection to {self.port}")


def main():
    """
    Main function for OLED testing.
    """
    parser = argparse.ArgumentParser(
        description='Test OLED display without microphone hardware',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Test Modes:
  auto         Automated test with various chords and confidence levels
  cycle        Cycle through all available chords
  gradient     Show confidence gradient for a single chord
  interactive  Manually enter chord predictions

Examples:
  python test_oled.py --port /dev/ttyACM0 --mode auto
  python test_oled.py --port COM3 --mode cycle --delay 2
  python test_oled.py --mode gradient --chord C --steps 15
  python test_oled.py --mode interactive
        """
    )

    parser.add_argument('--port', type=str, default=None,
                        help='Serial port (e.g., /dev/ttyACM0 or COM3)')
    parser.add_argument('--baudrate', type=int, default=115200,
                        help='Baud rate (default: 115200)')
    parser.add_argument('--mode', type=str,
                        choices=['auto', 'cycle', 'gradient', 'interactive'],
                        default='auto',
                        help='Test mode (default: auto)')
    parser.add_argument('--delay', type=float, default=4.0,
                        help='Delay between tests in seconds (default: 4.0)')
    parser.add_argument('--cycles', type=int, default=2,
                        help='Number of cycles for cycle mode (default: 2)')
    parser.add_argument('--chord', type=str, default='C',
                        help='Chord for gradient test (default: C)')
    parser.add_argument('--steps', type=int, default=10,
                        help='Number of steps for gradient test (default: 10)')
    parser.add_argument('--list', action='store_true',
                        help='List available serial ports and exit')

    args = parser.parse_args()

    # List ports if requested
    if args.list or args.port is None:
        available = list_serial_ports()
        if not args.list and len(available) > 0:
            print(f"\nUsing first available port: {available[0]}")
            args.port = available[0]
        elif not args.list:
            print("\nNo serial ports found!")
            print("Please specify a port with --port")
            return 1
        else:
            return 0

    # Create tester instance
    try:
        tester = OLEDTester(args.port, args.baudrate)

        # Run selected test mode
        if args.mode == 'auto':
            tester.run_automated_test(delay=args.delay)
        elif args.mode == 'cycle':
            tester.run_cycle_test(delay=args.delay, cycles=args.cycles)
        elif args.mode == 'gradient':
            tester.run_confidence_gradient_test(
                chord=args.chord.upper(),
                steps=args.steps,
                delay=args.delay
            )
        elif args.mode == 'interactive':
            tester.run_interactive_test()

        tester.close()

    except Exception as e:
        print(f"\nError: {e}")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
