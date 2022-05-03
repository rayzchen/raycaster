# Raycaster

Python and C++ versions.

# Python

`raycast2.py` is the version that uses PyGLM. `raycast.py` uses PyUnity vectors.
The requirements needed can be installed with `pip install -r requirements.txt`.
PyUnity will not be included in the requirements.

# C++

The C++ version uses SDL2 and currently has no way of exporting images.
To compile, download the SDL2 development libraries from https://www.libsdl.org/download-2.0.php.
Copy everything inside the `x86_64-w64-mingw32` subfolder into this repo folder.
To compile, use the commands in `run`. Adapt to your fitting.
The `bin/SDL2.dll` file is required to run the generated EXE.

Note: Only tested on Windows 64-bit with MinGW x86_64.
