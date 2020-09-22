"""
    This module contains a custom widget that functions as a countdown timer
    with a round progress bar
"""
from PyQt5.QtWidgets import QProgressBar, QWidget, QApplication, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QGuiApplication, QPalette
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint

import math


# TODO learn how to make this widget follow a Qt theme
class ProgressRing(QWidget):
    """
        Custom widget that acts like a QProgressBar but designed to display times
        To save time I am only making this work nicely with whole seconds.
    """
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.palette = QGuiApplication.palette()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.radius = 0
        self.timer_id = None
        self.duration = None
        self.show_seconds, self.show_minutes, self.show_hours = False, False, False

    def set_timer(self, interval, timeout=1000):
        self.duration = interval
        self.set_text_format()
        self.start_timer(timeout)

    def start_timer(self, timeout=1000):
        self.value = self.duration
        self.repaint()
        self.timer_id = self.startTimer(timeout)

    def stop_timer(self):
        if self.timer_id is None:
            return
        self.killTimer(self.timer_id)
        self.timer_id = None

    def set_duration(self, duration):
        self.duration = duration
        self.set_text_format()

    def set_text_format(self):
        """ Determine based on the duration if the clock should display seconds, minutes, and/or hours """
        # NOTE I feel like there must be a better way to do this
        if self.duration > 0:
            self.show_seconds = True
            self.font_div = 2
        if self.duration // 60:
            self.show_minutes = True
            self.font_div = 4
        if self.duration // 60 // 60:
            self.show_hours = True
            self.font_div = 5

    def text(self):
        # NOTE these calculations work but are very ugly and hastily made
        #      there has to be a better way to do this
        m, s = divmod(self.value, 60)
        h, m = divmod(m, 60)
        # build a string based on the show_hours/minutes/seconds flags
        # NOTE the reason I use show_[seconds/minutes/hours] flags is because
        #      they are determined by the duration from the start of the timer,
        #      not the current value.
        #      So even if there are 50 seconds in a timer, if the timer was
        #      originally set to 1 minute and 30 seconds, it will show the 
        #      minutes place as 0.
        #      I figured I'd do this so the user can get some sort of idea
        #      of where the timer started
        time_remaining = ''
        if self.show_hours:
            time_remaining += f'{h:0>2}'
            if self.show_minutes:
                time_remaining += ':'
        if self.show_minutes:
            time_remaining += f'{m:0>2}'
            if self.show_seconds:
                time_remaining += ':'
        if self.show_seconds:
            time_remaining += f'{s:0>2}'
        return time_remaining

    def circumference(self):
        return int(2 * 3.14159 * self.radius)

    def paintEvent(self, paint_event):
        qp = QPainter()
        qp.begin(self)
        self.drawMainCircle(paint_event, qp)
        self.drawProgressCircle(paint_event, qp)
        self.drawText(paint_event, qp)
        qp.end()

    def drawMainCircle(self, paint_event, painter):
        circle_pen = QPen(self.palette.color(QPalette.Active, QPalette.Midlight))
        circle_pen.setWidth(8)
        painter.setBrush(self.palette.brush(QPalette.Active, QPalette.Mid))
        painter.setPen(circle_pen)
        self.radius = int(min(paint_event.rect().width(), paint_event.rect().height()) * 0.9 // 2)
        center = paint_event.rect().center()
        # Keep a reference to that square that the main
        # circle is drawn inside of so the drawProgressCircle
        # can easily access it and draw on top of it.
        self.square = QRect(center - QPoint(self.radius, self.radius), center + QPoint(self.radius, self.radius))
        painter.drawEllipse(self.square)

    def drawProgressCircle(self, paint_event, painter):
        if not self.duration:
            return
        progress_pen = QPen(self.palette.color(QPalette.Active, QPalette.Link))
        progress_pen.setWidth(12)
        progress_pen.setCapStyle(Qt.RoundCap)
        painter.setPen(progress_pen)
        painter.setBrush(self.palette.brush(QPalette.Active, QPalette.Button))

        if self.value == 0:
            painter.drawEllipse(self.square)
            return
        # The QPainter.drawArc() method specifies the angles
        # to 1 / 16th of a degree, that's why I multiply degrees by 16
        seconds_per_step = self.duration / (360 * 16)

        # This ends up drawing 1 degree for every 1 / 5760th of the duration that has passed
        # I feel like there is a better way to do this.
        angle_span = -1 * abs(int((360 * 16) - (self.value / seconds_per_step)))
        start_angle = (90 * 16) # Start at the top of the circle
        painter.drawArc(self.square, start_angle, angle_span)

    def drawText(self, paint_event, painter):
        painter.setPen(QPen(self.palette.color(QPalette.Active, QPalette.WindowText)))
        painter.setBrush(self.palette.brush(QPalette.Active, QPalette.WindowText))
        timer_font = QFont("")
        timer_font.setStyleHint(QFont.Monospace)
        timer_font.setPointSize(self.radius // self.font_div)
        painter.setFont(timer_font)
        painter.drawText(paint_event.rect(), Qt.AlignCenter, self.text())

    def timerEvent(self, timer_event):
        if self.timer_id == timer_event.timerId():
            self.value -= 1
            self.repaint()
            # The reason I do this if-statement is so the user has a moment to see the circle completely colored in.
            # IDK. It's probably not the best way to handle this.
            # A better way is probably for the standup widget to leave the timer on the screen.
            # Forcing the timer to take an extra 600ms kind of invalidates the timer.
            # IDK.
            # NOTE consider changing the standup method and returning this method back to normal
            if self.value == 0:
                self.killTimer(self.timer_id)
                self.timer_id = None
                self.final_timer = self.startTimer(600)
        elif self.final_timer == timer_event.timerId():
            self.killTimer(self.final_timer)
            self.final_timer = None
            self.finished.emit()

if __name__ == '__main__':
    import sys
    app = QApplication([])

    test = ProgressRing()
    test.setWindowTitle("Timer")
    test.finished.connect(lambda: test.set_timer(60))
    test.show()
    test.set_timer(4)
    print(test.circumference())

    sys.exit(app.exec_())
