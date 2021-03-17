"""
    GUI application to plan work sessions with focus and break intervals.
"""

import webbrowser

import sys
from PySide6 import QtWidgets as qw
from PySide6 import QtCore, QtGui

from QProgressRing import QProgressRing
import reminders

def get_children(layout):
    """
        Generator to get all widgets from a layout without relying on
        the children() method
    """
    index = 0
    count = layout.count()
    while index < count:
        yield layout.itemAt(index).widget()
        index += 1

class DurationSpinBox(qw.QSpinBox):
    """
        This widget aims to provide a user-friendly and intuitive method of
        entering a duration of time in hours and minutes.
        It currently does not work as well as I want it to.
        I think QSpinBox is not right parent widget
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(1, 600)

    def textFromValue(self, value):
        h, m = divmod(value, 60)
        return f'{h}h {m}m'

# NOTE this doesn't really need to be a class.
#      Instead I can make a function that returns a deque or queue
class SessionQueue():
    """
        Class meant to abstract the work of determining when a session is over
        and when to repeat the intervals and what not
        Not sure if this is really necessary, but I figured I'd give it a shot
    """
    def __init__(self, total_length, focus_intervals, break_intervals):
        # TODO Implement Me
        self.session_remaining = total_length
        self.focus_intervals = focus_intervals
        self.focus_index = 0
        self.break_intervals = break_intervals
        self.break_index = 0
        self.is_break = True

    # NOTE I don't like this.
    def get_next_interval(self):
        self.is_break = not self.is_break
        if self.session_remaining <= 0:
            return None, None, None
        interval_length = None
        if self.is_break:
            interval_length, reminder = self.break_intervals[self.break_index]
            self.break_index += 1
            if self.break_index == len(self.break_intervals):
                self.break_index = 0
        else:
            interval_length, reminder = self.focus_intervals[self.focus_index]
            self.focus_index += 1
            if self.focus_index == len(self.focus_intervals):
                self.focus_index = 0

        self.session_remaining -= interval_length


        return self.is_break, interval_length, reminder

    def __repr__(self):
        return f'{self.__class__.__name__}'\
                f'({self.session_remaining}, '\
                f'{self.focus_interval}, '\
                f'{self.break_interval})'


class ReminderOptionContainer(qw.QWidget):
    def __init__(self, option_dict):
        super().__init__()
        self.option_dict = option_dict
        self.initUI()

    def initUI(self):
        self.layout = qw.QVBoxLayout(self)
        #self.reminder_instruction = qw.QLabel("Reminder Type",
        #                                      alignment=QtCore.Qt.AlignCenter)
        self.reminder_select = qw.QComboBox()
        self.reminder_select.currentTextChanged.connect(self.reminderSelected)
        self.reminder_options = None

        #self.layout.addWidget(self.reminder_instruction)
        self.layout.addWidget(self.reminder_select, QtCore.Qt.AlignTop)

        for reminder_type in reminders.reminder_option_dict.keys():
            self.reminder_select.addItem(reminder_type)


    def reminderSelected(self, reminder_name):
        if self.reminder_options:
            self.reminder_options.deleteLater()
        self.reminder_options = reminders.reminder_option_dict[reminder_name]()
        self.layout.addWidget(self.reminder_options, QtCore.Qt.AlignTop)

    def getReminder(self):
        reminder = self.reminder_options.getReminder()
        return reminder


class IntervalOptions(qw.QWidget):
    def __init__(self, reminder_dict):
        super().__init__()
        self.initUI(reminder_dict)

    def initUI(self, reminder_dict):
        self.layout = qw.QFormLayout(self)
        self.layout.setFieldGrowthPolicy(qw.QFormLayout.FieldsStayAtSizeHint)
        self.layout.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignTop)
        self.duration_label = qw.QLabel("Interval Length:")
        self.duration_input = DurationSpinBox()
        self.reminder_label = qw.QLabel("Reminder")
        self.reminder_options = ReminderOptionContainer(reminder_dict)

        self.layout.addRow(self.duration_label, self.duration_input)
        self.layout.addRow(self.reminder_label)
        self.layout.addRow(self.reminder_options)

    def getInterval(self):
        duration = self.duration_input.value() * 60
        reminder = self.reminder_options.getReminder()
        return (duration, reminder)


class SessionOptions(qw.QWidget):
    def __init__(self, reminder_options):
        super().__init__()
        #self._palette = QtGui.QGuiApplication.palette()
        self.reminder_options = reminder_options
        self.init_ui()

    def init_ui(self):
        self.layout = qw.QGridLayout(self)

        # TODO customize SpinBoxes so they work nicely for time
        # The units for these SpinBoxes is minutes but the timer uses seconds
        self.session_dur_label = qw.QLabel("Session Length:")
        self.session_duration = DurationSpinBox()

        # TODO add controls that let the user make a queue out of these
        self.interval_options_container = qw.QWidget()
        self.interval_options_grid = qw.QGridLayout(self.interval_options_container)

        focus_label = qw.QLabel("Focus Intervals")
        break_label = qw.QLabel("Break Intervals")

        focus_interval_frame = qw.QFrame()
        focus_interval_frame.setFrameStyle(qw.QFrame.StyledPanel | qw.QFrame.Sunken)
        self.focus_intervals_container = qw.QVBoxLayout(focus_interval_frame)
        self.addFocusInterval()
        #default_focus_option = IntervalOptions(self.reminder_options)
        #self.focus_intervals_container.addWidget(default_focus_option)

        break_interval_frame = qw.QFrame()
        break_interval_frame.setFrameStyle(qw.QFrame.StyledPanel | qw.QFrame.Sunken)
        self.break_intervals_container = qw.QVBoxLayout(break_interval_frame)
        self.addBreakInterval()
        #default_break_option = IntervalOptions(self.reminder_options)
        #self.break_intervals_container.addWidget(default_break_option)

        self.add_focus_interval = qw.QPushButton("Add Focus Interval")
        self.add_focus_interval.clicked.connect(self.addFocusInterval)
        self.add_break_interval = qw.QPushButton("Add Break Interval")
        self.add_break_interval.clicked.connect(self.addBreakInterval)

        self.interval_options_grid.addWidget(focus_label, 0, 0)
        self.interval_options_grid.addWidget(break_label, 0, 1)

        self.interval_options_grid.addWidget(focus_interval_frame, 1, 0, 2, 1)
        self.interval_options_grid.addWidget(break_interval_frame, 1, 1, 2, 1)
        self.interval_options_grid.addWidget(self.add_focus_interval, 3, 0)
        self.interval_options_grid.addWidget(self.add_break_interval, 3, 1)

        self.layout.addWidget(self.session_dur_label, 0, 0)
        self.layout.addWidget(self.session_duration, 0, 1)
        self.layout.addWidget(self.interval_options_container, 1, 0, 1, 2)

    def addFocusInterval(self, *args):
        new_widget = IntervalOptions(self.reminder_options)
        new_widget.setAutoFillBackground(True)
        palette = new_widget.palette()

        if(self.focus_intervals_container.count() % 2):
            palette.setColor(palette.Window, palette.color(palette.Active, palette.Base))
        else:
            palette.setColor(palette.Window, palette.color(palette.Active, palette.AlternateBase))

        new_widget.setPalette(palette)

        self.focus_intervals_container.addWidget(new_widget)

    def addBreakInterval(self, *args):
        new_widget = IntervalOptions(self.reminder_options)
        new_widget.setAutoFillBackground(True)
        palette = new_widget.palette()

        if(self.break_intervals_container.count() % 2):
            palette.setColor(palette.Window, palette.color(palette.Active, palette.AlternateBase))
        else:
            palette.setColor(palette.Window, palette.color(palette.Active, palette.Base))

        new_widget.setPalette(palette)

        self.break_intervals_container.addWidget(new_widget)

    def get_session_queue(self):
        session_duration = self.session_duration.value() * 60

        focus_intervals = [focus_widget.getInterval()
                            for focus_widget
                            in get_children(self.focus_intervals_container)]

        break_intervals = [break_widget.getInterval()
                            for break_widget
                            in get_children(self.break_intervals_container)]

        session_queue = SessionQueue(session_duration,
                                     focus_intervals,
                                     break_intervals)

        return session_queue


# TODO implement me
class SessionInfo(qw.QDockWidget):
    """
        Widget that shows info about the current session
    """

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        pass


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

        self.session_options = SessionOptions(reminders.reminder_option_dict)

        self.start_session_button = qw.QPushButton("Start Session")
        self.start_session_button.clicked.connect(self.start_session)

        self.start_layout.addWidget(self.title)
        self.start_layout.addWidget(self.session_instruction)
        self.start_layout.addWidget(self.session_options)
        self.start_layout.addWidget(self.start_session_button)

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

        # NOTE this does nothing right now
        self.session_info = SessionInfo()

        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.session_info)


    def start_next_interval(self):
        self.is_break, self.interval_duration, self.reminder = self.session_queue.get_next_interval()

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
            if self.reminder:
                self.transition_message.setText(self.reminder.message)
                self.reminder.handle()
                self.screen_stack.setCurrentWidget(self.transition_screen)
            else:
                self.start_next_interval()
        else:
            self.finish_session()

    @QtCore.Slot()
    def start_session(self):
        self.session_queue = self.session_options.get_session_queue()
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
