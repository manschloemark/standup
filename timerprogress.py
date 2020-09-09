"""
    This module contains a custom widget that functions as a countdown timer
    with a round progress bar
"""
from PyQt5.QtWidgets import QProgressBar, QWidget, QApplication, QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint

import math


class ProgressRing(QWidget):
    """
        Custom widget that acts like a QProgressBar but designed to display times
        To save time I am only making this work nicely with whole seconds.
    """
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.radius = 0
        self.timer_id = None
        self.duration = None
        self.value = None
        self.show_seconds, self.show_minutes, self.show_hours = False, False, False

    def set_timer(self, duration, timeout=1000):
        self.duration = duration
        self.value = self.duration
        self.set_text_format()
        self.timer_id = self.startTimer(timeout)

    def start_timer(self, timeout=1000):
        self.timer_id = self.startTimer(timeout)

    def stop_timer(self):
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
        if self.timer_id is None:
            return "Not Running"
        m, s = divmod(self.value, 60)
        h, m = divmod(m, 60)
        # build a string based on the show_hours/minutes/seconds flags
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
        circle_pen = QPen(QColor(0, 0, 0))
        circle_pen.setWidth(8)
        painter.setPen(circle_pen)
        self.radius = int(min(paint_event.rect().width(), paint_event.rect().height()) * 0.9 // 2)
        center = paint_event.rect().center()
        self.square = QRect(center - QPoint(self.radius, self.radius), center + QPoint(self.radius, self.radius))
        painter.drawEllipse(self.square)

    def drawProgressCircle(self, paint_event, painter):
        if not self.duration:
            return
        # Since the arc angle must be specified in 1/16th of a degree
        # I will use that as the step, the smallest fraction of time change to draw
        seconds_per_step = self.duration / (360 * 16)

        # This ends up drawing 1 degree for every 1 / 5760th of the duration that has passed
        # I feel like there is a better way to do this.
        angle_span = -1 * abs(int((360 * 16) - (self.value / seconds_per_step)))

        start_angle = (90 * 16) # Start at the top of the circle

        progress_circle_pen = QPen(QColor(0, 100, 50))
        progress_circle_pen.setWidth(12)

        painter.setPen(progress_circle_pen)
        painter.drawArc(self.square, start_angle, angle_span)


    def drawText(self, paint_event, painter):
        painter.setPen(QColor(0, 0, 0))
        timer_font = QApplication.instance().font()
        timer_font.setPointSize(self.radius // self.font_div)
        painter.setFont(timer_font)
        painter.drawText(paint_event.rect(), Qt.AlignCenter, self.text())

    def timerEvent(self, timer_event):
        if self.timer_id == timer_event.timerId():
            self.value -= 1
            self.repaint()
            if self.value == 0:
                self.killTimer(self.timer_id)
                self.finished.emit()

if __name__ == '__main__':
    import sys
    app = QApplication([])

    test = ProgressRing()
    test.setWindowTitle("Timer")
    test.finished.connect(lambda: test.start_timer(60))
    test.show()
    test.start_timer(2)
    print(test.circumference())

    sys.exit(app.exec_())
