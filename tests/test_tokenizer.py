import pytest

from dice.dice import DiceTokenizer
import re


def test_dice_tokenizer():
    TEST_PAIRS = (
        ("0d0", ("0", "d0")),
        ("3d6", ("3", "d6")),
        ("10d7+4", ("10", "d7", "+4")),
        ("8d12-3", ("8", "d12", "-3")),
        ("4d2-2L", ("4", "d2", "-2L")),
        ("23d24-5H", ("23", "d24", "-5H")),
        ("7(d20+1)-L-2H", ("7", "(", "d20", "+1", ")", "-L", "-2H")),
        ("5(d10-1)+15-3L-H", ("5", "(", "d10", "-1", ")", "+15", "-3L", "-H")),
        ("4d2-2l", ("4", "d2", "-2l")),
        ("23d24-5h", ("23", "d24", "-5h")),
        ("7(d20+1)-l-2h", ("7", "(", "d20", "+1", ")", "-l", "-2h")),
        ("5(d10-1)+15-3l-h", ("5", "(", "d10", "-1", ")", "+15", "-3l", "-h")),
    )

    for dice_str, answer in TEST_PAIRS:
        tokens = tuple(DiceTokenizer(dice_str))
        assert tokens == answer


def test_dice_tokenizer_raise():
    TESTS = (
        "3$5",
        "#4d5-L-H",
        "7(d10-1)+L-R",
    )
    for format_str in TESTS:
        with pytest.raises(ValueError) as err_info:
            tokens = tuple(DiceTokenizer(format_str))
        match_str = r"Illegal character '.+' found in dice format string!"
        err_str = str(err_info.value)
        assert re.match(match_str, err_str)
