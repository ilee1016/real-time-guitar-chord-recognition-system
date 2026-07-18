# Real-Time Guitar Chord Recognition System

An embedded machine learning system for real-time guitar chord recognition. The STM32 Nucleo-F401RE handles audio acquisition and DSP via ARM CMSIS-DSP; a Python ML pipeline on the host computer performs classification and returns predictions for display on an OLED.

## Overview

This project implements an end-to-end embedded machine learning pipeline for guitar chord recognition. Signal acquisition and FFT processing run on the microcontroller; ML classification runs on a connected host computer. The two subsystems communicate over USB serial — FFT magnitude data flows to the host, and chord predictions flow back to the display. See [docs/architecture.md](docs/architecture.md) for a detailed breakdown.

## Technical Highlights

- ARM CMSIS-DSP RFFT integrated and validated on STM32 Nucleo-F401RE
- SSD1331 OLED display driver with text rendering and hardware-accelerated drawing
- Complete host-side ML pipeline: data collection, feature extraction, training, and real-time inference
- Bidirectional serial protocol for microcontroller ↔ host data exchange
- Automatic classifier selection from k-NN, Logistic Regression, and Random Forest
- Pitch intensity and harmonic feature extraction from FFT magnitude spectra

## System Architecture

```text
        Guitar
           │
           ▼
 Electret Microphone
           │
           ▼
 STM32 Nucleo-F401RE
 ├── ADC Sampling
 ├── FFT (CMSIS-DSP)
 └── Serial Transmission
           │
           ▼
     Host Computer
 ├── Feature Extraction
 ├── ML Classification
 └── Prediction
           │
           ▼
 STM32 Nucleo-F401RE
           │
           ▼
      OLED Display
```

## Hardware

- STM32 Nucleo-F401RE
- Electret microphone
- SSD1331 OLED display
- Breadboard and signal conditioning circuit
- USB serial connection

## Software Stack

### Embedded

- C++
- Mbed OS
- ARM CMSIS-DSP
- ADC audio sampling
- FFT processing
- Serial communication
- OLED driver

### Host

- Python
- NumPy
- scikit-learn
- PySerial

## Machine Learning Pipeline

1. Capture guitar audio using the microphone.
2. Sample the signal with the STM32 ADC.
3. Compute an FFT using ARM CMSIS-DSP.
4. Transmit spectral data to the host computer.
5. Extract frequency-domain features.
6. Classify the chord using a machine learning model.
7. Send the prediction back to the STM32.
8. Display the predicted chord and confidence score on the OLED.

Supported chords:

- C Major
- G Major
- D Major
- A Major
- E Major

The host-side pipeline (steps 5–7) is fully implemented in `guitar_ML/`. The embedded firmware for audio capture, FFT computation, and serial transmission (steps 1–4) is in progress; the ARM CMSIS-DSP layer has been validated on hardware in `test_cmsis_dsp.cpp`.

## Implementation Status

| Component | Status |
|---|---|
| ARM CMSIS-DSP library integration | Complete — validated on hardware |
| SSD1331 OLED display driver | Complete |
| Serial communication protocol | Defined |
| Host-side ML pipeline | Complete |
| Full audio capture → FFT → serial TX embedded firmware | In progress |

## System Specifications

- 8 kHz audio sampling rate via STM32 ADC
- Near real-time end-to-end inference
- Continuous operation without manual reset
- Low-latency serial communication at 115200 baud
- Embedded FFT computation within STM32 memory constraints

## Repository Structure

```text
.
├── test_cmsis_dsp.cpp        # CMSIS-DSP integration test (hardware validation)
├── ssd1331.cpp / ssd1331.h   # OLED display driver
├── CMakeLists.txt            # Embedded build configuration
├── mbed_app.json             # Mbed OS target configuration
├── mbed-os.lib               # Mbed OS submodule reference
├── MAX9814.pdf               # Microphone amplifier datasheet
├── CMSIS-DSP/                # Vendored ARM CMSIS-DSP library
│   ├── Include/
│   └── Source/
├── docs/
│   ├── architecture.md       # System design and data flow
│   └── hardware.md           # Component specs and signal path
└── guitar_ML/                # Host-side ML pipeline
    ├── README.md
    ├── requirements.txt
    ├── collect_data.py       # Record training data from Nucleo
    ├── features.py           # FFT feature extraction
    ├── train_model.py        # Train and evaluate ML classifiers
    ├── run_inference.py      # Real-time chord classification
    ├── serial_io.py          # Serial communication with Nucleo
    ├── test_fft.py           # FFT spectrum visualizer
    ├── test_microphone.py    # Audio capture verification
    ├── test_oled.py          # OLED display testing
    └── data/                 # Training data (per-chord FFT samples)
        ├── C/
        ├── G/
        ├── D/
        ├── A/
        └── E/
```

## Building the Firmware

The embedded firmware uses [Mbed OS](https://os.mbed.com/) and CMake. The build was developed with Arm Compiler 6 (ARMC6) targeting the Nucleo-F401RE.

**Prerequisites:**
- [Arm Compiler 6](https://developer.arm.com/tools-and-software/embedded/arm-compiler)
- CMake ≥ 3.19 and [Ninja](https://ninja-build.org/)
- Python 3 with Mbed tools: `pip install mbed-tools`

**Initialize Mbed OS (first clone only):**

```bash
git submodule update --init
```

**Configure and build:**

```bash
mbed-tools configure -m NUCLEO_F401RE -t ARMC6
cmake -S . -B cmake_build/NUCLEO_F401RE/develop/ARMC6 -GNinja
cmake --build cmake_build/NUCLEO_F401RE/develop/ARMC6
```

**Flash:** Copy the generated `guitar-fft-cmsis-dsp.bin` to the Nucleo USB mass storage drive (appears as `NUCLEO` when connected).

Currently this builds and runs `test_cmsis_dsp.cpp`, which validates the CMSIS-DSP library on hardware.

## Challenges

- Working within the STM32's memory and processing constraints
- Balancing FFT size for frequency resolution and execution time
- Building reliable low-latency serial communication
- Extracting meaningful frequency features despite harmonics and noise
- Integrating embedded software with host-side machine learning

## Future Improvements

- Deploy the machine learning model directly on the microcontroller using TinyML
- Expand support for additional chord types (minor, seventh, suspended, etc.)
- Increase the training dataset to improve model accuracy
- Display chord diagrams on the OLED
- Reduce overall system latency

## Technologies

- C++
- Python
- STM32 Nucleo-F401RE
- Mbed OS
- ARM CMSIS-DSP
- NumPy
- scikit-learn
- PySerial
- Embedded Machine Learning
- Digital Signal Processing (DSP)

## Author: Isaac Lee
