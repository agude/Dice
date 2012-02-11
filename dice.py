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
        self.ints = ['0','1','2','3','4','5','6','7','8','9']
        self.LH = ['L','l','H','h']
        self.symbols = ['+','-','d']

    def __iter__(self):
        """ Allows iteration over self """
        return self.__makeIter()

    def __makeIter(self):
        """ Return next item in iterization """
        buffer = ''
        for i in xrange(self.end):
            char = self.input[i]
            if i == self.end-1 and char in (self.ints+self.LH):
                # End of stream, yield all
                yield buffer+char
            elif (char in self.symbols): 
                if (buffer == ''):
                    # If buffer is empty we add +,-,d as the first
                    buffer += char
                else: 
                    # But if we already have a buffer, we yield it, 
                    # and start a new one to avoid "-3-"
                    yield buffer
                    buffer = char
            elif (char in self.ints+self.LH):
                #Add numbers, or L/H to the buffer
                buffer += char
            else:
                # Some other character, yield the buffer, and restart
                if buffer:
                    yield buffer
                    buffer = ''
                yield char


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
        for streamElement in self.tokenizer:
            keepStreamElement = True
            while keepStreamElement and self.stack:
                stackElement = self.stack.pop()
                result = self.table.compare(stackElement, streamElement)
                print stackElement, streamElement, result
                if result is True:
                    keepStreamElement = False
                    continue 
                else:
                    self.table.pTable[stackElement](streamElement, self.stack)
        if self.stack:
            # Out of stream, but still have stack
            # We check to make sure the stack is isomorphic to ""
            streamElement = ''
            while self.stack:
                stackElement = self.stack.pop()
                result = self.table.compare(stackElement, streamElement)
                if result:
                    continue
                else:
                    self.table.pTable[stackElement](streamElement, self.stack)
            else:
                pass


# Parsing table
class Table:
    """ """
    def __init__(self):

        self.cTable = {
                "<START>": None,
                "<die-type>": None,
                "<local-mod>": self.__isLocalMod,
                "<global-mod>": self.__isGlobalMod,
                "<drop>": None,
                "<int-die-num>": self.__isInt,
                "<str-die-size>": self.__isStrDieSize,
                "<str-drop-mod>": self.__isStrDropMod,
                }

        self.pTable = {
                "<START>": self.__Start,
                "<die-type>": self.__dieType,
                "<drop>": self.__drop,
                "<local-mod>": self.__localMod,
                "<global-mod>": self.__globalMod,
                }

    def compare(self,a,b):
        """ Compare a,b using the compairison table. """
        if len(a) == 1:
            # For '(', ')', and other single characters
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
        if s == '(':
            stack.append(")")
            stack.append("<local-mod>")
            stack.append("<str-die-size>")
            stack.append("(")
            return True
        elif s[0] == 'd':
            stack.append("<str-die-size>")
        else:
            return False

    def __drop(self, s, stack):
        """ Take action when stack status is <drop> """
        if s == '':
            # Drop can be blank
            return True
        elif s[-1] in ['L','l','H','h']:
            stack.append("<drop>")
            stack.append("<str-drop-mod>")
            return True
        else:
            return False

    def __localMod(self, s, stack):
        """ Take action when stack status is <local-mod> """
        if s == '':
            # Local mod can be blank
            return True
        elif s[-1] in ['L','l','H','h']:
            # There is no local/global mod
            # We are already at the drop condition
            return True
        elif s[0] in ['-','+']:
            stack.append("<str-local-mod>")
            return True
        else:
            return False

    def __globalMod(self, s, stack):
        """ Take action when stack status is <global-mod> """
        return self.__localMod(s, stack)

    def __isStrDieSize(self,s):
        """ Check if s matches <str-die-size> """
        try:
            assert s[0] == 'd'
            int(s[1:])
        except AssertionError:
            return False
        except ValueError:
            return False
        else:
            return True

    def __isStrDropMod(self,s):
        """ Check if s matches <str-drop-mod> """
        try:
            assert s[0] == '-'
            assert s[-1] in ['L','l','H','h']
            mid = s[1:-1]
            if mid != '':
                int(mid)
        except AssertionError:
            return False
        except ValueError:
            return False
        else:
            return True

    def __isLocalMod(self,s):
        """ Check if s matches <local-mod> """
        if s == '':
            return True
        else:
            try:
                assert s[0] in ['-','+']
                int(s[1:])
            except AssertionError:
                return False
            except ValueError:
                return False
            else:
                return True

    def __isGlobalMod(self,s):
        """ Check if s matches <global-mod> """
        return self.__isLocalMod(s)

    def __isInt(self,s):
        """ Check if s is an integer """
        try:
            int(s)
            return True
        except ValueError:
            return False

BNF = """
<dice-notation> ::= <int-die-num> <die-type> <global-mod> <drop>
<die-type> ::= <str-die-size> | "(" <str-die-size> <local-mod> ")"
<local-mod> ::= <str-local-mod> | ""
<global-mod> ::= <str-global-mod> | ""
<drop> ::= <str-drop-mod> <drop> | ""
<str-drop-mod> ::= <str-drop-high> | <str-drop-low>
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

    strings = ['0d0','3d6', "10d7+4", "8d12-3", "4d2-2L", "23d24-5H", "7(d20+1)-L-2H", "18(d15-12)-1-3H","5(d10-1)+15-3L-H"]
    for string in strings:
        d = diceTokenizer(string)
        print "\n"+string
        t = Table()
        ll = llParser(t,d)
#    print p.compare("<int>", '42')
#    print p.compare("<int>", '42.1')
#    print p.compare('1', '1')
#    print p.compare('1', 'a')
