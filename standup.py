"""
    GUI application to plan work sessions with focus and break intervals.
"""

import webbrowser

import sys
from PySide6 import QtWidgets as qw
from PySide6 import QtCore

from QProgressRing import QProgressRing

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
        self.is_break = not self.is_break
        interval_length = None
        if self.is_break:
            interval_length = self.break_interval
        else:
            interval_length = self.focus_interval

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
        session_duration = self.session_duration.value()
        focus_interval = self.focus_duration.value()
        break_interval = self.break_duration.value()
        session_queue = SessionQueue(session_duration,
                                     focus_interval,
                                     break_interval)

        return session_queue


class TimerWidget(qw.QWidget):
    """
        Class that handles all timer events
        Uses a QProgressRing
    """

    stopped = QtCore.signal()

    def __init__(self):
        super().__init__()
        self.timer_id = None
        self.paused = True

        self._timer_interval = 1000

        self.init_ui()

    def init_ui(self):
        self.layout = qw.QVBoxLayout(self)

        self.progress_ring = QProgressRing()
        self.progress_ring.setFormat("countdown")

        self.pause_toggle = QPushButton("Pause")
        self.pause_toggle.clicked.connect(self.togglePause)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stopTimer)

        self.layout.addWidget(self.progress_ring)

    def startTimer(self):
        if self.timer_id is None:
            self.timer_id = super().startTimer(self._timer_interval)
            self.paused = False

    def killTimer(self, timer_id):
        if timer_id is not None:
            super().killTimer(timer_id)
            self.timer_id = None

    def togglePause(self):
        if self.paused:
            self.pause_button.setText("Pause")
            self.startTimer()
        else:
            self.pause_button.setText("Unpause")
            self.stopTimer(self.timer_id)

    def stopTimer(self):
        self.stopTimer(self.timer_id)
        self.stopped.emit()

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
        # TODO add options screen?

        # Set up start screen
        self.title = qw.QLabel('Stand Up',
                               alignment=QtCore.Qt.AlignCenter)

        self.session_instruction = qw.QLabel('Session Options',
                                             alignment=QtCore.Qt.AlignCenter)

        self.session_options = SessionOptions()

        self.start_session_button = qw.QPushButton("Start Session")
        self.start_session_button.clicked.connect(self.start_session)

        self.start_layout.addWidget(self.title)
        self.start_layout.addWidget(self.session_instruction)
        self.start_layout.addWidget(self.session_options)
        self.start_layout.addWidget(self.start_session_button)


        # Set up timer screen
        self.timer_widget = TimerWidget()

        # TODO gonna have some slot / signal to handle timer finish
        # TODO gonna need controls to cancel / pause timers, I suppose.
        # TODO but maybe those should be in the timer widgets?
        self.timer_layout.addWidget(self.timer_widget)


        self.screen_stack.addWidget(self.start_screen)
        self.screen_stack.addWidget(self.timer_screen)


        self.setCentralWidget(self.screen_stack)

    def start_timer(self, is_break, duration):
        # NOTE maybe move this somewhere else because it makes this method kind of ugly.
        if is_break:
            self.setWindowTitle(self.window_title + "- Break")
        else:
            self.setWindowTitle(self.window_title + "- Focus")

        self.screen_stack.setCurrentWidget(self.timer_screen)
        self.timer_widget.start_timer(duration)

    def start_next_interval(self):
        self.is_break, self.interval_duration = self.session_queue.get_next_interval()
        self.start_timer(self.is_break, self.interval_duration)

    @QtCore.Slot()
    def start_session(self):
        self.session_queue = self.session_options.get_session_queue()
        print(self.session_queue)

        self.start_next_interval()




def main():
    app = qw.QApplication([])
    standup = StandUpWindow()
    standup.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
