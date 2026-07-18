# Hardware

## Component List

| Component | Part | Role |
|---|---|---|
| Microcontroller board | STM32 Nucleo-F401RE | Audio sampling, FFT, serial, OLED control |
| Microphone amplifier | MAX9814 | Electret mic preamp with AGC |
| Display | SSD1331 96×64 OLED | Real-time chord and confidence display |
| Host connection | USB (STLink on-board) | Serial communication at 115200 baud |

## STM32 Nucleo-F401RE

| Specification | Value |
|---|---|
| Core | ARM Cortex-M4F |
| Clock | 84 MHz |
| Flash | 512 KB |
| SRAM | 96 KB |
| ADC | 12-bit SAR, up to 2.4 MSPS |
| FPU | Yes (hardware floating-point) |

The Cortex-M4F hardware FPU is required for the CMSIS-DSP RFFT. It is enabled by `ARM_MATH_CM4` and `__FPU_PRESENT=1` in `CMakeLists.txt` and `mbed_app.json`.

The Mbed OS peripheral aliases used in this project:
- `LED1` — on-board LED (PA_5)
- `USBTX` / `USBRX` — USB serial via STLink

## MAX9814 Microphone Amplifier

The MAX9814 is an electret microphone amplifier with automatic gain control (AGC). It conditions the raw microphone signal to a level compatible with the STM32 ADC input range.

Full datasheet: [`MAX9814.pdf`](../MAX9814.pdf)

Key characteristics:
- Selectable gain: 40 dB, 50 dB, or 60 dB (set via GAIN pin)
- Built-in AGC prevents clipping on loud transients
- Single-supply operation (2.7 V – 3.6 V), compatible with the Nucleo 3.3 V rail
- Analog output connects directly to a STM32 ADC input pin

## SSD1331 OLED Display

| Specification | Value |
|---|---|
| Resolution | 96 × 64 pixels |
| Color depth | 65K colors (16-bit RGB565) |
| Interface | SPI |
| Driver source | `ssd1331.cpp` / `ssd1331.h` |

The driver supports text rendering (6×8 font), solid color fills, and hardware-accelerated line and rectangle drawing via the SSD1331's built-in GAC commands. The display is used to show the predicted chord name and confidence score in real time.

## Signal Path

```
Electret Microphone
        │
        ▼
MAX9814 (amplification + AGC)
        │  0–3.3 V analog output
        ▼
STM32 ADC input pin
        │  12-bit samples (0–4095), 8 kHz
        ▼
CMSIS-DSP RFFT (512-point)
        │  float32 magnitude spectrum
        ▼
USB Serial → Host
```

## Sampling Parameters

| Parameter | Value | Notes |
|---|---|---|
| Sample rate | 8000 Hz | Set in firmware ADC configuration |
| ADC resolution | 12-bit | 0–4095 counts |
| FFT size | 512 points | Configurable in firmware |
| Frequency resolution | 15.6 Hz/bin | sample_rate / fft_size |
| Nyquist frequency | 4000 Hz | Covers guitar fundamentals and harmonics |

Guitar chord fundamental frequencies range from approximately 82 Hz (E2 open string) to 1175 Hz (D5). The 4 kHz Nyquist limit captures the first several harmonics of every standard chord voicing.
