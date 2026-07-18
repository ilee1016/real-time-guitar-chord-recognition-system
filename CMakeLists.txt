# Copyright (c) 2020 ARM Limited. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

cmake_minimum_required(VERSION 3.19.0 FATAL_ERROR)

set(MBED_PATH ${CMAKE_CURRENT_SOURCE_DIR}/mbed-os CACHE INTERNAL "")
set(MBED_CONFIG_PATH ${CMAKE_CURRENT_BINARY_DIR} CACHE INTERNAL "")
set(APP_TARGET guitar-fft-cmsis-dsp)

include(${MBED_PATH}/tools/cmake/app.cmake)

add_subdirectory(${MBED_PATH})

add_executable(${APP_TARGET})

mbed_configure_app_target(${APP_TARGET})

project(${APP_TARGET})

# Add CMSIS-DSP include directory
target_include_directories(${APP_TARGET}
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/CMSIS-DSP/Include
)

# Add CMSIS-DSP compiler definitions
target_compile_definitions(${APP_TARGET}
    PRIVATE
        ARM_MATH_CM4
        __FPU_PRESENT=1
        ARM_MATH_MATRIX_CHECK
        ARM_MATH_ROUNDING
)

# Glob CMSIS-DSP source files
file(GLOB CMSIS_DSP_SOURCES
    "${CMAKE_CURRENT_SOURCE_DIR}/CMSIS-DSP/Source/TransformFunctions/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/CMSIS-DSP/Source/CommonTables/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/CMSIS-DSP/Source/FastMathFunctions/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/CMSIS-DSP/Source/ComplexMathFunctions/*.c"
    "${CMAKE_CURRENT_SOURCE_DIR}/CMSIS-DSP/Source/BasicMathFunctions/*.c"
)

target_sources(${APP_TARGET}
    PRIVATE
        test_cmsis_dsp.cpp
        ssd1331.cpp
        ${CMSIS_DSP_SOURCES}
)

target_link_libraries(${APP_TARGET}
    PRIVATE
        mbed-os
)

mbed_set_post_build(${APP_TARGET})

option(VERBOSE_BUILD "Have a verbose build process")
if(VERBOSE_BUILD)
    set(CMAKE_VERBOSE_MAKEFILE ON)
endif()
