# Stand Up
StandUp is a program that reminds you to take breaks during long work sessions at your desk.

> Being sedentary for long periods of time can cause serious health issues.
> <br>It's important to take regular breaks to:
> 1. Stand up, walk around, stretch
> 1. Give your eyes a break from the screen
> 1. Give your mind a break from your work
>
> <br>But when you're in the zone and focusing on work it is easy to forget about that!
> <br>That's why I made this program, to make it hard to forget.

## Features

### Customize Sessions
- Session Duration : how long the program will run
  - If you set this to 0 the program will run until you stop it
- Work Intervals   : how long you work before taking a break
  - After a work interval ends the program will trigger the 'reminder' you set
- Break Intervals  : how long your breaks are
  - After a break interval ends the program will start the next work interval
  - If you set this to 0 the program will wait for your input to start the next work interval
- Reminder Type    : choose how you'd like the program to tell you when to take a break
  - Open a URL: enter any URL you'd like and the program will open a new tab to that page every interval.
  - Raise StandUp window: after every interval the StandUp window will be raised to the front of your desktop and will take focus. Preserves size of window.
  - Maximize StandUp window: the same as 'Raise StandUp window' but instead makes sure the window is maximized.

Written in Python 3 with PyQt5.
Uses the webbrowser standard library module to open URL's.

## Notes

- Sometimes the work and break intervals do not evenly divide the session duration
  - In this case the last interval length will be the time left in the session
    - ex: 1 hour session, 30 minute work intervals, 10 minute break intervals
    - after one work interval and one break interval, 40 minutes will have gone by
    - the next work interval is supposed to be 30 minutes, there is only 20 minutes left in the session, the work interval will be 20 minutes

## TODO

- Implement Qt QSettings so session configurations persist after closing the program
- Implement user profiles so users can save multiple session configurations and name them
- Allow users to enter multiple values for the work and break intervals
  - This would allow you to create a Pomodoro timer (work 25, break 5, work 25, break 5, work 25, break 5, work 25, break 20, repeat)
