"""
    GUI that lets you schedule reminders at regular intervals
    to help you give your mind and body and break while you work
    long hours at the computer
"""

import math
import webbrowser

from PyQt5.QtWidgets import QApplication, QMainWindow, QStackedWidget, QWidget, QLabel, QLineEdit, QGridLayout, QComboBox, QPushButton, QVBoxLayout, QSpinBox, QFormLayout, QButtonGroup, QGroupBox, QHBoxLayout, QRadioButton, QProgressBar
from PyQt5.QtCore import QTimer, QTime, QSettings, Qt, QBasicTimer

from timerprogress import ProgressRing

class StandUp(QMainWindow):

    def __init__(self):
        super().__init__()

        self.settings = QSettings("manschloemark", "StandUp")

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
        self.app_reminder_options = RaiseWindowReminderOptions(self.reminder_message)

        self.reminder_type_options.addWidget(self.url_options)
        self.reminder_type_options.addWidget(self.app_reminder_options)

        self.reminder_select.addItem("Open URL")
        self.reminder_select.addItem("Raise StandUp Window")

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
        self.timer_progress = ProgressRing()
        #self.timer_progress.setFixedSize(200, 200)
        self.timer_progress.finished.connect(self.interval_finished)
        stop_button = QPushButton("Stop Session")
        stop_button.clicked.connect(self.stop_session)

        self.running_vbox.addWidget(running_label)
        self.running_vbox.addWidget(self.timer_progress)
        self.running_vbox.addWidget(stop_button)
        self.running_vbox.setAlignment(Qt.AlignCenter)

        self.stack.addWidget(self.start_screen)
        self.stack.addWidget(self.running_screen)
        self.stack.addWidget(self.reminder_screen)

        self.setCentralWidget(self.stack)

    def init_settings(self):
        pass

    def init_reminder(self):
        return self.reminder_type_options.currentWidget().get_reminder()

    def set_infinite_intervals(self, works, breaks):
        self.infinite = True
        # This is so impractical it's hilarious. I'll leave it in for now.
        # Calculate number of times you need to iterate each list until the zipped sequence repeats
        if breaks:
            self.intervals = []
            lcm = (len(works) * len(breaks)) // math.gcd(len(works), len(breaks))
            for index in range(lcm):
                self.intervals.append(works[index])
                self.intervals.append(breaks[index])
        else:
            self.intervals = works



    def set_finite_intervals(self, duration, works, breaks):
        self.infinite = False
        self.intervals = []
        index = 0
        # If works and breaks are lists this will not work
        # Use walrus here so you don't have to do sum(intervals) twice
        while (current_sum := sum(self.intervals)) != duration:
            if breaks:
                if index % 2 == 0:
                    next_interval = works[index // 2 % len(works)]
                else:
                    next_interval = breaks[index // 2 % len(breaks)]
            else:
                next_interval = works[index % len(works)]

            if current_sum + next_interval > duration:
                if index % 2 == 1:
                    self.intervals[-1] += (duration - current_sum)
                else:
                    self.intervals.append(duration - current_sum)
            else:
                self.intervals.append(next_interval)

    # NOTE i will probably rewrite this because it does not let you view the time remaining
    def start_session(self):
        self.reminder = self.init_reminder()

        # TODO Refactor this stuff
        # TODO CHANGE * 5 to * 60 in both places
        #self.duration = self.duration_entry.value() * 60 * 60 # hours to seconds
        #self.interval = self.interval_entry.value() * 60 # minutes to seconds
        duration = self.duration_entry.value() * 2 * 5 # hours to seconds
        interval = [(self.interval_entry.value() * 5)] # minutes to seconds # NOTE NOTE 5 is just so testing is faster!
        # NOTE when I implement breaks I must be sure to include a break_intervals flag
        #      so the reminder handler knows whether or not to account for breaks.
        breaks = None
        self.break_intervals = False
        if duration:
            self.set_finite_intervals(duration, interval, breaks)
        else:
            self.set_infinite_intervals(interval, breaks)
        self.interval_index = 0
        # NOTE since the Progress Ring is now the widget that contains the timer and deals with timerEvents
        #      I will need to refactor this class to apropriately send intervals to the ProgressRing,
        #      and this class will need to make sure it stops when the session duration ends.

        print(self.intervals)
        self.start_next_interval()

    def start_next_interval(self):
        print(self.intervals[self.interval_index % len(self.intervals)])
        self.timer_progress.set_timer(self.intervals[self.interval_index % len(self.intervals)])
        self.stack.setCurrentWidget(self.running_screen)

    def stop_session(self):
        self.timer_progress.stop_timer()
        self.stack.setCurrentWidget(self.start_screen)

#    def timerEvent(self, te):
#        # Make sure you have the right timer
#        # NOTE maybe the timer should stop while the reminder screen is open
#        self.time_elapsed += 1
#        if self.timer_id == te.timerId():
#            if self.time_elapsed == self.duration:
#                # NOTE this currently just always triggers a reminder
#                #      when after the amount of time set in session_entry
#                #      but this is not always a good thing.
#                #      What if the session_duration is evenly divisible by
#                #      the interval?
#                # NOTE it might be cool to have a different reminder when the
#                #      session finishes. So the user knows they are done.
#                self.reminder.handle()
#                self.killTimer(self.timer_id)
#                self.timer_id = None
#            elif self.time_elapsed % self.interval == 0:
#                self.reminder.handle()
#                self.killTimer(self.timer_id)
#                if self.duration and self.time_elapsed + self.interval > self.duration:
#                    self.reset_progress_bar(self.duration - self.time_elapsed)
#                else:
#                    self.reset_progress_bar(self.interval)
#            else:
#                # Timer should keep going, UI should update time visualizer
#                self.update_progress_bar(self.time_elapsed % self.interval)
#        else:
#            raise ValueError(f"Uh so for some reason the timer that triggered this even is different from the last timer you created... oops? self.timer_id = {self.timer_id} vs. {te.timerId()}")
#
#    def reset_progress_bar(self, maximum):
#        self.timer_progress.setValue(0)
#        self.timer_progress.setMaximum(maximum)
#
#    def update_progress_bar(self, secs_remaining):
#        self.timer_progress.setValue(secs_remaining)

    def interval_finished(self):
        self.interval_index += 1
        if not self.infinite and self.interval_index >= len(self.intervals):
            # TODO maybe make a separate screen that tells you when you are done
            self.stack.setCurrentWidget(self.start_screen)
        # Must check if this session has any break intervals.
        # If not then very interval is a work interval, which means you call reminder.handle()
        elif self.break_intervals and self.interval_index % 2 == 0:
            # If the interval index is now even that means you just finished an odd-indexed interval
            # which means you just finished a break.
            # For now, breaks will go straight to the next work interval after finishing their timer.
            self.start_next_interval()
        else:
            self.reminder.handle()
            self.stack.setCurrentWidget(self.reminder_screen)

    def close_reminder(self):
            self.stack.setCurrentWidget(self.start_screen)
            self.start_next_interval()

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

        new_tab.setChecked(True) # By default do new tab. I think it's the most reasonable.
        hbox.addWidget(same_window)
        hbox.addWidget(new_window)
        hbox.addWidget(new_tab)

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


class Reminder:
    def __init__(self):
        super().__init__()

    def load_profile(self):
        raise NotImplementedError

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

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def handle(self):
        self.parent.activateWindow()


def main():
    import sys
    app = QApplication(sys.argv)

    standup = StandUp()
    standup.show()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
