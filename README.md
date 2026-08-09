# UNICODER v1.0

A basic, fast desktop tool for decoding raw binary hex streams into frame animations and encoding image files back into C-style matrix data arrays. 

Built using Python 3.11 and Tkinter, with Windows dark mode integration via pywinstyles.

## Features

- **Hex Stream Decoding:** Parses text data (0xXX format) from text/header files, segments it into sequential frames, and plays it back as a looping animation.
- **Image Encoding:** Converts local image assets (.png, .jpg, .bmp) into raw column-by-column hex data mapped directly to custom width and height inputs.
- **Hardware Protocol Alignment:** Integrated radio selectors for switching between STANDARD_LSB and REVERSE_MSB encoding/decoding on the fly.
- **Manual Controls:** Dynamic vertical skip (FRAME_SKIP) and byte alignment shift (ALIGN_SHIFT) to manually fix distorted or shifted matrix streams.
- **Zero Memory Leaks:** Explicit canvas destruction layer implemented in the frame renderer to maintain stable low RAM usage under high-FPS playback.

## Requirements

If you run it from the raw source code instead of using the release installer, install these modules via pip:


Pillow>=10.0.0
pywinstyles>=1.8

## Quick Start

# Clone or download this project
git clone https://github.com/guts787/UNICODER
cd unicoder

# Run the app core loop directly
python unicoder_v1.0.0.py


## Compilation Note
To compile the project yourself into a clean standalone .exe directory without a visible backend console, use Nuitka on Python 3.11 env:

python -m nuitka --standalone --windows-disable-console --onefile --windows-icon-from-ico=favicon.ico --enable-plugin=tk-inter unicoder_v1.0.0.py

## License
MIT
