# BlobTrack 🔵

A real-time blob detection and tracking application built with Python, OpenCV, and PyQt6.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-orange.svg)

## Features

- **Multiple Detection Modes**
  - Grayscale threshold detection
  - Canny edge detection
  - HSV color filtering

- **Customizable Visuals**
  - Shape styles (Circle, Square)
  - Color effects (Solid, Rainbow, Cycle, Breathe, Ripple, Firework)
  - Text overlays (Index, Random Words, Custom)
  - Trace trails with customizable thickness, lifetime, and color

- **Real-time Preview**
  - Live video processing
  - Adjustable parameters on-the-fly
  - Debug mode for threshold visualization

- **Modern UI**
  - Dark/Light theme toggle
  - Tabbed interface (Detection, Visuals, Project)
  - Resizable panels
  - Custom color picker with HSV gradient

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/BlobTrackCv.git
cd BlobTrackCv

# Create virtual environment
python -m venv venv

# Activate (Windows)
source venv/Scripts/activate  # Git Bash
# OR
.\venv\Scripts\activate  # PowerShell

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Click **Select Video** in the Project tab
2. Adjust detection parameters in the **Detection** tab
3. Customize visuals in the **Visuals** tab
4. Export processed video when ready

## Project Structure

```
BlobTrackCv/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── src/
│   ├── core/              # Core processing logic
│   │   ├── tracking.py    # Blob detection & centroid tracking
│   │   ├── video_processor.py
│   │   └── enums.py
│   ├── ui/                # User interface
│   │   ├── main_window.py
│   │   ├── themes.py
│   │   └── widgets/       # Reusable UI components
│   ├── visuals/           # Visualization strategies
│   │   ├── core.py        # Visualizer class
│   │   └── strategies.py  # Color, Shape, Text strategies
│   └── assets/            # Icons and images
└── venv/                  # Virtual environment
```

## Controls

| Key | Action |
|-----|--------|
| `Space` | Play/Pause |
| `D` | Toggle Debug Mode |
| Drag Slider | Seek through video |

## License

WTFPL License - See [LICENSE](LICENSE) for details.

## Author

Built with ❤️ using Python, OpenCV, and PyQt6.
