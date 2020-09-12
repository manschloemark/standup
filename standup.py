"""
    GUI that lets you schedule reminders at regular intervals
    to help you give your mind and body and break while you work
    long hours at the computer
"""

import math
import webbrowser

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QPushButton, QVBoxLayout, QSpinBox, QFormLayout, QButtonGroup, QGroupBox, QHBoxLayout, QRadioButton, QTextEdit, QCheckBox
from PyQt5.QtCore import QTimer, QTime, QSettings, Qt, QBasicTimer

from timerprogress import ProgressRing
from reminders import reminder_types

class StandUp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.settings = QSettings("manschloemark", "StandUp")

        self.init_ui()
        self.init_settings()

    def init_ui(self):
        self.stack = QStackedWidget()
        self.status = self.statusBar()

        # Reminder Screen - shown whenever the timer finishes.
        # Can be customized when the user chooses the RaiseWindow reminder
        self.reminder_screen = QWidget()
        reminder_vbox = QVBoxLayout(self.reminder_screen)
        reminder_heading = QLabel("Stand Up!")
        reminder_heading.setProperty("font-class", "heading")
        self.reminder_label = QLabel()
        close_reminder = QPushButton("Continue")
        close_reminder.clicked.connect(self.close_reminder)

        reminder_vbox.addWidget(reminder_heading)
        reminder_vbox.addWidget(self.reminder_label)
        reminder_vbox.addWidget(close_reminder)
        reminder_vbox.setAlignment(Qt.AlignCenter)

        # Start Screen - lets user customize a session and start it
        self.start_screen = QWidget()
        self.start_grid = QGridLayout(self.start_screen)

        app_title = QLabel("StandUp!")
        app_title.setProperty("font-class", "title")
        settings_label = QLabel("Session Settings")
        settings_label.setProperty("font-class", "heading")
        # TODO put a label and combo box for user profiles
        # TODO learn to implement custom QAbstractSpinBox
        #      that intuitively lets user enter [Hhours Mmins]
        session_duration_label = QLabel("Session Length:")
        self.duration_entry = QSpinBox()
        self.duration_entry.setSuffix(" hours")
        # Special case for duration entry - when duration is set to 0
        # the program will run until the user stops it.
        self.duration_entry.setSpecialValueText("Until Stopped")

        work_interval_label = QLabel("Work Intervals:")
        self.work_entry = QSpinBox()
        self.work_entry.setMinimum(1)
        self.work_entry.setSuffix(" minutes")

        #self.break_checkbox = QCheckBox("Break Intervals:")
        self.break_checkbox = QLabel("Break Intervals:")
        self.break_entry = QSpinBox()
        self.break_entry.setSuffix(" minutes")
        self.break_entry.setSpecialValueText("Wait for Input")
        #self.break_checkbox.stateChanged.connect(lambda x: self.break_entry.setEnabled(x))
        #self.break_checkbox.setChecked(True)


        reminder_type_label = QLabel("Reminder Type:")
        self.reminder_select = QComboBox()
        self.reminder_type_stack = QStackedWidget()
        self.reminder_select.currentIndexChanged.connect(
                self.reminder_type_stack.setCurrentIndex
                )

        for reminder_type in reminder_types:
            reminder_options = reminder_type(self.reminder_label)
            self.reminder_type_stack.addWidget(reminder_options)
            self.reminder_select.addItem(reminder_options.name)

        # TODO add buttons - a 'Save Profile' button, a 'Set Default'
        #      and a 'Save New Profile'
        #      or maybe these could be in a toolbar / menubar

        start_button = QPushButton("Start Session")
        start_button.clicked.connect(self.start_session)

        self.start_grid.addWidget(app_title, 0, 0, 1, 2)
        self.start_grid.addWidget(settings_label, 1, 0)
        self.start_grid.addWidget(session_duration_label, 2, 0)
        self.start_grid.addWidget(self.duration_entry, 2, 1)
        self.start_grid.addWidget(work_interval_label, 3, 0)
        self.start_grid.addWidget(self.work_entry, 3, 1)
        self.start_grid.addWidget(self.break_checkbox, 4, 0)
        self.start_grid.addWidget(self.break_entry, 4, 1)
        self.start_grid.addWidget(reminder_type_label, 5, 0)
        self.start_grid.addWidget(self.reminder_select, 5, 1)
        self.start_grid.addWidget(self.reminder_type_stack, 6, 0, 2, 2)
        self.start_grid.addWidget(start_button, 8, 0, 1, 2, Qt.AlignCenter)
        self.start_grid.setAlignment(Qt.AlignCenter)

        # Running Screen - shown while a timer is running, whether that be
        # break timer or work timer.
        # Contains a ProgressRing and a button to cancel the timer
        self.running_screen = QWidget()
        self.running_vbox = QVBoxLayout(self.running_screen)

        self.running_label = QLabel()
        self.running_label.setProperty("font-class", "heading")
        self.timer = ProgressRing()
        self.timer.finished.connect(self.interval_finished)
        stop_button = QPushButton("Stop Session")
        stop_button.clicked.connect(self.session_complete)

        self.running_vbox.addWidget(self.running_label)
        self.running_vbox.addWidget(self.timer)
        self.running_vbox.addWidget(stop_button)
        self.running_vbox.setAlignment(Qt.AlignCenter)

        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.running_screen)
        self.stack.addWidget(self.reminder_screen)

        self.setCentralWidget(self.stack)

    def init_settings(self):
        pass

    def init_reminder(self):
        return self.reminder_type_stack.currentWidget().get_reminder()

    def set_status_bar(self):
        status_text = str(self.intervals[self.interval_index % len(self.intervals):])
        self.status.showMessage(status_text)

    def start_session(self):
        # NOTE this methods does a lot. Maybe I should refactor?
        self.reminder = self.init_reminder()

        self.session_time = self.duration_entry.value() * 60 * 60 # hours to seconds
        self.finite = bool(self.session_time) # Lame band-aid
        self.work_length = self.work_entry.value() * 60 # minutes to seconds

        self.break_length = self.break_entry.value() * 60

        self.work_interval = True

        self.start_next_interval()

    def start_next_interval(self):
        if self.work_interval:
            # Flip the work_interval flag to False if the user has break timers set
            self.work_interval = self.break_length == 0
            self.running_label.setText("Focus Mode")
            if self.finite and self.session_time < self.work_length:
                self.timer.set_timer(self.session_time)
                self.session_time = 0
            else:
                self.timer.set_timer(self.work_length)
                if self.finite:
                    self.session_time -= self.work_length
        else:
            self.work_interval = not self.work_interval
            self.running_label.setText("Break Timer")

            if self.finite and self.session_time < self.break_length:
                self.timer.set_timer(self.session_time)
                self.session_time = 0
            else:
                self.timer.set_timer(self.break_length)
                if self.finite:
                    self.session_time -= self.break_length

        self.stack.setCurrentWidget(self.running_screen)

    def set_work_message(self):
        self.reminder_label.setText(self.work_text)

    def session_complete(self):
        self.stack.setCurrentWidget(self.start_screen)
        self.timer.stop_timer()

    def interval_finished(self):
        if self.finite and self.session_time <= 0:
            # Maybe I should make a separete reminder for the final reminder
            self.reminder.handle()
            self.session_complete()
        else:
            if self.work_interval:
                if self.break_length == 0:
                    self.reminder.handle()
                    self.stack.setCurrentWidget(self.reminder_screen)
                else:
                    self.start_next_interval()
            else:
                self.reminder.handle()
                self.start_next_interval()

    # NOTE this method doesn't know what it's doing. Neither do I.
    def close_reminder(self):
            self.start_next_interval()


