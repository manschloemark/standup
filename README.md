# Stand Up
Remind your future self to stand up every once in a while.

Stand Up is a desktop application that helps you manage work sessions with focus and break intervals.  
Set custom reminders that tell you when to take a break.  
These reminders are meant to draw your attention away from your work and remind you to take breaks.
It might sound odd that you're trying to break your focus but taking breaks can be more productive and healthy in the long run.

It's important to take breaks regularly and:
 1. stretch your body
 1. rest your eyes
 1. clear your head

Despite knowing all this, I struggle to actually implement it in my routine.  
Sometimes it's hard to pull yourself away from an interesting or difficult problem.  
I've tried using regular alarms but I tend to filter them out after a while. I just shut off the alarm without breaking my focus.  

That's why I made Stand Up.

## How to run it
First, make sure you have at least Python 3.6 by running:  
` python3 --version `  
Second, make sure you have the PyQt5 module for Python.
Check if PyQt5 is in the output of this command:  
`python3 -m pip list`  
If you do not see PyQt5 in this list, you need to install it with:
 `python3 -m pip install PyQt5`  

If you have a Python environment that can run it, clone this repo with:  
`git clone https://github.com/manschloemark/standup.git`  
Open the directory and run standup.py:  
`python3 standup.py`  

## How it works

### Set the timers
- Session Duration : how long the program will run intervals
  - Set this to 0 to run intervals until you stop it
- Work Intervals   : how long you work before taking a break
  - After a work interval ends the program will trigger your selected _reminder_
- Break Intervals  : how long your breaks are
  - After a break interval ends the program will automatically start the next work interval
  - Set this to 0 if you want to manually start the next work interval

### Set the reminder
- Reminder Type    : choose what happens at the end of a work interval
  - Open a URL: enter any URL you'd like and the program will open it in your default browser
  - Raise StandUp window: Raise the app's window to the top of your desktop and gives it focus. This will not change the size of the window.
  - Maximize StandUp window: the same as 'Raise StandUp window' but instead makes sure the window is maximized.

### That's it!
Stand Up makes it easy to remember by providing unconventional reminder mechanisms.  

## TODO
- Fix RaiseWindow and MaximizeWindow reminders
  - these reminders are supposed to display a message during the reminder
  - when the user sets a break timer this message is not displayed
- Add 'profiles' so users can save settings for quick reuse and name them
- Allow users to queue intervals for more dynamic sessions
  - e.g. a pomodoro timer
