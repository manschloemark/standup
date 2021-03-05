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
