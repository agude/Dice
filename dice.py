#!/usr/bin/python3
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
version = "%prog Version 2.0.0\n\nCopyright (C) 2012 Alexander Gude - alex.public.account+Dice@gmail.com\nThis is free software.  You may redistribute copies of it under the terms of\nthe GNU General Public License <http://www.gnu.org/licenses/gpl.html>.\nThere is NO WARRANTY, to the extent permitted by law.\n\nWritten by Alexander Gude."
parser = OptionParser(usage=usage,version=version)
parser.add_option("-d", "--dice", action="store", type="string", dest="dice", help="the dice to be rolled, such as '4d6'")
parser.add_option("-s", "--sum", action="store_true", dest="sum", default=False, help="sum final result")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="print status messages to stdout")

(options, args) = parser.parse_args()

#Tokenizer
class diceTokenizer:
    """ Returns a dice token """
    def __init__(self, input):
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
        for i in range(self.end):
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

#LL Parser
class llParser:
    """ LL Parser """
    def __init__(self, table, tokenizer):
        """ """
        self.table = table
        self.input = input
        self.stack = ['<START>']
        self.tokenizer = tokenizer
        self.__loop()

    def __loop(self):
        """ Run while loop until self.stack is empty """
        for streamElement in self.tokenizer:
            keepStreamElement = True
            while keepStreamElement and self.stack:
                stackElement = self.stack.pop()
                result = self.table.compare(stackElement, streamElement)
                #print stackElement, streamElement, result
                if result is True:
                    keepStreamElement = False
                    self.table.sTable[stackElement] = streamElement
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
            # Need to add a state check to avoid infinite loop in fail case

