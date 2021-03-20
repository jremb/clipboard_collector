"""
MClipGui.py

Inspired by the multi-clipboard project by Al Sweigart in Automate the Boring Stuff. Uses pyperclip to
monitor clipboard and pastes its content onto the textfield so that the user can later copy multiple clippings
into a single copy.

John Bowling
"""
import pyperclip
import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
from PyQt5.QtCore import (
    QThread,
    QObject,
)
from PyQt5.QtGui import QTextCursor


class MainGui(QWidget):
    """The main GUI window containing all the widgets and primary methods."""
    def __init__(self):
        super().__init__()
        self.initializeUI()


    def initializeUI(self):
        """Create and set the widgets for the GUI."""
        self.setWindowTitle('Clipboard Collector')

        self.v_layout = QVBoxLayout()
        self.h_layout = QHBoxLayout()

        self.text_window = QTextEdit()
        self.text_window.setPlaceholderText('Text copied to clipboard will be pasted here.')
        self.text_window_cursor = self.text_window.textCursor()

        self.cursor = QTextCursor(self.text_window_cursor)

        self.clipboard = app.clipboard()

        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.startWorker)

        self.stop_button = QPushButton('Stop')
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stopWorker)

        self.copy_all = QPushButton('Copy All')
        self.copy_all.setEnabled(False)
        self.copy_all.clicked.connect(self.copyAll)

        self.clear_all = QPushButton('Clear Text Field')
        self.clear_all.clicked.connect(self.clearText)

        self.h_layout.addWidget(self.start_button)
        self.h_layout.addWidget(self.stop_button)
        self.h_layout.addWidget(self.copy_all)
        self.h_layout.addWidget(self.clear_all)

        self.v_layout.addWidget(self.text_window)
        self.v_layout.addLayout(self.h_layout)

        self.setLayout(self.v_layout)
        self.show()

    def stopWorker(self):
        """Calls kill method of ClipBoardExtractor class and
        exits the thread."""
        self.copy_all.setEnabled(True)
        self.worker.kill()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.thread.exit()


    def startWorker(self):
        """Clears the clipboard of any text that may
        otherwise be unintentionally captured. Begins
        run method of ClipboardExtractor class in a
        separate thread."""
        self.clipboard.clear()
        self.thread = QThread()
        self.worker = ClipboardExtractor(self.cursor)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.thread.start()

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def copyAll(self):
        """Copy all the text QTextEdit"""
        self.clipboard.setText(self.text_window.toPlainText(), mode=self.clipboard.Clipboard)

    def clearText(self):
        """Remove all text on QTextEdit"""
        self.cursor.movePosition(self.cursor.Start, QTextCursor.KeepAnchor)
        self.cursor.removeSelectedText()


class ClipboardExtractor(QObject):
    """Watches clipboard for content. If content on clipboard
    pastes content to QTextEdit."""
    def __init__(self, cursor):
        super().__init__()
        self.threadactive = True
        self.cursor = cursor

    def run(self):
        """Starts an infinite loop, waiting for content
        to be copied to the clipboard."""
        while self.threadactive:
            if pyperclip.paste() != '':
                text = pyperclip.paste()
                self.cursor.insertText(text + '\n\n')
                pyperclip.copy('')

    def kill(self):
        """Breaks out of the infinite loop and returns
        to MainGUI to kill thread."""
        self.threadactive = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainGui()
    sys.exit(app.exec())
