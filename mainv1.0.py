import sys
from PyQt5.QtCore import Qt, QEvent, QRect
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QTextEdit
import pygetwindow as gw

class VideoCapture(QWidget):
    def __init__(self):
        super().__init__()

        # Set window properties
        self.setWindowTitle("TubeTracker Video Capture")
        self.setGeometry(100, 100, 400, 300)

        # Enable capturing mode
        self.capturing = False

        # Register global hotkey (Ctrl+Alt+C) to toggle capturing mode
        self.register_hotkey()

        # Add QTextEdit widgets for displaying messages and captured URLs
        self.message_display = QTextEdit(self)
        self.message_display.setReadOnly(True)  # Make it read-only
        self.message_display.setPlaceholderText("Messages will appear here.")

        self.url_display = QTextEdit(self)
        self.url_display.setReadOnly(True)  # Make it read-only
        self.url_display.setPlaceholderText("Captured URLs will appear here.")

        # Layout setup
        layout = QVBoxLayout(self)
        layout.addWidget(self.message_display)
        layout.addWidget(self.url_display)

        # Set window to stay on top
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

    def register_hotkey(self):
        # You may customize the hotkey as needed
        QApplication.instance().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.KeyPress and event.key() == Qt.Key_C and (
            event.modifiers() & Qt.ControlModifier and event.modifiers() & Qt.AltModifier
        ):
            self.toggle_capturing()
            return True
        return super().eventFilter(obj, event)


    def toggle_capturing(self):
        self.capturing = not self.capturing
        if self.capturing:
            self.display_message("Capturing mode enabled. Click on YouTube videos to capture their URLs.")
        else:
            self.display_message("Capturing mode disabled.")

    def mousePressEvent(self, event):
        if self.capturing:
            print("Mouse Press Detected")
            active_window = gw.getActiveWindow()
            if "YouTube" in active_window.title:
                print("Currently in YT")
                url = self.get_youtube_url_under_cursor()
                if url:
                    self.display_message(f"Captured YouTube video URL: {url}")
                    self.display_url(url)
                else:
                    self.display_message("Could not capture YouTube video URL.")
            else:
                self.display_message("Please click on a YouTube video to capture its URL.")

    def get_youtube_url_under_cursor(self):
        # Implement logic to retrieve the YouTube video URL under the cursor
        # For simplicity, let's return a dummy URL
        return "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

    def display_message(self, message):
        self.message_display.append(message)

    def display_url(self, url):
        self.url_display.append(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    video_capture = VideoCapture()
    video_capture.show()
    sys.exit(app.exec_())

#This works, but it doesn't capture the URLs yet. I think I'm overcomplicating it. We can keep the GUI, but instead of having code listen for button clicks and having users click on the videos they want, in the next version, we just put a button and a textbox for URLs. When the button is clicked all text matching a pattern for a URL and containing youtube or whatever will be copied from the user's clipboard and put into a JSON file and be displayed and then gets downloaded.