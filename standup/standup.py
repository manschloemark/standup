"""
    GUI application to plan work sessions with focus and break intervals.
"""

import webbrowser

import sys
from PySide6 import QtWidgets as qw
from PySide6 import QtCore

from QProgressRing import QProgressRing
import reminders

class SessionQueue():
    """
        Class meant to abstract the work of determining when a session is over
        and when to repeat the intervals and what not
        Not sure if this is really necessary, but I figured I'd give it a shot
    """
    def __init__(self, total_length, focus_interval, break_interval):
        # TODO Implement Me
        self.session_remaining = total_length
        self.focus_interval = focus_interval
        self.break_interval = break_interval
        self.is_break = True

    # NOTE I don't like this.
    def get_next_interval(self):
        if self.session_remaining <= 0:
            return None, None
        self.is_break = not self.is_break
        interval_length = None
        if self.is_break:
            interval_length = self.break_interval
        else:
            interval_length = self.focus_interval

        self.session_remaining -= interval_length

        return self.is_break, interval_length

    def __repr__(self):
        return f'{self.__class__.__name__}'\
                f'({self.session_remaining}, '\
                f'{self.focus_interval}, '\
                f'{self.break_interval})'

class SessionOptions(qw.QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = qw.QGridLayout(self)

        # TODO customize SpinBoxes so they work nicely for time
        # The units for these SpinBoxes is minutes but the timer uses seconds
        self.session_dur_label = qw.QLabel("Session Length:")
        self.session_duration = qw.QSpinBox()
        self.focus_dur_label = qw.QLabel("Focus Interval Length:")
        self.focus_duration = qw.QSpinBox()
        self.break_dur_label = qw.QLabel("Break Interval Length:")
        self.break_duration = qw.QSpinBox()
        # TODO add controls that let the user make a queue out of these

        self.layout.addWidget(self.session_dur_label)
        self.layout.addWidget(self.session_duration)
        self.layout.addWidget(self.focus_dur_label)
        self.layout.addWidget(self.focus_duration)
        self.layout.addWidget(self.break_dur_label)
        self.layout.addWidget(self.break_duration)

    def get_session_queue(self):
        session_duration = self.session_duration.value() * 60
        focus_interval = self.focus_duration.value() * 60
        break_interval = self.break_duration.value() * 60
        session_queue = SessionQueue(session_duration,
                                     focus_interval,
                                     break_interval)

        return session_queue

class ReminderOptionContainer(qw.QWidget):
    def __init__(self, option_dict):
        super().__init__()
        self.option_dict = option_dict
        self.initUI()

    def initUI(self):
        self.layout = qw.QVBoxLayout(self)
        self.reminder_instruction = qw.QLabel("Reminder Type",
                                              alignment=QtCore.Qt.AlignCenter)
        self.reminder_select = qw.QComboBox()
        self.reminder_select.currentTextChanged.connect(self.reminderSelected)
        self.reminder_options = None

        self.layout.addWidget(self.reminder_instruction)
        self.layout.addWidget(self.reminder_select)

        for reminder_type in reminders.reminder_option_dict.keys():
            self.reminder_select.addItem(reminder_type)


    def reminderSelected(self, reminder_name):
        if self.reminder_options:
            self.reminder_options.deleteLater()
        self.reminder_options = reminders.reminder_option_dict[reminder_name]()
        self.layout.addWidget(self.reminder_options)

    def getReminder(self):
        reminder = self.reminder_options.getReminder()
        return reminder


class TimerWidget(qw.QWidget):
    """
        Class that handles all timer events
        Uses a QProgressRing
    """

    done = QtCore.Signal(bool) # Bool tells if timer was cancelled (False) or run to completion (True)

    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.paused = True

        self._timer_interval = 1000

        self.initUI()

    def initUI(self):
        self.layout = qw.QVBoxLayout(self)

        self.progress_ring = QProgressRing()
        self.progress_ring.setMinimum(0)
        self.progress_ring.setFormat("countdown")

        self.progress_ring.complete.connect(self.timerFinished)

        self.control_container = qw.QHBoxLayout()
        # Stop button cancels the timer and emits 'False'
        self.stop_button = qw.QPushButton("Stop")
        self.stop_button.clicked.connect(self.stopTimer)

        self.pause_toggle = qw.QPushButton("Unpause")
        self.pause_toggle.clicked.connect(self.togglePause)

        # Finish button stops the timer and emits 'True'
        self.finish_button = qw.QPushButton("Finish")
        self.finish_button.clicked.connect(self.timerFinished)

        self.control_container.addWidget(self.stop_button)
        self.control_container.addWidget(self.pause_toggle)
        self.control_container.addWidget(self.finish_button)

        self.layout.addWidget(self.progress_ring)
        self.layout.addLayout(self.control_container)


    def startTimer(self):
        if self.timer_id is None:
            self.timer_id = super().startTimer(self._timer_interval)
            self.paused = False
            self.pause_toggle.setText("Pause")

    def killTimer(self, timer_id):
        if timer_id is not None:
            super().killTimer(timer_id)
            self.timer_id = None
            self.paused = True
            self.pause_toggle.setText("Unpause")

    def togglePause(self):
        if self.paused:
            self.startTimer()
        else:
            self.killTimer(self.timer_id)

    def stopTimer(self, _):
        self.killTimer(self.timer_id)
        self.done.emit(False)

    def timerFinished(self):
        self.killTimer(self.timer_id)
        self.done.emit(True)

    def startNewCountdown(self, duration):
        self.progress_ring.setMaximum(duration)
        self.progress_ring.setValue(0)
        self.startTimer()

    def timerEvent(self, timer_event):
        if self.timer_id == timer_event.timerId():
            self.progress_ring.setValue(self.progress_ring.value() + 1)



class StandUpWindow(qw.QMainWindow):
    def __init__(self):
        super().__init__()

        self.window_title = "Stand Up"

        self.init_ui()

    def init_ui(self):
        self.screen_stack = qw.QStackedWidget(self)

        self.start_screen = qw.QWidget()
        self.start_layout = qw.QVBoxLayout(self.start_screen)

        self.timer_screen = qw.QWidget()
        self.timer_layout = qw.QVBoxLayout(self.timer_screen)

        self.transition_screen = qw.QWidget()
        self.transition_layout = qw.QVBoxLayout(self.transition_screen)

        # Set up start screen
        self.title = qw.QLabel('Stand Up',
                               alignment=QtCore.Qt.AlignCenter)

        self.session_instruction = qw.QLabel('Session Options',
                                             alignment=QtCore.Qt.AlignCenter)

        self.session_options = SessionOptions()

        self.reminder_options = ReminderOptionContainer(reminders.reminder_option_dict)

        self.start_session_button = qw.QPushButton("Start Session")
        self.start_session_button.clicked.connect(self.start_session)

        self.start_layout.addWidget(self.title)
        self.start_layout.addWidget(self.session_instruction)
        self.start_layout.addWidget(self.session_options)
        self.start_layout.addWidget(self.reminder_options)
        self.start_layout.addWidget(self.start_session_button)
        # Load reminder types after setting layout so
        # the reminderSelectedMethod works properly

        # Set up timer screen
        self.timer_widget = TimerWidget()
        self.timer_widget.done.connect(self.interval_ended)

        # TODO gonna have some slot / signal to handle timer finish
        # TODO gonna need controls to cancel / pause timers, I suppose.
        # TODO but maybe those should be in the timer widgets?
        self.timer_layout.addWidget(self.timer_widget)

        # Timer End Screen / Transition Screen

        self.transition_message = qw.QLabel()
        self.continue_button = qw.QPushButton("Next Interval")
        self.continue_button.clicked.connect(self.start_next_interval)

        self.transition_layout.addWidget(self.transition_message, QtCore.Qt.AlignCenter)
        self.transition_layout.addWidget(self.continue_button, QtCore.Qt.AlignCenter)

        self.screen_stack.addWidget(self.start_screen)
        self.screen_stack.addWidget(self.timer_screen)
        self.screen_stack.addWidget(self.transition_screen)

        self.setCentralWidget(self.screen_stack)


    def start_next_interval(self):
        self.is_break, self.interval_duration = self.session_queue.get_next_interval()

        if self.is_break is None and self.interval_duration is None:
            self.finish_session()
        else:
            if self.is_break:
                self.setWindowTitle(self.window_title + " - Break")
            else:
                self.setWindowTitle(self.window_title + " - Focus")

            self.screen_stack.setCurrentWidget(self.timer_screen)
            self.timer_widget.startNewCountdown(self.interval_duration)

    def interval_ended(self, timer_finished):
        if timer_finished:
            if self.is_break:
                self.start_next_interval()
            else:
                self.reminder.handle()
                self.screen_stack.setCurrentWidget(self.transition_screen)
            # TODO add new screen for after intervals
        else:
            #TODO Interval was cancelled, what do?
            self.finish_session()

    @QtCore.Slot()
    def start_session(self):
        self.session_queue = self.session_options.get_session_queue()
        self.reminder = self.reminder_options.getReminder()
        self.transition_message.setText(self.reminder.message)
        self.start_next_interval()

    def finish_session(self):
        self.setWindowTitle(self.window_title)
        self.screen_stack.setCurrentWidget(self.start_screen)


def main():
    app = qw.QApplication([])
    #w = TimerWidget()
    #w.show()
    standup = StandUpWindow()
    standup.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
