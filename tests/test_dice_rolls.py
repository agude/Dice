import pytest

from dice.dice import Dice

def test_dice_rolls():
    dice = Dice("1d6")
    # Make sure our rolls are as we expect
    for _ in range(100):
        assert 1 <= dice.roll()[0] <= 6


def test_fate_rolls():
    dice = Dice("1dF")
    for _ in range(100):
        assert -1 <= dice.roll()[0] <= 1


def test_dice_rolls_with_local_mod():
    dice = Dice("1(d6+3)")
    # Make sure our rolls are as we expect
    for _ in range(100):
        assert 4 <= dice.roll()[0] <= 9


def test_fate_rolls_with_local_mod():
    dice = Dice("1(dF+3)")
    for _ in range(100):
        assert 2 <= dice.roll()[0] <= 4


def test_dice_rolls_with_global_mod():
    dice = Dice("1d6+3")
    # Make sure our rolls are as we expect
    for _ in range(100):
        assert 4 <= dice.roll() <= 9


def test_fate_rolls_with_global_mod():
    dice = Dice("1dF+3")
    for _ in range(100):
        assert 2 <= dice.roll() <= 4


def test_drop_high_low():
    dice = Dice("3d6-L-H")
    # Make sure our rolls are as we expect
    for _ in range(100):
        assert len(dice.roll()) == 1
