"""
Real-time chord inference using trained ML model.
Receives FFT data from Nucleo via serial, classifies chord, and sends result back.
"""

import numpy as np
import pickle
import json
import time
from pathlib import Path
import serial_io
import features


class ChordClassifier:
    """
    Wrapper for loaded ML model to classify guitar chords from FFT data.
    """

    def __init__(self, model_dir='models'):
        """
        Load trained model, scaler, and metadata.

        Args:
            model_dir: Directory containing saved model files
        """
        model_path = Path(model_dir)

        # Load model
        model_file = model_path / 'chord_classifier.pkl'
        if not model_file.exists():
            raise FileNotFoundError(f"Model file not found: {model_file}")

        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)

        print(f"Loaded model from {model_file}")

        # Load scaler
        scaler_file = model_path / 'scaler.pkl'
        if not scaler_file.exists():
            raise FileNotFoundError(f"Scaler file not found: {scaler_file}")

        with open(scaler_file, 'rb') as f:
            self.scaler = pickle.load(f)

        print(f"Loaded scaler from {scaler_file}")

        # Load metadata
        metadata_file = model_path / 'metadata.json'
        if not metadata_file.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_file}")

        with open(metadata_file, 'r') as f:
            self.metadata = json.load(f)

        self.sample_rate = self.metadata['sample_rate']
        self.fft_size = self.metadata['fft_size']
        self.chord_labels = self.metadata['chord_labels']

        print(f"Model configuration:")
        print(f"  Sample rate: {self.sample_rate} Hz")
        print(f"  FFT size: {self.fft_size}")
        print(f"  Chord labels: {self.chord_labels}")

    def predict(self, fft_magnitude):
        """
        Predict chord from FFT magnitude spectrum.

        Args:
            fft_magnitude: FFT magnitude array

        Returns:
            Tuple of (predicted_label, confidence)
        """
        # Extract features
        feature_vector = features.extract_pitch_features(
            fft_magnitude, self.sample_rate, self.fft_size
        )

        # Normalize features
        feature_vector = self.scaler.transform(feature_vector.reshape(1, -1))

        # Predict
        prediction = self.model.predict(feature_vector)[0]

        # Get confidence (probability)
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(feature_vector)[0]
            confidence = np.max(probabilities)
        else:
            # For models without probability (e.g., k-NN with uniform weights)
            # Use distance-based confidence
            if hasattr(self.model, 'kneighbors'):
                distances, _ = self.model.kneighbors(feature_vector)
                # Convert distance to confidence (closer = higher confidence)
                avg_distance = np.mean(distances)
                confidence = 1.0 / (1.0 + avg_distance)
            else:
                confidence = 1.0  # Unknown confidence

        return prediction, confidence


def run_inference_loop(classifier, serial_port, baudrate=115200):
    """
    Run continuous inference loop:
    1. Receive FFT data from Nucleo via serial
    2. Classify chord
    3. Send prediction back to Nucleo

    Args:
        classifier: ChordClassifier instance
        serial_port: Serial port name (e.g., '/dev/ttyACM0' or 'COM3')
        baudrate: Serial baud rate
    """
    print(f"\n{'='*60}")
    print("Starting inference loop...")
    print(f"{'='*60}")
    print("Waiting for FFT data from Nucleo...")

    ser = serial_io.SerialConnection(serial_port, baudrate)

    try:
        while True:
            # Receive FFT data
            fft_data = ser.receive_fft_data()

            if fft_data is not None:
                # Classify chord
                start_time = time.time()
                predicted_chord, confidence = classifier.predict(fft_data)
                inference_time = (time.time() - start_time) * 1000  # Convert to ms

                print(f"\nPrediction: {predicted_chord} (confidence: {confidence:.2f})")
                print(f"Inference time: {inference_time:.2f} ms")

                # Send prediction back to Nucleo
                ser.send_prediction(predicted_chord, confidence)

            time.sleep(0.01)  # Small delay to avoid busy waiting

    except KeyboardInterrupt:
        print("\n\nStopping inference loop...")
    finally:
        ser.close()


def test_inference_from_file(classifier, fft_file):
    """
    Test inference on a single FFT file (for debugging).

    Args:
        classifier: ChordClassifier instance
        fft_file: Path to .npy file containing FFT data
    """
    print(f"Testing inference on {fft_file}...")

    # Load FFT data
    data = np.load(fft_file, allow_pickle=True)

    if isinstance(data, dict):
        fft_magnitude = data['fft']
    else:
        fft_magnitude = data

    # Predict
    predicted_chord, confidence = classifier.predict(fft_magnitude)

    print(f"\nPrediction: {predicted_chord}")
    print(f"Confidence: {confidence:.3f}")

    return predicted_chord, confidence


def main():
    """
    Main inference entry point.
    """
    import argparse

    parser = argparse.ArgumentParser(description='Run chord classification inference')
    parser.add_argument('--serial-port', type=str, default='/dev/ttyACM0',
                        help='Serial port for Nucleo communication')
    parser.add_argument('--baudrate', type=int, default=115200,
                        help='Serial baud rate')
    parser.add_argument('--test-file', type=str, default=None,
                        help='Test on a single FFT file instead of live serial')
    parser.add_argument('--model-dir', type=str, default='models',
                        help='Directory containing trained model')

    args = parser.parse_args()

    # Load classifier
    print("Loading trained model...")
    classifier = ChordClassifier(model_dir=args.model_dir)

    if args.test_file:
        # Test mode: run inference on a single file
        test_inference_from_file(classifier, args.test_file)
    else:
        # Live mode: continuous inference from serial
        run_inference_loop(classifier, args.serial_port, args.baudrate)


if __name__ == '__main__':
    main()
