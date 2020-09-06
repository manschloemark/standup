"""
    GUI that lets you schedule reminders at regular intervals
    to help you give your mind and body and break while you work
    long hours at the computer
"""

import webbrowser

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QPushButton, QVBoxLayout, QSpinBox, QFormLayout, QButtonGroup, QGroupBox, QHBoxLayout, QRadioButton
from PyQt5.QtCore import QTimer, QTime, QSettings, Qt


class StandUp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.settings = QSettings("manschloemark", "StandUp")
        self.timer = QTimer()
        self.timer.timeout.connect(self.remind)

        self.init_ui()
        self.init_settings()

    def init_ui(self):
        self.stack = QStackedWidget()

        self.reminder_screen = QWidget()
        reminder_vbox = QVBoxLayout(self.reminder_screen)
        self.reminder_message = QLabel()
        close_reminder = QPushButton("Close Reminder")
        close_reminder.clicked.connect(self.close_reminder)
        reminder_vbox.addWidget(self.reminder_message)
        reminder_vbox.addWidget(close_reminder)

        self.start_screen = QWidget()
        self.start_grid = QGridLayout(self.start_screen)

        app_title = QLabel("StandUp!")

        self.settings_label = QLabel("Session Settings")
        # TODO put a label and combo box for user profiles

        session_duration_label = QLabel("Session Duration:")
        # TODO learn to implement custom QAbstractSpinBox
        #      that intuitively lets user enter [Hhours Mmins]
        self.duration_entry = QSpinBox()
        self.duration_entry.setSuffix(" hours")
        self.duration_entry.setSpecialValueText("Until Stopped")

        reminder_interval_label = QLabel("Reminder Interval:")
        self.interval_entry = QSpinBox()
        self.interval_entry.setMinimum(1)
        self.interval_entry.setSuffix(" minutes")

        reminder_type_label = QLabel("Reminder Type:")
        self.reminder_select = QComboBox()
        self.reminder_type_options = QStackedWidget()
        self.reminder_select.currentIndexChanged.connect(self.reminder_type_options.setCurrentIndex)

        self.url_options = BrowserReminderOptions()
        self.app_reminder_options = RaiseWindowReminderOptions(self.stack, self.reminder_screen, self.reminder_message)

        self.reminder_type_options.addWidget(self.url_options)
        self.reminder_type_options.addWidget(self.app_reminder_options)

        self.reminder_select.addItem("Open URL")
        self.reminder_select.addItem("Raise StandUp")

        # TODO add buttons - a 'Save Profile' button, a 'Set Default'
        #      and a 'Save New Profile'
        #      or maybe these could be in a toolbar / menubar

        start_button = QPushButton("Start Session")
        start_button.clicked.connect(self.start_session)

        self.start_grid.addWidget(app_title, 0, 0, 1, 2)
        self.start_grid.addWidget(session_duration_label, 1, 0)
        self.start_grid.addWidget(self.duration_entry, 1, 1)
        self.start_grid.addWidget(reminder_interval_label, 2, 0)
        self.start_grid.addWidget(self.interval_entry, 2, 1)
        self.start_grid.addWidget(reminder_type_label, 3, 0)
        self.start_grid.addWidget(self.reminder_select, 3, 1)
        self.start_grid.addWidget(self.reminder_type_options, 4, 0, 2, 2)
        self.start_grid.addWidget(start_button, 6, 0, 1, 2, Qt.AlignCenter)
        self.start_grid.setAlignment(Qt.AlignCenter)

        self.running_screen = QWidget()
        self.running_vbox = QVBoxLayout(self.running_screen)

        running_label = QLabel("Session Running")
        self.next_break = QLabel()
        stop_button = QPushButton("Stop Session")
        stop_button.clicked.connect(self.stop_session)

        self.running_vbox.addWidget(running_label)
        self.running_vbox.addWidget(self.next_break)
        self.running_vbox.addWidget(stop_button)
        self.running_vbox.setAlignment(Qt.AlignCenter)

        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.running_screen)
        self.stack.addWidget(self.reminder_screen)

        self.setCentralWidget(self.stack)

    def init_settings(self):
        pass

    # NOTE i will probably rewrite this because it does not let you view the time remaining
    def start_session(self):
        self.duration = self.duration_entry.value()
        self.interval = self.interval_entry.value()

        if self.duration == 0:
            self.breaks_remaining = -1
        else:
            self.breaks_remaining = int(((self.duration * 60) // self.interval))
        timeout = self.interval * 60 * 1000


        self.timer.start(timeout)
        self.stack.setCurrentWidget(self.running_screen)

    def stop_session(self):
        self.timer.stop()
        self.stack.setCurrentWidget(self.start_screen)

    def remind(self):
        # First, trigger the reminder
        # TODO validate urls
        if self.reminder_type == 'URL':
            webbrowser.open_new_tab(self.url_entry.text())
        elif self.reminder_type == 'FOCUS':
            self.stack.setCurrentWidget(self.reminder_screen)
            self.reminder_message.setText(self.reminder_text.text())
            # TODO make this app the focus of the PC

        # Second, find out if you are done
        if self.breaks_remaining > 0:
            self.breaks_remaining -= 1
        if self.breaks_remaining == 0:
            self.stop_timer()
            return

    def close_reminder(self):
        if self.timer.isActive():
            time_left = QTime.currentTime().addSecs(self.interval * 60)
            self.next_break.setText(f"Next break at: {time_left.toString('h:m p')}")
            self.stack.setCurrentWidget(self.running_screen)
        else:
            self.stack.setCurrentWidget(self.start_screen)

class ReminderOptions(QWidget):

    def __init__(self):
        super().__init__()

    def get_reminder(self):
        raise NotImplementedError

class BrowserReminderOptions(ReminderOptions):

    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        form = QFormLayout(self)

        url_label = QLabel("URL:")
        self.url_entry = QLineEdit()

        tab_policies = QGroupBox("Open URL In...")
        self.policy_group = QButtonGroup()
        tab_policies.setFlat(True)
        hbox = QHBoxLayout(tab_policies)
        same_window = QRadioButton("Same Window")
        new_window = QRadioButton("New Window")
        new_tab = QRadioButton("New Tab")

        self.policy_group.addButton(same_window, id=0)
        self.policy_group.addButton(new_window, id=1)
        self.policy_group.addButton(new_tab, id=2)
        hbox.addWidget(same_window)
        hbox.addWidget(new_window)
        hbox.addWidget(new_tab)

        form.addRow(url_label, self.url_entry)
        form.addRow(tab_policies)

    def get_reminder(self):
        return BrowserReminder(self.url_entry.text(), self.policy_group.checkedId())

class RaiseWindowReminderOptions(ReminderOptions):

    def __init__(self, parent_stack, reminder_widget, message_widget):
        super().__init__()

        self.parent_stack = parent_stack
        self.reminder_widget = reminder_widget
        self.message_widget = message_widget

        self.init_ui()

    def init_ui(self):
        form = QFormLayout(self)

        reminder_message_label = QLabel("Reminder Message:")
        self.reminder_input = QLineEdit()

        form.addRow(reminder_message_label, self.reminder_input)

    def set_reminder_text(self):
        self.message_widget.setText(self.reminder_input.text())

    def get_reminder(self):
        self.set_reminder_text()
        return RaiseWindowReminder(self.parent_stack, self.reminder_widget)


class Reminder:
    def __init__(self):
        super().__init__()

    def handle(self):
        raise NotImplementedError

class BrowserReminder(Reminder):

    def __init__(self, url, new_tab_policy=2):
        super().__init__()
        self.url = url
        self.new_tab_policy = new_tab_policy

    def handle(self):
        webbrowser.open(self.url, new=self.new_tab_policy)

class RaiseWindowReminder(Reminder):

    def __init__(self, parent_stack, reminder_widget):
        super().__init__()
        self.parent_stack = parent_stack
        self.reminder_widget = reminder_widget

    def handle(self):
        self.parent_stack.setCurrentWidget(self.reminder_widget)
        self.reminder_widget.activateWindow()


def main():
    import sys
    app = QApplication(sys.argv)

    standup = StandUp()
    standup.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
