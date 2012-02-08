#!/usr/bin/python
#  Copyright (C) 2009  Alexander Gude - alex.public.account+DiceRoller@gmail.com
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
#  The most recent version of this program is avaible at:
#  Somewhere?
#
#  Version 1.0.0

""" Allows command line options to be parsed. Called first to in order to let functions use them.

    Version 1.0.0
    July 23rd (Saturday), 2011
    Alexander Gude

"""

from optparse import OptionParser
from random import randint

usage = "usage: %prog [OPTIONS] -d 'xDy'"
version = "%prog Version 1.0.0\n\nCopyright (C) 2011 Alexander Gude - alex.public.account+Dice@gmail.com\nThis is free software.  You may redistribute copies of it under the terms of\nthe GNU General Public License <http://www.gnu.org/licenses/gpl.html>.\nThere is NO WARRANTY, to the extent permitted by law.\n\nWritten by Alexander Gude."
parser = OptionParser(usage=usage,version=version)
parser.add_option("-d", "--dice", action="store", type="string", dest="dice", help="the dice to be rolled, such as '4d6'")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="print status messages to stdout")

(options, args) = parser.parse_args()

class dice:
    """

    """
    def __init__(self,imute):
        """ Sets up the dice by parsing a string of its type: 3d5 """
        self.imute = imute
        self.lowest = 0 # Subtract n lowest dice
        self.addToTotal = 0 # Add this number to total roll
        self.addToEach = 0 # Add this number to each die
        self.number = 0 # Number of dice to roll
        self.size = 0 # Size of each die
        self.__parse__()

        if 'L'  in self.type:
            numL = (self.type.split('L')[0]).split('-')[-1]
            if not numL:
                self.lowest = 1
            else:
                self.lowest = int(numL)
            self.type = '-'.join(self.type.split('-')[:-1])
            print self.type
        self.number = int(self.type.split('d')[0])
        self.size = int(self.type.split('d')[1])

    def __parse__(self):
        """ Parse a imute format string. """
        self.__getLowest__()
        self.__getAddToTotal__()
        self.__getAddToEach__()
        self.__getNumber__()
        self.__getSize__()

    def roll(self,dosum=False):
        """ Roll the dice and print the result. """
        values = []
        for i in xrange(0,self.number):
            values.append(randint(1,self.size))
        values.sort()
        values.reverse()
        for i in xrange(0,self.lowest):
            values.pop()
        if dosum:
            print sum(values)
        else:
            print values


# Test Function
def testClass(toTest, inStr, number=0, size=0, addToTotal=0, addToEach=0, lowest=0):
    t = toTest(inStr)
    assert t.number == number
    assert t.size == size
    assert t.addToTotal == addToTotal
    assert t.addToEach == addToEach
    assert t.lowest == lowest

# Tests
testClass(dice, "3d6", 3, 6)
