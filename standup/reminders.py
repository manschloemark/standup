"""
    Module containing classes for different reminders for
    standup.py

    There are two types of classes: ReminderOptions and Reminders
    For every reminder the user can select, there is one ReminderOption type
    and one corresponding Reminder

    ReminderOptions are widgets that allow the user to set options specific
    to the Reminder

    ReminderOptions constructors all take one argument - a QLabel
        - some reminder types will clear the label text, some will allow the
          user to set a custom message

    ReminderOption subclasses should set the name attribute to something
    appropriate for a QComboBox - this is what the user sees and picks from

    ReminderOptions should implement three methods:
        1. set_reminder_text() - sets the QLabel text
        1. load_profile()      - sets the reminder widgets to values specified
                                 in a user profile.
                                 NOTE: profiles are not implemented yet.
        1. get_reminder()      - returns a new Reminder object with the options
                                 given.

    Reminders are classes that must have a handle() method.
        - This method triggers the actual reminder meant to get the user's
          attention.
"""

import webbrowser
import PySide6.QtWidgets as qw
from PySide6.QtCore import Qt

### BASE CLASSES ###

class ReminderOptions(qw.QWidget):
    name = "Abstract Base Class"

    def __init__(self):
        super().__init__()

    def initUI(self):
        raise NotImplementedError

    def loadProfile(self):
        raise NotImplementedError

    def getReminder(self):
        raise NotImplementedError

    def __repr__(self):
        return f'{self.__class__.__name__}: {dir(self)}'

class NoReminderOptions(qw.QLabel, ReminderOptions):
    """
        This is for a reminder that does nothing and starts the next interval immediately
        getReminder returns None so the StandUp app can handle it by truthiness check.
    """
    name = "None"
    def __init__(self):
        super().__init__()
        self.setText("The next interval will start right away.")

    def getReminder(self):
        return None

class MessageReminderOptions(qw.QWidget):
    """ Since multiple ReminderOptions subclasses just accept simple messages for their reminders I am making this it's own class that those other reminders will inherit. """
    name = "Abstract Base Class"

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = qw.QFormLayout(self)

        message_label = qw.QLabel("Message:")
        self.message_input = qw.QLineEdit()

        self.layout.addRow(message_label, self.message_input)


class BrowserReminderOptions(ReminderOptions):
    name = "Open URL"
    description = "Opens a URL in your default browser."

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.layout = qw.QFormLayout(self)

        url_label = qw.QLabel("URL:")
        self.url_input = qw.QLineEdit()

        tab_policies = qw.QGroupBox("Open URL In...")
        self.policy_group = qw.QButtonGroup()
        tab_policies.setFlat(True)
        vbox = qw.QVBoxLayout(tab_policies)

        same_window = qw.QRadioButton("Existing Window")
        new_window = qw.QRadioButton("New Window")
        new_tab = qw.QRadioButton("New Tab")

        self.policy_group.addButton(same_window, id=0)
        self.policy_group.addButton(new_window, id=1)
        self.policy_group.addButton(new_tab, id=2)

        new_tab.setChecked(True)
        vbox.addWidget(new_tab)
        vbox.addWidget(new_window)
        vbox.addWidget(same_window)

        self.layout.addRow(url_label, self.url_input)
        self.layout.addRow(tab_policies)

    def getReminder(self):
        url = self.url_input.text()
        policy = self.policy_group.checkedId()
        return BrowserReminder(url, policy)



class RaiseWindowReminderOptions(MessageReminderOptions, ReminderOptions):
    name = "Raise StandUp Window"

    def __init__(self):
        super().__init__()

    def getReminder(self):
        message = self.message_input.text()
        return RaiseWindowReminder(message, self.window())


class MaximizeWindowReminderOptions(MessageReminderOptions, ReminderOptions):
    name = "Maximize Standup Window"

    def __init__(self):
        super().__init__()

    def getReminder(self):
        message = self.message_input.text()
        return MaximizeWindowReminder(message, self.window())


class Reminder:
    def handle(self):
        raise NotImplementedError

    def __repr__(self):
        return f'{self.__class__.__name__}()'


class BrowserReminder(Reminder):
    message = "Opening URL..."
    def __init__(self, url, policy):
        self.url = url
        self.policy = policy

    def handle(self):
        webbrowser.open(self.url, new=self.policy)


class RaiseWindowReminder(Reminder):
    def __init__(self, message, window):
        super().__init__()
        self.message = message
        self.window = window

    def handle(self):
        # NOTE: There is a chance this doesn't work on Windows or Mac.
        # Or maybe even window managers other than X11
        self.window.setWindowState(self.window.windowState() &
                                   ~Qt.WindowMinimized | Qt.WindowActive)
        self.window.activateWindow()

class MaximizeWindowReminder(Reminder):
    def __init__(self, message, window ):
        super().__init__()
        self.message = message
        self.window = window

    def handle(self):
        self.window.setWindowState(Qt.WindowMaximized)
        self.window.activateWindow()

reminder_option_dict = {subclass.name: subclass for subclass in ReminderOptions.__subclasses__()}


