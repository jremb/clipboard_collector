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
    QGridLayout,
    QPushButton,
    QCheckBox,
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

        v_layout = QVBoxLayout()
        g_layout = QGridLayout()

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

        self.cb_bullet = QCheckBox('Bullet Points', self)
        self.cb_bullet.setEnabled(False)
        self.cb_bullet.stateChanged.connect(self.bulletPoints)

        g_layout.addWidget(self.start_button, 0, 0)
        g_layout.addWidget(self.stop_button, 0, 1)
        g_layout.addWidget(self.copy_all, 0, 2)
        g_layout.addWidget(self.clear_all, 0, 3)
        g_layout.addWidget(self.cb_bullet, 1, 0)

        v_layout.addWidget(self.text_window)
        v_layout.addLayout(g_layout)

        self.setLayout(v_layout)
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
        self.cb_bullet.setEnabled(True)
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

    def bulletPoints(self):
        self.worker.bp()


class ClipboardExtractor(QObject):
    """Watches clipboard for content. If content on clipboard
    pastes content to QTextEdit."""
    def __init__(self, cursor):
        super().__init__()
        self.threadactive = True
        self.cursor = cursor
        self.bpActive = False

    def run(self):
        """Starts an infinite loop, waiting for content
        to be copied to the clipboard."""
        while self.threadactive:
            if pyperclip.paste() != '':
                text = pyperclip.paste()
                if self.bpActive:
                    lines: list = text.split('\n')
                    for i in range(len(lines)):
                        lines[i] = '* ' + lines[i]
                    text = '\n\n'.join(lines)
                    pyperclip.copy(text)
                self.cursor.insertText(text + '\n\n')
                pyperclip.copy('')

    def bp(self):
        """Checks if bullet point boole is active.
        If active, inactivates. If inactive, activates."""
        if not self.bpActive:
            self.bpActive = True
        else:
            self.bpActive = False

    def kill(self):
        """Breaks out of the infinite loop and returns
        to MainGUI to kill thread."""
        self.threadactive = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainGui()
    sys.exit(app.exec())
