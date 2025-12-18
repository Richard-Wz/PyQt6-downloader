import sys
import os 
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QProgressBar, QTextEdit, QFileDialog, QMessageBox,
                             QComboBox)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QFont, QIcon
from yt_dlp import YoutubeDL
import re

# Regex to strip ANSI escape sequences (colors / styles)
_ANSI_ESCAPE_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

def strip_ansi_codes(s: str) -> str:
    if not isinstance(s, str):
        return s
    return _ANSI_ESCAPE_RE.sub('', s)

# Downloader Thread Class 
# Allow multithreading for downloads to prevent UI blocking
class DownloadThread(QThread):
    progress_DL = pyqtSignal(str)           # Signal to update progress messages
    finished_DL = pyqtSignal(bool, str)     # Signal to indicate download completion or error
    
    # Init method
    def __init__(self, url, download_dir, format_type, bitrate):
        super().__init__()
        self.url = url
        self.download_dir = download_dir
        self.format_type = format_type
        self.bitrate = bitrate

    # Run method to start the download process
    def run(self): 
        # Determine output directory based on format
        if self.format_type == "MP3":
            output_dir = os.path.join(self.download_dir, "Audio")
        else:  # MP4
            output_dir = os.path.join(self.download_dir, "Video")
        
        os.makedirs(output_dir, exist_ok=True)

        # Configure download options based on format and bitrate
        if self.format_type == "MP3":
            ydl_opts = {
                "format": "bestaudio/best",
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": self.bitrate,
                    },
                    {
                        "key": "FFmpegThumbnailsConvertor",
                        "format": "jpg",
                    },
                    {
                        "key": "EmbedThumbnail",
                        "already_have_thumbnail": False,
                    },
                    {
                        "key": "FFmpegMetadata",
                        "add_metadata": True,
                    },
                ],
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [self.progress_hook],
                "overwrites": True,
                "writethumbnail": True,
                "postprocessor_args": {
                    "thumbnailsconvertor": [
                        "-vf",
                        "scale=500:500:force_original_aspect_ratio=decrease,pad=500:500:(ow-iw)/2:(oh-ih)/2,setsar=1"
                    ]
                },
            }
        else:  # MP4
            # For MP4, use format selection with video quality
            if self.bitrate == "Best":
                format_str = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                # Select video by height/quality approximation
                format_str = f"bestvideo[height<={self.bitrate}][ext=mp4]+bestaudio[ext=m4a]/best[height<={self.bitrate}][ext=mp4]/best"
            
            ydl_opts = {
                "format": format_str,
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                "progress_hooks": [self.progress_hook],
                "merge_output_format": "mp4",
                "overwrites": True,
                "postprocessors": [
                    {
                        "key": "FFmpegThumbnailsConvertor",
                        "format": "jpg",
                        "when": "before_dl",
                    },
                    {
                        "key": "EmbedThumbnail",
                        "already_have_thumbnail": False,
                    },
                    {
                        "key": "FFmpegMetadata",
                        "add_metadata": True,
                    },
                ],
                "writethumbnail": True,
                "postprocessor_args": {
                    "thumbnailsconvertor": ["-vf", "scale=500:-2,setsar=1"]
                },
            }

        # Download process with error handling
        try:
            self.progress_DL.emit(f"Starting download: {self.url}")
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=True)
                title = info.get('title', 'Unknown')
                self.finished_DL.emit(True, f"Download completed: {title}")
        except Exception as e:
            self.finished_DL.emit(False, f"Error: {str(e)}")
    
    # Progress hook to emit download progress updates
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A')
            speed = d.get('_speed_str', 'N/A')
            self.progress_DL.emit(f"Downloading... {percent} at {speed}")
        elif d['status'] == 'finished':
            if self.format_type == "MP3":
                self.progress_DL.emit("Processing audio file...")
            else:
                self.progress_DL.emit("Processing video file...")

# UI design Information
# #252C37 color for background
# #F8C61E color for text

