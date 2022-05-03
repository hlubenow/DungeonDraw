### DungeonDraw 1.5

A simple dungeon editor in Python/Tkinter for role-playing games like for example "Dungeons & Dragons".

Just draw your walls and doors on a grid.

Version 1.5: Also draw symbols for stairs and for "points of interest" in a dungeon: Select the corresponding option in the menu, put the cursor on a vertical line and press the mouse button. The symbol is drawn into the box to the right of the line.

As of 03-2022, I bought a new PC, so I can make a version 1.3, that's better suitable for Windows 10. If you use that operating-system, you can now just go to [python.org](https://www.python.org/downloads/), and download the latest release of Python 3. In the installation-process, make sure, that `Add python-directory to the $PATH-variable` (or something like that) is selected.
Then, to install the `Pillow`-library (for drawing the dungeon as a png-image), open the "Windows PowerShell" and type in and run the command
```
pip install Pillow
```
After that it should be possible to run the script by double-clicking on `dungeondraw.pyw`.

I'm putting the old release into a directory `linux_python27`.

In the program, available keys are: `w` Draw wall, `d` Draw door, `r` Remove drawings. The color of the cursor shows, in which mode you're in.

License: GNU GPL, version 3.

![DungeonDraw](https://github.com/hlubenow/DungeonDraw/blob/main/dungeondraw.png)
