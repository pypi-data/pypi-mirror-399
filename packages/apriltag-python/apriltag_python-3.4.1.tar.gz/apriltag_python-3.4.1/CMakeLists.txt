# Top-level CMakeLists.txt for scikit-build-core
cmake_minimum_required(VERSION 3.16)
project(apriltag-python
        VERSION 3.4.1
        DESCRIPTION "Python wrapper for the AprilTag visual fiducial detector"
        LANGUAGES C)

# Set rpath for shared libraries to be found at runtime
if(APPLE)
    set(CMAKE_INSTALL_RPATH "@loader_path")
    set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
elseif(UNIX)
    set(CMAKE_INSTALL_RPATH "$ORIGIN")
    set(CMAKE_BUILD_WITH_INSTALL_RPATH TRUE)
endif()

# Find Python and NumPy
find_package(Python3 REQUIRED COMPONENTS Development NumPy)
message(STATUS "Found Python ${Python3_VERSION}")

add_subdirectory(src/apriltag/apriltag)

# Install the Python module
# scikit-build-core will automatically handle installation to the correct location
install(TARGETS apriltag.${Python3_SOABI}
        LIBRARY DESTINATION apriltag
        RUNTIME DESTINATION apriltag)

install(TARGETS apriltag
        LIBRARY DESTINATION apriltag
        RUNTIME DESTINATION apriltag)
