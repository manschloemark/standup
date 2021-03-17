# Stand Up
Remind your future self to stand up every once in a while.

Stand Up is a tool that helps you focus and stay healthy over long periods of work.  
With Stand Up you can set timers for periods of focus and rest and customize reminders that tell you when to switch.

It's important to take breaks regularly and:
 1. stretch your body
 1. rest your eyes
 1. clear your head

## How to run it
First, make sure you have at least Python 3.6 by running:  
` python3 --version `  
Second, make sure you have the PySide6 module for Python.
Check if PySide6 is in the output of this command:  
`python3 -m pip list`  
If you do not see PySide6 in this list, you need to install it with:
 `python3 -m pip install PySide6`  

Once you have a Python environment that can run it, clone this repo with:  
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
- Interval Queues  :
  - Break up the monotony with interval queues. Instead of alternating between one focus interval and one break interval you can plan multiple focus and break intervals, each with different reminders, to keep things fresh.
  - This feature makes it possible to implement the Pomodoro Technique, for example.

### Customize reminders
- Reminder Type    : choose what happens at the end of a work interval
  - Open a URL: enter any URL you'd like and the program will open it in your default browser
  - Raise StandUp window: Raise the app's window to the top of your desktop and gives it focus. This will not change the size of the window.
  - Maximize StandUp window: the same as 'Raise StandUp window' but instead makes sure the window is maximized.
- You can set different reminders for the end of focus and break intervals

### That's it!

## TODO
- Make it easy to install and run
- Add 'profiles' so users can save settings for quick reuse and name them
