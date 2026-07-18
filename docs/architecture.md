# System Architecture

## Overview

The system is split into two subsystems that communicate over USB serial:

**Embedded (STM32 Nucleo-F401RE)**
- Captures audio via the STM32 12-bit ADC at 8 kHz
- Computes a 512-point RFFT using ARM CMSIS-DSP
- Transmits the FFT magnitude spectrum to the host
- Receives chord predictions and displays them on the SSD1331 OLED

**Host (Python — `guitar_ML/`)**
- Receives raw FFT magnitude data over serial
- Extracts pitch intensity and harmonic features
- Classifies the chord using a trained ML model
- Sends the chord label and confidence score back to the microcontroller

## Data Flow

```
Guitar Signal
      │
      ▼
MAX9814 Microphone Amplifier
      │  (analog audio)
      ▼
STM32 ADC  (12-bit, 8 kHz)
      │  (raw PCM samples)
      ▼
ARM CMSIS-DSP RFFT  (512-point)
      │  (FFT magnitude spectrum, float32[256])
      ▼
USB Serial  (115200 baud)
      │
      ▼
guitar_ML/features.py  (feature extraction)
      │  (30-element feature vector)
      ▼
guitar_ML/run_inference.py  (ML classifier)
      │  (chord label + confidence score)
      ▼
USB Serial  (115200 baud)
      │
      ▼
STM32 → SSD1331 OLED
```

## Serial Protocol

### Nucleo → Host: FFT Data

Binary framed packet, little-endian:

```
"FFT_START\n"
<fft_size: uint32_t, 4 bytes>
<fft_magnitude: float32[], fft_size × 4 bytes>
"FFT_END\n"
```

### Host → Nucleo: Prediction

UTF-8 string:

```
"CHORD:<label>,<confidence>\n"
```

Example: `CHORD:G,0.91`

Implemented in `guitar_ML/serial_io.py` (`SerialConnection.receive_fft_data` and `send_prediction`).

## Feature Extraction

Implemented in `guitar_ML/features.py`. Two feature groups are computed per FFT frame:

**Chromatic note intensities (18 features)**
Average FFT magnitude within a ±10 Hz band around each note from C3 to G5. Captures which pitches are present in the chord.

**Harmonic content (12 features)**
Average magnitude at the 2nd and 3rd harmonics of each open guitar string fundamental (E2, A2, D3, G3, B3, E4). Captures timbral characteristics that help discriminate chords sharing common notes.

Total feature vector: **30 features**.

## ML Model

Implemented in `guitar_ML/train_model.py`. Four configurations are trained and compared:

| Model | Parameter |
|---|---|
| k-NN | k = 3 |
| k-NN | k = 5 |
| Logistic Regression | max_iter = 1000 |
| Random Forest | n_estimators = 50 |

Features are normalized with `StandardScaler` before training and at inference time. The model with the highest held-out test accuracy is saved to `models/chord_classifier.pkl` alongside `models/scaler.pkl` and `models/metadata.json`.

Typical recommendation: 20–30 samples per chord for reliable classification.

## Implementation Status

| Component | Status |
|---|---|
| ARM CMSIS-DSP library integration | Complete — validated on hardware (`test_cmsis_dsp.cpp`) |
| SSD1331 OLED display driver | Complete (`ssd1331.cpp` / `ssd1331.h`) |
| Serial communication protocol | Defined |
| Host-side ML pipeline | Complete |
| Full audio capture → FFT → serial TX embedded firmware | In progress |