class ReminderOptions(QWidget):

    def __init__(self):
        super().__init__()

    def load_profile(self):
        raise NotImplementedError

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

        new_tab.setChecked(True) # I think new tab is a reasonable default
        hbox.addWidget(new_tab)
        hbox.addWidget(new_window)
        hbox.addWidget(same_window)

        form.addRow(url_label, self.url_entry)
        form.addRow(tab_policies)

    def get_reminder(self):
        return BrowserReminder(self.url_entry.text(), self.policy_group.checkedId())

class RaiseWindowReminderOptions(ReminderOptions):

    def __init__(self, message_widget):
        super().__init__()
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
        return RaiseWindowReminder(self)

class MaximizeWindowReminderOptions(RaiseWindowReminderOptions):

    def __init__(self, *args):
        super().__init__(*args)

    def get_reminder(self):
        super().set_reminder_text()
        return MaximizeWindowReminder(self)


#class Reminder:
#    def __init__(self):
#        super().__init__()
#
#    def handle(self):
#        raise NotImplementedError
#
#class BrowserReminder(Reminder):
#
#    def __init__(self, url, new_tab_policy=2):
#        super().__init__()
#        self.url = url
#        self.new_tab_policy = new_tab_policy
#
#    def handle(self):
#        webbrowser.open(self.url, new=self.new_tab_policy)
#
#class RaiseWindowReminder(Reminder):
#
#    def __init__(self, parent):
#        super().__init__()
#        self.window = parent.window()
#
#    def handle(self):
#        # There is a chance this doesn't work on Windows or Mac. Or maybe even other Window Managers on Linux.
#        self.window.setWindowState(self.window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
#        self.window.activateWindow()
#
#class MaximizeWindowReminder(RaiseWindowReminder):
#
#    def __init__(self, *args):
#        super().__init__(*args)
#
#    def handle(self):
#        self.window.setWindowState(Qt.WindowMaximized)
#        self.window.activateWindow()
#

def main():
    import os
    import sys
    app = QApplication(sys.argv)

    standup = StandUp()
    with open(os.path.join(os.path.dirname(__file__), "standup-styles.qss")) as styles:
        standup.setStyleSheet(styles.read())
    standup.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
