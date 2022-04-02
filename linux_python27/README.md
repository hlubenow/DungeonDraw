### DungeonDraw 1.2

This is the older release. If you use Windows 10, use version 1.3 in the main directory above instead.

A simple dungeon editor in Python/Tkinter for role-playing games like for example "Dungeons & Dragons".

Just draw your walls and doors on a grid (nothing more).

To run the script on Windows, the [interpreter of Python 2.7](https://www.python.org/downloads/release/python-2718/) has to be installed. The file "[Windows x86-64 MSI installer](https://www.python.org/ftp/python/2.7.18/python-2.7.18.amd64.msi)" is probably, what is required.
If clicking the `.pyw`-file doesn't start the interpreter after installation, try running `startdd.bat`.

For support of the `Save Image` functionality, the `PIL-image-library` (today called [Pillow](https://pypi.org/project/Pillow/)) would be needed. If it's not installed, the script will still work, but `Save Image` will not be available. But of course, you still could use an external program for making and saving screenshots.

In the program, available keys are: `w` Draw wall, `d` Draw door, `r` Remove drawings. The color of the cursor shows, in which mode you're in.

License: GNU GPL, version 3.

![DungeonDraw](https://github.com/hlubenow/DungeonDraw/blob/main/dungeondraw.png)
