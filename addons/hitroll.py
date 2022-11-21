#!/usr/bin/python
# coding: utf-8

"""
    hitroll.py - Check for D&D monster hits and damages.

    Copyright (C) 2022 hlubenow

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

import sys
import random

def getNeededRoll(hd_inp, ac_inp):
    # Hit rolls don't change for example between level 9 and level 11:
    n = (10, 12, 14, 16)
    hd_temp = 1
    ac_temp = 9
    needed_roll = 10
    while hd_temp < hd_inp:
        if hd_temp not in n and hd_temp < 18:
            needed_roll -= 1
        hd_temp += 1
    while ac_temp > ac_inp:
        needed_roll += 1
        ac_temp -= 1
    if needed_roll > 20:
        needed_roll = 20
    if needed_roll < 2:
        needed_roll = 2
    return needed_roll

def getDamagePoints(weaponstring):
    weapons = {"sword" : 8, "club" : 6, "staff" : 4}
    for i in weapons:
        if i in weaponstring:
            return random.randrange(weapons[i]) + 1
    return "Error"


# Main:

if len(sys.argv) < 3:
    print "\nUsage: hitroll.py [hit dices monster] [armor class player]\n"
    sys.exit()

hd_inp = int(sys.argv[1])
ac_inp = int(sys.argv[2])

hashit = False

hitroll = random.randrange(20) + 1

print

if hitroll == 1:
    print "The monster has rolled 1, missing in any case."
    hashit = False

if hitroll == 20:
    print "The monster has rolled 20, hitting in any case."
    hashit = True

if not hashit:
    needed_roll = getNeededRoll(hd_inp, ac_inp)
    print "Hit dices monster:   " + str(hd_inp)
    print "Armor class player:  " + str(ac_inp)
    print
    print "The monster needs " + str(needed_roll) +" to hit the player."
    print "The monster rolls " + str(hitroll) + "."
    print
    if hitroll >= needed_roll:
        print "The monster has hit the player."
        hashit = True
    else:
        print "The monster has missed."
        hashit = False

if hashit:
    print
    w = ("sword", "club", "staff")
    for i in w:
        d = getDamagePoints(i)
        s = "- With a " + i + ", the monster causes "
        s += str(d)
        s += " point"
        if d > 1:
            s += "s"
        s += " of damage."
        print s

print
