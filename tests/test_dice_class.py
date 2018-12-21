import pytest

from dice.dice import Dice


def test_dice_rolls():
    dice = Dice("1d6")
    # Make sure our rolls are as we expect
    for _ in range(100):
        assert 1 <= dice.roll()[0] <= 6


def test_drop_high_low():
    dice = Dice("3d6-L-H")
    # Make sure our rolls are as we expect
    for _ in range(100):
        assert len(dice.roll()) == 1


def test_dice_number():
    TEST_PAIRS = (
        ("0d0", 0),
        ("3d6", 3),
        ("10d7+4", 10),
        ("8d12-3", 8),
        ("4d2-2L", 4),
        ("23d24-5H", 23),
        ("7(d20+1)-L-2H", 7),
        ("5(d10-1)+15-3L-H", 5),
        ("4d2-2l", 4),
        ("23d24-5h", 23),
        ("7(d20+1)-l-2h", 7),
        ("5(d10-1)+15-3l-h", 5),
    )

    for dice_str, answer in TEST_PAIRS:
        d = Dice(dice_str)
        assert d.number == answer


def test_dice_size():
    TEST_PAIRS = (
        ("0d0", 0),
        ("3d6", 6),
        ("10d7+4", 7),
        ("8d12-3", 12),
        ("4d2-2L", 2),
        ("23d24-5H", 24),
        ("7(d20+1)-L-2H", 20),
        ("5(d10-1)+15-3L-H", 10),
        ("4d2-2l", 2),
        ("23d24-5h", 24),
        ("7(d20+1)-l-2h", 20),
        ("5(d10-1)+15-3l-h", 10),
    )

    for dice_str, answer in TEST_PAIRS:
        d = Dice(dice_str)
        assert d.size == answer


def test_dice_globalmod():
    TEST_PAIRS = (
        ("0d0", 0),
        ("3d6", 0),
        ("10d7+4", 4),
        ("8d12-3", -3),
        ("4d2-2L", 0),
        ("23d24-5H", 0),
        ("7(d20+1)-L-2H", 0),
        ("5(d10-1)+15-3L-H", 15),
        ("4d2-2l", 0),
        ("23d24-5h", 0),
        ("7(d20+1)-l-2h", 0),
        ("5(d10-1)+15-3l-h", 15),
    )

    for dice_str, answer in TEST_PAIRS:
        d = Dice(dice_str)
        assert d.global_mod == answer


def test_dice_localmod():
    TEST_PAIRS = (
        ("0d0", 0),
        ("3d6", 0),
        ("10d7+4", 0),
        ("8d12-3", 0),
        ("4d2-2L", 0),
        ("23d24-5H", 0),
        ("7(d20+1)-L-2H", 1),
        ("5(d10-1)+15-3L-H", -1),
        ("4d2-2l", 0),
        ("23d24-5h", 0),
        ("7(d20+1)-l-2h", 1),
        ("5(d10-1)+15-3l-h", -1),
    )

    for dice_str, answer in TEST_PAIRS:
        d = Dice(dice_str)
        assert d.local_mod == answer


def test_dice_lowestmod():
    TEST_PAIRS = (
        ("0d0", 0),
        ("3d6", 0),
        ("10d7+4", 0),
        ("8d12-3", 0),
        ("4d2-2L", 2),
        ("23d24-5H", 0),
        ("7(d20+1)-L-2H", 1),
        ("5(d10-1)+15-3L-H", 3),
        ("4d2-2l", 2),
        ("23d24-5h", 0),
        ("7(d20+1)-l-2h", 1),
        ("5(d10-1)+15-3l-h", 3),
    )

    for dice_str, answer in TEST_PAIRS:
        d = Dice(dice_str)
        assert d.lowest_mod == answer


def test_dice_highestmod():
    TEST_PAIRS = (
        ("0d0", 0),
        ("3d6", 0),
        ("10d7+4", 0),
        ("8d12-3", 0),
        ("4d2-2L", 0),
        ("23d24-5H", 5),
        ("7(d20+1)-L-2H", 2),
        ("5(d10-1)+15-3L-H", 1),
        ("4d2-2l", 0),
        ("23d24-5h", 5),
        ("7(d20+1)-l-2h", 2),
        ("5(d10-1)+15-3l-h", 1),
    )

    for dice_str, answer in TEST_PAIRS:
        d = Dice(dice_str)
        assert d.highest_mod == answer
