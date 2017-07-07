# ##############################################################################
# Basic configuration
# @author Alessandro Danese
# @author Luca Piccolboni
# ##############################################################################

# Project information
project(BENCHMARKS)
set(THIRDPARTY_STUDENTS_VERSION_MAJOR 1)
set(THIRDPARTY_STUDENTS_VERSION_MINOR 0)

# Checking cmake version
cmake_minimum_required(VERSION 2.8.12)

# Configure directory of executable
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# ##############################################################################
# Thirdparty configuration
# ##############################################################################

# Show messagge during configuration
message("-- Configuring third party libraries")

# Set the thirdparty default home directory
set(THIRDPARTY_HOME ${CMAKE_CURRENT_SOURCE_DIR}/../thirdparty_students)

# Set the thirdparty default build directory
set(THIRDPARTY_BUILD ${CMAKE_CURRENT_SOURCE_DIR}/../thirdparty_students/build)

# Include external libraries from thirdparty
include("${THIRDPARTY_BUILD}/Config.cmake")

# ##############################################################################
# Compiler configuration
# ##############################################################################

# Show messagge during configuration
message("-- Configuring compiler")

# ##############################################################################
# Subdirectories
# ##############################################################################
add_subdirectory(utils)
add_subdirectory(sources)

