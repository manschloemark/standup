"""
    GUI application to plan work sessions with focus and break intervals.
"""
import json
import os

import webbrowser

import sys
from PySide2 import QtWidgets as qw
from PySide2 import QtCore, QtGui

from standup import rcicons

from standup.QProgressRing import QProgressRing
from standup import reminders


def get_profile_location():
    home = os.getenv("HOME")
    filename = "profiles.json"
    if sys.platform == "win32":
        profile_path = os.path.join(home, "AppData", "Roaming", "standup", filename)
    elif sys.platform.startswith("linux"):
        profile_path = os.path.join(home, ".local", "share", "standup", filename)
    elif sys.platform == "darwin": # Mac
        profile_path = os.path.join(home, "Library", "Application Support", "standup", filename)
    else:
        profile_path = os.path.join(os.path.dirname(__file__), filename)
    if profile_path:
        os.makedirs(os.path.dirname(profile_path), exist_ok=True)
    return profile_path


def validate_reminder_types(profiles):
    """
    Checks profile data for invalid reminder types and fixes errors
    ex: profile uses a reminder type that has been removed)
    If an invalid reminder type is found it is replaced with 'None'
    """

    for profile in profiles:
        for interval in profiles[profile]["focus_intervals"]:
            if interval["reminder"]["name"] not in reminders.reminder_option_dict:
                interval["reminder"]["name"] = "None"
        for interval in profiles[profile]["break_intervals"]:
            if interval["reminder"]["name"] not in reminders.reminder_option_dict:
                interval["reminder"]["name"] = "None"
    return profiles


def read_profiles(filename=None):
    if filename is None:
        filename = get_profile_location()
    with open(filename, "a+") as config:
        config.seek(0)
        try:
            profiles = json.load(config)
        except json.JSONDecodeError:
            profiles = {}
        profiles = validate_reminder_types(profiles)
        write_profiles(profiles, None)
        return profiles


def load_profile(profile_name: str):
    profile = read_profiles().get(profile_name)
    return profile


def write_profiles(data, filename=None):
    if filename is None:
        filename = get_profile_location()
    with open(filename, "w+") as config:
        json.dump(data, config, indent="  ")


def save_profile(profile_name: str, data: dict):
    profiles = read_profiles()
    profiles[profile_name] = data
    write_profiles(profiles)


def delete_profile(profile_name):
    profiles = read_profiles()
    del profiles[
        profile_name
    ]  # TODO add try-catch? Technically this shouldn't fail but you never know
    write_profiles(profiles)


def get_children(layout):
    """
    Generator to get all widgets from a layout.
    """
    index = 0
    count = layout.count()
    while index < count:
        yield layout.itemAt(index).widget()
        index += 1


