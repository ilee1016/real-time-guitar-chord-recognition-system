"""
Train ML models for guitar chord classification.
Supports k-NN, Logistic Regression, and Random Forest classifiers.
"""

import numpy as np
import pickle
import os
import json
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import features


# Chord labels
CHORD_LABELS = ['C', 'G', 'D', 'A', 'E']


def load_training_data(data_dir='data'):
    """
    Load training data from the data directory.

    Expected directory structure:
        data/
            C/
                sample_0.npy  (FFT magnitude data)
                sample_1.npy
                ...
            G/
                ...
            D/
                ...
            A/
                ...
            E/
                ...

    Args:
        data_dir: Path to data directory

    Returns:
        X: Feature matrix (n_samples, n_features)
        y: Label array (n_samples,)
        metadata: Dictionary with sample_rate and fft_size
    """
    data_path = Path(data_dir)

    X_list = []
    y_list = []
    metadata = None

    for chord_label in CHORD_LABELS:
        chord_dir = data_path / chord_label
        if not chord_dir.exists():
            print(f"Warning: Directory {chord_dir} does not exist. Skipping {chord_label}.")
            continue

        # Load all .npy files in this chord directory
        for sample_file in sorted(chord_dir.glob('*.npy')):
            try:
                data = np.load(sample_file, allow_pickle=True)

                # Handle two formats:
                # 1. Just FFT magnitude array
                # 2. Dictionary with 'fft', 'sample_rate', 'fft_size'
                if isinstance(data, dict):
                    fft_magnitude = data['fft']
                    sample_rate = data.get('sample_rate', 8000)
                    fft_size = data.get('fft_size', len(fft_magnitude) * 2 - 2)
                else:
                    fft_magnitude = data
                    # Default values if not provided
                    sample_rate = 8000
                    fft_size = len(fft_magnitude) * 2 - 2

                # Store metadata from first sample
                if metadata is None:
                    metadata = {
                        'sample_rate': sample_rate,
                        'fft_size': fft_size
                    }

                # Extract features
                feature_vector = features.extract_pitch_features(
                    fft_magnitude, sample_rate, fft_size
                )

                X_list.append(feature_vector)
                y_list.append(chord_label)

            except Exception as e:
                print(f"Error loading {sample_file}: {e}")

    if len(X_list) == 0:
        raise ValueError("No training data found!")

    X = np.array(X_list)
    y = np.array(y_list)

    print(f"Loaded {len(X)} samples across {len(set(y))} chord classes")
    for chord in CHORD_LABELS:
        count = np.sum(y == chord)
        print(f"  {chord}: {count} samples")

    return X, y, metadata


def train_models(X_train, y_train, X_test, y_test):
    """
    Train multiple classifier models and compare performance.

    Args:
        X_train: Training features
        y_train: Training labels
        X_test: Test features
        y_test: Test labels

    Returns:
        Dictionary of trained models with their scores
    """
    models = {
        'knn_3': KNeighborsClassifier(n_neighbors=3),
        'knn_5': KNeighborsClassifier(n_neighbors=5),
        'logistic_regression': LogisticRegression(max_iter=1000, random_state=42),
        'random_forest': RandomForestClassifier(n_estimators=50, random_state=42)
    }

    results = {}

    for name, model in models.items():
        print(f"\n{'='*60}")
        print(f"Training {name}...")
        print(f"{'='*60}")

        # Train the model
        model.fit(X_train, y_train)

        # Evaluate on training set
        train_score = model.score(X_train, y_train)
        print(f"Training accuracy: {train_score:.3f}")

        # Evaluate on test set
        test_score = model.score(X_test, y_test)
        print(f"Test accuracy: {test_score:.3f}")

        # Cross-validation score (if enough data)
        if len(X_train) >= 10:
            cv_scores = cross_val_score(model, X_train, y_train, cv=min(5, len(X_train)))
            print(f"Cross-validation accuracy: {cv_scores.mean():.3f} (+/- {cv_scores.std():.3f})")

        # Classification report
        y_pred = model.predict(X_test)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))

        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))

        results[name] = {
            'model': model,
            'train_score': train_score,
            'test_score': test_score
        }

    return results


def save_model(model, scaler, metadata, save_path='models'):
    """
    Save the trained model, scaler, and metadata.

    Args:
        model: Trained scikit-learn model
        scaler: Fitted StandardScaler
        metadata: Dictionary with sample_rate, fft_size, etc.
        save_path: Directory to save model files
    """
    save_dir = Path(save_path)
    save_dir.mkdir(exist_ok=True)

    # Save model
    model_file = save_dir / 'chord_classifier.pkl'
    with open(model_file, 'wb') as f:
        pickle.dump(model, f)
    print(f"\nModel saved to {model_file}")

    # Save scaler
    scaler_file = save_dir / 'scaler.pkl'
    with open(scaler_file, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Scaler saved to {scaler_file}")

    # Save metadata
    metadata_file = save_dir / 'metadata.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"Metadata saved to {metadata_file}")


def main():
    """
    Main training pipeline.
    """
    print("="*60)
    print("Guitar Chord Classification - Model Training")
    print("="*60)

    # Load data
    print("\nLoading training data...")
    X, y, metadata = load_training_data('data')

    # Split into train/test
    test_size = 0.2
    if len(X) < 20:
        print(f"\nWarning: Only {len(X)} samples. Using 1 sample per class for testing.")
        # Ensure at least 1 sample per class in test set
        test_size = min(0.3, 5 / len(X))

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42, stratify=y
    )

    print(f"\nTraining set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")

    # Normalize features
    print("\nNormalizing features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train models
    results = train_models(X_train_scaled, y_train, X_test_scaled, y_test)

    # Select best model based on test accuracy
    best_model_name = max(results, key=lambda k: results[k]['test_score'])
    best_model = results[best_model_name]['model']
    best_score = results[best_model_name]['test_score']

    print(f"\n{'='*60}")
    print(f"Best model: {best_model_name}")
    print(f"Test accuracy: {best_score:.3f}")
    print(f"{'='*60}")

    # Save the best model
    metadata['model_name'] = best_model_name
    metadata['chord_labels'] = CHORD_LABELS
    save_model(best_model, scaler, metadata, save_path='models')

    print("\nTraining complete!")


if __name__ == '__main__':
    main()