#LL Table
class diceTable:
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
                "<str-drop-mod>": None,
                "<str-drop-high>": self.__isStrDropHigh,
                "<str-drop-low>": self.__isStrDropLow,
                }
        self.pTable = {
                "<START>": self.__Start,
                "<die-type>": self.__dieType,
                "<drop>": self.__drop,
                "<str-drop-mod>": self.__strDropMod,
                "<local-mod>": self.__localMod,
                "<global-mod>": self.__globalMod,
                }
        self.sTable = {
                "<int-die-num>":None,
                "<str-die-size>":None,
                "<str-drop-high>":None,
                "<str-drop-low>":None,
                "<global-mod>":None,
                "<local-mod>":None,
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

    def __strDropMod(self, s, stack):
        """ Take action when stack status is <drop> """
        if s[0] == '-':
            if s[-1] in ['L','l']:
                stack.append("<str-drop-low>")
                return True
            elif s[-1] in ['H','h']:
                stack.append("<str-drop-high>")
                return True
            else:
                return False
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

    def __isStrDropLow(self,s,chars=['L','l']):
        """ Check if s matches <str-drop-low> """
        try:
            assert s[0] == '-' 
            assert s[-1] in chars
            mid = s[1:-1]
            if mid != '':
                int(mid)
        except AssertionError:
            return False
        except ValueError:
            return False
        else:
            return True

    def __isStrDropHigh(self,s):
        """ Check if s matches <str-drop-high> """
        return self.__isStrDropLow(s,chars=['H','h'])

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

#Dice
class dice:
    """

    """
    def __init__(self, diceStr, parser=llParser, tokenizer=diceTokenizer, table=diceTable):
        """ Sets up the dice by parsing a string of its type: 3d5 """
        self.diceStr = diceStr
        self.table = diceTable()
        self.tokenizer = diceTokenizer(self.diceStr)
        self.parser = llParser(self.table, self.tokenizer)
        self.sTable = self.table.sTable
        self.__parse()

    def __parse(self):
        """ Parse a imute format string. """
        self.__getNumber()
        self.__getSize()
        self.__getLocalMod()
        self.__getGlobalMod()
        self.__getHighestMod()
        self.__getLowestMod()
        self.__getDoSum()

    def __getDoSum(self):
        """ Set self.doSum """
        if self.globalMod:
            self.doSum = True
        else:
            self.doSum = False

    def __getNumber(self):
        """ Set self.number """
        self.number = 0
        self.number = int(self.sTable["<int-die-num>"])

    def __getSize(self):
        """ Set self.size """
        self.size = 0
        self.size = int(self.sTable["<str-die-size>"][1:])

    def __getDieMod(self, modStr):
        """ Get general die mod """
        try:
            mod = self.sTable[modStr]
        except KeyError:
            return 0
        if mod is None:
            return 0
        else:
            return int(mod)

    def __getLocalMod(self):
        """ Set self.localMod """
        self.localMod = self.__getDieMod("<local-mod>")

    def __getGlobalMod(self):
        """ Set self.globalMod """
        self.globalMod = self.__getDieMod("<global-mod>")

    def __getDropMod(self, modStr):
        """ Get geneal drop mod """
        mod = self.sTable[modStr]
        if mod is None:
            return 0
        else:
            mod = mod[1:] # Drop -
            mod = mod.rstrip('HhLl')
            if mod:
                return int(mod)
            else:
                return 1
        
    def __getHighestMod(self):
        """ Set self.highestMod """
        self.highestMod = self.__getDropMod("<str-drop-high>")

    def __getLowestMod(self):
        """ Set self.highestMod """
        self.lowestMod = self.__getDropMod("<str-drop-low>")

    def roll(self,doSum=None):
        """ Roll the dice and print the result. """
        # If self.doSum, we must do the sum
        if self.doSum == True:
            doSum == True
        #Generate numbers
        values = []
        for i in range(0,self.number):
            dieVal = randint(1,self.size) + self.localMod
            dieVal = max(dieVal,0) # Dice must roll at least 0 after mods
            values.append(dieVal)
        #Remove Highest and Lowest dice
        values.sort()
        starti = self.lowestMod
        endi = len(values) - self.highestMod
        values = values[starti:endi]
        #Return values
        if doSum:
            print(sum(values) + self.globalMod)
        else:
            print(values)

# Test Function
def testClass(toTest, inStr, number=0, size=0, globalMod=0, localMod=0, lowestMod=0, highestMod=0):
    t = toTest(inStr)
    try:
        assert t.number == number
    except AssertionError:
        print("Fail %s: %s = %i"%(inStr,"number",t.number))
        print(t.sTable)
    else:
        try:
            assert t.size == size
        except AssertionError:
            print("Fail %s: %s = %i"%(inStr,"size",t.size))
            print(t.sTable)
        else:
            try:
                assert t.globalMod == globalMod
            except AssertionError:
                print("Fail %s: %s = %i"%(inStr,"globalMod",t.globalMod))
                print(t.globalMod,globalMod)
                print(t.sTable)
            else:
                try:
                    assert t.localMod == localMod
                except AssertionError:
                    print("Fail %s: %s = %i"%(inStr,"localMod",t.localMod))
                    print(t.sTable)
                else:
                    try:
                        assert t.lowestMod == lowestMod
                    except AssertionError:
                        print("Fail %s: %s = %i"%(inStr,"lowestMod",t.lowestMod))
                        print(t.sTable)
                    else:
                        try:
                            assert t.highestMod == highestMod
                        except AssertionError:
                            print("Fail %s: %s = %i"%(inStr,"highestMod",t.highestMod))
                            print(t.sTable)
                        else:
                            print("Pass %s"%(inStr))

# Tests
if __name__ == '__main__':
    #testClass(dice, "0d0") # Always passes
    #testClass(dice, "3d6", 3, 6)
    #testClass(dice, "10d7+4", 10, 7, 4)
    #testClass(dice, "8d12-3", 8, 12, -3)
    #testClass(dice, "4d2-2L", 4, 2, 0, 0, 2)
    #testClass(dice, "23d24-5H", 23, 24, 0, 0, 0, 5)
    #testClass(dice, "7(d20+1)-L-2H", 7, 20, 0, 1, 1, 2)
    #testClass(dice, "5(d10-1)+15-3L-H", 5, 10, 15, -1, 3, 1)

    d = dice(options.dice)
    d.roll(options.sum)
