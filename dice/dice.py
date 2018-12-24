#!/usr/bin/python3

from random import randint
import argparse
import logging


class DiceTokenizer:
    """ Returns a dice token """
    def __init__(self, input):
        """ """
        self.input = input
        self.end = len(self.input)

        # The three types of characters we encounter in a dice format string
        self.INT_CHARS = frozenset(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
        self.FATE_CHARS = frozenset(['F'])
        self.LH_CHARS = frozenset(['L', 'l', 'H', 'h'])
        self.SYMBOL_CHARS = frozenset(['+', '-', 'd'])
        self.PARENS = frozenset(['(', ')'])

    def __iter__(self):
        """ Allows iteration over self. """
        return self.__make_iter()

    def __make_iter(self):
        """ Return next item in iterator. """
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


class LLParser:
    """ LL Parser """
    def __init__(self, table, tokenizer):
        """ """
        self.table = table
        self.stack = ['<START>']
        self.tokenizer = tokenizer
        self.__loop()

    def __loop(self):
        """ Run while loop until self.stack is empty """
        for stream_element in self.tokenizer:
            keep_stream_element = True
            while keep_stream_element and self.stack:
                stack_element = self.stack.pop()
                result = self.table.compare(stack_element, stream_element)
                if result is True:
                    keep_stream_element = False
                    self.table.saved_value_table[stack_element] = stream_element
                    continue
                else:
                    self.table.stack_action_table[stack_element](stream_element, self.stack)


class DiceTable:
    """ """
    def __init__(self):
        self.comparison_table = {
            "<START>": None,
            "<die-type>": None,
            "<die-num>": self.__is_die_num,
            "<die-size>": self.__is_str_die_size,
            "<local-mod>": self.__is_local_mod,
            "<global-mod>": self.__is_global_mod,
            "<drop-mod>": None,
            "<drop-high>": self.__is_str_drop_high,
            "<drop-low>": self.__is_str_drop_low,
        }
        self.stack_action_table = {
            "<START>": self.__start,
            "<die-type>": self.__die_type,
            # Global mod can be blank, in which case we don't have anything to
            # add to the stack, but we still need to call a function.
            "<global-mod>": lambda stream_token, strack: False,
            "<drop-mod>": self.__drop_mod,
        }
        self.saved_value_table = {
            "<die-num>": None,
            "<die-size>": None,
            "<local-mod>": None,
            "<global-mod>": None,
            "<drop-high>": None,
            "<drop-low>": None,
        }

    def compare(self, token_string, stream_token):
        """ Compare a token from the stream to the token string on the stack.

        In an LL Parser, we need to check if the item on the stack
        (token_string) and the item from the stream (stream_token) match. If
        they do we remove the items and process the next item in the stream. If
        they do not match, we take some action and add items to the stack.

        This function compares the two items, which sometimes requires a
        specialized comparison function specified in the comparison_table.

        For single character token_strings (mostly parenthesis) the equality
        operator is used to check instead of a specialized function.

        Args:
            token_string (str): The token string from the stack, like '<START>'
                or '<die-type>'.
            stream_token (str): An item from the tokenized stream, like 'd6' or '-H'

        Returns:
            Bool: True if the stream_token is the same as the token_string, False
                otherwise.

        """
        # If a is a single character, then the comparison is just equality
        if len(token_string) == 1:
            return token_string == stream_token

        # Otherwise get the comparison function for the 'a' object and use it
        comp_function = self.comparison_table[token_string]
        if comp_function is None:
            return False

        return comp_function(stream_token)

    def __start(self, stream_token, stack):
        """ Take action when stack status is <START>.

        Replaces the <START> token with the four parts of a dice format string:

            <die-num> <die-type> <global-mod> <drop-mod>

        Args:
            stream_token (str): The token from the stream, although it is ignored.
            stack (list): The stack of `token_string`s, which we may modify by
                pushing more `token_string`s onto.

        Returns:
            True: No matching is required, so always returns true.

        """
        # Reversed() is used because we use a stack, so the first item to test
        # is the last item on the stack. However, it is easier for the author
        # to think left to right.
        stack += reversed(["<die-num>", "<die-type>", "<global-mod>", "<drop-mod>"])
        return True

    def __die_type(self, stream_token, stack):
        """ Take action when stack status is <die-type>.

        Die type can lead down two paths, depending on the `stream_token`. If
        the `stream_token` is '(', then we might be starting a die type with
        local mod:

            ( <die-size> <local-mod> )

        Otherwise, if our token starts with 'd', it is just the die size:

            <die-size>

        Args:
            stream_token (str): The token from the stream.
            stack (list): The stack of `token_string`s, which we may modify by
                pushing more `token_string`s onto.

        Returns:
            bool: True if we successfully matched an action to the
                `stream_token`, False otherwise.

        """
        # If we found a parenthesis, then we might have a local mod
        if stream_token == '(':
            stack += reversed(["(", "<die-size>", "<local-mod>", ")"])
            return True
        # Otherwise it is just a normal die size
        elif stream_token[0] == 'd':
            stack.append("<die-size>")
            return True

        return False

    def __drop_mod(self, stream_token, stack):
        """ Take action when stack status is <drop-mod>.

        Drop mod is nothing if `stream_token` is empty, or it can by a drop mod
        low followed by another drop mod if the `stream_token` ends in 'L', or
        a drop mod high followed by another drop mod if `stream_token` ends in
        'H', as follows:

            <drop-low> <drop-mod> | <drop-high> <drop-mod>

        Args:
            stream_token (str): The token from the stream.
            stack (list): The stack of `token_string`s, which we may modify by
                pushing more `token_string`s onto.

        Returns:
            bool: True if we successfully matched an action to the
                `stream_token`, False otherwise.

        """
        # Drop can be blank
        if stream_token == '':
            return True
        # Or it can be a drop mod
        elif stream_token[0] == '-':
            # either low
            if stream_token[-1] in ['L', 'l']:
                stack += reversed(["<drop-low>", "<drop-mod>"])
                return True
            # or high
            elif stream_token[-1] in ['H', 'h']:
                stack += reversed(["<drop-high>", "<drop-mod>"])
                return True

        return False

    def __is_str_die_size(self, stream_token):
        """ Check if s matches <die-size>.

        Args:
            stream_token (str): The token from the stream.

        Returns:
            bool: True if we successfully matched an action to the
                `stream_token`, False otherwise.

        """
        # Must have a "d" as the first part of the token
        if not stream_token[0] == 'd':
            return False
        # Must then be followed by an integer or an F for fate dice
        is_int = stream_token[1:].isdecimal()
        if not is_int and stream_token[1] != 'F':
            return False

        return True

    def __is_str_drop_mod(self, stream_token, chars):
        """ Check if stream_token matches <drop-low>.

        Args:
            stream_token (str): The token from the stream.
            chars (supports in): An object that supports `in` testing,
                containing the acceptable drop mode flags, normally ['l', 'L']
                for lowest and ['h', 'H'] for highest.

        Returns:
            bool: True if we successfully matched an action to the
                `stream_token`, False otherwise.

        """
        # A drop mod has three pieces:
        #
        # It starts with a -
        has_minus = stream_token[0] == '-'
        # It ends with a specific character
        has_char = stream_token[-1] in chars
        # And the middle is an integer or empty
        mid = stream_token[1:-1]
        ok_mid = mid == '' or mid.isdecimal()

        return has_minus and has_char and ok_mid

    def __is_str_drop_low(self, stream_token):
        """ Check if stream_token matches <drop-low> """
        return self.__is_str_drop_mod(stream_token, chars=['L', 'l'])

    def __is_str_drop_high(self, stream_token):
        """ Check if stream_token matches <drop-high> """
        return self.__is_str_drop_mod(stream_token, chars=['H', 'h'])

    def __is_local_mod(self, stream_token):
        """ Check if stream_token matches <str-local-mod> """
        # A local mod is allowed to be empty
        if stream_token == '':
            return True
        # Otherwise it must look like a sign and an integer
        has_sign = stream_token[0] in ['-', '+']
        has_int = stream_token[1:].isdecimal()

        if has_sign and has_int:
            return True

        return False

    def __is_global_mod(self, stream_token):
        """ Check if stream_token matches <global-mod> """
        # A global mod has the exact same form as a local mod, so we can reuse
        # the check.
        return self.__is_local_mod(stream_token)

    def __is_die_num(self, stream_token):
        """ Check if stream_token matches <die-num> """
        return stream_token.isdecimal()

BNF = """
<dice-notation> ::= <die-num> <die-type> <global-mod> <drop-mod>
<die-type> ::= <die-size> | "(" <die-size> <local-mod> ")"
<drop-mod> ::= <drop-high> <drop-mod> | <drop-low> <drop-mod> | ""
"""


#Dice
class Dice:
    """ A class to roll dice based on a dice format string. """

    def __init__(self, dice_str, parser=LLParser, tokenizer=DiceTokenizer, table=DiceTable):
        """ Sets up the dice by parsing a string of its type: 3d5 """
        self.dice_str = dice_str
        self.table = table()
        self.tokenizer = tokenizer(self.dice_str)
        self.parser = parser(self.table, self.tokenizer)
        self.saved_value_table = self.table.saved_value_table

        self.number = int(self.saved_value_table["<die-num>"])
        die_size = self.saved_value_table["<die-size>"][1:]
        if die_size == "F":
            self.size = die_size
        else:
            self.size = int(die_size)

        self.local_mod = self.__get_die_mod("<local-mod>")
        self.global_mod = self.__get_die_mod("<global-mod>")
        self.highest_mod = self.__get_drop_mod("<drop-high>")
        self.lowest_mod = self.__get_drop_mod("<drop-low>")

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
            dropped = self.highest_mod + self.lowest_mod
            err = "Number of dice dropped ({}) greater than or equal to number rolled ({}).".format(dropped, self.number)
            raise ValueError(err)

        # If the local mod is too large, all rolls will be 0
        # (but Fate dice are allowed to go negative, so we ignore in that case)
        if self.size != "F" and self.size + self.local_mod <= 0:
            err = "Local mod {} is larger than die size {}; all rolls would be 0!".format(self.local_mod, self.size)
            raise ValueError(err)

    def __get_die_mod(self, mod_str):
        """ Get general die mod """
        mod = self.saved_value_table.get(mod_str, None)
        if mod is None:
            return 0

        return int(mod)

    def __get_drop_mod(self, mod_str):
        """ Get general drop mod """
        mod = self.saved_value_table[mod_str]

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
