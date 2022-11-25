#!/usr/bin/python
# coding: utf-8

"""
    DungeonDraw 2.4 - A small dungeon editor for role-playing games.
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

import tkinter as tk
import tkinter.messagebox as tkmessagebox
import tkinter.filedialog as tkfiledialog

import os, sys

APPLICATIONFONT = ("Calibri", 10)
LETTERFONT_TK   = ("Calibri", 12)
LETTERFONT_PIL  = ("C:\\Windows\\Fonts\\calibri.ttf", 18)

FILEDIR   = os.getcwd()

LINESEPARATOR = "\n"

COLORS = {"tk"  : {"background"      : "white",
                   "circle_blue"     : "#0000c0",
                   "circle_green"    : "#00c000",
                   "circle_red"      : "#c00000",
                   "door"            : "brown",
                   "door_locked"     : "#0000c0",
                   "empty"           : "lightgrey",
                   "key"             : "#0000c0",
                   "letter"          : "black",
                   "measuring"       : "grey",
                   "stairs"          : "black",
                   "transparentwall" : "#ff0000",
                   "wall"            : "black"} }

DRAWENTRIES = ("wall",
               "door",
               "door_locked",
               "key",
               "stairs",
               "transparentwall",
               "separator_1",
               "circle_red",
               "circle_green",
               "circle_blue",
               "separator_2",
               "letter",
               "separator_3",
               "remove")

WALLWIDTH             = 4
TRANSPARENTWALLWIDTH  = 4

class Board:

    def __init__(self):
        self.border     = 20
        self.lines_xnr  = 50
        self.lines_ynr  = 25
        self.linesize   = 22
        self.linestates = ("empty", "wall", "door", "door_locked", "key", "transparentwall")

    def receiveCanvas(self, canvas):
        self.canvas = canvas

    def buildLines(self, keypixels):
        self.keypixels = keypixels
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

    def drawGrid(self):
        for line in self.lines:
            if line.p1[0] in self.measuringtape[line.orientation]["x"] and line.p1[1] in self.measuringtape[line.orientation]["y"]:
                self.canvas.create_line(line.p1, line.p2, width = 2, fill = 'grey')
                line.setGrey()
            else:
                # The ordinary lightgrey lines of the grid:
                self.canvas.create_line(line.p1, line.p2, width = 2, fill = 'lightgrey')

    def setMeasuringTapeCoordinates(self, canvassize):
        boxdivision = 10
        vx = []
        hy = []
        for i in range(int(self.lines_xnr / boxdivision - 1)):
            vx.append(self.border + (i + 1) * boxdivision * self.linesize)
        for i in range(int(self.lines_ynr / boxdivision)):
            hy.append(canvassize[1] - (self.border + (i + 1) * boxdivision * self.linesize))
        self.measuringtape = {"horizontal" : {"x" : (self.border, canvassize[0] - self.border - self.linesize),
                                              "y" : hy},
                              "vertical"   : {"x" : vx,
                                              "y" : (self.border, canvassize[1] - self.border - self.linesize)}}

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

    def update(self):
        for i in self.lines:
            i.drawTk()

    def collectData(self):
        # Data format example: "0,wall", "5,stairs", "7,circle_red", "10,letter:B"
        data = []
        for i in self.lines:
            # 0 bis 5:
            n = str(self.linestates.index(i.state))
            if i.attachment:
                n += "," + i.attachment.name
                if i.attachment.name == "letter":
                    n += ":" + i.attachment.letter
            data.append(n)
        return data

    def pokeInData(self, data):
        for i in range(len(self.lines)):
            n = data[i]
            n = n.rstrip(LINESEPARATOR)
            a = n.split(",")
            self.lines[i].setState(self.linestates[int(a[0])])
            if len(a) > 1:
                if "letter" in a[1]:
                    b = a[1].split(":")
                    self.lines[i].addAttachment("letter", b[1])
                else:
                    self.lines[i].addAttachment(a[1], "")


class Line:

    def __init__(self, nr, xnr, ynr, orientation, board):
        self.nr     = nr
        self.board  = board
        self.canvas = self.board.canvas
        self.orientation = orientation 
        self.state = "empty"
        self.isgrey = False
        self.canvasobjects = []
        self.door       = None
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

    def drawTk(self):

        """ First, the line's canvas objects are cleared and deleted from the canvas.
            Then, they are redrawn. """

        self.removeAllCanvasObjects()

        self.drawAttachmentTk()

        if self.state == "door":
            self.door = Door(self, False)
            self.door.drawTk()

        if self.state == "door_locked":
            self.door = Door(self, True)
            self.door.drawTk()

        if self.state not in ("door", "door_locked"):
            self.door = None

        if self.state == "wall":
            self.addCanvasObject(self.canvas.create_line(self.p1, self.p2, width = WALLWIDTH, fill = COLORS["tk"][self.state]))

        if self.state == "transparentwall":
            for i in self.lparts:
                self.addCanvasObject(self.canvas.create_line(i[0], i[1], width = TRANSPARENTWALLWIDTH, fill = COLORS["tk"][self.state]))

    def addAttachment(self, name, letter):
        if self.orientation == "horizontal":
            return
        if self.lastcolumn:
            return
        if self.attachment:
            if self.attachment.name == name:
                if self.attachment.name != "letter" or self.attachment.letter == letter:
                    return
            self.clearAttachment()
        if name == "stairs":
            self.attachment = Stairs(name, self)
        if name == "key":
            self.attachment = Key(name, self, self.board.keypixels)
        if name == "letter" and letter != "":
            self.attachment = Letter(name, self, letter)
        if name.startswith("circle"):
            self.attachment = Circle(name, self)

    def hasAttachment(self):
        if self.attachment:
            return True
        else:
            return False

    def drawAttachmentTk(self):
        if not self.attachment:
            return
        self.attachment.drawTk()

    def clearAttachment(self):
        if not self.attachment:
            return
        self.attachment.remove()
        self.attachment = None

    def addCanvasObject(self, id):
        self.canvasobjects.append(id)

    def removeAllCanvasObjects(self):
        for i in self.canvasobjects:
            self.canvas.delete(i)
        self.canvasobjects = []

    def setGrey(self):
        self.isgrey = True

    def setLast(self):
        self.lastcolumn = True

    def setState(self, state):
        self.state = state


class Door:

    def __init__(self, line, locked):
        self.line     = line
        self.canvas   = self.line.canvas
        self.locked   = locked
        self.ovalsize = 4
        if self.locked:
            self.color_tk  = COLORS["tk"]["door_locked"]
        else:
            self.color_tk  = COLORS["tk"]["door"]

    def getOvalCoordinates(self):
        if self.line.orientation == "horizontal":
            return ((self.line.p1[0], self.line.p1[1] - self.ovalsize),
                    (self.line.p2[0], self.line.p2[1] + self.ovalsize))
        else:
            return ((self.line.p1[0] - self.ovalsize, self.line.p1[1]),
                    (self.line.p2[0] + self.ovalsize, self.line.p2[1]))

    def drawTk(self):

        oc = self.getOvalCoordinates()

        ids = []
        ids.append(self.canvas.create_oval(oc[0], oc[1], width = 3, fill = '', outline = self.color_tk))
        for i in ids:
            self.line.addCanvasObject(i)


class Attachment:

    def __init__(self, name, line):
        self.name   = name
        self.line   = line
        self.canvas = self.line.canvas
        self.canvasobjects = []

    def remove(self):
        for i in self.canvasobjects:
            self.canvas.delete(i)

class Stairs(Attachment):

    def __init__(self, name, line):
        Attachment.__init__(self, name, line)

    def getStairCoordinates(self):
        sc = []
        for i in range(0, 501, 250):
            stairs_p1 = (self.line.p1[0] + self.line.board.linesize // 4,
                         self.line.p1[1] + self.line.board.linesize // 4 + i / 1000. * self.line.board.linesize)
            stairs_p2 = (self.line.p1[0] + self.line.board.linesize * 3 // 4,
                         stairs_p1[1])
            sc.append((stairs_p1, stairs_p2))
        return sc

    def drawTk(self):
        sc = self.getStairCoordinates()
        for i in sc:
            self.canvasobjects.append(self.canvas.create_line(i[0], i[1], width = 2, fill = COLORS["tk"]["stairs"]))


class Key(Attachment):

    def __init__(self, name, line, keypixels):

        Attachment.__init__(self, name, line)
        self.keypixels   = keypixels
        self.pixelsize   = 1.1
        self.topleft     = (self.line.p1[0] + self.line.board.linesize // 8,
                            self.line.p1[1] + self.line.board.linesize // 3)

    def getCoordinates(self):
        # Converting the pixeldata to screen coordinates:
        c = []
        for i in self.keypixels:
            c.append((i[0] * self.pixelsize + self.topleft[0],
                      i[1] * self.pixelsize + self.topleft[1]))
        return c

    def drawTk(self):
        c = self.getCoordinates()
        for i in c:
            self.canvasobjects.append(self.canvas.create_rectangle(i[0], i[1], i[0] + self.pixelsize, i[1] + self.pixelsize, fill = COLORS["tk"]["key"], outline = COLORS["tk"]["key"]))


class Circle(Attachment):

    def __init__(self, name, line):
        Attachment.__init__(self, name, line)

    def getCircleCoordinates(self):
        return ((self.line.p1[0] + self.line.board.linesize // 4,
                 self.line.p1[1] + self.line.board.linesize // 4),
                (self.line.p1[0] + self.line.board.linesize * 3 // 4,
                 self.line.p1[1] + self.line.board.linesize * 3 // 4))
 
    def drawTk(self):
        cc = self.getCircleCoordinates()
        self.canvasobjects.append(self.canvas.create_oval(cc[0], cc[1], width = 3, fill = COLORS["tk"][self.name], outline = COLORS["tk"][self.name]))


class Letter(Attachment):

    def __init__(self, name, line, letter):
        Attachment.__init__(self, name, line)
        self.letter = letter

    def drawTk(self):
        center = (self.line.p1[0] + self.line.board.linesize // 2,
                  self.line.p1[1] + self.line.board.linesize // 2)
        self.canvasobjects.append(self.canvas.create_text(center[0], center[1],
                                                          fill = "black",
                                                          font = LETTERFONT_TK,
                                                          text = self.letter))

class Cursor:

    def __init__(self, canvas):
        self.canvas       = canvas
        self.canvasobject = None
        self.colors       = {"wall"            : "blue",
                             "door"            : COLORS["tk"]["door"],
                             "door_locked"     : COLORS["tk"]["door_locked"],
                             "key"             : COLORS["tk"]["key"],
                             "stairs"          : "blue",
                             "letter"          : "blue",
                             "transparentwall" : "red",
                             "remove"          : "cyan"}
        
        for i in ("red", "green", "blue"):
            self.colors["circle_" + i] = COLORS["tk"]["circle_" + i]

    def show(self, currentline, drawmode):
        self.color = "blue"
        if drawmode == "remove":
            self.color = "cyan"
        self.canvasobject = self.canvas.create_line(currentline.p1,
                                                    currentline.p2,
                                                    width = WALLWIDTH,
                                                    fill = self.colors[drawmode])
        
    def setOff(self):
        self.canvas.delete(self.canvasobject)
        self.canvasobject = None


class Main:

    def __init__(self):

        self.mw = tk.Tk()
        self.mw.option_add("*font", APPLICATIONFONT)
        self.mw.geometry("1200x650+20+0")
        self.setDefaultTitle()
        self.mw.bind(sequence = "<Control-q>", func = lambda e: self.mw.destroy())
        self.mw.bind(sequence = "<w>", func = lambda e: self.setDrawMode("wall"))
        self.mw.bind(sequence = "<d>", func = lambda e: self.setDrawMode("door"))
        self.mw.bind(sequence = "<l>", func = lambda e: self.setDrawMode("door_locked"))
        self.mw.bind(sequence = "<r>", func = lambda e: self.setDrawMode("remove"))
        self.board = Board()
        self.canvassize            = (2 * self.board.border + self.board.lines_xnr * self.board.linesize,
                                      2 * self.board.border + self.board.lines_ynr * self.board.linesize)
        self.board.setMeasuringTapeCoordinates(self.canvassize)
        self.drawmode              = "wall"
        self.currentline           = None
        self.previouscursorlinenr  = None
        self.previousmouseposition = (0, 0)
        self.button_down           = False
        self.letter                = ""
        self.lettersused           = False
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
                                      command = lambda: self.load(""))
        self.menu_file.insert_command(2,
                                      label = "Save as Data",
                                      command = self.saveAs)
        self.menu_file.insert_separator(3)
        self.menu_file.insert_command(4, label = "Exit", command = self.mw.destroy)
        self.mb_file.config(menu = self.menu_file)

        self.menu_draw = tk.Menu(self.mb_draw, tearoff = tk.FALSE)
        self.menu_draw.insert_command(DRAWENTRIES.index("wall"),
                                      label = "Wall",
                                      command = lambda : self.setDrawMode("wall"),
                                      foreground = 'blue')
        self.menu_draw.insert_command(DRAWENTRIES.index("door"),
                                      label = "Door",
                                      command = lambda : self.setDrawMode("door"))
        self.menu_draw.insert_command(DRAWENTRIES.index("door_locked"),
                                      label = "Locked Door",
                                      command = lambda : self.setDrawMode("door_locked"))
        self.menu_draw.insert_command(DRAWENTRIES.index("key"),
                                      label = "Key",
                                      command = lambda : self.setDrawMode("key"))
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
        self.menu_draw.insert_command(DRAWENTRIES.index("letter"),
                                      label = "Letter",
                                      command = lambda : self.addLetter())
        self.menu_draw.insert_separator(DRAWENTRIES.index("separator_3"))
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
        self.initBitmaps()
        self.board.receiveCanvas(self.canvas)
        self.board.buildLines(self.keypixels)
        self.board.drawGrid()
        self.cursor = Cursor(self.canvas)
        self.checkCommandLineForMap()
        self.mw.mainloop()

    def initBitmaps(self):
        # To do this only once. And not every time, a key is drawn:
        self.keypixels = self.bitmapDataToPixelData(("000111000000000",
                                                     "001101100000000",
                                                     "011000111111111",
                                                     "011000111111111",
                                                     "001101100000110",
                                                     "000111000000010"))

    def bitmapDataToPixelData(self, bitmapdata):
        pixeldata = []
        x = 0
        y = 0
        xlen = len(bitmapdata[0])
        for i in bitmapdata:
            for u in i:
                if u == "1":
                    pixeldata.append((x, y))
                x += 1
            y += 1
            x -= xlen
        return pixeldata

    def addLetter(self):
        self.dialogwindow = tk.Toplevel()
        self.dialogwindow.title("Which letter?")
        self.dialogwindow.geometry("+500+250")
        self.dialoglabel = tk.Label(self.dialogwindow,
                           text = "Draw which letter?")
        self.dialoglabel.pack(padx = 50, pady = 5)
        self.dialogentry = tk.Entry(self.dialogwindow,
                                    width = 2)
        self.dialogentry.pack()
        self.dialogentry.pack(pady = 5)
        self.dialogentry.bind(sequence = "<Return>", func = lambda e: self.dialogEnd(True))
        self.dialogentry.bind(sequence = "<Control-q>", func = lambda e: self.dialogEnd(False))
        self.dialogentry.focus()
        self.dialogbutton = tk.Button(self.dialogwindow,
                              text = "Ok",
                              command = lambda e: self.dialogEnd(True))
        self.dialogbutton.pack(pady = 10)
        self.mw.wait_window(self.dialogwindow)

    def dialogEnd(self, get):
        if get:
            self.letter = self.dialogentry.get()
            if self.letter:
                self.letter = self.letter[0]
            else:
                self.letter = ""
        else:
            self.letter = ""
        self.dialogwindow.destroy() 
        if get:
            self.setDrawMode("letter")

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
            self.board.update()
            self.lettersused = False
            self.setDefaultTitle()

    def load(self, filename):
        if not filename:
            filename = tkfiledialog.askopenfilename(initialdir = FILEDIR,
                                                filetypes = (("map files","*.map"),))
            if not filename:
                """
                a = "Nothing loaded."
                tkmessagebox.showwarning(title = a, message = a)
                """
                return
        fh = open(filename, "r")
        data = []
        line = True
        while line:
            line = fh.readline()
            if "letter" in line:
                self.lettersused = True
            if line:
                data.append(line)
        fh.close()
        self.board.clear()
        self.board.pokeInData(data)
        self.board.update()
        self.setWindowTitle(os.path.basename(filename))

    def checkCommandLineForMap(self):
        filename = ""
        if len(sys.argv) > 1:
            filename = sys.argv[1]
        if not filename.endswith(".map"):
            return
        if not os.path.exists(filename):
            return
        self.load(filename)

    def setDefaultTitle(self):
        self.setWindowTitle("DungeonDraw")

    def setWindowTitle(self, title):
        self.mw.title(title)

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
        fh = open(filename, "w")
        for i in data:
            fh.write(i + LINESEPARATOR)
        fh.close()
        self.setWindowTitle(os.path.basename(filename))

    def redrawCursor(self):
        if not self.currentline:
            return
        """ Prevent the cursor from being redrawn, until its line has changed.
            The previous drawmode doesn't need to be checked, because
            to set a new drawmode, the cursor has to be moved up to the
            menu anyway, causing the line to change.
        """
        if self.previouscursorlinenr == self.currentline.nr:
            return
        self.cursor.setOff()
        self.cursor.show(self.currentline, self.drawmode) 
        self.previouscursorlinenr = self.currentline.nr

    def mouseMovement(self, event):
        mouse_x, mouse_y = event.x, event.y
        if mouse_x <= self.board.border or mouse_x >= self.canvassize[0] - self.board.border or mouse_y <= self.board.border or mouse_y >= self.canvassize[1] - self.board.border:
            self.cursor.setOff()
            return
        self.currentline = self.board.getClosestLine(mouse_x, mouse_y)
        self.redrawCursor()

    def mouseClick(self, event):
        # Do this, when mouse is clicked:
        if self.drawmode in ("wall", "transparentwall", "door", "door_locked"):
            self.currentline.setState(self.drawmode)
        if self.drawmode in ("stairs", "key"):
            self.currentline.addAttachment(self.drawmode, "")
        if self.drawmode.startswith("circle"):
            self.currentline.addAttachment(self.drawmode, "")
        if self.drawmode.startswith("letter"):
            self.currentline.addAttachment(self.drawmode, self.letter)
            self.lettersused = True
        if self.drawmode == "remove":
            self.currentline.setState("empty")
            self.currentline.clearAttachment()
        self.currentline.drawTk()
        self.redrawCursor()

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
        m = "DungeonDraw 2.4\n\nA small dungeon editor for\ntabletop role-playing games.\n\nCopyright (C) 2022,\nHauke Lubenow\nLicense: GNU GPL, version 3."
        tkmessagebox.showinfo(title = "DungeonDraw", message = m)

if __name__ == "__main__":
   app = Main()
