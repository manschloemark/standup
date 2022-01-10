"""
    Mark Schloeman

    Custom PyQt2 QWidget that functions like a QProgressBar
    that draws a circle instead of a bar.
"""

import math
from PySide2 import QtGui, QtCore, QtWidgets


class QProgressRing(QtWidgets.QWidget):
    _TOTAL_DEGREES = 360 * 16  # I'm not satisfied with this name
    # but this variable exists because
    # QtGui.QPainter.drawArc can draw
    # to 1/16 degrees
    # Meaning there are 360 * 16 possible values

    _ARC_OFFSET = 90 * 16  # This variable is used to offset the arc
    # since I want the progress ring
    # to start that the 12 o'clock position (90deg)
    # TODO make this easily adjustable
    complete = QtCore.Signal()

    def __init__(self):
        super().__init__()
        self._palette = QtGui.QGuiApplication.palette()
        self._minimum = 0
        self._maximum = 0
        self._value = 0
        self._clockwise = True
        self._format = "%"

        self.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding
        )
        self.calcRadius(self.rect().size())
        self.calcSquare(self.rect().center())

    def setRadius(self, radius):
        self._radius = radius

    def setValue(self, value):
        self._value = value
        self.update()
        if self._value == self._maximum:
            self.complete.emit()

    def setMinimum(self, minimum):
        self._minimum = minimum

    def setMaximum(self, maximum):
        self._maximum = maximum

    def setFormat(self, fmt):
        self._format = fmt

    def radius(self):
        return self._radius

    def circumference(self):
        return 2 * math.pi * self._radius

    def value(self):
        return self._value

    def minimum(self):
        return self._minimum

    def maximum(self):
        return self._maximum

    def progress(self):
        return self._value - self._minimum

    def remaining(self):
        return self._maximum - self._value

    def range(self):
        return self._maximum - self._value

    def percentComplete(self):
        return round(((self.progress() / self.range()) * 100), 1)

    def getFormattedText(self):
        if self._value == self._maximum:
            return "Done!"
        if self._format == "%":
            return f"{self.percentComplete()}%"
        elif self._format == "countdown":
            m, s = divmod(self.remaining(), 60)
            h, m = divmod(m, 60)
            if h:
                time_string = f"{h:0>2}h {m:0>2}m {s:0>2}s"
            elif m:
                time_string = f"{m:0>2}m {s:0>2}s"
            else:
                time_string = f"{s:0>2}s"
            return time_string

    def calcSquare(self, center):
        self._square = QtCore.QRect(
            center - QtCore.QPoint(self._radius, self._radius),
            center + QtCore.QPoint(self._radius, self._radius),
        )

    def calcRadius(self, size):
        new_radius = min(size.width(), size.height())
        self._radius = int((new_radius * 0.4))

    def drawOutline(self, qp):
        circle_pen = QtGui.QPen(
            self._palette.color(QtGui.QPalette.Active, QtGui.QPalette.Midlight)
        )
        circle_pen.setWidth(8)

        qp.setBrush(self._palette.brush(QtGui.QPalette.Active, QtGui.QPalette.Mid))
        qp.setPen(circle_pen)

        qp.drawEllipse(self._square)

    def drawProgressArc(self, qp):
        if not self._maximum:
            return

        progress_pen = QtGui.QPen(
            self._palette.color(QtGui.QPalette.Active, QtGui.QPalette.Link)
        )

        progress_pen.setWidth(12)
        progress_pen.setCapStyle(QtCore.Qt.RoundCap)

        qp.setPen(progress_pen)
        qp.setBrush(self._palette.brush(QtGui.QPalette.Active, QtGui.QPalette.Button))
        if self._value == self._maximum:
            qp.drawEllipse(self._square)
        else:
            percent_complete = (self._value - self._minimum) / (
                self._maximum - self._minimum
            )
            arc_span = (self._TOTAL_DEGREES) * percent_complete
            if self._clockwise:
                arc_span *= -1
            qp.drawArc(self._square, self._ARC_OFFSET, arc_span)

    def drawText(self, qp):
        qp.setPen(
            QtGui.QPen(
                self._palette.color(QtGui.QPalette.Active, QtGui.QPalette.WindowText)
            )
        )

        qp.setBrush(
            self._palette.brush(QtGui.QPalette.Active, QtGui.QPalette.WindowText)
        )

        timer_font = QtGui.QFont("monospace")
        timer_font.setStyleHint(QtGui.QFont.Monospace)
        timer_font.setPointSize(
            12
            )  # TODO : make this not hardcoded or change based on size of widget?

        qp.setFont(timer_font)
        qp.drawText(self._square, int(QtCore.Qt.AlignCenter), self.getFormattedText())

    def render(self):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.setRenderHints(qp.Antialiasing)
        self.drawOutline(qp)
        self.drawProgressArc(qp)
        self.drawText(qp)
        qp.end()

    def paintEvent(self, paint_event):
        super().paintEvent(paint_event)
        self.render()

    def resizeEvent(self, resize_event):
        super().resizeEvent(resize_event)
        self.calcRadius(resize_event.size())
        self.calcSquare(self.rect().center())


# Testing
if __name__ == "__main__":
    import sys
    import time

    app = QtWidgets.QApplication([])
    ex = QtWidgets.QWidget()
    l = QtWidgets.QVBoxLayout(ex)
    ring = QProgressRing()
    ring.setFormat("countdown")
    ring.setMinimum(0)
    ring.setMaximum(10)
    ring.setValue(0)
    button = QtWidgets.QPushButton("Add a number")
    button.clicked.connect(lambda x: ring.setValue(ring.value() + 1))

    l.addWidget(ring)
    l.addWidget(button)
    ring.show()
    ex.show()
    sys.exit(app.exec_())