class DurationSpinBox(qw.QSpinBox):
    """
    Spin box that is made for entering time duration
    Currently unfinished but it works for now
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setRange(1, 600)
        self.setSuffix(" min")



class SessionQueue:
    """
    Handles session runtime
    Iterates through focus and break interval lists
    """

    def __init__(self, total_length, focus_intervals, break_intervals):
        self.session_remaining = total_length
        self.focus_intervals = focus_intervals
        self.focus_index = 0
        self.break_intervals = break_intervals
        self.break_index = 0
        self.is_break = True

    def get_next_interval(self):
        self.is_break = not self.is_break
        if self.session_remaining <= 0:
            return None, None, None
        interval_length = None
        if self.is_break and len(self.break_intervals):
            interval_length, reminder = self.break_intervals[self.break_index]
            self.break_index += 1
            if self.break_index == len(self.break_intervals):
                self.break_index = 0
        elif len(self.focus_intervals):
            interval_length, reminder = self.focus_intervals[self.focus_index]
            self.focus_index += 1
            if self.focus_index == len(self.focus_intervals):
                self.focus_index = 0
        else:
            return None, None, None

        self.session_remaining -= interval_length

        return self.is_break, interval_length, reminder

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"({self.session_remaining}, "
            f"{self.focus_interval}, "
            f"{self.break_interval})"
        )


class IntervalOptions(qw.QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.setStyles()

    def initUI(self):
        self.layout = qw.QGridLayout(self)
        #self.layout.setFieldGrowthPolicy(qw.QFormLayout.FieldsStayAtSizeHint)
        self.remove_button = qw.QToolButton()
        #self.remove_button.setSizePolicy(qw.QSizePolicy(qw.QSizePolicy.Maximum, qw.QSizePolicy.Fixed))
        self.remove_button.clicked.connect(self.deleteSelf)
        self.remove_button.setToolTip("Remove Interval")
        self.duration_label = qw.QLabel("Interval Length:")
        self.duration_input = DurationSpinBox()
        self.reminder_label = qw.QLabel("Reminder:")
        self.reminder_select = qw.QComboBox()
        self.reminder_select.currentTextChanged.connect(self.reminderSelected)
        self.reminder_options = None

        for reminder_type in reminders.reminder_option_dict.keys():
            self.reminder_select.addItem(reminder_type)

        self.layout.addWidget(self.remove_button, 0, 0)
        self.layout.addWidget(self.duration_label, 0, 1)
        self.layout.addWidget(self.duration_input, 0, 2)
        self.layout.addWidget(self.reminder_label, 1, 1)
        self.layout.addWidget(self.reminder_select, 1, 2)

        self.setSizePolicy(qw.QSizePolicy.Expanding, qw.QSizePolicy.Fixed)

    def setStyles(self):

        # NOTE : I wanted to change the color of the icon but I couldn't.
        #palette = QtGui.QPalette()
        #palette.setColor(
            #palette.ButtonText, palette.color(palette.Active, palette.ButtonText)
        #)
        #self.remove_button.setPalette(palette)

        self.remove_button.setIcon(QtGui.qApp.style().standardIcon(qw.QStyle.SP_TrashIcon))
        
        self.remove_button.setStyleSheet("QToolButton { background-color: darkred }")

    def deleteSelf(self):
        self.deleteLater()

    def getData(self):
        duration = self.duration_input.value()
        reminder_settings = self.reminder_options.getData()
        return {"duration": duration, "reminder": reminder_settings}

    def putData(self, data):
        self.duration_input.setValue(data["duration"])
        reminder_type = data["reminder"]["name"]
        if reminder_type not in reminders.reminder_option_dict:
            reminder_type = "None"
        self.reminder_select.setCurrentText(reminder_type)
        self.reminder_options.putData(data["reminder"])

    def reminderSelected(self, reminder_name):
        if self.reminder_options:
            self.reminder_options.deleteLater()
        self.reminder_options = reminders.reminder_option_dict[reminder_name]()
        self.layout.addWidget(self.reminder_options, 2, 1, 1, 2)

    def getInterval(self):
        duration = self.duration_input.value() * 60
        reminder = self.reminder_options.getReminder()
        return (duration, reminder)


class SessionOptions(qw.QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Create palettes used by intervals
        # NOTE : this was part of the colorContainer and addInterval rework.
        # I don't even know if it is worth the tradeoff because now I store a list with two QPalettes instead of making them on the fly.
        # I think it's better to avoid calling colorContainer multiple times for no reason.
        _ODD_PALETTE = QtGui.QPalette()
        _ODD_PALETTE.setColor(
            _ODD_PALETTE.Window, _ODD_PALETTE.color(_ODD_PALETTE.Active, _ODD_PALETTE.AlternateBase)
        )
        _EVEN_PALETTE = QtGui.QPalette()
        _EVEN_PALETTE.setColor(
            _EVEN_PALETTE.Window, _EVEN_PALETTE.color(_EVEN_PALETTE.Active, _EVEN_PALETTE.Base)
        )
        self._PALETTES = [_EVEN_PALETTE, _ODD_PALETTE]
        self.layout = qw.QGridLayout(self)

        # The units for these SpinBoxes is minutes but the timer uses seconds
        self.session_dur_label = qw.QLabel("Session Length:")
        self.session_duration = DurationSpinBox()

        self.interval_options_container = qw.QWidget()
        self.interval_options_grid = qw.QGridLayout(self.interval_options_container)

        focus_label = qw.QLabel("Focus Intervals")
        break_label = qw.QLabel("Break Intervals")

        focus_interval_scroll = qw.QScrollArea()
        focus_interval_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        focus_interval_scroll.setWidgetResizable(True)
        focus_interval_scroll.setSizePolicy(
            qw.QSizePolicy.Minimum, qw.QSizePolicy.Expanding
        )
        focus_interval_frame = qw.QFrame()
        focus_interval_frame.setFrameStyle(qw.QFrame.StyledPanel | qw.QFrame.Sunken)
        self.focus_intervals_container = qw.QVBoxLayout(focus_interval_frame)
        self.focus_intervals_container.setAlignment(QtCore.Qt.AlignTop)
        focus_interval_scroll.setWidget(focus_interval_frame)

        break_interval_scroll = qw.QScrollArea()
        break_interval_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        break_interval_scroll.setWidgetResizable(True)
        break_interval_scroll.setSizePolicy(
            qw.QSizePolicy.Minimum, qw.QSizePolicy.Expanding
        )
        break_interval_frame = qw.QFrame()
        break_interval_frame.setFrameStyle(qw.QFrame.StyledPanel | qw.QFrame.Sunken)
        self.break_intervals_container = qw.QVBoxLayout(break_interval_frame)
        self.break_intervals_container.setAlignment(QtCore.Qt.AlignTop)
        break_interval_scroll.setWidget(break_interval_frame)

        self.add_focus_interval = qw.QPushButton("+ Focus")
        self.add_focus_interval.clicked.connect(self.addFocusInterval)
        self.add_focus_interval.setToolTip("Add focus interval")

        self.add_break_interval = qw.QPushButton("+ Break")
        self.add_break_interval.clicked.connect(self.addBreakInterval)
        self.add_break_interval.setToolTip("Add break interval")

        self.interval_options_grid.addWidget(focus_label, 0, 0, QtCore.Qt.AlignCenter)
        self.interval_options_grid.addWidget(break_label, 0, 1, QtCore.Qt.AlignCenter)

        self.interval_options_grid.addWidget(focus_interval_scroll, 1, 0)
        self.interval_options_grid.addWidget(break_interval_scroll, 1, 1)

        self.interval_options_grid.addWidget(self.add_focus_interval, 2, 0)
        self.interval_options_grid.addWidget(self.add_break_interval, 2, 1)

        self.interval_options_grid.setRowStretch(1, 1)

        self.layout.addWidget(self.session_dur_label, 0, 0, QtCore.Qt.AlignRight)
        self.layout.addWidget(self.session_duration, 0, 1, QtCore.Qt.AlignLeft)
        self.layout.addWidget(self.interval_options_container, 1, 0, 1, 2)

        self.layout.setRowStretch(1, 1)

        self.addFocusInterval()
        self.addBreakInterval()

    def addFocusInterval(self):
        new_widget = IntervalOptions()
        new_widget.destroyed.connect(self.colorIntervals)
        new_widget.setAutoFillBackground(True)
        self.focus_intervals_container.addWidget(new_widget)
        palette_index = (self.focus_intervals_container.count() - 1) % 2 # even or odd?
        new_widget.setPalette(self._PALETTES[palette_index])

    def addBreakInterval(self):
        new_widget = IntervalOptions()
        new_widget.destroyed.connect(self.colorIntervals)
        new_widget.setAutoFillBackground(True)
        self.break_intervals_container.addWidget(new_widget)
        self.colorContainer(self.break_intervals_container)
        palette_index = (self.break_intervals_container.count() - 1) % 2
        new_widget.setPalette(self._PALETTES[palette_index])

    def colorIntervals(self, obj):
            self.colorContainer(self.focus_intervals_container, obj)
            self.colorContainer(self.break_intervals_container, obj)

    def colorContainer(self, container, deleted_widget=None):
        i = 0
        for widget in get_children(container):
            if widget is deleted_widget:
                continue
            widget.setPalette(self._PALETTES[i % 2])
            i += 1


    # NOTE: since this removes intervals from the bottom you do not
    # need to use colorIntervals
    def removeIntervals(self, container, num_removing=1):
        count = container.count()
        for offset in range(min(count - 1, num_removing)):
            w = container.itemAt(count - offset - 1).widget()
            # NOTE : this is to prevent the destroyed signal from emitting and causing colorIntervals to run for no reason
            w.blockSignals(True)
            w.deleteLater()

    def _clearIntervals(self, container):
        for index in range(container.count(), 0, -1):
            w = container.itemAt((index) - 1).widget()
            # NOTE : this is to prevent the destroyed signal from emitting and causing colorIntervals to run for no reason
            w.blockSignals(True)
            w.deleteLater()

    def get_session_queue(self):
        session_duration = self.session_duration.value() * 60

        focus_intervals = [
            focus_widget.getInterval()
            for focus_widget in get_children(self.focus_intervals_container)
        ]

        break_intervals = [
            break_widget.getInterval()
            for break_widget in get_children(self.break_intervals_container)
        ]

        session_queue = SessionQueue(session_duration, focus_intervals, break_intervals)

        return session_queue

    def serializeData(self):
        data = dict()
        data["session_duration"] = self.session_duration.value()
        data["focus_intervals"] = [
            focus_widget.getData()
            for focus_widget in get_children(self.focus_intervals_container)
        ]
        data["break_intervals"] = [
            break_widget.getData()
            for break_widget in get_children(self.break_intervals_container)
        ]

        return data

    def putData(self, data):
        self.session_duration.setValue(data["session_duration"])

        # Reuse as many IntervalOptions widgets as possible
        diff = len(data["focus_intervals"]) - self.focus_intervals_container.count()
        if diff < 0:
            for _ in range(diff, 0):
                self.removeIntervals(self.focus_intervals_container, abs(diff))
        elif diff > 0:
            for _ in range(0, diff):
                self.addFocusInterval()
        for index, focus_interval in enumerate(data["focus_intervals"]):
            self.focus_intervals_container.itemAt(index).widget().putData(
                focus_interval
            )

        diff = len(data["break_intervals"]) - self.break_intervals_container.count()
        if diff < 0:
            for _ in range(abs(diff)):
                self.removeIntervals(self.break_intervals_container, abs(diff))
        elif diff > 0:
            for _ in range(diff):
                self.addBreakInterval()
        for index, break_interval in enumerate(data["break_intervals"]):
            self.break_intervals_container.itemAt(index).widget().putData(
                break_interval
            )


class TimerWidget(qw.QWidget):
    """
    Class that handles all timer events
    Uses a QProgressRing
    """

    done = QtCore.Signal(
        bool
    )  # Bool tells if timer was cancelled (False) or run to completion (True)

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


class ProfileSelect(qw.QWidget):

    # NOTE do I need all of these signals?
    #      should StandUpWindow just connect to the signals of the buttons directly?
    profileChanged = QtCore.Signal(str)
    createProfile = QtCore.Signal(str)
    updateProfile = QtCore.Signal(str)
    deleteProfile = QtCore.Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__()
        # self._filename = filename
        self.initUI()

    def initUI(self):
        self.layout = qw.QHBoxLayout(self)

        self.profile_dropdown = qw.QComboBox()
        self.profile_dropdown.currentTextChanged.connect(self.profileSelected)

        self.PLACEHOLDER_TEXT = "-- Choose Profile --"
        self.profile_dropdown.addItem(self.PLACEHOLDER_TEXT)
        for profile_name in read_profiles().keys():
            self.profile_dropdown.addItem(profile_name)

        update_profile = qw.QPushButton("Save")
        update_profile.clicked.connect(
                self.overwriteProfileClicked
        )

        save_new_profile = qw.QPushButton("Save As...")
        save_new_profile.clicked.connect(self.saveNewProfileClicked)

        delete_current_profile = qw.QPushButton("Delete")
        delete_current_profile.clicked.connect(self.deleteProfileClicked)

        self.layout.addWidget(self.profile_dropdown, 2)
        self.layout.addWidget(update_profile, 1)
        self.layout.addWidget(save_new_profile, 1)
        self.layout.addWidget(delete_current_profile, 1)

        self.profile_dropdown.setCurrentIndex(0)


    def profileSelected(self, name):
        if name == self.PLACEHOLDER_TEXT:
            return
        if name != self.PLACEHOLDER_TEXT:
            self.profile_dropdown.removeItem(self.profile_dropdown.findText(self.PLACEHOLDER_TEXT))
        if name:
            self.profileChanged.emit(name)

    def getUniqueProfileName(self):
        taken_names = [profile_name.lower() for profile_name in read_profiles().keys()]
        taken_names.append(self.PLACEHOLDER_TEXT)
        valid_name = False
        name = None
        first_loop = True
        while not valid_name:
            if first_loop:
                msg = "Profile Name"
            else:
                msg = "Invalid Name! Try a different name"

            name, ok_clicked = qw.QInputDialog.getText(
                self, "New Profile", msg
            )
            if not ok_clicked:
                break
            valid_name = (name and name.strip()) and (name.lower() not in taken_names)
            first_loop = False
        return name if valid_name else None

    def saveNewProfileClicked(self, *args):
        new_name = self.getUniqueProfileName()
        if new_name is None:
            return
        self.createProfile.emit(new_name)
        self.profile_dropdown.addItem(new_name)
        self.profile_dropdown.setCurrentText(new_name)

    def overwriteProfileClicked(self, *args):
        profile_name = self.profile_dropdown.currentText()
        if profile_name and profile_name.strip():
            self.updateProfile.emit(profile_name)

    def deleteProfileClicked(self, *args):
        deleted_name = self.profile_dropdown.currentText()
        if deleted_name == self.PLACEHOLDER_TEXT:
            return
        index_to_remove = self.profile_dropdown.currentIndex()
        self.profile_dropdown.setCurrentIndex(-1)
        self.profile_dropdown.removeItem(index_to_remove)
        self.deleteProfile.emit(deleted_name)


class StandUpWindow(qw.QMainWindow):
    def __init__(self):
        super().__init__()
        self.window_title = "Stand Up"
        self.setWindowTitle(self.window_title)

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
        self.profile_select = ProfileSelect()
        self.profile_select.profileChanged.connect(self.loadProfile)
        self.profile_select.createProfile.connect(self.saveProfile)
        self.profile_select.updateProfile.connect(self.saveProfile)
        self.profile_select.deleteProfile.connect(self.deleteProfile)

        #self.session_instruction = qw.QLabel(
        #    "Session Options", alignment=QtCore.Qt.AlignCenter
        #)

        self.session_options = SessionOptions()

        self.start_session_button = qw.QPushButton("Start Session")
        self.start_session_button.clicked.connect(self.start_session)

        self.start_layout.addWidget(self.profile_select, 0, QtCore.Qt.AlignCenter)
        #self.start_layout.addWidget(self.session_instruction, 0, QtCore.Qt.AlignCenter)
        self.start_layout.addWidget(self.session_options, 1)
        self.start_layout.addWidget(self.start_session_button, 0, QtCore.Qt.AlignTop)

        # Set up timer screen
        self.timer_widget = TimerWidget()
        self.timer_widget.done.connect(self.interval_ended)

        self.timer_layout.addWidget(self.timer_widget)

        # Set up transition screen
        self.transition_message = qw.QLabel()
        self.transition_message.setAlignment(QtCore.Qt.AlignCenter)
        self.transition_message.setWordWrap(True)
        self.transition_message.setStyleSheet("QLabel{font-size: 26pt; text-align: center; margin: auto}")
        self.continue_button = qw.QPushButton("Next Interval")
        self.continue_button.clicked.connect(self.start_next_interval)

        self.transition_layout.addWidget(self.transition_message, 0, QtCore.Qt.AlignCenter)
        self.transition_layout.addWidget(self.continue_button, 0, QtCore.Qt.AlignCenter)

        self.screen_stack.addWidget(self.start_screen)
        self.screen_stack.addWidget(self.timer_screen)
        self.screen_stack.addWidget(self.transition_screen)

        self.setCentralWidget(self.screen_stack)

    def loadProfile(self, profile_name):
        profile = load_profile(profile_name)
        self.session_options.putData(profile)

    def saveProfile(self, profile_name):
        profile = self.session_options.serializeData()
        save_profile(profile_name, profile)

    def deleteProfile(self, profile_name):
        delete_profile(profile_name)

    def start_next_interval(self):
        (
            self.is_break,
            self.interval_duration,
            self.reminder,
        ) = self.session_queue.get_next_interval()

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
                start_next = self.reminder.trigger()
                if start_next:
                    self.start_next_interval()
                else:
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
    standup = StandUpWindow()
    standup.setWindowIcon(QtGui.QIcon(":/icons/window_icon.png"))
    standup.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
