"""
    Module containing classes for different reminders in
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
    appropriate for a QComboBox

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

from PyQt5.QtWidgets import QWidget, QFormLayout, QLabel, QLineEdit, QGroupBox, QButtonGroup, QHBoxLayout, QRadioButton
from PyQt5.QtCore import Qt

### REMINDER OPTION WIDGETS

class ReminderOptions(QWidget):

    name = "If you see this, something went wrong"

    def __init__(self, reminder_label):
        super().__init__()
        self.message_widget = reminder_label

    def load_profile(self):
        raise NotImplementedError

    def set_reminder_text(self):
        raise NotImplementedError

    def get_reminder(self):
        raise NotImplementedError

class BrowserReminderOptions(ReminderOptions):

    name = "Open URL"

    def __init__(self, *args):
        super().__init__(*args)

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

    def set_reminder_text(self):
        self.message_widget.setText("")

    def get_reminder(self):
        self.set_reminder_text()
        return BrowserReminder(self.url_entry.text(), self.policy_group.checkedId())

class RaiseWindowReminderOptions(ReminderOptions):

    name = "Raise StandUp Window"

    def __init__(self, *args):
        super().__init__(*args)
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

class MaximizeWindowReminderOptions(RaiseWindowReminderOptions, ReminderOptions):

    name = "Maximize StandUp Window"

    def __init__(self, *args):
        super().__init__(*args)

    def get_reminder(self):
        super().set_reminder_text()
        return MaximizeWindowReminder(self)

### REMINDERS

class Reminder:
    def __init__(self):
        super().__init__()

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
        self.window = parent.window()

    def handle(self):
        # There is a chance this doesn't work on Windows or Mac. Or maybe even other Window Managers on Linux.
        self.window.setWindowState(self.window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        self.window.activateWindow()

class MaximizeWindowReminder(RaiseWindowReminder):

    def __init__(self, *args):
        super().__init__(*args)

    def handle(self):
        self.window.setWindowState(Qt.WindowMaximized)
        self.window.activateWindow()

def get_reminder_options():
    return ReminderOptions.__subclasses__()



# NOTE this tuple is meant to be used by standup.py to programatically
#      load all reminder types into the UI
#      Every time you create a new reminder you should add it to this
#      tuple, you don't need to change any code in standup.py
# TODO learn more about reflection, I think that is something people
#      do in situations like these
