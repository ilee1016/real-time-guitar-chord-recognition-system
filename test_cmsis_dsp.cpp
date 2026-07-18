#include "mbed.h"
#include <cmath>
#include <cstring>
#include <cstdio>
#include "arm_math.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

// ============================================================================
// Minimal CMSIS-DSP Test - Verifies library is working
// ============================================================================

// LED1 is on PA_5 for Nucleo-F401RE
DigitalOut led(LED1);

// UnbufferedSerial for output
UnbufferedSerial pc(USBTX, USBRX, 115200);

void print(const char* msg) {
    pc.write(msg, strlen(msg));
}

void blink_success() {
    // Fast blink = success
    for (int i = 0; i < 6; i++) {
        led = 1;
        wait_us(100000);  // 100ms
        led = 0;
        wait_us(100000);
    }
}

void blink_fail() {
    // Slow blink = fail
    for (int i = 0; i < 3; i++) {
        led = 1;
        wait_us(500000);  // 500ms
        led = 0;
        wait_us(500000);
    }
}

int main() {
    char buf[128];

    // Small delay for serial to initialize
    wait_us(500000);

    print("\n\n=== CMSIS-DSP Integration Test ===\n\n");

    int tests_passed = 0;

    // Test 1: Basic math function
    print("Test 1: arm_cos_f32()...\n");
    float cos_result = arm_cos_f32(0.0f);
    snprintf(buf, sizeof(buf), "  cos(0) = %.4f (expected 1.0000)\n", cos_result);
    print(buf);

    if (fabsf(cos_result - 1.0f) < 0.01f) {
        print("  PASS\n\n");
        tests_passed++;
    } else {
        print("  FAIL\n\n");
    }

    // Test 2: FFT initialization
    print("Test 2: arm_rfft_fast_init_f32()...\n");
    arm_rfft_fast_instance_f32 fft_instance;
    arm_status status = arm_rfft_fast_init_f32(&fft_instance, 256);

    if (status == ARM_MATH_SUCCESS) {
        print("  FFT init successful\n");
        print("  PASS\n\n");
        tests_passed++;
    } else {
        snprintf(buf, sizeof(buf), "  FFT init failed with status %d\n", status);
        print(buf);
        print("  FAIL\n\n");
    }

    // Test 3: Simple FFT on test signal
    print("Test 3: Simple FFT on 440Hz sine wave...\n");

    const int FFT_SIZE = 256;
    const float SAMPLE_RATE = 8000.0f;
    const float TEST_FREQ = 440.0f;  // A4 note

    float input[FFT_SIZE];
    float output[FFT_SIZE * 2];  // Complex output
    float magnitude[FFT_SIZE / 2];

    // Generate 440Hz sine wave
    for (int i = 0; i < FFT_SIZE; i++) {
        float t = (float)i / SAMPLE_RATE;
        input[i] = sinf(2.0f * M_PI * TEST_FREQ * t);
    }

    // Perform FFT
    arm_rfft_fast_f32(&fft_instance, input, output, 0);

    // Calculate magnitude spectrum
    magnitude[0] = fabsf(output[0]);
    for (int i = 1; i < FFT_SIZE / 2; i++) {
        float real = output[i * 2];
        float imag = output[i * 2 + 1];
        magnitude[i] = sqrtf(real * real + imag * imag);
    }

    // Find peak frequency
    float max_mag = 0.0f;
    int peak_bin = 0;
    for (int i = 0; i < FFT_SIZE / 2; i++) {
        if (magnitude[i] > max_mag) {
            max_mag = magnitude[i];
            peak_bin = i;
        }
    }

    float peak_freq = (float)peak_bin * SAMPLE_RATE / FFT_SIZE;
    snprintf(buf, sizeof(buf), "  Peak frequency: %.1f Hz\n", peak_freq);
    print(buf);
    snprintf(buf, sizeof(buf), "  Expected: %.1f Hz\n", TEST_FREQ);
    print(buf);

    // Check if detected frequency is close to input frequency (within 2 bins)
    float freq_error = fabsf(peak_freq - TEST_FREQ);
    float freq_resolution = SAMPLE_RATE / FFT_SIZE;

    if (freq_error < (2 * freq_resolution)) {
        print("  PASS\n\n");
        tests_passed++;
    } else {
        snprintf(buf, sizeof(buf), "  Error: %.1f Hz (too large)\n", freq_error);
        print(buf);
        print("  FAIL\n\n");
    }

    // Final verdict
    print("=== Test Complete ===\n");
    snprintf(buf, sizeof(buf), "Tests passed: %d/3\n\n", tests_passed);
    print(buf);

    if (tests_passed == 3) {
        print("SUCCESS! CMSIS-DSP is working correctly!\n\n");
        blink_success();
    } else {
        print("FAILURE - Some tests failed!\n\n");
        blink_fail();
    }

    // Continuous blink to show program is running
    while (true) {
        led = 1;
        wait_us(1000000);  // 1 second
        led = 0;
        wait_us(1000000);
    }
}
