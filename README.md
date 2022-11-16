### DungeonDraw 2.2

A small dungeon editor in Python/Tkinter for tabletop role-playing games like "Dungeons & Dragons".

Draw your walls and doors on a grid.

Also draw symbols for stairs and for "points of interest" (circles of different colors) in a dungeon: Select the corresponding option in the menu, put the cursor on a vertical line and press the mouse button. The symbol is drawn into the box to the right of the line.
Also "transparent walls" as symbols for force fields or other obstacles can now be drawn.
And single letters: When you select the option in the menu, a dialog-window appears, asking which letter to draw.

Requirements on Windows 10 are "Python 3" from [python.org](https://www.python.org/downloads/). And the `Pillow`-library. To get it, open the "Windows PowerShell" and run the command
```
pip install Pillow
```
In the program, available keys are: `w` Draw wall, `d` Draw door, `r` Remove drawings. The color of the cursor shows, in which mode you're in.

There's also a feature called "FTP Upload". If you have upload access to a FTP server somewhere on the internet, you can edit the beginning of the script and enter the access data for the server there. You'd also have to set the variable `FTP_ENABLED` in the script to `True`. Then, when you select "FTP Upload" in the menu at runtime, the current dungeon image is saved to a file called
```
./saves/dungeon.png
```
which is then automatically uploaded to the given FTP-server. That way, it can be shared quickly with other players.
The feature uses the Python library `ftplib`, which may already be part of the Python distribution.

- Version 2.1: Prevented the cursor from getting redrawn more often than necessary.
- To be able to draw letters, the file format for saving maps has changed to lines of texts again.
- Drawing of letters with PIL needs a font-file. If the file's not found, letters aren't drawn (and there's a warning about it).

License: GNU GPL, version 3.

![DungeonDraw](https://github.com/hlubenow/DungeonDraw/blob/main/dungeondraw.png)
