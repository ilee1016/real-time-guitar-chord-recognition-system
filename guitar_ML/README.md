# Guitar Chord Classification ML Pipeline

Machine learning pipeline for real-time guitar chord recognition using FFT features from the Nucleo board.

## Overview

This system classifies guitar chords (C, G, D, A, E major) from FFT magnitude data:

1. **Nucleo** captures audio → computes FFT → sends to host via serial
2. **Host** extracts pitch features → classifies with ML model → sends prediction back
3. **Nucleo** displays chord on OLED

## Setup

### 1. Install Python Dependencies

```bash
cd guitar_ML
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create Data Directories

```bash
mkdir -p data/{C,G,D,A,E}
mkdir -p models
```

## Usage Workflow

### Step 1: Collect Training Data

Once your Nucleo is programmed to send FFT data over serial:

#### Interactive Mode (Recommended for mixed collection)
```bash
python collect_data.py --port /dev/ttyACM0
```

- Play a chord
- Wait for FFT data to be received
- Type the chord label (C, G, D, A, or E)
- Repeat for all chords

#### Batch Mode (Collect many samples of one chord)
```bash
# Collect 20 samples of C chord with 2-second intervals
python collect_data.py --port /dev/ttyACM0 --batch --chord C --num-samples 20 --delay 2.0
```

**Tips for good training data:**
- Record 20-30 samples per chord
- Vary strumming patterns (downstroke, upstroke, fingerpicking)
- Vary microphone position slightly
- Include slight timing variations (don't be too mechanical)

### Step 2: Train the Model

After collecting data:

```bash
python train_model.py
```

This will:
- Load all samples from `data/`
- Extract pitch intensity features
- Train multiple models (k-NN, Logistic Regression, Random Forest)
- Evaluate and select the best model
- Save the trained model to `models/`

Expected output structure:
```
models/
  ├── chord_classifier.pkl   # Trained model
  ├── scaler.pkl              # Feature normalizer
  └── metadata.json           # Config (sample_rate, fft_size, labels)
```

### Step 3: Run Inference

Start real-time chord classification:

```bash
python run_inference.py --serial-port /dev/ttyACM0 --baudrate 115200
```

Or test on a single file:

```bash
python run_inference.py --test-file data/C/sample_0.npy
```

## Serial Communication Protocol

### Nucleo → Host (FFT Data)

```
"FFT_START\n"
<fft_size: uint32, 4 bytes, little-endian>
<fft_magnitude: float32 array, fft_size*4 bytes, little-endian>
"FFT_END\n"
```

### Host → Nucleo (Prediction)

```
"CHORD:<label>,<confidence>\n"
```

Example: `CHORD:C,0.95\n`

## File Descriptions

| File | Purpose |
|------|---------|
| `features.py` | Extract pitch intensity features from FFT |
| `train_model.py` | Train and evaluate ML classifiers |
| `run_inference.py` | Real-time chord prediction |
| `serial_io.py` | Serial communication with Nucleo |
| `collect_data.py` | Record training data |
| `requirements.txt` | Python dependencies |

## Feature Engineering

The feature extractor (`features.py`) computes:

1. **Chromatic note intensities**: Average FFT magnitude around 18 note frequencies (C through G5)
2. **Harmonic content**: 2nd and 3rd harmonics of each guitar string frequency

This captures both the fundamental pitches and timbral characteristics of chords.

## Model Selection

The training script evaluates:
- **k-NN (k=3, k=5)**: Simple, works well for small datasets
- **Logistic Regression**: Fast, interpretable
- **Random Forest**: Handles complex patterns

Best model is auto-selected based on test accuracy.

## Troubleshooting

### Serial Port Issues

List available ports:
```bash
python serial_io.py --list
```

Test connection:
```bash
python serial_io.py --port /dev/ttyACM0
```

### Common Issues

**"No training data found"**
- Ensure data is in `data/<chord>/sample_*.npy` format
- Run `collect_data.py` to record samples

**"Model file not found"**
- Run `train_model.py` first to create the model

**Serial timeout**
- Check Nucleo is connected and programmed
- Verify correct port and baud rate
- Check that Nucleo is sending FFT data in correct format

## Future Improvements

- **On-device inference**: Deploy the trained model directly on the STM32 using TinyML, eliminating the host dependency
- **Expanded chord vocabulary**: Add minor chords, seventh chords, and suspended chords by extending `CHORD_LABELS`
- **Larger training dataset**: More samples per chord, varied strumming patterns, and multiple microphone positions would improve generalization
- **Reduced latency**: Tune FFT window size and sampling rate for the best accuracy/speed trade-off

## Parameters to Match Nucleo

Update these in your scripts if your Nucleo uses different settings:

```python
--sample-rate 8000     # Must match Nucleo ADC sampling rate
--fft-size 512         # Must match Nucleo FFT window size
--baudrate 115200      # Must match Nucleo serial baud rate
```
