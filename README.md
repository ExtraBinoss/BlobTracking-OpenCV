# BlobTrack Processor

**BlobTrack** is a computer vision tool designed to create generative visuals from video content. By leveraging the power of OpenCV, it extracts organic shapes and movements from source videos, allowing for real-time manipulation and high-quality export for VJ loops, motion graphics, and creative coding projects.

---

> **Author's Note**  
> "TouchDesigner blob tracking capabilities is cool, I wanted to recreate that effect using the same library as them, OpenCV. This effect is very good for VJ loops or any other content that could need it. Let your artist's imagination run wild!"

---

## 🚀 Features

- **Advanced Detection**: Multiple detection modes including Edge Detection (Canny), Grayscale Thresholding, and Color Range Isolation.
- **Dynamic Visuals**: Customize shapes, colors, and effects (Rainbow, cycle, breathe, etc.).
- **Real-Time Preview**: Tweak parameters instantly while watching the result.
- **High-Quality Export**: Process and save your creations as MP4 files.

## 🛠️ Requirements

BlobTrack is built with Python and utilizes industry-standard libraries:
- **Python 3.8+**
- **OpenCV** (`opencv-python`)
- **PyQt6**
- **NumPy**

## 📦 Installation

We provide an easy installation script to get you up and running quickly.

### Automatic Installation (Recommended)

**Windows (Git Bash recommended) / macOS / Linux:**
Run the included install script to automatically create a virtual environment and install all dependencies.

```bash
./install.sh
```

### Manual Installation

If you prefer to set it up manually:

1. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

2. **Activate the Environment:**
   - **Windows:** `source venv/Scripts/activate` (Git Bash) or `venv\Scripts\activate` (CMD/PowerShell)
   - **Mac/Linux:** `source venv/bin/activate`

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 Usage

1. **Launch the Application**:
   ```bash
   source venv/Scripts/activate && python main.py
   ```
   *(Note: On Windows PowerShell, use `.\venv\Scripts\activate`)*

2. **Select Video**: Click **"Select Video File"** to load your source footage.

3. **Tweak Settings**: 
   - Use the **Detection** tab to isolate the shapes you want.
   - Use the **Visuals** tab to apply colors, shapes, and effects.

4. **Export**: Once you're happy with the look, click **"Export Processed Video"**. 

## 📝 License

WTFPL License - See [LICENSE](LICENSE) for details.

In short : Do whatever you want.

## 🥳 Author

Built with ❤️ using Python, OpenCV, and PyQt6.

For all questions, suggestions, or bug reports, please open an issue on GitHub.

