from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QTimer

class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pomodoro Timer")

        self.sessions = 4
        self.work_time = 25
        self.break_time = 5
        self.long_break_time = 15
        self.long_break_interval = 4

        self.current_session = 0
        self.timer_running = False
        self.remaining_time = 0

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        settings_layout = QVBoxLayout()

        self.sessions_input = self.create_setting_input("Number of sessions:", self.sessions, settings_layout)
        self.work_time_input = self.create_setting_input("Work time (min):", self.work_time, settings_layout)
        self.break_time_input = self.create_setting_input("Break time (min):", self.break_time, settings_layout)
        self.long_break_time_input = self.create_setting_input("Long break time (min):", self.long_break_time, settings_layout)
        self.long_break_interval_input = self.create_setting_input("Long break interval (sessions):", self.long_break_interval, settings_layout)

        layout.addLayout(settings_layout)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_timer)
        layout.addWidget(self.start_button)

        self.timer_label = QLabel("00:00")
        self.timer_label.setStyleSheet("font-size: 48px;")
        layout.addWidget(self.timer_label)

        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

    def create_setting_input(self, label_text, default_value, layout):
        setting_layout = QHBoxLayout()
        label = QLabel(label_text)
        setting_layout.addWidget(label)
        input_field = QLineEdit(str(default_value))
        setting_layout.addWidget(input_field)
        layout.addLayout(setting_layout)
        return input_field

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.current_session = 0
            self.sessions = int(self.sessions_input.text())
            self.work_time = int(self.work_time_input.text())
            self.break_time = int(self.break_time_input.text())
            self.long_break_time = int(self.long_break_time_input.text())
            self.long_break_interval = int(self.long_break_interval_input.text())
            self.next_phase()

    def next_phase(self):
        if self.current_session < self.sessions:
            if self.current_session % self.long_break_interval == 0 and self.current_session != 0:
                self.remaining_time = self.long_break_time * 60
            elif self.current_session % 2 == 0:
                self.remaining_time = self.work_time * 60
            else:
                self.remaining_time = self.break_time * 60
            self.current_session += 1
            self.timer.start(1000)
        else:
            self.timer_running = False

    def update_timer(self):
        minutes, seconds = divmod(self.remaining_time, 60)
        self.timer_label.setText(f"{minutes:02}:{seconds:02}")
        if self.remaining_time > 0:
            self.remaining_time -= 1
        else:
            self.timer.stop()
            self.next_phase()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = PomodoroTimer()
    window.show()
    sys.exit(app.exec_())
