#!/usr/bin/python
# coding: utf-8

"""
    DungeonDraw 2.0 - A dungeon editor for role-playing games.
    Copyright (C) 2022 Hauke Lubenow

    This program is free software: you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

# Set this to "private", if you want FTP-upload:
VERSION = "public"

import tkinter as tk
import tkinter.messagebox as tkmessagebox
import tkinter.filedialog as tkfiledialog

from PIL import Image, ImageDraw

if VERSION == "private":
    import ftplib

import os

# ------- Settings: -------

"""
FTP-access-data. Example:

FTPSERVER    = "your-ftp-server.com"
FTPDIRECTORY = "your-ftp-server.com"
FTPLOGIN     = ("username", "password")

Now edit accordingly right here below, if you want FTP-upload:
"""

FTPSERVER    = ""
FTPDIRECTORY = ""
FTPLOGIN     = ()

FONT = ("Calibri", 10)

DRAW_MEASURING_TAPE_WITH_PIL = False

if VERSION == "private":
    # The private version automatically saves the image to "./saves/dungeon.py".
    FILEDIR   = os.path.join(os.getcwd(), "saves")
    IMAGEFILE = os.path.join(FILEDIR, "dungeon.png")
else:
    # The public version asks the user for the name of the imagefile:
    FILEDIR   = os.getcwd()
    IMAGEFILE = ""

# ------- End of Settings -------

COLORS = {"tk"  : {"background"      : "white",
                   "empty"           : "lightgrey",
                   "measuring"       : "grey",
                   "wall"            : "black",
                   "transparentwall" : "black",
                   "door"            : "#c000c0",
                   "stairs"          : "black",
                   "circle_red"      : "#c00000",
                   "circle_green"    : "#00c000",
                   "circle_blue"     : "#0000c0"},

          "pil" : {"background"      : (255, 255, 255),
                   "empty"           : (192, 192, 192),
                   "measuring"       : (80, 80, 80),
                   "wall"            : (0, 0, 0),
                   "transparentwall" : (0, 0, 0),
                   "door"            : (192, 0, 192),
                   "stairs"          : (0, 0, 0),
                   "circle_red"      : (192, 0, 0),
                   "circle_green"    : (0, 192, 0),
                   "circle_blue"     : (0, 0, 192)}}

DRAWENTRIES = ("wall",
               "door",
               "stairs",
               "transparentwall",
               "separator_1",
               "circle_red",
               "circle_green",
               "circle_blue",
               "separator_2",
               "remove")

class Board:

    def __init__(self):
        self.border    = 20
        self.lines_xnr = 50
        self.lines_ynr = 25
        self.linesize  = 22
        self.buildLines()

    def buildLines(self):
        self.lines = []
        nr         = 0
        for y in range(self.lines_ynr):
            for x in range(self.lines_xnr):
                self.lines.append(Line(nr, x, y, "horizontal", self))
                nr += 1
                self.lines.append(Line(nr, x, y, "vertical", self))
                nr += 1
            # Last column of grid:
            l = Line(nr, self.lines_xnr, y, "vertical", self)
            l.setLast()
            self.lines.append(l)
            nr += 1

        # Last row of grid:
        for x in range(self.lines_xnr):
            self.lines.append(Line(nr, x, self.lines_ynr, "horizontal", self))
            nr += 1

    def getClosestLine(self, mouse_x, mouse_y):
        xmin = 10000
        verticallines = []
        for line in self.lines:
            if line.orientation == "vertical":
                if mouse_y >= line.p1[1] and mouse_y <= line.p2[1]:
                    verticallines.append(line)
        for line in verticallines:
            dx = mouse_x - line.p1[0]
            if dx < 0:
                dx = dx * (-1)
            if dx < xmin:
                xmin = dx
                xminline = line

        ymin = 10000
        horizontallines = []
        for line in self.lines:
            if line.orientation == "horizontal":
                if mouse_x >= line.p1[0] and mouse_x <= line.p2[0]:
                    horizontallines.append(line)

        for line in horizontallines:
            dy = mouse_y - line.p1[1]
            if dy < 0:
                dy = dy * (-1)
            if dy < ymin:
                ymin = dy
                yminline = line
        if ymin <= xmin:
            # yminline is the horizontal line.
            return yminline
        else:
            return xminline

    def clear(self):
        for i in self.lines:
            i.setState("empty")
            i.clearAttachment()

    def collectData(self):
        # The len of states must be < 10, because 10-20 is already reserved 
        # for combinations with the first attachment (which is "stairs"):
        states = ("empty", "wall", "door", "transparentwall")
        # +10 for stairs (code below):
        additions  = {"red" : 20, "green" : 30, "blue" : 40}
        data = []
        for i in self.lines:
            n = states.index(i.state)
            if i.attachment:
                if i.attachment.name == "stairs":
                    n += 10
                for u in additions.keys():
                    if i.attachment.name == "circle_" + u:
                        n += additions[u]
            data.append(n)
        return data

    def pokeInData(self, data, canvas):
        states = ("empty", "wall", "door", "transparentwall")
        colors = ("red", "green", "blue")
        for i in range(len(self.lines)):
            n = data[i]
            if n >= 10 and n < 20:
                self.lines[i].addAttachment("stairs", canvas)
                n -= 10
            for u in range(len(colors)):
                from_ = 20 + 10 * u
                to_   = from_ + 10
                if n >= from_ and n < to_:
                    self.lines[i].addAttachment("circle_" + colors[u], canvas)
                    n -= from_
            self.lines[i].setState(states[n])

class Line:

    def __init__(self, nr, xnr, ynr, orientation, board):
        self.nr = nr
        self.board = board
        self.orientation = orientation 
        self.state = "empty"
        self.isgrey = False
        self.canvasobjects = []
        self.attachment = None
        self.lastcolumn = False
        border = self.board.border
        width  = self.board.linesize
        height = self.board.linesize
        self.p1 = (border + xnr * width, border + ynr * height)
        if self.orientation == "horizontal":
            self.p2 = (self.p1[0] + width, self.p1[1])
            # For transparent walls. Format: ((p1, p2), (p1, p2)):
            self.lparts = ((self.p1, (self.p1[0] + width // 4, self.p1[1])),
                           ((self.p1[0] + width // 2, self.p1[1]), (self.p1[0] + width * 3 // 4, self.p1[1])))
        if self.orientation == "vertical":
            self.p2 = (self.p1[0], self.p1[1] + height)
            # For transparent walls. Format: ((p1, p2), (p1, p2)):
            self.lparts = ((self.p1, (self.p1[0], self.p1[1] + height // 4)),
                           ((self.p1[0], self.p1[1] + height // 2), (self.p1[0], self.p1[1] + height * 3 // 4)))

    def addAttachment(self, name, canvas):
        if self.orientation == "horizontal":
            return
        if self.lastcolumn:
            return
        if self.attachment:
            if self.attachment.name == name:
                return
            self.clearAttachment()
        if name == "stairs":
            self.attachment = Stairs(name, canvas, self)
        if name.startswith("circle"):
            self.attachment = Circle(name, canvas, self)

    def drawAttachment(self, mode, pildraw):
        if not self.attachment:
            return
        self.attachment.draw(mode, pildraw)

    def clearAttachment(self):
        if not self.attachment:
            return
        self.attachment.remove()
        self.attachment = None

    def addCanvasObject(self, id):
        self.canvasobjects.append(id)

    def setGrey(self):
        self.isgrey = True

    def setLast(self):
        self.lastcolumn = True

    def setState(self, state):
        self.state = state


class Attachment:

    def __init__(self, name, canvas, line):
        self.name = name
        self.canvas = canvas
        self.line = line
        self.canvasobjects = []

    def remove(self):
        for i in self.canvasobjects:
            self.canvas.delete(i)

class Stairs(Attachment):

    def __init__(self, name, canvas, line):
        Attachment.__init__(self, name, canvas, line)

    def draw(self, mode, pildraw):
        for i in range(0, 501, 250):
            stairs_p1 = (self.line.p1[0] + self.line.board.linesize // 4,
                         self.line.p1[1] + self.line.board.linesize // 4 + i / 1000. * self.line.board.linesize)
            stairs_p2 = (self.line.p1[0] + self.line.board.linesize * 3 // 4,
                         stairs_p1[1])
            self.createLine(stairs_p1, stairs_p2, mode, pildraw)

    def createLine(self, stairs_p1, stairs_p2, mode, pildraw):
        if mode == "tk":
            self.canvasobjects.append(self.canvas.create_line(stairs_p1, stairs_p2, width = 2, fill = COLORS["tk"]["stairs"]))
        else:
            pildraw.line(xy = (stairs_p1[0], stairs_p1[1], stairs_p2[0], stairs_p2[1]), width = 2, fill = COLORS["pil"]["stairs"])


class Circle(Attachment):

    def __init__(self, name, canvas, line):
        Attachment.__init__(self, name, canvas, line)

    def draw(self, mode, pildraw):
        circle_p1 = (self.line.p1[0] + self.line.board.linesize // 4,
                  self.line.p1[1] + self.line.board.linesize // 4)
        circle_p2 = (self.line.p1[0] + self.line.board.linesize * 3 // 4,
                  self.line.p1[1] + self.line.board.linesize * 3 // 4)
 
        if mode == "tk":
            self.canvasobjects.append(self.canvas.create_oval(circle_p1, circle_p2, width = 3, fill = COLORS["tk"][self.name], outline = COLORS["tk"][self.name]))
        else:
            pildraw.ellipse((circle_p1[0], circle_p1[1], circle_p2[0], circle_p2[1]), fill = COLORS["pil"][self.name], outline = COLORS["pil"][self.name])


class Cursor:

    def __init__(self, wallwidth, canvas):
        self.wallwidth    = wallwidth
        self.canvas       = canvas
        self.canvasobject = None
        self.colors       = {"wall"            : "blue",
                             "door"            : COLORS["tk"]["door"],
                             "stairs"          : "blue",
                             "transparentwall" : "blue",
                             "remove"          : "cyan"}
        c = ("red", "green", "blue")
        for i in c:
            self.colors["circle_" + i] = COLORS["tk"]["circle_" + i]

    def show(self, currentline, drawmode):
        self.color = "blue"
        if drawmode == "remove":
            self.color = "cyan"
        self.canvasobject = self.canvas.create_line(currentline.p1,
                                                    currentline.p2,
                                                    width = self.wallwidth,
                                                    fill = self.colors[drawmode])
    def setOff(self):
        self.canvas.delete(self.canvasobject)
        self.canvasobject = None


class Main:

    def __init__(self):

        self.mw = tk.Tk()
        self.mw.option_add("*font", FONT)
        self.mw.geometry("1200x650+20+0")
        self.mw.title("DungeonDraw")
        self.mw.bind(sequence = "<Control-q>", func = lambda e: self.mw.destroy())
        self.mw.bind(sequence = "<w>", func = lambda e: self.setDrawMode("wall"))
        self.mw.bind(sequence = "<d>", func = lambda e: self.setDrawMode("door"))
        self.mw.bind(sequence = "<r>", func = lambda e: self.setDrawMode("remove"))
        self.board = Board()
        self.canvassize            = (2 * self.board.border + self.board.lines_xnr * self.board.linesize,
                                      2 * self.board.border + self.board.lines_ynr * self.board.linesize)
        self.setMeasuringTapeCoordinates()
        self.wallwidth             = 4
        self.transparentwallwidth  = 3
        self.doorovalsize          = 4
        self.drawmode              = "wall"
        self.currentline           = None
        self.previousmouseposition = (0, 0)
        self.button_down           = False
        self.menubar = tk.Frame(self.mw, relief = tk.RIDGE, bd = 5);
        self.mb_file = tk.Menubutton(self.menubar, text = "File")
        self.mb_draw = tk.Menubutton(self.menubar, text = "Draw")
        self.mb_info = tk.Button(self.menubar,
                                 text = "Info",
                                 relief = tk.FLAT,
                                 command = self.showInfo)
        self.menu_file = tk.Menu(self.mb_file, tearoff = tk.FALSE)
        self.menu_file.insert_command(0,
                                      label = "New",
                                      command = self.new)
        self.menu_file.insert_command(1,
                                      label = "Open",
                                      command = self.load)
        self.menu_file.insert_command(2,
                                      label = "Save as Data",
                                      command = self.saveAs)
        self.menu_file.insert_command(3,
                                      label = "Save Image",
                                      command = self.saveImage)
        self.menu_file.insert_command(4, label = "FTP Upload", command = self.uploadToFTP)
        self.menu_file.insert_separator(5)
        self.menu_file.insert_command(6, label = "Exit", command = self.mw.destroy)
        if VERSION != "private":
            self.menu_file.entryconfig(4, state = tk.DISABLED)
        self.mb_file.config(menu = self.menu_file)

        self.menu_draw = tk.Menu(self.mb_draw, tearoff = tk.FALSE)
        self.menu_draw.insert_command(DRAWENTRIES.index("wall"),
                                      label = "Wall",
                                      command = lambda : self.setDrawMode("wall"),
                                      foreground = 'blue')
        self.menu_draw.insert_command(DRAWENTRIES.index("door"),
                                      label = "Door",
                                      command = lambda : self.setDrawMode("door"))
        self.menu_draw.insert_command(DRAWENTRIES.index("stairs"),
                                      label = "Stairs",
                                      command = lambda : self.setDrawMode("stairs"))
        self.menu_draw.insert_command(DRAWENTRIES.index("transparentwall"),
                                      label = "Transparent Wall",
                                      command = lambda : self.setDrawMode("transparentwall"))
        self.menu_draw.insert_separator(DRAWENTRIES.index("separator_1"))
        self.menu_draw.insert_command(DRAWENTRIES.index("circle_red"),
                                      label = "Circle (Red)",
                                      command = lambda : self.setDrawMode("circle_red"))
        self.menu_draw.insert_command(DRAWENTRIES.index("circle_green"),
                                      label = "Circle (Green)",
                                      command = lambda : self.setDrawMode("circle_green"))
        self.menu_draw.insert_command(DRAWENTRIES.index("circle_blue"),
                                      label = "Circle (Blue)",
                                      command = lambda : self.setDrawMode("circle_blue"))
        self.menu_draw.insert_separator(DRAWENTRIES.index("separator_2"))
        self.menu_draw.insert_command(DRAWENTRIES.index("remove"),
                                      label = "Remove",
                                      command = lambda : self.setDrawMode("remove"))
        self.mb_draw.config(menu = self.menu_draw)

        self.menubar.pack(side = tk.TOP, fill = tk.X)
        self.mb_file.pack(side = tk.LEFT)
        self.mb_draw.pack(side = tk.LEFT, padx = 20)
        self.mb_info.pack(side = tk.RIGHT, padx = 10)

        self.canvas = tk.Canvas(self.mw,
                                bg     = COLORS["tk"]["background"],
                                width  = self.canvassize[0],
                                height = self.canvassize[1])
        self.canvas.pack()

        self.canvas.bind('<Motion>', self.mouseMovement)
        self.canvas.bind('<B1-Motion>', self.mouseMovementWithButton)
        self.canvas.bind('<ButtonRelease-1>', self.buttonReleased)
        self.canvas.bind('<Button-1>', self.mouseClick)
        self.drawGrid()
        self.cursor = Cursor(self.wallwidth, self.canvas)
        self.mw.mainloop()

    def setDrawMode(self, drawmode):
        self.drawmode = drawmode
        self.makeMenuEntryBlue()

    def makeMenuEntryBlue(self):
        # Make the menu_draw-entry blue:
        black_letters = []
        for i in DRAWENTRIES:
            if i == self.drawmode or i.startswith("separator"):
                continue
            black_letters.append(DRAWENTRIES.index(i))
        self.menu_draw.entryconfig(DRAWENTRIES.index(self.drawmode), foreground = 'blue')
        for i in black_letters:
            self.menu_draw.entryconfig(i, foreground = 'black')

    def new(self):
        answer = tkmessagebox.askyesno(title = "Clear grid?", message = "Are you sure?")
        if answer == True:
            self.board.clear()
            self.updateBoard()

    def load(self):
        filename = tkfiledialog.askopenfilename(initialdir = FILEDIR,
                                                filetypes = (("map files","*.map"),))
        if not filename:
            """
            a = "Nothing loaded."
            tkmessagebox.showwarning(title = a, message = a)
            """
            return
        fh = open(filename, "rb")
        data = []
        while True:
            b = fh.read(1)
            if not b:
                break
            data.append(ord(b))
        fh.close()
        self.board.clear()
        self.board.pokeInData(data, self.canvas)
        self.updateBoard()

    def getSaveName(self, initdir, filetypes):
        filename = tkfiledialog.asksaveasfilename(initialdir = initdir,
                                                  filetypes = filetypes)
        if not filename:
            a = "Nothing saved."
            tkmessagebox.showwarning(title = a, message = a)
            return None
        suf = filetypes[0][1][1:5]
        if not filename.endswith(suf):
            filename += suf
        return filename
 
    def saveAs(self):
        filename = self.getSaveName(FILEDIR, (("map files", "*.map"),) )
        if not filename:
            return
        data = self.board.collectData()
        fh = open(filename, "wb")
        fh.write(bytearray(data))
        fh.close()

    def getOvalCoords(self, line):
        if line.orientation == "horizontal":
            return ((line.p1[0], line.p1[1] - self.doorovalsize),
                    (line.p2[0], line.p2[1] + self.doorovalsize))
        if line.orientation == "vertical":
            return ((line.p1[0] - self.doorovalsize, line.p1[1]),
                    (line.p2[0] + self.doorovalsize, line.p2[1]))

    def saveImage(self):
        if VERSION == "public":
            filename = self.getSaveName(FILEDIR, (("png files", "*.png"),) )
            if not filename:
                return
        # Using PIL to redraw the image on the Canvas:
        image1 = Image.new("RGB", self.canvassize, COLORS["pil"]["background"])
        draw = ImageDraw.Draw(image1)
        for line in self.board.lines:
            if line.state =="wall":
                lwidth = self.wallwidth
            elif line.state =="door":
                if line.orientation == "horizontal":
                    lwidth = 3
                else:
                    lwidth = 2
            else:
                lwidth = 1
            if line.state == "door":
                draw.ellipse(self.getOvalCoords(line), fill = None, outline = COLORS["pil"][line.state])

            if DRAW_MEASURING_TAPE_WITH_PIL and line.state == "empty" and line.isgrey:
                draw.line(xy = (line.p1[0], line.p1[1], line.p2[0], line.p2[1]),
                                width = lwidth,
                                fill = COLORS["pil"]["measuring"])
            elif line.state in ("wall", "empty"):
                draw.line(xy = (line.p1[0], line.p1[1], line.p2[0], line.p2[1]),
                                width = lwidth,
                                fill = COLORS["pil"][line.state])

            if line.state == "transparentwall":
                for i in line.lparts:
                    draw.line(xy = (i[0][0], i[0][1], i[1][0], i[1][1]), width = 2, fill = COLORS["pil"][line.state])

            line.drawAttachment("pil", draw)

        if VERSION == "public":
            image1.save(filename, "PNG")
        else:
            image1.save(IMAGEFILE, "PNG")

    def uploadToFTP(self):
        if VERSION != "private":
            # Shouldn't even get here, because menu entry should be disabled in public version:
            return
        if FTPSERVER == "" or FTPDIRECTORY == "" or len(FTPLOGIN) < 2:
            tkmessagebox.showwarning(title = "FTP-data not found", message = "FTP-data not found. Nothing transmitted.\n\nTo use this feature, you have to edit the lines about the data for FTP access at the beginning of the script.\nAn example of the required format can be found there too.")
            return
        self.saveImage()
        if not os.path.exists(IMAGEFILE):
            tkmessagebox.showwarning(title = "Image-File not found", message = "Image-File not found.\nNothing transmitted.")
            return
        """
        answer = tkmessagebox.askyesno(title = "Transfer file?", message = "File ready.\nStart FTP-upload now?")
        if not answer:
            return
        """
        if os.name == "posix":
            a = IMAGEFILE.split("/")
        else:
            a = IMAGEFILE.split("\\")
        fname = a.pop()
        ftp = ftplib.FTP(FTPSERVER)
        ftp.login(FTPLOGIN[0], FTPLOGIN[1])
        ftp.cwd(FTPDIRECTORY)
        ftp.storbinary('STOR ' + fname, open(IMAGEFILE, 'rb'))
        ftp.quit()

    def updateBoard(self):
        for i in self.board.lines:
            self.currentline = i
            self.drawLine(i, "update")

    def setMeasuringTapeCoordinates(self):
        boxdivision = 10
        vx = []
        hy = []
        for i in range(int(self.board.lines_xnr / boxdivision - 1)):
            vx.append(self.board.border + (i + 1) * boxdivision * self.board.linesize)
        for i in range(int(self.board.lines_ynr / boxdivision)):
            hy.append(self.canvassize[1] - (self.board.border + (i + 1) * boxdivision * self.board.linesize))
        self.measuringtape = {"horizontal" : {"x" : (self.board.border, self.canvassize[0] - self.board.border - self.board.linesize),
                                              "y" : hy},
                              "vertical"   : {"x" : vx,
                                              "y" : (self.board.border, self.canvassize[1] - self.board.border - self.board.linesize)}}

    def drawGrid(self):
        for line in self.board.lines:
            if line.p1[0] in self.measuringtape[line.orientation]["x"] and line.p1[1] in self.measuringtape[line.orientation]["y"]:
                self.canvas.create_line(line.p1, line.p2, width = 2, fill = 'grey')
                line.setGrey()
            else:
                # The ordinary lightgrey lines of the grid:
                self.canvas.create_line(line.p1, line.p2, width = 2, fill = 'lightgrey')

    def clearLine(self, line):
        for i in line.canvasobjects:
            self.canvas.delete(i)
        line.canvasobjects = []

    def redrawCursor(self):
        if not self.currentline:
            return
        self.cursor.setOff()
        self.cursor.show(self.currentline, self.drawmode) 

    def drawLine(self, line, caller):

        self.clearLine(line)
        if caller != "update":
            self.redrawCursor()

        line.drawAttachment("tk", None)

        if line.state == "door":
            ids = []
            oc = self.getOvalCoords(line)
            ids.append(self.canvas.create_oval(oc[0], oc[1], width = 3, fill = '', outline = COLORS["tk"]["door"]))
            for i in ids:
                line.addCanvasObject(i)

        if line.state == "wall":
            line.addCanvasObject(self.canvas.create_line(line.p1, line.p2, width = self.wallwidth, fill = COLORS["tk"][line.state]))

        if line.state == "transparentwall":
            for i in line.lparts:
                line.addCanvasObject(self.canvas.create_line(i[0], i[1], width = self.transparentwallwidth, fill = COLORS["tk"][line.state]))

    def mouseMovement(self, event):
        mouse_x, mouse_y = event.x, event.y
        if mouse_x <= self.board.border or mouse_x >= self.canvassize[0] - self.board.border or mouse_y <= self.board.border or mouse_y >= self.canvassize[1] - self.board.border:
            self.cursor.setOff()
            return
        self.currentline = self.board.getClosestLine(mouse_x, mouse_y)
        self.redrawCursor()

    def mouseClick(self, event):
        # Do this, when mouse is clicked:
        if self.drawmode in ("wall", "transparentwall", "door"):
            self.currentline.setState(self.drawmode)
        if self.drawmode == "stairs":
            self.currentline.addAttachment(self.drawmode, self.canvas)
        if self.drawmode.startswith("circle"):
            self.currentline.addAttachment(self.drawmode, self.canvas)
        if self.drawmode == "remove":
            self.currentline.setState("empty")
            self.currentline.clearAttachment()
        self.drawLine(self.currentline, "mouseclick")
        self.cursor.setOff()

    def mouseMovementWithButton(self, event):
        self.button_down = True
        self.mouseMovement(event)
        if self.currentline.orientation == self.getMouseDirection(event):
            self.mouseClick(event)

    def getMouseDirection(self, event):
        currentmouseposition = (event.x, event.y)
        d_x = abs(currentmouseposition[0] - self.previousmouseposition[0])
        d_y = abs(currentmouseposition[1] - self.previousmouseposition[1])
        self.previousmouseposition = currentmouseposition
        if d_x > d_y:
            return "horizontal"
        else:
            return "vertical"

    def buttonReleased(self, event):
        self.button_down = False

    def showInfo(self):
        m = "DungeonDraw 2.0\n\nA simple dungeon editor for\nrole-playing games.\n\nCopyright (C) 2022,\nHauke Lubenow\nLicense: GNU GPL, version 3."
        tkmessagebox.showinfo(title = "DungeonDraw", message = m)

if __name__ == "__main__":
   app = Main()
