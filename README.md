Dice
====

A very complicated way of rolling dice.

Mainly an exercise in LL parsers and Backus–Naur Form.


Usage
-----

If the program is called as follows:

    dice.py -h

It will provide the following usage guide:

    Usage: dice [OPTIONS] -d 'xDy'

    Options:
      --version             show program's version number and exit
      -h, --help            show this help message and exit
      -d DICE, --dice=DICE  the dice to be rolled, such as '4d6'
      -s, --sum             sum final result
      -v, --verbose         print status messages to stdout

The simplest usage case is:

    dice.py -d "1d6"

Which will print the results of rolling one six-sided die. Other examples are:

Roll 3d6 without summing the result:

    dice.py -d "3d6"  

Rull 10d7, sum the dice, and add 4 to the total:

    dice.py -s -d "10d7+4"

Roll 8d12, sum the dice, and subtract 3 from the total:

    dice.py -s -d "8d12-3"

Roll 4d2, drop the two lowest rolls:

    dice.py -d "4d2-2L"

Roll 23d24, drop the five highest rolls, then sum:

    dice.py -s -d "23d24-5H"

Roll 7d20, add 1 to each die, then drop the lowest roll and the two highest
rolls, sum the final result:

    dice.py -s -d "7(d20+1)-L-2H"

Roll 5d10, subract 1 from each die, then drop the three lowest rolls and the
highest roll, then sum the dice and add 15:

    dice.py -s -d "5(d10-1)+15-3L-H"
