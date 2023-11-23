import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton
from PyQt5.QtCore import QObject, pyqtSignal, Qt
import re
import yt_dlp

class ClipboardListener(QObject):
    clipboard_updated = pyqtSignal()

    def __init__(self, app):
        super().__init__()

        self.clipboard = app.clipboard()
        self.clipboard.dataChanged.connect(self.clipboard_changed)

    def clipboard_changed(self):
        mime_data = self.clipboard.mimeData()
        if mime_data.hasText():
            clipboard_text = mime_data.text()

            # Check if the clipboard text contains URLs
            url_pattern = r'https?://(?:www\.)?(?:youtube\.com|youtu\.be|xvideos\.com)/\S+' #You can add more sites inside the (?: ... ) You put in a | to act as an or, and then use \ to escape the dot
            urls = re.findall(url_pattern, clipboard_text)

            if urls:
                self.clipboard_updated.emit()

class VideoCapture(QWidget):
    def __init__(self, clipboard_listener):
        super().__init__()

        self.clipboard_listener = clipboard_listener

        # Set window properties
        self.setWindowTitle("TubeTracker Video Capture")
        self.setGeometry(100, 100, 400, 300)

        # Add QTextEdit widgets for displaying messages and captured URLs
        self.message_display = QTextEdit(self)
        self.message_display.setReadOnly(True)  # Make it read-only
        self.message_display.setPlaceholderText("Messages will appear here.")

        self.url_display = QTextEdit(self)
        self.url_display.setReadOnly(True)  # Make it read-only
        self.url_display.setPlaceholderText("Captured URLs will appear here.")

        # Add button for downloading
        self.download_button = QPushButton("Download Videos", self)

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(self.message_display)
        layout.addWidget(self.url_display)
        layout.addWidget(self.download_button)

        # Connect the clipboard listener to the function capturing URLs
        self.clipboard_listener.clipboard_updated.connect(self.capture_url_from_clipboard)
        self.download_button.clicked.connect(self.download_videos)

        # List to store captured URLs
        self.captured_urls = []

        # Set window to stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def display_message(self, message):
        self.message_display.append(message)

    def display_url(self, url):
        self.url_display.append(url)

    def capture_url_from_clipboard(self):
        mime_data = self.clipboard_listener.clipboard.mimeData()
        if mime_data.hasText():
            clipboard_text = mime_data.text()

            # Check if the clipboard text contains URLs
            url_pattern = r'https?://\S+'
            urls = re.findall(url_pattern, clipboard_text)

            if urls:
                self.captured_urls.extend(urls)
                # self.display_message("URL captured from clipboard")
                for url in urls:
                    self.display_url(url)

    def display_captured_urls(self):
        self.display_message("Captured URLs:")
        for url in self.captured_urls:
            self.display_url(url)

    def download_videos(self):
        if not self.captured_urls:
            self.display_message("No URLs to download.")
            return

        try:
            with yt_dlp.YoutubeDL() as ydl:
                self.display_message("Downloading video(s)")
                ydl.download(self.captured_urls)
                self.display_message("Videos downloaded successfully.")

                # Clear the captured URLs and text boxes
                self.captured_urls = []
                self.url_display.clear()
        except Exception as e:
            self.display_message(f"Error downloading videos: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create an instance of the ClipboardListener, passing the QApplication instance
    clipboard_listener = ClipboardListener(app)

    video_capture = VideoCapture(clipboard_listener)
    video_capture.show()

    sys.exit(app.exec_())

#Alright, now I need to make sure the app doesn't hang while videos are being downloaded. It must give continuous feedback about the videos and it must remove duplicate URLs before downloading. When downloading it should create a folder with the days date if it doesn't exist already and then download the videos inside there if this is at all possible.