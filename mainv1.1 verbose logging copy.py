import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit, QPushButton, QPlainTextEdit
from PyQt5.QtCore import QObject, pyqtSignal, QProcess, Qt
from datetime import datetime

class ConsoleRedirect(QObject):
    text_written = pyqtSignal(str)

    def write(self, text):
        self.text_written.emit(text)

    def flush(self):
        pass

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
            url_pattern = r'https?://(?:www\.)?(?:youtube\.com|youtu\.be|xvideos\.com)/\S+'
            urls = re.findall(url_pattern, clipboard_text)

            if urls:
                self.clipboard_updated.emit()

class VideoCapture(QWidget):
    def __init__(self, clipboard_listener):
        super().__init__()

        self.clipboard_listener = clipboard_listener

        # Set window properties
        self.setWindowTitle("TubeTracker Video Capture")
        self.setGeometry(100, 100, 600, 400)

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

        # Redirect console output to the GUI
        console_redirect = ConsoleRedirect()
        console_redirect.text_written.connect(self.display_message)
        sys.stdout = console_redirect
        sys.stderr = console_redirect

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
                for url in urls:
                    self.display_url(url)

    def download_videos(self):
        self.display_message("Downloading video(s)")
        if not self.captured_urls:
            self.display_message("No URLs to download.")
            return

        # Remove duplicates from the list
        unique_urls = list(set(self.captured_urls))

        # Create a folder with the current date as the name
        folder_name = datetime.now().strftime("%d %b %Y")

        # Construct the yt-dlp command
        command = ["yt-dlp", "--output", f"{folder_name}/%(title)s.%(ext)s"] + unique_urls

        # Create a QProcess to run the command
        process = QProcess()
        process.setProcessChannelMode(QProcess.MergedChannels)

        # Start the process
        process.start("yt-dlp", command)

        # Wait for the process to finish
        process.waitForFinished()

        # Capture the output
        output = process.readAllStandardOutput().data().decode("utf-8")
        self.display_message(output)

        # Display message after download completion
        self.download_completed()


    def read_output(self):
        process = self.sender()
        output = process.readAllStandardOutput().data().decode("utf-8")
        self.display_message(output)

    def download_completed(self):
        self.display_message("Videos downloaded successfully.")

        # Clear the captured URLs and text boxes
        self.captured_urls = []
        self.url_display.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create an instance of the ClipboardListener, passing the QApplication instance
    clipboard_listener = ClipboardListener(app)

    video_capture = VideoCapture(clipboard_listener)
    video_capture.show()

    sys.exit(app.exec_())
