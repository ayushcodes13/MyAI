from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QStackedWidget, QLineEdit, QGridLayout, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSizePolicy, QWidget, QFrame
from PyQt5.QtGui import QIcon, QPainter, QMovie, QColor, QTextCharFormat, QFont, QPixmap, QTextBlockFormat
from PyQt5.QtCore import Qt, QSize, QTimer
from dotenv import dotenv_values
import sys
import os

# Load environment variables
env_vars = dotenv_values(".env")
Assistantname = env_vars.get("Assistantname")

# Define paths
current_dir = os.getcwd()
old_chat_message = ""
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    return '\n'.join(non_empty_lines)

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "what", "who", "where", "when", "why", "which", "whose", "whom", "can you", "what's", "where's", "how's"]
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['-', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['-', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)

def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        return file.read()

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)

def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        return file.read()

def GraphicsDirectoryPath(Filename):
    return rf'{GraphicsDirPath}\{Filename}'

def TempDirectoryPath(Filename):
    return rf'{TempDirPath}\{Filename}'

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Response.data', "w", encoding='utf-8') as file:
        file.write(Text)

class ChatSection(QWidget):
    def __init__(self):
        super(ChatSection, self).__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(-10, 40, 40, 100)
        layout.setSpacing(-100)

        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        layout.addWidget(self.chat_text_edit)

        self.setStyleSheet("background-color:black;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1,1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding))
        text_color = QColor(Qt.blue)
        text_color_format = QTextCharFormat()
        text_color_format.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_format)

        self.gif_label = QLabel()
        self.gif_label.setStyleSheet("border: none;")
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        max_gif_size_W = 480
        max_gif_size_H = 270
        movie.setScaledSize(QSize(max_gif_size_W, max_gif_size_H))
        self.gif_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.gif_label.setMovie(movie)
        movie.start()
        layout.addWidget(self.gif_label)

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-right:195px; border: none; margin-top: -30px")
        self.label.setAlignment(Qt.AlignRight)
        layout.addWidget(self.label)
        layout.setSpacing(-10)
        layout.addWidget(self.gif_label)
        

        font = QFont()
        font.setPointSize(13)
        self.chat_text_edit.setFont(font)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessages)
        self.timer.timeout.connect(self.SpeechRecognitionText)
        self.timer.start(5)

        self.chat_text_edit.viewport().installEventFilter(self)

        self.setStyleSheet("""
            QScrollBar:Vertical {
                border: none;
                background: black;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }
            QScrollBar::handle:vertical {
                background: white;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical {
                background: black;
                subcontrol-position:bottom;
                subcontrol-origin:margin;
                height: 10px;
            }
            QScrollBar::sub-line:vertical {
                background: black;
                subcontrol-position:top;
                subcontrol-origin:margin;
                height: 10px;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical{
                border:none;
                background:none;
                color:none;
            }
            QScrollBar:: add-page:vertical,QScrollBar::sub-page:vertical{
                background: none;
            }
        """)

    def loadMessages(self):
        global old_chat_message
        with open(TempDirectoryPath('Response.data'), "r", encoding='utf-8') as file:
            messages = file.read()
        if messages and messages != old_chat_message:
            self.addMessage(message=messages, color='White')
            old_chat_message = messages

    def SpeechRecognitionText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def addMessage(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        format = QTextCharFormat()
        block_format = QTextBlockFormat()
        block_format.setTopMargin(10)
        block_format.setLeftMargin(10)
        format.setForeground(QColor(color))
        cursor.setCharFormat(format)
        cursor.setBlockFormat(block_format)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)

class InitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        content_layout = QVBoxLayout()
        label= QLabel("")
       
        chat_section = ChatSection()
        
        
        content_layout.setContentsMargins(0, 0, 0, 0)

        gif_label = QLabel()
        movie = QMovie(GraphicsDirectoryPath('Jarvis.gif'))
        gif_label.setMovie(movie)
        max_gif_size_H = int(screen_width / 16 * 9)
        movie.setScaledSize(QSize(screen_width, max_gif_size_H))
        gif_label.setAlignment(Qt.AlignCenter)
        movie.start()
        gif_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.icon_label = QLabel()
        pixmap = QPixmap(GraphicsDirectoryPath('Mic_on.png'))
        new_pixmap = pixmap.scaled(60, 60)
        self.icon_label.setPixmap(new_pixmap)
        self.icon_label.setFixedSize(150, 150)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.toggled = True
        self.icon_label.mousePressEvent = self.toggle_icon

        self.label = QLabel("")
        self.label.setStyleSheet("color: white; font-size:16px; margin-bottom:0;")

        content_layout.addWidget(gif_label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.label, alignment=Qt.AlignCenter)
        content_layout.addWidget(self.icon_label, alignment=Qt.AlignCenter)
        content_layout.setContentsMargins(0, 0, 0, 150)

        self.setLayout(content_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        self.setStyleSheet("background-color:black;")

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.SpeechRecognitionText)
        self.timer.start(5)

    def SpeechRecognitionText(self):
        with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
            messages = file.read()
            self.label.setText(messages)

    def load_icon(self, path, width=60, height=60):
        pixmap = QPixmap(path)
        new_pixmap = pixmap.scaled(width, height)
        self.icon_label.setPixmap(new_pixmap)

    def toggle_icon(self, event=None):
        if self.toggled:
            self.load_icon(GraphicsDirectoryPath('Mic_on.png'), 60, 60)
            SetMicrophoneStatus("True")
        else:
            self.load_icon(GraphicsDirectoryPath('Mic_off.png'), 60, 60)
            SetMicrophoneStatus("False")

        self.toggled = not self.toggled

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()

    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()

        # Initialize QStackedWidget and screens
        self.stacked_widget = QStackedWidget(self)
        initial_screen = InitialScreen()
        chat_screen = ChatSection()
        self.stacked_widget.addWidget(initial_screen)
        self.stacked_widget.addWidget(chat_screen)

        # Create small buttons for Home and Chat
        self.home_button = QPushButton("Home")
        self.chat_button = QPushButton("Chat")

        self.home_button.setFixedSize(60, 40)
        self.chat_button.setFixedSize(60, 40)

        self.home_button.clicked.connect(self.showHomeScreen)
        self.chat_button.clicked.connect(self.showChatScreen)

        # Set up a horizontal layout for buttons (no spacing)
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margin
        button_layout.setSpacing(0)  # Remove spacing between buttons
        button_layout.addWidget(self.home_button)
        button_layout.addWidget(self.chat_button)

        # Style the buttons (small and sleek look)
        self.home_button.setStyleSheet("""
            QPushButton {
                background-color: #1E90FF;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 5px;
                border: 2px solid transparent;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #4682B4;
            }
        """)
        
        self.chat_button.setStyleSheet("""
            QPushButton {
                background-color: #32CD32;
                color: white;
                font-size: 14px;
                border-radius: 10px;
                padding: 5px;
                border: 2px solid transparent;
                box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background-color: #228B22;
            }
        """)

        # Combine button layout with the stacked widget
        main_layout = QVBoxLayout()
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.stacked_widget)

        # Set the combined layout as the main layout
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("background-color:black;")

    def showHomeScreen(self):
        """Switch to the Home Screen."""
        self.stacked_widget.setCurrentIndex(0)  # Index 0 corresponds to the home screen

    def showChatScreen(self):
        """Switch to the Chat Screen."""
        self.stacked_widget.setCurrentIndex(1)  # Index 1 corresponds to the chat screen

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
