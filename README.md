# Dice

A very complicated way of rolling dice by specifying the [dice notation][dn].

[dn]: https://en.wikipedia.org/wiki/Dice_notation

Mainly an exercise in writing a [LL parser][ll] and [Backus–Naur Form][bnf].

[ll]: https://en.wikipedia.org/wiki/LL_parser
[bnf]: https://en.wikipedia.org/wiki/Backus%E2%80%93Naur_form

## Usage

If the program is called as follows:

```
dice.py -h
```

It will provide the following usage guide:

```
usage: Dice [-h] [-v] [-s] dice_notation

A very complicated way of rolling dice.

positional arguments:
  dice_notation  the dice notation for the dice to roll, such as 4d6

optional arguments:
  -h, --help     show this help message and exit
  -v, --version  show program's version number and exit
  -s, --sum      sum the results of the roll
```

The simplest usage case is:

```
dice.py "1d6"
```

Which will print the results of rolling one six-sided die. Other examples are:

Roll 3d6 without summing the result:

```
dice.py "3d6"  
```

Rull 10d7, sum the dice, and add 4 to the total:

```
dice.py -s "10d7+4"
```

Roll 8d12, sum the dice, and subtract 3 from the total:

```
dice.py -s "8d12-3"
```

Roll 4d2, drop the two lowest rolls:

```
dice.py "4d2-2L"
```

Roll 23d24, drop the five highest rolls, then sum:

```
dice.py -s "23d24-5H"
```

Roll 7d20, add 1 to each die, then drop the lowest roll and the two highest
rolls, sum the final result:

```
dice.py -s "7(d20+1)-L-2H"
```

Roll 5d10, subract 1 from each die, then drop the three lowest rolls and the
highest roll, then sum the dice and add 15:

```
dice.py -s "5(d10-1)+15-3L-H"
```

Roll 4 [fate dice][fd] and sum the results:

```
dice.py -s "4dF"
```

[fd]: https://en.wikipedia.org/wiki/Fudge_(role-playing_game_system)#Fudge_dice
