# PyQt6 Media Downloader (yt-dlp GUI)

A desktop application built with **Python** and **PyQt6** that provides a graphical user interface for downloading media using **yt-dlp**.

This project is created **for educational purposes**, personal learning, and demonstration of desktop application development using Python.

---

## Educational Use & Disclaimer

⚠️ **This project is not intended for illegal downloading.**

It is designed to be used only for:
- Personal videos
- Content you own
- Content you have explicit permission to download
- Non-copyrighted or Creative Commons content

**Users are responsible for complying with:**
- YouTube's Terms of Service
- Local and international copyright laws

The author assumes **no liability** for misuse of this software.

---

## Features

- ✨ Simple and modern GUI built with PyQt6
- 🎥 Download videos in **MP4** format with selectable quality
- 🎵 Extract audio as **MP3** with selectable bitrate
- ⚡ Background downloading using QThread (non-blocking UI)
- 📝 Automatic metadata and thumbnail embedding
- 📁 Custom download directory selection

---

## Technologies Used

- Python 3
- PyQt6
- yt-dlp
- FFmpeg
- PyInstaller (optional, for building executable)

---

## Project Highlights & Learning Outcomes

This project was **designed and implemented independently** as a hands-on learning exercise in Python and PyQt6 development.

Through this project, I gained practical experience in:

- Designing a complete desktop application using **PyQt6**
- Building a responsive GUI with proper layout management and custom styling
- Implementing **multithreading using QThread** to prevent UI blocking during long-running operations
- Integrating third-party libraries (**yt-dlp**) programmatically instead of relying on command-line execution
- Managing media post-processing workflows using **FFmpeg**
- Handling user input validation, progress reporting, and error handling in a desktop environment
- Structuring a Python project for maintainability and version control using Git and GitHub

This project reflects a focus on **clean code**, **usability**, and **responsible software design**, and was developed strictly for **educational and personal learning purposes**.

---

## Project Structure

```
PyQt6-downloader/
│
├── src/
│   ├── downloader.py
│   └── icon.ico
│
├── requirements.txt
├── README.md
└── LICENSE
```

---

## Requirements

- Python 3.9 or newer
- pip
- FFmpeg (required)

---

## Installation

### 1. Install FFmpeg (Windows)

```powershell
winget install ffmpeg
```

Make sure `ffmpeg` is available in your system PATH.

### 2. Clone the Repository

```bash
git clone https://github.com/Richard-Wz/PyQt6-downloader.git
cd PyQt6-downloader
```

### 3. Install Python Dependencies

```bash
python -m pip install -r requirements.txt
```

**(Optional)** Verify installed packages:

```bash
python -m pip list
```

---

## Running the Application

```bash
cd src
python downloader.py
```

---

## Building a Standalone Executable (Optional)

This step is optional and intended for learning application packaging.

### 1. Copy FFmpeg Binary (Windows)

```powershell
Copy-Item "C:\Users\<USERNAME>\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-*\bin\ffmpeg.exe" -Destination ".\ffmpeg.exe"
```

Ensure `ffmpeg.exe` is placed inside the `src` directory.

### 2. Prepare Application Icon

Place an `.ico` file named `icon.ico` inside the `src` directory.

### 3. Build Using PyInstaller

```bash
python -m PyInstaller --onefile --windowed --name "<APPNAME>" --icon=icon.ico --add-binary "ffmpeg.exe;." --add-data "icon.ico;." downloader.py
```

### 4. Output

The generated executable will be available in the `dist` folder.

---

## License

This project is licensed under the terms specified in the LICENSE file.

---

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

---

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Command-line program to download videos
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python bindings for Qt
- [FFmpeg](https://ffmpeg.org/) - Multimedia framework

---
