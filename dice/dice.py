#!/usr/bin/python3

"""
Allows command line options to be parsed. Called first to in order to let
functions use them.
"""

from optparse import OptionParser
from random import randint


#Tokenizer
class DiceTokenizer:
    """ Returns a dice token """
    def __init__(self, input):
        """ """
        self.input = input
        self.end = len(self.input)

        # The three types of charactesr we encounter in a dice format string
        self.INT_CHARS = frozenset(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        self.LH_CHARS = frozenset(['L', 'l', 'H', 'h'])
        self.SYMBOL_CHARS = frozenset(['+', '-', 'd'])
        self.PARENS = frozenset(['(', ')'])

    def __iter__(self):
        """ Allows iteration over self """
        return self.__make_iter()

    def __make_iter(self):
        """ Return next item in iterization """
        buffer = ''
        for i in range(self.end):
            char = self.input[i]

            # End of stream check, where we yield all remaining
            if i == self.end - 1 and char in self.INT_CHARS.union(self.LH_CHARS):
                yield buffer + char

            # Handle symbols
            elif char in self.SYMBOL_CHARS:
                if not buffer:
                    # If buffer is empty we add +, -, d as the first
                    buffer += char
                else:
                    # But if we already have a buffer, we yield it,
                    # and start a new one to avoid "-3-"
                    yield buffer
                    buffer = char

            # Handle numbers and H/L mods
            elif char in self.INT_CHARS.union(self.LH_CHARS):
                #Add numbers, or L/H to the buffer
                buffer += char

            # Handle parenthesis.
            #
            # First yield the buffer if it has items, then reset the buffer,
            # then yield the character.
            #
            # This will result in two items in some cases, like "d6" followed
            # by ")". This is why we yield twice, and not add them together.
            elif char in self.PARENS:
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
                "<int-die-num>": None,
                "<str-die-size>": None,
                "<str-drop-high>": None,
                "<str-drop-low>": None,
                "<global-mod>": None,
                "<local-mod>": None,
                }

    def compare(self, a, b):
        """ Compare a, b using the compairison table. """
        if len(a) == 1:
            # For '(', ')', and other single characters
            return a == b
        else:
            try:
                compFunction = self.cTable[a]
            except KeyError:
                return None  # Should raise error
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
        elif s[-1] in ['L', 'l', 'H', 'h']:
            stack.append("<drop>")
            stack.append("<str-drop-mod>")
            return True
        else:
            return False

    def __strDropMod(self, s, stack):
        """ Take action when stack status is <drop> """
        if s[0] == '-':
            if s[-1] in ['L', 'l']:
                stack.append("<str-drop-low>")
                return True
            elif s[-1] in ['H', 'h']:
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
        elif s[-1] in ['L', 'l', 'H', 'h']:
            # There is no local/global mod
            # We are already at the drop condition
            return True
        elif s[0] in ['-', '+']:
            stack.append("<str-local-mod>")
            return True
        else:
            return False

    def __globalMod(self, s, stack):
        """ Take action when stack status is <global-mod> """
        return self.__localMod(s, stack)

    def __isStrDieSize(self, s):
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

    def __isStrDropLow(self, s, chars=['L', 'l']):
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

    def __isStrDropHigh(self, s):
        """ Check if s matches <str-drop-high> """
        return self.__isStrDropLow(s, chars=['H', 'h'])

    def __isLocalMod(self, s):
        """ Check if s matches <local-mod> """
        if s == '':
            return True
        else:
            try:
                assert s[0] in ['-', '+']
                int(s[1:])
            except AssertionError:
                return False
            except ValueError:
                return False
            else:
                return True

    def __isGlobalMod(self, s):
        """ Check if s matches <global-mod> """
        return self.__isLocalMod(s)

    def __isInt(self, s):
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
class Dice:
    """ A class to roll dice based on a dice format string. """

    def __init__(self, dice_str, parser=llParser, tokenizer=DiceTokenizer, table=diceTable):
        """ Sets up the dice by parsing a string of its type: 3d5 """
        self.dice_str = dice_str
        self.table = diceTable()
        self.tokenizer = DiceTokenizer(self.dice_str)
        self.parser = parser(self.table, self.tokenizer)
        self.sTable = self.table.sTable

        self.number = int(self.sTable["<int-die-num>"])
        self.size = int(self.sTable["<str-die-size>"][1:])

        self.local_mod = self.__getDieMod("<local-mod>")
        self.global_mod = self.__getDieMod("<global-mod>")
        self.highest_mod = self.__getDropMod("<str-drop-high>")
        self.lowest_mod = self.__getDropMod("<str-drop-low>")

        # If we have a global mod, we must sum all the dice to apply it
        self.do_sum = bool(self.global_mod)

    def __getDieMod(self, modStr):
        """ Get general die mod """
        mod = self.sTable.get(modStr, None)
        if mod is None:
            return 0

        return int(mod)

    def __getDropMod(self, modStr):
        """ Get geneal drop mod """
        mod = self.sTable[modStr]

        # No modifier
        if mod is None:
            return 0

        # See if the modifier is just a switch like -H,
        # or has a number like -2H
        mod = mod[1:]  # Drop -
        mod = mod.rstrip('HhLl')
        if mod:
            return int(mod)

        # No number, so modifier is 1
        return 1

    def roll(self, doSum=None):
        """ Roll the dice and print the result. """
        # Generate rolls
        values = []
        for _ in range(0, self.number):
            die_val = randint(1, self.size) + self.local_mod
            die_val = max(die_val, 0)  # Dice must roll at least 0 after mods
            values.append(die_val)

        # Remove highest and lowest dice
        start_i = self.lowest_mod
        end_i = len(values) - self.highest_mod

        values = sorted(values)[start_i:end_i]

        #Return values
        if self.do_sum:
            output = sum(values) + self.global_mod
        else:
            output = values

        print(output)
        return output


def main():
    usage = "usage: %prog [OPTIONS] -d 'xDy'"
    version = "%prog Version 1.0.0\n\nCopyright (C) 2018 Alexander Gude - alex.public.account+Dice@gmail.com"
    parser = OptionParser(usage=usage, version=version)
    parser.add_option("-d", "--dice", action="store", type="string", dest="dice", help="the dice to be rolled, such as '4d6'")
    parser.add_option("-s", "--sum", action="store_true", dest="sum", default=False, help="sum final result")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="print status messages to stdout")

    (options, args) = parser.parse_args()

    d = Dice(options.dice)
    d.roll(options.sum)


if __name__ == '__main__':
    main()
