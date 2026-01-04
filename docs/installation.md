# Installation

BlobTrack is built with Python 3.8+ and uses standard libraries like OpenCV and PyQt6. We provide an automated installer for convenience, but manual installation is also fully supported.

## Prerequisites

Before installing, ensure you have **Python 3.8** or newer installed on your system.
You can download it from [python.org](https://www.python.org/downloads/).

---

## Automatic Installation (Recommended)

We provide a shell script that automates the setup process, including creating a virtual environment and installing dependencies.

**For Windows (Git Bash), macOS, and Linux:**

1.  Open your terminal in the `BlobTrackCv` project directory.
2.  Run the install script:

    ```bash
    ./install.sh
    ```

3.  Once the script completes, you are ready to run the app!

---

## Manual Installation

If you prefer to configure the environment yourself, follow these steps:

### 1. Create a Virtual Environment

It is good practice to run Python applications in isolation.

```bash
python -m venv venv
```

### 2. Activate the Environment

*   **Windows (Command Prompt / PowerShell):**
    ```powershell
    .\venv\Scripts\activate
    ```

*   **Windows (Git Bash):**
    ```bash
    source venv/Scripts/activate
    ```

*   **macOS / Linux:**
    ```bash
    source venv/bin/activate
    ```

### 3. Install Dependencies

Install the required packages from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## Running the Application

After installation, you can launch BlobTrack with:

```bash
python main.py
```

!!! tip
    Make sure your virtual environment is activated before running the command! You should see `(venv)` in your terminal prompt.
