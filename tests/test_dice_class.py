import pytest

from dice.dice import Dice
import re


def test_dice_number():
    TEST_PAIRS = (
        ("3d6", 3),
        ("4dF", 4),
        ("10d7+4", 10),
        ("8d12-3", 8),
        ("4d2-2L", 4),
        ("23d24-5H", 23),
        ("7(d20+1)-L-2H", 7),
        ("4(dF-1)-L", 4),
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
        ("3d6", 6),
        ("4dF", "F"),
        ("10d7+4", 7),
        ("8d12-3", 12),
        ("4d2-2L", 2),
        ("23d24-5H", 24),
        ("7(d20+1)-L-2H", 20),
        ("4(dF-1)-L", "F"),
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
        ("3d6", 0),
        ("4dF", 0),
        ("10d7+4", 4),
        ("8d12-3", -3),
        ("4d2-2L", 0),
        ("23d24-5H", 0),
        ("7(d20+1)-L-2H", 0),
        ("4(dF-1)-L", 0),
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
        ("3d6", 0),
        ("4dF", 0),
        ("10d7+4", 0),
        ("8d12-3", 0),
        ("4d2-2L", 0),
        ("23d24-5H", 0),
        ("7(d20+1)-L-2H", 1),
        ("4(dF-1)-L", -1),
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
        ("3d6", 0),
        ("4dF", 0),
        ("10d7+4", 0),
        ("8d12-3", 0),
        ("4d2-2L", 2),
        ("23d24-5H", 0),
        ("7(d20+1)-L-2H", 1),
        ("4(dF-1)-L", 1),
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
        ("3d6", 0),
        ("4dF", 0),
        ("10d7+4", 0),
        ("8d12-3", 0),
        ("4d2-2L", 0),
        ("23d24-5H", 5),
        ("7(d20+1)-L-2H", 2),
        ("4(dF-1)-L", 0),
        ("5(d10-1)+15-3L-H", 1),
        ("4d2-2l", 0),
        ("23d24-5h", 5),
        ("7(d20+1)-l-2h", 2),
        ("5(d10-1)+15-3l-h", 1),
    )

    for dice_str, answer in TEST_PAIRS:
        d = Dice(dice_str)
        assert d.highest_mod == answer


def test_too_few_dice():
    TEST = (
        "0d0",
        "0d1",
        "0dF",
    )
    for dice_str in TEST:
        with pytest.raises(ValueError) as err_info:
            Dice(dice_str)
        match_str = r"Number of dice .?[0-9]+ is less than 1."
        assert err_info.match(match_str)


def test_too_small_die():
    TEST = (
        "1d0",
        "3d1",
    )
    for dice_str in TEST:
        with pytest.raises(ValueError) as err_info:
            Dice(dice_str)
        match_str = r"Die size of [0-9]+ is less than 2."
        assert err_info.match(match_str)


def test_too_many_drops():
    TEST = (
        "1d6-L",
        "3d6-2L-2H",
        "3dF-4H",
    )
    for dice_str in TEST:
        with pytest.raises(ValueError) as err_info:
            Dice(dice_str)
        match_str = r"Too many \([0-9]+\) dice dropped, but only [0-9]+ dice used."
        assert err_info.match(match_str)


def test_too_large_local_mod():
    TEST = (
        "1(d6-7)",
        "3(d2-2)-2H",
    )
    for dice_str in TEST:
        with pytest.raises(ValueError) as err_info:
            Dice(dice_str)
        match_str = r"Local mod -[0-9]+ is larger than die size [0-9]+; all rolls would be 0!"
        assert err_info.match(match_str)
