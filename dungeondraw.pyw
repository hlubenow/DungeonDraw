#!/usr/bin/python
# coding: utf-8

"""
    DungeonDraw 1.1 - A simple dungeon editor for role-playing games.

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

import Tkinter as tk
import tkMessageBox
import tkFileDialog

# Check, if PIL is available:
SAVEIMAGESTATE = tk.ACTIVE
try:
    from PIL import Image, ImageDraw
except:
    SAVEIMAGESTATE = tk.DISABLED

import os

FONT = ("Arial", 14)

FILEDIR = os.getcwd()

class Board:

    def __init__(self):
        self.border    = 20
        self.lines_xnr = 50
        self.lines_ynr = 25
        self.linesize  = 23
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
            self.lines.append(Line(nr, self.lines_xnr, y, "vertical", self))
            nr += 1

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
            i.cursor = False
            i.setState("empty")

    def collectData(self):
        states = ("empty", "wall", "door")
        data = ""
        for i in self.lines:
            data += str(states.index(i.state))
        return data

    def pokeInData(self, data):
        states = ("empty", "wall", "door")
        for i in range(len(self.lines)):
            self.lines[i].setState(states[int(data[i:i+1])])

class Line:

    def __init__(self, nr, xnr, ynr, orientation, board):
        self.nr = nr
        self.board = board
        self.orientation = orientation 
        self.cursor = False
        self.state = "empty"
        self.canvasobjects = []
        self.cursorobjects = []
        self.setColor()
        border = self.board.border
        width  = self.board.linesize
        height = self.board.linesize
        self.p1 = (border + xnr * width, border + ynr * height)
        if self.orientation == "horizontal":
            self.p2 = (self.p1[0] + width, self.p1[1])
        if self.orientation == "vertical":
            self.p2 = (self.p1[0], self.p1[1] + height)

    def addCanvasObject(self, id):
        self.canvasobjects.append(id)

    def addCursorObject(self, id):
        self.cursorobjects.append(id)

    def setState(self, state):
        self.state = state
        self.setColor()

    def cursorOn(self):
        self.cursor = True

    def cursorOff(self):
        self.cursor = False

    def setColor(self):
        if self.state == "wall":
            self.color = "black"
        elif self.state == "door":
            # ZX Spectrum Magenta:
            self.color = "#c000c0"
        else:
            self.color = "lightgrey"

    def showState(self):
        print self.state
        print self.cursor
        print self.color
        print


class Main:

    def __init__(self):

        self.mw = tk.Tk()
        self.mw.option_add("*font", FONT)
        self.mw.geometry("1200x650+40+0")
        self.mw.title("DungeonDraw")
        self.mw.bind(sequence = "<Control-q>", func = lambda e: self.mw.destroy())
        self.mw.bind(sequence = "<w>", func = lambda e: self.setDrawMode("wall"))
        self.mw.bind(sequence = "<d>", func = lambda e: self.setDrawMode("door"))
        self.mw.bind(sequence = "<r>", func = lambda e: self.setDrawMode("empty"))
        self.board                 = Board()
        self.canvassize            = (2 * self.board.border + self.board.lines_xnr * self.board.linesize,
                                      2 * self.board.border + self.board.lines_ynr * self.board.linesize)
        self.wallwidth             = 4
        self.doorovalsize          = 4
        self.drawmode              = "wall"
        self.currentline           = None
        self.previousline          = None
        self.previousmouseposition = (0, 0)
        self.button_down           = False
        self.cursorcolors  = {"wall" : "blue",
                              "door" : "#c000c0",
                              "empty": "cyan"}

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
                                      label   = "Save Image",
                                      command = self.saveImage,
                                      state   = SAVEIMAGESTATE)
        self.menu_file.insert_separator(4)
        self.menu_file.insert_command(5, label = "Exit", command = self.mw.destroy)
        self.mb_file.config(menu = self.menu_file)

        self.menu_draw = tk.Menu(self.mb_draw, tearoff = tk.FALSE)
        self.menu_draw.insert_command(0,
                                      label = "Wall",
                                      command = lambda : self.setDrawMode("wall"),
                                      foreground = 'blue')
        self.menu_draw.insert_command(1,
                                      label = "Door",
                                      command = lambda : self.setDrawMode("door"))
        self.menu_draw.insert_separator(2)
        self.menu_draw.insert_command(3,
                                      label = "Remove",
                                      command = lambda : self.setDrawMode("empty"))
        self.mb_draw.config(menu = self.menu_draw)

        self.menubar.pack(side = tk.TOP, fill = tk.X)
        self.mb_file.pack(side = tk.LEFT)
        self.mb_draw.pack(side = tk.LEFT, padx = 20)
        self.mb_info.pack(side = tk.RIGHT, padx = 10)

        self.cv = tk.Canvas(self.mw,
                            bg     = "white",
                            width  = self.canvassize[0],
                            height = self.canvassize[1])
        self.cv.pack()

        self.cv.bind('<Motion>', self.mouseMovement)
        self.cv.bind('<B1-Motion>', self.mouseMovementWithButton)
        self.cv.bind('<ButtonRelease-1>', self.buttonReleased)
        self.cv.bind('<Button-1>', self.mouseClick)
        self.drawGrid()
        self.mw.mainloop()

    def setDrawMode(self, drawmode):
        self.drawmode = drawmode
        # Make menu_draw-entry blue:
        all = (0, 1, 3)
        h = {"wall" : 0, "door" : 1, "empty" : 3}
        black_letters = []
        for i in all:
            if i == h[self.drawmode]:
                continue
            black_letters.append(i)
        self.menu_draw.entryconfig(h[self.drawmode], foreground = self.cursorcolors[self.drawmode])
        for i in black_letters:
            self.menu_draw.entryconfig(i, foreground = 'black')
        # Redraw cursor in new color:
        if self.currentline:
            self.drawLine(self.currentline)

    def new(self):
        answer = tkMessageBox.askyesno(title = "Clear grid?", message = "Are you sure?")
        if answer == True:
            self.board.clear()
            self.updateBoard()

    def load(self):
        filename = tkFileDialog.askopenfilename(initialdir = FILEDIR,
                                                filetypes = (("map files","*.map"),))
        if not filename:
            a = "Nothing loaded."
            tkMessageBox.showwarning(title = a, message = a)
            return
        fh = open(filename, "r")
        data = fh.read()
        fh.close()
        self.board.pokeInData(data)
        self.updateBoard()

    def getSaveName(self, initdir, filetypes):
        filename = tkFileDialog.asksaveasfilename(initialdir = initdir,
                                                  filetypes = filetypes)
        if not filename:
            a = "Nothing saved."
            tkMessageBox.showwarning(title = a, message = a)
            return None

        return filename

    def saveAs(self):
        filename = self.getSaveName(FILEDIR, (("map files", "*.map"),) )
        if not filename:
            return
        data = self.board.collectData()
        fh = open(filename, "w")
        fh.write(data)
        fh.close()

    def getOvalCoords(self, line):
        if line.orientation == "horizontal":
            return ((line.p1[0], line.p1[1] - self.doorovalsize),
                    (line.p2[0], line.p2[1] + self.doorovalsize))
        if line.orientation == "vertical":
            return ((line.p1[0] - self.doorovalsize, line.p1[1]),
                    (line.p2[0] + self.doorovalsize, line.p2[1]))

    def saveImage(self):
        filename = self.getSaveName(FILEDIR, (("png files", "*.png"),) )
        # filename = self.getSaveName(FILEDIR, (("jpg files", "*.jpg"),) )
        if not filename:
            return
        # Using PIL to redraw the image on the Canvas:
        colors = {"lightgrey" : (192, 192, 192),
                  "black"     : (0, 0, 0),
                  "#c000c0"   : (192, 0, 192),
                  "white"     : (255, 255, 255)}
        image1 = Image.new("RGB", self.canvassize, colors["white"])
        draw   = ImageDraw.Draw(image1)
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
                draw.ellipse(self.getOvalCoords(line), fill = None, outline = colors[line.color])
            draw.line(xy = (line.p1[0], line.p1[1], line.p2[0], line.p2[1]),
                            width = lwidth,
                            fill = colors[line.color])
        image1.save(filename, "PNG")

    def updateBoard(self):
        for i in self.board.lines:
            self.drawLine(i)

    def drawGrid(self):
        # A lot of calculations just to get a few grey lines at the right places:
        boxdivision = 10
        measuring = {"horizontal" : [], "vertical" : []}
        for i in range(self.board.lines_xnr / boxdivision - 1):
            measuring["vertical"].append(self.board.border + (i + 1) * boxdivision * self.board.linesize)
        for i in range(self.board.lines_ynr / boxdivision):
            measuring["horizontal"].append(self.canvassize[1] - (self.board.border + (i + 1) * boxdivision * self.board.linesize))
        for line in self.board.lines:
            grey = False
            for i in measuring[line.orientation]:
                if line.orientation == "vertical" and line.p1[0] == i:
                    if line.p1[1] == self.board.border or line.p1[1] == self.canvassize[1] - self.board.border - self.board.linesize:
                        grey = True
                if line.orientation == "horizontal" and line.p1[1] == i:
                    if line.p1[0] == self.board.border or line.p1[0] == self.canvassize[0] - self.board.border - self.board.linesize:
                        grey = True
            if grey:
                self.cv.create_line(line.p1, line.p2, width = 2, fill = 'grey')
            else:
                # The ordinary lightgrey lines of the grid:
                self.cv.create_line(line.p1, line.p2, width = 2, fill = 'lightgrey')

    def clearLine(self, line):
        for i in line.canvasobjects:
            self.cv.delete(i)
        line.canvasobjects = []

    def drawLine(self, line):

        if line.cursor:
            line.addCursorObject(self.cv.create_line(line.p1,
                                                     line.p2,
                                                     width = self.wallwidth,
                                                     fill = self.cursorcolors[self.drawmode]))
            return
        else:
            for i in line.cursorobjects:
                self.cv.delete(i)
            line.cursorobjects = []

        if line.state == "empty":
            self.clearLine(line)
            return

        if line.state == "door":
            self.clearLine(line)
            ids = []
            oc = self.getOvalCoords(line)
            ids.append(self.cv.create_oval(oc[0], oc[1], width = 3, fill = '', outline = line.color))
            # ids.append(self.cv.create_line(line.p1, line.p2, width = 4, fill = line.color))
            for i in ids:
                line.addCanvasObject(i)

        if line.state == "wall":
            self.clearLine(line)
            line.addCanvasObject(self.cv.create_line(line.p1, line.p2, width = self.wallwidth, fill = line.color))

    def mouseMovement(self, event):
        mouse_x, mouse_y = event.x, event.y
        if mouse_x <= self.board.border or mouse_x >= self.canvassize[0] - self.board.border or mouse_y <= self.board.border or mouse_y >= self.canvassize[1] - self.board.border:
            if self.currentline:
                self.currentline.cursorOff()
                self.drawLine(self.currentline)
            return
        self.currentline = self.board.getClosestLine(mouse_x, mouse_y)
        if not self.previousline:
            self.previousline = self.currentline
        if self.currentline is not self.previousline:
            self.previousline.cursorOff()
            self.drawLine(self.previousline)
            if not self.button_down:
                self.currentline.cursorOn()
                self.drawLine(self.currentline)
            self.previousline = self.currentline

    def mouseClick(self, event):
        self.currentline.setState(self.drawmode)
        self.currentline.cursorOff()
        self.drawLine(self.currentline)

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
        m = "DungeonDraw 1.1\n\nA simple dungeon editor for\nrole-playing games.\n\nCopyright (C) 2022,\nHauke Lubenow\nLicense: GNU GPL, version 3."
        tkMessageBox.showinfo(title = "DungeonDraw", message = m)

if __name__ == "__main__":
   app = Main()
