#!/usr/bin/python3

"""
Allows command line options to be parsed. Called first to in order to let
functions use them.
"""

import argparse
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
        self.FATE_CHARS = frozenset(['F'])
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
            if i == self.end - 1 and char in self.INT_CHARS.union(self.LH_CHARS).union(self.FATE_CHARS):
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
            elif char in self.INT_CHARS.union(self.LH_CHARS).union(self.FATE_CHARS):
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

            # Something illegal!
            else:
                err = "Illegal character '{}' found in dice format string!".format(char)
                raise ValueError(err)


#LL Parser
class llParser:
    """ LL Parser """
    def __init__(self, table, tokenizer):
        """ """
        self.table = table
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
                "<local-mod>": self.__is_local_mod,
                "<global-mod>": self.__is_global_mod,
                "<drop>": None,
                "<int-die-num>": self.__isInt,
                "<str-die-size>": self.__isStrDieSize,
                "<str-drop-mod>": None,
                "<str-drop-high>": self.__is_str_drop_high,
                "<str-drop-low>": self.__is_str_drop_low,
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
        # Must have a "d" as the first part of the token
        if not s[0] == 'd':
            return False
        # Must then be followed by an integer or an F for fate dice
        is_int = s[1:].isdigit()
        if not is_int and s[1] != 'F':
            return False

        return True

    def __is_str_drop_mod(self, s, chars):
        """ Check if s matches <str-drop-low> """
        # A drop mod has three pieces:
        #
        # It starts with a -
        has_minus = s[0] == '-'
        # It ends with a specific character
        has_char = s[-1] in chars
        # And the midle is an integer or empty
        mid = s[1:-1]
        ok_mid = mid == '' or mid.isdigit()

        return has_minus and has_char and ok_mid

    def __is_str_drop_low(self, s):
        """ Check if s matches <str-drop-low> """
        return self.__is_str_drop_mod(s, chars=['L', 'l'])

    def __is_str_drop_high(self, s):
        """ Check if s matches <str-drop-high> """
        return self.__is_str_drop_mod(s, chars=['H', 'h'])

    def __is_local_mod(self, s):
        """ Check if s matches <local-mod> """
        # A local mod is allowed to be empty
        if s == '':
            return True
        # Otherwise it must look like a sign and an integer
        has_sign = s[0] in ['-', '+']
        has_int = s[1:].isdigit()

        if has_sign and has_int:
            return True

        return False

    def __is_global_mod(self, s):
        """ Check if s matches <global-mod> """
        # A global mod has the exact same form as a local mod, so we can reuse
        # the check.
        return self.__is_local_mod(s)

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
        die_size = self.sTable["<str-die-size>"][1:]
        if die_size == "F":
            self.size = die_size
        else:
            self.size = int(die_size)

        self.local_mod = self.__get_die_mod("<local-mod>")
        self.global_mod = self.__get_die_mod("<global-mod>")
        self.highest_mod = self.__get_drop_mod("<str-drop-high>")
        self.lowest_mod = self.__get_drop_mod("<str-drop-low>")

        # If we have a global mod, we must sum all the dice to apply it
        self.do_sum = bool(self.global_mod)

        # Error checking to make sure the above values lead to valid
        # combinations of dice.
        self.__do_error_checking()

    def __do_error_checking(self):
        # If we are rolling 0 (or fewer) dice
        if self.number < 1:
            err = "Number of dice {} is less than 1.".format(self.number)
            raise ValueError(err)

        # If the die size is less than 2, then there are no interesting results
        if self.size != "F" and self.size < 2:
            err = "Die size of {} is less than 2.".format(self.size)
            raise ValueError(err)

        # If we have zero (or fewer) dice left after dropping
        if self.highest_mod + self.lowest_mod >= self.number:
            dropped = self.highest_mod + self.local_mod
            err = "More dice dropped ({}) than rolled ({}).".format(dropped, self.number)
            raise ValueError(err)

        # If the local mod is too large, all rolls will be 0
        # (but Fate dice are allowed to go negative, so we ignore in that case)
        if self.size != "F" and self.size + self.local_mod <= 0:
            err = "Local mod {} is larger than die size {}; all rolls would be 0!".format(self.local_mod, self.size)
            raise ValueError(err)

    def __get_die_mod(self, modStr):
        """ Get general die mod """
        mod = self.sTable.get(modStr, None)
        if mod is None:
            return 0

        return int(mod)

    def __get_drop_mod(self, modStr):
        """ Get general drop mod """
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

    def roll(self, do_sum=False):
        """ Roll the dice and print the result. """
        # Generate rolls
        values = []
        for _ in range(0, self.number):
            # Fate Dice use F, and have sides (-1, 0, 1)
            if self.size == "F":
                die_val = randint(-1, 1) + self.local_mod
            else:
                die_val = randint(1, self.size) + self.local_mod
                die_val = max(die_val, 0)  # Dice must roll at least 0 after mods

            values.append(die_val)

        # Remove highest and lowest dice
        start_i = self.lowest_mod
        end_i = len(values) - self.highest_mod

        values = sorted(values)[start_i:end_i]

        #Return values
        if self.do_sum or do_sum:
            output = sum(values) + self.global_mod
        else:
            output = values

        print(output)
        return output


def main():
    # Command line parsing
    parser = argparse.ArgumentParser(
        prog="Dice",
        description="A very complicated way of rolling dice.",
    )
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 3.1.2")
    parser.add_argument("dice_notation", type=str, help="the dice notation for the dice to roll, such as '4d6'")
    parser.add_argument("-s", "--sum", help="sum the results of the roll", action="store_true", default=False)
    args = parser.parse_args()

    d = Dice(args.dice_notation)
    d.roll(args.sum)


if __name__ == '__main__':
    main()
