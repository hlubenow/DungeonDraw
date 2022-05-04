#!/usr/bin/python
# coding: utf-8

"""
    DungeonDraw 1.5 - A simple dungeon editor for role-playing games.
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

from PIL import Image, ImageDraw

import os

FILEDIR = os.getcwd()

FONT = ("Calibri", 10)

COLORS = {"wall"      : "black",
          "door"      : "#c000c0",
          "empty"     : "lightgrey",
          "measuring" : "grey",
          "stairs"    : "black",
          "poi"       : "#00c000"}

CR = '\r\n'

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
        states = ("empty", "wall", "door")
        data = ""
        for i in self.lines:
            n = states.index(i.state)
            if i.attachment:
                if i.attachment.name == "stairs":
                    n += 3
                else:
                    n += 6
            n = str(n)
            data += n
        return data

    def pokeInData(self, data, canvas):
        states = ("empty", "wall", "door")
        for i in range(len(self.lines)):
            n = int(data[i:i+1])
            if n >= 3 and n <= 5:
                self.lines[i].addAttachment("stairs", canvas)
                n -= 3
            if n >= 6:
                self.lines[i].addAttachment("poi", canvas)
                n -= 6
            self.lines[i].setState(states[n])

class Line:

    def __init__(self, nr, xnr, ynr, orientation, board):
        self.nr = nr
        self.board = board
        self.orientation = orientation 
        self.state = "empty"
        self.canvasobjects = []
        self.attachment = None
        self.lastcolumn = False
        self.setColor()
        border = self.board.border
        width  = self.board.linesize
        height = self.board.linesize
        self.p1 = (border + xnr * width, border + ynr * height)
        if self.orientation == "horizontal":
            self.p2 = (self.p1[0] + width, self.p1[1])
        if self.orientation == "vertical":
            self.p2 = (self.p1[0], self.p1[1] + height)

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
        if name == "poi":
            self.attachment = PointOfInterest(name, canvas, self)

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

    def setLast(self):
        self.lastcolumn = True

    def setState(self, state):
        self.state = state
        self.setColor()

    def setColor(self):
        self.color = COLORS[self.state]


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
            self.canvasobjects.append(self.canvas.create_line(stairs_p1, stairs_p2, width = 2, fill = COLORS["stairs"]))
        else:
            pildraw.line(xy = (stairs_p1[0], stairs_p1[1], stairs_p2[0], stairs_p2[1]), width = 2, fill = (0, 0, 0))


class PointOfInterest(Attachment):

    def __init__(self, name, canvas, line):
        Attachment.__init__(self, name, canvas, line)

    def draw(self, mode, pildraw):
        poi_p1 = (self.line.p1[0] + self.line.board.linesize // 4,
                  self.line.p1[1] + self.line.board.linesize // 4)
        poi_p2 = (self.line.p1[0] + self.line.board.linesize * 3 // 4,
                  self.line.p1[1] + self.line.board.linesize * 3 // 4)
 
        if mode == "tk":
            self.canvasobjects.append(self.canvas.create_oval(poi_p1, poi_p2, width = 3, fill = COLORS["poi"], outline = COLORS["poi"]))
        else:
            green = (0, 192, 0)
            pildraw.ellipse((poi_p1[0], poi_p1[1], poi_p2[0], poi_p2[1]), fill = green, outline = green)

class Cursor:

    def __init__(self, wallwidth, canvas):
        self.wallwidth    = wallwidth
        self.canvas       = canvas
        self.canvasobject = None
        self.colors       = {"wall"   : "blue",
                             "door"   : COLORS["door"],
                             "stairs" : "blue",
                             "poi"    : COLORS["poi"],
                             "delete" : "cyan"}

    def show(self, currentline, drawmode):
        self.color = "blue"
        if drawmode == "delete":
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
        self.mw.bind(sequence = "<r>", func = lambda e: self.setDrawMode("delete"))
        self.board = Board()
        self.canvassize            = (2 * self.board.border + self.board.lines_xnr * self.board.linesize,
                                      2 * self.board.border + self.board.lines_ynr * self.board.linesize)
        self.drawMeasuringTapeWithPIL = False
        self.setMeasuringTapeCoordinates()
        self.wallwidth             = 4
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
        self.menu_draw.insert_command(2,
                                      label = "Stairs",
                                      command = lambda : self.setDrawMode("stairs"))
        self.menu_draw.insert_command(3,
                                      label = "Point of Interest",
                                      command = lambda : self.setDrawMode("poi"))
        self.menu_draw.insert_separator(4)
        self.menu_draw.insert_command(5,
                                      label = "Remove",
                                      command = lambda : self.setDrawMode("delete"))
        self.mb_draw.config(menu = self.menu_draw)

        self.menubar.pack(side = tk.TOP, fill = tk.X)
        self.mb_file.pack(side = tk.LEFT)
        self.mb_draw.pack(side = tk.LEFT, padx = 20)
        self.mb_info.pack(side = tk.RIGHT, padx = 10)

        self.canvas = tk.Canvas(self.mw,
                            bg     = "white",
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
        all = (0, 1, 2, 3, 5)
        h = {"wall" : 0, "door" : 1, "stairs" : 2, "poi" : 3, "delete" : 5}
        black_letters = []
        for i in all:
            if i == h[self.drawmode]:
                continue
            black_letters.append(i)
        self.menu_draw.entryconfig(h[self.drawmode], foreground = 'blue')
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
        fh = open(filename, "r")
        data = fh.read()
        fh.close()
        data = data.rstrip(CR)
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
        fh = open(filename, "w")
        fh.write(data)
        fh.write(CR)
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
        if not filename:
            return
        # Using PIL to redraw the image on the Canvas:
        colors = {"lightgrey" : (192, 192, 192),
                  "grey"      : (80, 80, 80),
                  "black"     : (0, 0, 0),
                  "#c000c0"   : (192, 0, 192),
                  "white"     : (255, 255, 255),
                  "#00c000"   : (0, 192, 0)}

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

            if self.drawMeasuringTapeWithPIL and self.lineIsGrey(line):
                draw.line(xy = (line.p1[0], line.p1[1], line.p2[0], line.p2[1]),
                                width = lwidth,
                                fill = colors[line.color])
            else:
                draw.line(xy = (line.p1[0], line.p1[1], line.p2[0], line.p2[1]),
                                width = lwidth,
                                fill = colors[line.color])
            line.drawAttachment("pil", draw)

        image1.save(filename, "PNG")

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

    def lineIsGrey(self, line):
        if line.p1[0] in self.measuringtape[line.orientation]["x"] and line.p1[1] in self.measuringtape[line.orientation]["y"]:
            return True
        else:
            return False

    def drawGrid(self):
        for line in self.board.lines:
            if self.lineIsGrey(line):
                self.canvas.create_line(line.p1, line.p2, width = 2, fill = 'grey')
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
            ids.append(self.canvas.create_oval(oc[0], oc[1], width = 3, fill = '', outline = COLORS["door"]))
            for i in ids:
                line.addCanvasObject(i)

        if line.state == "wall":
            line.addCanvasObject(self.canvas.create_line(line.p1, line.p2, width = self.wallwidth, fill = line.color))


    def mouseMovement(self, event):
        mouse_x, mouse_y = event.x, event.y
        if mouse_x <= self.board.border or mouse_x >= self.canvassize[0] - self.board.border or mouse_y <= self.board.border or mouse_y >= self.canvassize[1] - self.board.border:
            self.cursor.setOff()
            return
        self.currentline = self.board.getClosestLine(mouse_x, mouse_y)
        self.redrawCursor()

    def mouseClick(self, event):
        # Do this, when mouse is clicked:
        if self.drawmode in ("wall", "door"):
            self.currentline.setState(self.drawmode)
        if self.drawmode in ("stairs", "poi"):
            self.currentline.addAttachment(self.drawmode, self.canvas)
        if self.drawmode == "delete":
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
        m = "DungeonDraw 1.5\n\nA simple dungeon editor for\nrole-playing games.\n\nCopyright (C) 2022,\nHauke Lubenow\nLicense: GNU GPL, version 3."
        tkmessagebox.showinfo(title = "DungeonDraw", message = m)

if __name__ == "__main__":
   app = Main()
