import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy
from PyQt5.QtCore import QTimer, Qt, QSize, QPropertyAnimation
from PyQt5.QtGui import QIcon, QFont
import configparser

class MainTimerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")
        self.load_config()

        self.sessions = 4
        self.work_time = 25
        self.break_time = 5
        self.long_break_time = 15
        self.long_break_interval = 4

        self.current_session = 0
        self.timer_running = False
        self.remaining_time = 0

        self.main_message = "Study!"
        self.secondary_message = "Break:)"

        self.initUI()

    def initUI(self):
        self.setStyleSheet(f"background-color: {self.background_color}; color: {self.font_color}; font-family: {self.font_family};")

        layout = QVBoxLayout()

        self.message_label = QLabel(self.main_message)
        self.message_label.setStyleSheet(f"font-size: {self.session_font_size}px;")
        layout.addWidget(self.message_label, alignment=Qt.AlignCenter)

        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet(f"font-size: {self.timer_font_size}px;")
        layout.addWidget(self.timer_label, alignment=Qt.AlignCenter)

        self.session_label = QLabel(f"Session: {self.current_session}/{self.sessions}")
        self.session_label.setStyleSheet(f"font-size: {self.session_font_size}px;")
        layout.addWidget(self.session_label, alignment=Qt.AlignCenter)

        buttons_layout = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_button.clicked.connect(self.start_timer)
        buttons_layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Pause")
        self.stop_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e53935;
            }
        """)
        self.stop_button.clicked.connect(self.pause_timer)
        buttons_layout.addWidget(self.stop_button)

        gear_button = QPushButton()
        gear_button.setIcon(QIcon('Github-Octicons-Gear-16.svg'))
        gear_button.setIconSize(QSize(16, 16))
        gear_button.setFixedSize(30, 30)
        gear_button.setStyleSheet("""
            QPushButton {
                background-color: #808080;
                border: none;
                color: white;
                padding: 5px;
                text-align: center;
                font-size: 16px;
                border-radius: 50%;
            }
            QPushButton:hover {
                background-color: #737373;
            }
        """)
        gear_button.clicked.connect(self.toggle_settings)
        buttons_layout.addWidget(gear_button)

        layout.addLayout(buttons_layout)

        self.settings_panel = QWidget()
        self.settings_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.settings_panel.setMaximumHeight(0)
        self.settings_layout = QVBoxLayout()

        self.sessions_input = self.create_setting_input("Number of sessions:", self.sessions, self.settings_layout)
        self.work_time_input = self.create_setting_input("Work time (min):", self.work_time, self.settings_layout)
        self.break_time_input = self.create_setting_input("Break time (min):", self.break_time, self.settings_layout)
        self.long_break_time_input = self.create_setting_input("Long break time (min):", self.long_break_time, self.settings_layout)
        self.long_break_interval_input = self.create_setting_input("Long break interval (sessions):", self.long_break_interval, self.settings_layout)

        apply_button = QPushButton("Apply")
        apply_button.setStyleSheet("""
            QPushButton {
                background-color: #008CBA;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0073e6;
            }
        """)
        apply_button.clicked.connect(self.save_settings)
        self.settings_layout.addWidget(apply_button)

        self.settings_panel.setLayout(self.settings_layout)
        layout.addWidget(self.settings_panel)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.settings_animation = QPropertyAnimation(self.settings_panel, b"maximumHeight")
        self.settings_animation.setDuration(500)

    def load_config(self):
        config = configparser.ConfigParser()
        config.read('config.txt')

        self.background_color = config.get('Appearance', 'background_color')
        self.font_color = config.get('Appearance', 'font_color')
        self.font_family = config.get('Appearance', 'font_family')
        self.timer_font_size = int(config.get('Appearance', 'timer_font_size'))
        self.session_font_size = int(config.get('Appearance', 'session_font_size'))
        self.settings_font_size = int(config.get('Appearance', 'settings_font_size'))

        self.main_message = config.get('Messages', 'main_message', fallback='Study!')
        self.secondary_message = config.get('Messages', 'secondary_message', fallback='Break:)')

    def create_setting_input(self, label_text, default_value, layout):
        setting_layout = QHBoxLayout()
        label = QLabel(label_text)
        setting_layout.addWidget(label)
        input_field = QLineEdit(str(default_value))
        setting_layout.addWidget(input_field)
        layout.addLayout(setting_layout)
        return input_field

    def toggle_settings(self):
        if self.settings_panel.maximumHeight() == 0:
            self.settings_animation.setStartValue(0)
            self.settings_animation.setEndValue(self.settings_layout.sizeHint().height())
        else:
            self.settings_animation.setStartValue(self.settings_layout.sizeHint().height())
            self.settings_animation.setEndValue(0)
        self.settings_animation.start()

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.current_session = 0
            self.next_phase()

    def pause_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.timer.stop()
            self.stop_button.setText("Resume")
        else:
            self.timer_running = True
            self.timer.start(1000)
            self.stop_button.setText("Pause")

    def next_phase(self):
        if self.current_session < self.sessions:
            if self.current_session % self.long_break_interval == 0 and self.current_session != 0:
                self.remaining_time = self.long_break_time * 60
                self.message_label.setText(self.secondary_message)
            elif self.current_session % 2 == 0:
                self.remaining_time = self.work_time * 60
                self.message_label.setText(self.main_message)
            else:
                self.remaining_time = self.break_time * 60
                self.message_label.setText(self.secondary_message)
            self.current_session += 1
            self.update_session_label()
            self.timer.start(1000)
        else:
            self.timer_running = False

    def update_session_label(self):
        self.session_label.setText(f"Session: {self.current_session}/{self.sessions}")

    def update_timer(self):
        minutes, seconds = divmod(self.remaining_time, 60)
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")
        if self.remaining_time > 0:
            self.remaining_time -= 1
        else:
            self.timer.stop()
            self.next_phase()

    def save_settings(self):
        self.sessions = int(self.sessions_input.text())
        self.work_time = int(self.work_time_input.text())
        self.break_time = int(self.break_time_input.text())
        self.long_break_time = int(self.long_break_time_input.text())
        self.long_break_interval = int(self.long_break_interval_input.text())
        self.setStyleSheet(f"background-color: {self.background_color}; color: {self.font_color}; font-family: {self.font_family};")
        self.timer_label.setStyleSheet(f"font-size: {self.timer_font_size}px;")
        self.message_label.setStyleSheet(f"font-size: {self.session_font_size}px;")
        self.session_label.setStyleSheet(f"font-size: {self.session_font_size}px;")
        self.toggle_settings()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainTimerWindow()
    main_window.show()
    sys.exit(app.exec_())
