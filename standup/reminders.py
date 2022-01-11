"""
    Module containing classes of different reminders for
    standup.py

    There are two types of classes: ReminderOptions and Reminders
    For every reminder the user can select, there is one ReminderOption type
    and one corresponding Reminder

    ReminderOptions are widgets that allow the user to set options specific
    to the Reminder

    ReminderOption subclasses should set the name attribute to a short descriptive string
    appropriate for a QComboBox - this is what the user sees and picks from

    ReminderOptions should implement two methods:
        1. getReminder()      - returns a new Reminder object with the input
                                 given.
        1. putData()          - sets the reminder widgets to values specified
                                 from a user profile.
                                 NOTE: profiles are not implemented yet.
        1. getData()          - returns a tuple with reminder name and any parameters
                                 for loading this as a profile. Should be compatible with
                                 loadProfile()

    Reminders must implement one method:
        1. handle()           - This method triggers the actual reminder
                                meant to get the user's attention.
"""

import webbrowser
import PySide2.QtWidgets as qw
from PySide2.QtCore import Qt

### BASE CLASSES ###


class ReminderOptions(qw.QWidget):
    name = "Base Class"

    def __init__(self):
        super().__init__()

    def initUI(self):
        raise NotImplementedError

    def getData(self):
        raise NotImplementedError

    def putData(self):
        raise NotImplementedError

    def getReminder(self):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}: {dir(self)}"


class NoReminderOptions(ReminderOptions):
    """
    This is for a reminder that does nothing and starts the next interval immediately
    getReminder returns None so the StandUp app can handle it by truthiness check.
    """

    name = "None"

    def __init__(self):
        super().__init__()
        # self.setText("No reminder - the next interval will start right away.")

    def getData(self):
        return {"name": self.name}

    def putData(self, *args, **kwargs):
        pass

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

    def getData(self):
        return {"name": self.name, "message": self.message_input.text()}


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

    def getData(self):
        data = dict()
        data["name"] = self.name
        data["url"] = self.url_input.text()
        data["policy"] = self.policy_group.checkedId()
        return data

    def putData(self, data):
        self.url_input.setText(data["url"])
        self.policy_group.button(data["policy"]).setChecked(True)

    def getReminder(self):
        url = self.url_input.text()
        policy = self.policy_group.checkedId()
        return BrowserReminder(url, policy)


class PopupWindowReminderOptions(MessageReminderOptions, ReminderOptions):
    name = "Popup Window"

    def __init__(self):
        super().__init__()

    def putData(self, data):
        self.message_input.setText(data["message"])

    def getReminder(self):
        return PopupWindowReminder(self.message_input.text())


### NOTE: Reminders that raise the window do not seem to work on Linux so I am just removing them for now.
### Popup reminders should basically get the job done.
#class RaiseWindowReminderOptions(MessageReminderOptions, ReminderOptions):
#    name = "Raise Window"
#
#    def __init__(self):
#        super().__init__()
#
#    def getData(self):
#        return {"name": self.name, "message": self.message_input.text()}
#
#    def putData(self, data):
#        self.message_input.setText(data["message"])
#
#    def getReminder(self):
#        message = self.message_input.text()
#        return RaiseWindowReminder(message, self.window())
#
#
#class MaximizeWindowReminderOptions(MessageReminderOptions, ReminderOptions):
#    name = "Maximize Window"
#
#    def __init__(self):
#        super().__init__()
#
#    def getData(self):
#        return {"name": self.name, "message": self.message_input.text()}
#
#    def putData(self, data):
#        self.message_input.setText(data["message"])
#
#    def getReminder(self):
#        message = self.message_input.text()
#        return MaximizeWindowReminder(message, self.window())


class Reminder:
    def trigger(self):
        raise NotImplementedError

    def __repr__(self):
        return f"{self.__class__.__name__}()"


class BrowserReminder(Reminder):
    message = "Opening URL..."

    def __init__(self, url, policy):
        self.url = url
        self.policy = policy

    def trigger(self):
        webbrowser.open(self.url, new=self.policy)
        return False


#class RaiseWindowReminder(Reminder):
#    def __init__(self, message, window):
#        super().__init__()
#        self.message = message
#        self.window = window
#
#    def trigger(self):
#        # NOTE: There is a chance this doesn't work on Windows or Mac.
#        # Or maybe even window managers other than X11
#        #self.window.setWindowState(
#        #    self.window.windowState() & ~Qt.WindowMinimized | Qt.WindowActive
#        #)
#        #self.window.activateWindow()
#        self.window.showNormal()
#        return False
#
#
#class MaximizeWindowReminder(Reminder):
#    def __init__(self, message, window):
#        super().__init__()
#        self.message = message
#        self.window = window
#
#    def trigger(self):
#        #self.window.setWindowState(Qt.WindowMaximized)
#        #self.window.activateWindow()
#        self.window.showMaximized()
#        return False

class PopupWindowReminder(Reminder):
    def __init__(self, message):
        super().__init__()
        self.message = message

    def trigger(self):
        popup = qw.QMessageBox()
        popup.addButton("Close", qw.QMessageBox.RejectRole)
        continue_button = popup.addButton("Next Interval", qw.QMessageBox.AcceptRole)
        popup.setWindowTitle("Stand Up Reminder")
        popup.setText(self.message)
        response = popup.exec()
        return popup.clickedButton() == continue_button
        


reminder_option_dict = {
    subclass.name: subclass for subclass in ReminderOptions.__subclasses__()
}
