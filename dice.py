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
        self.highest = 0 # Subtract n highest dice
        self.addToTotal = 0 # Add this number to total roll
        self.addToEach = 0 # Add this number to each die
        self.number = 0 # Number of dice to roll
        self.size = 0 # Size of each die
        self.doSum = False # Sum dice by default.
        self.__parse()

        #if 'L'  in self.type:
        #    numL = (self.type.split('L')[0]).split('-')[-1]
        #    if not numL:
        #        self.lowest = 1
        #    else:
        #        self.lowest = int(numL)
        #    self.type = '-'.join(self.type.split('-')[:-1])
        #    print self.type
        #self.number = int(self.type.split('d')[0])
        #self.size = int(self.type.split('d')[1])

    def __parse(self):
        """ Parse a imute format string. """
        self.__getLowestHighest()
        #self.__getLowest()
        #self.__getAddToTotal()
        #self.__getAddToEach()
        #self.__getNumber()
        #self.__getSize()

    def __getLowestHighest(self):
        """ Parse "-nL-mH" and set lowest = n, highest = m """
        if "L" in self.imute:
            pass

    def roll(self,doSum=None):
        """ Roll the dice and print the result. """
        if doSum == None:
            doSum = self.doSum
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

#Tokenizer
class diceTokenizer:
    """ Returns a dice token """
    def __init__(self,input):
        """ """
        self.input = input
        self.end = len(self.input)
        self.i = 0
        self.ints = ['0','1','2','3','4','5','6','7','8','9']
    
    def __iter__(self):
        """ Allows iteration over self """
        return self.__makeIter()

    def __makeIter(self):
        """ Return next item in iterization """
        buffer = ''
        for i in xrange(self.end):
            char = self.input[i]
            if char not in self.ints:
                if buffer:
                    yield buffer
                    buffer = ''
                yield char
            elif i == self.end-1:
                yield char
            else:
                buffer += char


# LL Parser
class llParser:
    """ LL Parser """
    def __init__(self, table, tokenizer, k=1):
        """ """
        self.k = k
        self.table = table
        self.input = input
        self.stack = ['<START>']
        self.transform = []
        self.tokenizer = tokenizer
        self.__loop()

    def __loop(self):
        """ Run while loop until self.stack is empty """
        streamElement = ''
        keepStreamElement = True

        for streamElement in self.tokenizer:
            while keepStreamElement and self.stack:
                stackElement = self.stack.pop()
                comp = self.table.compare
                result = self.table.compare(stackElement, streamElement)
                print result
                if result is True:
                    continue 
                else:
                    self.table.pTable[stackElement](streamElement, self.stack)
                print self.stack


# Parsing table
class Table:
    """ """
    def __init__(self):

        self.cTable = {
            "<START>": None,
            "<die-type>": None,
            "<local-mod>": None,
            "<global-mod>": None,
            "<drop>": None,
            "<drop-mod>": None,
            "<drop-mod-body>": None,
            "<drop-mod-end>": self.__isLH,
            "<int-die-num>": self.__isInt,
            "<int-die-size>": self.__isInt,
            "<int-local-mod>": self.__isInt,
            "<int-global-mod>": self.__isInt,
            "<int-drop-mod>": self.__isInt,
                }
        
        self.pTable = {
                "<START>": self.__Start,
                "<die-type>": self.__dieType
                "<local-mod>": self.__localMod
                }

    def compare(self,a,b):
        """ Compare a,b using the compairison table """
        if len(a) == 1:
           return a == b 
        else:
            try:
                compFunction = self.cTable[a]
            except KeyError:
                return None # Should raise error
            if compFunction is None:
                return None
            else:
                return compFunction(b)

    def __Start(self, s, stack):
        """ Take action when stack status is <START> """
        stack.append("<drop>")
        stack.append("<global-mod>")
        stack.append("<die-type>")
        stack.append("<int-die-num>")
        return True

    def __dieType(self, s, stack):
        """ Take action when stack status is <die-type> """
        if s == 'd':
            stack.append("<int-die-size>")
            stack.append("d")
            return True
        elif s == '(':
            stack.append(")")
            stack.append("<local-mod>")
            stack.append("<int-die-size>")
            stack.append("d")
            stack.append("(")
            return True
        else:
            return False

    def __LocalMod(self, s, stack):
        """ Take action when stack status is <die-type> """
        symbol = None
        if s == ')':
            return True
        elif s == '+':
            symbol = '+'   
        elif s == '-':
            symbol = '-'
        if symbol:
            stack.append("<int-die-size>")
            stack.append(symbol)
        else:
            return False
            return True
        else:
            return False

    def __isInt(self,s):
        """ Check if s is an integer """
        try:
            int(s)
            return True
        except ValueError:
            return False

    def __isLH(self,s):
        """ Check if s is L or H """
        if s in ['L','l','H','h']:
            return True
        else:
            return False

BNF = """
<dice-notation> ::= <int-die-num> <die-type> <global-mod> <drop>
<die-type> ::= "d" <int-die-size> | "(" "d" <int-die-size> <local-mod> ")"
<local-mod> ::= "+" <int-local-mod> | "-" <int-local-mod> | ""
<global-mod> ::= "+" <int-global-mod> | "-" <int-global-mod> | ""
<drop> ::= <drop-mod> <drop-mod> | <drop-mod> | ""
<drop-mod> ::= "-" <drop-mod-body> | "+" <drop-mod-body>
<drop-mod-body> ::= <int-drop-mod> <drop-mod-end> | <drop-mod-end>
<drop-mod-end> ::= "h" | "l"
"""

# Test Function
def testClass(toTest, inStr, number=0, size=0, addToTotal=0, addToEach=0, lowest=0, highest=0):
    t = toTest(inStr)
    try:
        assert t.number == number
        assert t.size == size
        assert t.addToTotal == addToTotal
        assert t.addToEach == addToEach
        assert t.lowest == lowest
        assert t.highest == highest
    except AssertionError:
        print "Fail %s"%(inStr)
    else:
        print "Pass %s"%(inStr)

# Tests
if __name__ == '__main__':
#    testClass(dice, "0d0") # Always passes
#    testClass(dice, "3d6", 3, 6)
#    testClass(dice, "10d7+4", 10, 7, 4)
#    testClass(dice, "8d12-3", 8, 12, -3)
#    testClass(dice, "4d2-2L", 4, 2, 0, 0, 2)
#    testClass(dice, "23d24-5H", 23, 24, 0, 0, 0, 5)
#    testClass(dice, "7(d20+1)-L-2H", 4, 20, 0, 1, 1, 2)
#    testClass(dice, "5(d10-1)+15-3L-H", 5, 10, 0, -1, 3, 1)

    d = diceTokenizer("5(d10-1)+15-3L-H")
    t = Table()

    ll = llParser(t,d)
#    print p.compare("<int>", '42')
#    print p.compare("<int>", '42.1')
#    print p.compare('1', '1')
#    print p.compare('1', 'a')
