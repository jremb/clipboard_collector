"""
ClipboardCollector.py

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
    QHBoxLayout,
    QPushButton,
    QCheckBox,
    QLineEdit,
    QLabel,
)
from PyQt5.QtCore import (
    QThread,
    QObject,
)
from PyQt5.QtGui import QTextCursor

style_settings = """
QWidget#AppendBar{background-color: #DCDCDC}
QCheckBox{padding: 1px}
QLabel{padding: 6px}
"""

class MainGui(QWidget):
    """The main GUI window containing all the widgets and primary methods."""
    def __init__(self):
        super().__init__()
        self.initializeUI()


    def initializeUI(self):
        """Create and set the widgets for the GUI."""
        self.setWindowTitle('Clipboard Collector')
        self.setGeometry(100, 100, 100, 400)

        append_layout = QVBoxLayout()
        #append_layout.setSizeConstraint(10)
        right_side_layout = QVBoxLayout()
        g_layout = QGridLayout()
        h_layout = QHBoxLayout()

        self.text_window = QTextEdit()
        self.text_window.setPlaceholderText('Text copied to clipboard will be automatically pasted here.')
        self.text_window.setAcceptDrops(True)
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

        self.cb_custom_prefix = QCheckBox('Custom Prefix', self)
        self.cb_custom_prefix.setEnabled(False)
        self.cb_custom_prefix.stateChanged.connect(self.customPrefix)

        self.cb_custom_suffix = QCheckBox('Custom Suffix', self)
        self.cb_custom_suffix.setEnabled(False)
        self.cb_custom_suffix.stateChanged.connect(self.customSuffix)

        self.prefix = QLineEdit()
        self.prefix.setPlaceholderText('Enter prefix here')

        self.suffix = QLineEdit()
        self.suffix.setPlaceholderText('Enter suffix here')

        self.append_label = QLabel('Append Options')

        g_layout.addWidget(self.start_button, 0, 0)
        g_layout.addWidget(self.stop_button, 0, 1)
        g_layout.addWidget(self.copy_all, 0, 2)
        g_layout.addWidget(self.clear_all, 0, 3)

        self.left_side_widget = QWidget()
        self.left_side_widget.setObjectName('AppendBar')
        self.left_side_widget.setLayout(append_layout)

        append_layout.addWidget(self.append_label)
        append_layout.addWidget(self.cb_bullet)
        append_layout.addWidget(self.cb_custom_prefix)
        append_layout.addWidget(self.prefix)
        append_layout.addWidget(self.cb_custom_suffix)
        append_layout.addWidget(self.suffix)
        append_layout.addStretch()

        right_side_layout.addWidget(self.text_window)
        right_side_layout.addLayout(g_layout)

        h_layout.addWidget(self.left_side_widget)
        h_layout.addLayout(right_side_layout, 1)

        self.setLayout(h_layout)
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
        self.cb_custom_prefix.setEnabled(True)
        self.cb_custom_suffix.setEnabled(True)
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

    def customPrefix(self):
        self.worker.prefix()

    def customSuffix(self):
        self.worker.suffix()

    def getPrefix(self):
        return self.prefix.text()

    def getSuffix(self):
        return self.suffix.text()


class ClipboardExtractor(QObject):
    """Watches clipboard for content. If content on clipboard
    pastes content to QTextEdit."""
    def __init__(self, cursor):
        super().__init__()
        self.cursor = cursor

        self.threadActive = True
        self.bpActive = False
        self.prefixActive = False
        self.suffixActive = False

    def run(self):
        """Starts an infinite loop, waiting for content
        to be copied to the clipboard."""
        while self.threadActive:
            prefix = ''
            suffix = ''
            if pyperclip.paste() != '':
                text = pyperclip.paste()
                if self.bpActive:
                    prefix = '* '
                if self.prefixActive:
                    prefix = prefix + window.getPrefix()
                if self.suffixActive:
                    suffix = window.getSuffix()
                lines: list = text.split('\n')
                for i in range(len(lines)):
                    print(prefix)
                    lines[i] = prefix + lines[i] + suffix
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

    def prefix(self):
        if not self.prefixActive:
            self.prefixActive = True
        else:
            self.prefixActive = False

    def suffix(self):
        if not self.suffixActive:
            self.suffixActive = True
        else:
            self.suffixActive = False

    def kill(self):
        """Breaks out of the infinite loop and returns
        to MainGUI to kill thread."""
        self.threadActive = False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(style_settings)
    window = MainGui()
    sys.exit(app.exec())