# Downloader Class
class Downloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.download_dir = os.path.join(os.path.expanduser("~"), "Downloads")
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Downloader")
        
        # Set window icon (for taskbar and title bar)
        icon_path = self.get_icon_path()
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

        # Set the window position to the center of the screen
        screen_x = QApplication.primaryScreen().size().width()
        screen_y = QApplication.primaryScreen().size().height()
        self.setGeometry(int(screen_x/2) - 300, int(screen_y/2) - 250, 600, 500)

        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        central_widget.setStyleSheet("background-color: #252C37;")

        # URL input layout
        url_layout = QHBoxLayout()
        url_label = QLabel("Link:")
        url_label.setStyleSheet("font-size: 14px; color: #F8C61E; font-weight: bold;")
        url_label.setFixedWidth(70)
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Enter URL here...")
        self.url_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                color: #F8C61E;
                border: 2px solid #555;
                background-color: #2a3139;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 2px solid #F8C61E;
            }
        """)
        url_layout.addWidget(url_label)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        # Format selection layout
        format_layout = QHBoxLayout()
        format_label = QLabel("Format:")
        format_label.setStyleSheet("font-size: 14px; color: #F8C61E; font-weight: bold;")
        format_label.setFixedWidth(70)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["MP3", "MP4"])
        self.format_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 14px;
                color: #F8C61E;
                border: 2px solid #555;
                background-color: #2a3139;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #F8C61E;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a3139;
                color: #F8C61E;
                selection-background-color: #F8C61E;
                selection-color: #252C37;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3a4149;
                color: #F8C61E;
                border-left: 2px solid #F8C61E;
            }                                                                           
        """)
        self.format_combo.currentTextChanged.connect(self.update_bitrate_options)
        
        format_layout.addWidget(format_label)
        format_layout.addWidget(self.format_combo, 1)
        layout.addLayout(format_layout)
        
        # Bitrate selection layout
        bitrate_layout = QHBoxLayout()
        bitrate_label = QLabel("Quality:")
        bitrate_label.setStyleSheet("font-size: 14px; color: #F8C61E; font-weight: bold;")
        bitrate_label.setFixedWidth(70)
        
        self.bitrate_combo = QComboBox()
        self.bitrate_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                font-size: 14px;
                color: #F8C61E;
                border: 2px solid #555;
                background-color: #2a3139;
                min-height: 20px;
            }
            QComboBox:focus {
                border: 2px solid #F8C61E;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #2a3139;
                color: #F8C61E;
                selection-background-color: #F8C61E;
                selection-color: #252C37;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #3a4149;
                color: #F8C61E;
                border-left: 2px solid #F8C61E;
            }                                                                       
        """)
        
        bitrate_layout.addWidget(bitrate_label)
        bitrate_layout.addWidget(self.bitrate_combo, 1)
        layout.addLayout(bitrate_layout)
        
        # Initialize bitrate options for default format (MP3)
        self.update_bitrate_options("MP3")

        # Download directory layout
        dir_layout = QHBoxLayout()

        # Directory label and display
        dir_label = QLabel("Save to:")
        dir_label.setStyleSheet("font-size: 14px; color: #F8C61E; font-weight: bold;")
        dir_label.setFixedWidth(70)
        self.dir_display = QLineEdit(self.download_dir)
        self.dir_display.setReadOnly(True)
        self.dir_display.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                color: #F8C61E;
                border: 2px solid #555;
                background-color: #2a3139;
                min-height: 20px;
            }
        """)

        # Browse button 
        self.browse_btn = QPushButton("Browse")
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #F8C61E;
                color: #252C37;
                padding: 10px 15px;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #E6B91A;          
            }
            QPushButton:disabled { 
                background-color: #cccccc;
            }                                                           
        """)
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(dir_label) 
        dir_layout.addWidget(self.dir_display)
        dir_layout.addWidget(self.browse_btn)
        layout.addLayout(dir_layout)

        # Download button
        self.download_btn = QPushButton("Download")
        self.download_btn.setStyleSheet("""
            QPushButton {
                background-color: #F8C61E;
                color: #252C37;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #E6B91A;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.download_btn.clicked.connect(self.start_download)
        layout.addWidget(self.download_btn)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #F8C61E;
                border-radius: 5px;
                text-align: center;
                background-color: #1a1f28;
                min-height: 10px;
                max-height: 10px;
            }
            QProgressBar::chunk {
                background-color: #F8C61E;
            }
        """)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status/Log area
        status_label = QLabel("Status:")
        status_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #F8C61E;")
        layout.addWidget(status_label)

        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet("color: #F8C61E; font-size: 13px;")
        layout.addWidget(self.status_text)

        # Initial status message
        self.append_status("Welcome!")

    # Functions
    def get_icon_path(self):
        """Get the path to the icon file, works for both script and EXE"""
        if getattr(sys, 'frozen', False):
            # Running as compiled EXE
            base_path = sys._MEIPASS
        else:
            # Running as script
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(base_path, 'icon.ico')
        return icon_path
    
    def update_bitrate_options(self, format_type):
        """Update bitrate options based on selected format"""
        self.bitrate_combo.clear()
        
        if format_type == "MP3":
            # MP3 audio bitrates in kbps
            self.bitrate_combo.addItems(["320", "256", "192", "128", "96"])
        else:  # MP4
            # MP4 video quality options (by resolution height)
            self.bitrate_combo.addItems(["Best", "2160", "1440", "1080", "720", "480", "360"])
    
    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Directory", self.download_dir)
        if directory:
            self.download_dir = directory
            self.dir_display.setText(directory)
            self.append_status(f"Download directory set to: {directory}")

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Input Error", "Please enter a valid URL.")
            return
        
        format_type = self.format_combo.currentText()
        bitrate = self.bitrate_combo.currentText()
        
        self.download_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.format_combo.setEnabled(False)
        self.bitrate_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        quality_str = f"{bitrate}kbps" if format_type == "MP3" else ("Best Quality" if bitrate == "Best" else f"{bitrate}p")
        self.append_status(f"\n{'='*60}\nStarting download for URL: {url}\nFormat: {format_type} | Quality: {quality_str}")

        self.download_thread = DownloadThread(url, self.download_dir, format_type, bitrate)
        self.download_thread.progress_DL.connect(self.update_progress)
        self.download_thread.finished_DL.connect(self.download_finished)
        self.download_thread.start()

    # Update progress messages in the status area
    def update_progress(self, message):
        self.append_status(message)
    
    # Handle download completion or error
    def download_finished(self, success, message):
        self.append_status(message)
        self.progress_bar.setVisible(False)
        self.download_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.format_combo.setEnabled(True)
        self.bitrate_combo.setEnabled(True)

        if success:
            QMessageBox.information(self, "Download Complete", message)
            self.url_input.clear()
        else:
            QMessageBox.critical(self, "Download Error", message)
            self.url_input.clear()

    # Append status messages to the text area
    def append_status(self, message):
        # Strip ANSI color/control sequences before appending to the QTextEdit
        message = strip_ansi_codes(message)
        self.status_text.append(message)
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

def main():
    app = QApplication(sys.argv)
    window = Downloader()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()