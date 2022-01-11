# Stand Up
_Remind your future self to take a break every once in a while._

Stand Up is an app for planning work sessions with periods of focus and breaks.  


## How it works
1. Set Timers
2. Customize Reminders
3. Hit Start Session

### Set Timers
- Session Length : total time you plan to work at your computer
  - Setting this to 0 will run intervals until you stop it
- Focus Intervals  : how long you work before taking a break
- Break Intervals  : how long your breaks are
- Interval Queues  :
  - You don't need to match every focus interval to a break interval. You can have different numbers of each.
  - This feature makes it possible to implement the Pomodoro Technique, for example.

### Customize Reminders
- Every focus and break interval has a reminder associated with it
- Reminder Types    : choose what happens at the end of a work interval
  - No Reminder: nothing will happen after the interval, the program will immediately start the next interval.
  - Open a URL: enter any URL you'd like and the program will open it in your default browser
  - Popup Window: Stand Up will raise an annoying popup window to grab your attention. You can include a message for yourself in the popup.

### Save Session Profiles
- You can save your session settings in profiles which can be quickly loaded any time.

![Session Setup](./docs/ex_setup.jpg?raw=true) ![Countdown Timer](./docs/ex_timer.jpg?raw=true)

## How to run it

### Command Line
First, make sure you have at least Python 3.6 by running:  
` python3 --version `  
Second, make sure you have the PySide2 module for Python.
Check if PySide2 is in the output of this command:  
`python3 -m pip list`  
If you do not see PySide2 in this list, you need to install it with:
 `python3 -m pip install PySide2`  

Once you have a Python environment that can run it, clone this repo with:  
`git clone https://github.com/manschloemark/standup.git`  
Open the directory and run standup.py:  
`python3 standup.py`  
