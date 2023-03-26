### DungeonDraw 2.6

A small dungeon editor in Python/Tkinter for tabletop role-playing games like "Dungeons & Dragons".

Draw your walls and doors on a grid.

Other symbols, that can be drawn are:
- "Stairs": Select the corresponding option in the menu, put the cursor on a vertical line and press the mouse button. The symbol is drawn into the box to the right of the line.
- "Locked Doors": They have their own symbol now.
- "Keys": Proceed as described for "stairs".
- "Transparent walls": As symbols for force fields or other obstacles.
- "Points of interest" (drawn as circles of different colors). Proceed as described for "stairs".
- "Single letters": When you select the option in the menu, a dialog-window appears, asking for the letter to be drawn. Then again proceed as described for "stairs".

Requirements on Windows 10 are "Python 3" from [python.org](https://www.python.org/downloads/). And the `Pillow`-library. To get it, open the "Windows PowerShell" and run the command
```
pip install Pillow
```
If you are a Windows 10-user, and aren't by any means able to install a separated Python library or module, there's a simplified version of DungeonDraw in the subfolder `simple`, that only requires the Python interpreter and nothing more. The file is called `dd_simple.pyw`.

In the program, available keys are: `w` Draw wall, `d` Draw door, `r` Remove drawings. The color of the cursor shows, in which mode you're in.

There's also a feature called "FTP Upload". If you have upload access to a FTP server somewhere on the internet, you can edit the beginning of the script and enter the access data for the server there. You'd also have to set the variable `FTP_ENABLED` in the script to `True`. Then, when you select "FTP Upload" in the menu at runtime, the current dungeon image is saved to a file called
```
./saves/dungeon.png
```
which is then automatically uploaded to the given FTP-server. That way, it can be shared quickly with other players.
The feature uses the Python library `ftplib`, which may already be part of the Python distribution.

License: GNU GPL, version 3.

![DungeonDraw](https://github.com/hlubenow/DungeonDraw/blob/main/dungeondraw.png)
