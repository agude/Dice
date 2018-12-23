import pytest

from dice.dice import DiceTable

from itertools import product
import re


def test_compare_single_char():
    TEST_PAIRS = (
        ('(', '('),
        (')', ')'),
    )
    table = DiceTable()
    for token_string, stream_token in TEST_PAIRS:
        assert table.compare(token_string, stream_token)


def test_compare_match_none():
    # These should never match
    STARTS = (
        "<START>",
        "<die-type>",
        "<drop>",
        "<str-drop-mod>",
    )
    POSSIBLE_MATCHES = ("d6", "(", "-H", "-12", "+15",)
    table = DiceTable()
    for token_string, stream_token in product(STARTS, POSSIBLE_MATCHES):
        assert not table.compare(token_string, stream_token)


def test_compare_is_local_mod():
    TEST_PAIRS = (
        # True
        ("-0", True),
        ("-15", True),
        ("-35", True),
        ("+0", True),
        ("+1", True),
        ("+15", True),
        ("+35", True),
        # False
        ("d5", False),
        ("dF", False),
        ("d100", False),
        ("(", False),
        (")", False),
        ("-L", False),
        ("-2L", False),
        ("-2l", False),
        ("-H", False),
        ("-3H", False),
        ("-3h", False),
        ("0", False),
        ("1", False),
        ("10", False),
    )
    table = DiceTable()
    for stream_token, answer in TEST_PAIRS:
        assert table.compare("<local-mod>", stream_token) == answer


def test_compare_is_global_mod():
    TEST_PAIRS = (
        # True
        ("-0", True),
        ("-15", True),
        ("-35", True),
        ("+0", True),
        ("+1", True),
        ("+15", True),
        ("+35", True),
        # False
        ("d5", False),
        ("dF", False),
        ("d100", False),
        ("(", False),
        (")", False),
        ("-L", False),
        ("-2L", False),
        ("-2l", False),
        ("-H", False),
        ("-3H", False),
        ("-3h", False),
        ("0", False),
        ("1", False),
        ("10", False),
    )
    table = DiceTable()
    for stream_token, answer in TEST_PAIRS:
        assert table.compare("<global-mod>", stream_token) == answer


def test_compare_is_str_die_size():
    TEST_PAIRS = (
        # True
        ("d5", True),
        ("dF", True),
        ("d100", True),
        # False
        ("-0", False),
        ("-15", False),
        ("-35", False),
        ("+0", False),
        ("+1", False),
        ("+15", False),
        ("+35", False),
        ("(", False),
        (")", False),
        ("-L", False),
        ("-2L", False),
        ("-2l", False),
        ("-H", False),
        ("-3H", False),
        ("-3h", False),
        ("0", False),
        ("1", False),
        ("10", False),
    )
    table = DiceTable()
    for stream_token, answer in TEST_PAIRS:
        assert table.compare("<str-die-size>", stream_token) == answer


def test_compare_is_str_drop_high():
    TEST_PAIRS = (
        # True
        ("-H", True),
        ("-3H", True),
        ("-3h", True),
        # False
        ("d5", False),
        ("dF", False),
        ("d100", False),
        ("-0", False),
        ("-15", False),
        ("-35", False),
        ("+0", False),
        ("+1", False),
        ("+15", False),
        ("+35", False),
        ("(", False),
        (")", False),
        ("-L", False),
        ("-2L", False),
        ("-2l", False),
        ("0", False),
        ("1", False),
        ("10", False),
    )
    table = DiceTable()
    for stream_token, answer in TEST_PAIRS:
        assert table.compare("<str-drop-high>", stream_token) == answer


def test_compare_is_str_drop_low():
    TEST_PAIRS = (
        # True
        ("-L", True),
        ("-2L", True),
        ("-2l", True),
        # False
        ("d5", False),
        ("dF", False),
        ("d100", False),
        ("-0", False),
        ("-15", False),
        ("-35", False),
        ("+0", False),
        ("+1", False),
        ("+15", False),
        ("+35", False),
        ("(", False),
        (")", False),
        ("-H", False),
        ("-3H", False),
        ("-3h", False),
        ("0", False),
        ("1", False),
        ("10", False),
    )
    table = DiceTable()
    for stream_token, answer in TEST_PAIRS:
        assert table.compare("<str-drop-low>", stream_token) == answer


def test_compare_is_die_num():
    TEST_PAIRS = (
        # True
        ("0", True),
        ("1", True),
        ("10", True),
        # False
        ("d5", False),
        ("dF", False),
        ("d100", False),
        ("-0", False),
        ("-15", False),
        ("-35", False),
        ("+0", False),
        ("+1", False),
        ("+15", False),
        ("+35", False),
        ("(", False),
        (")", False),
        ("-L", False),
        ("-2L", False),
        ("-2l", False),
        ("-H", False),
        ("-3H", False),
        ("-3h", False),
    )
    table = DiceTable()
    for stream_token, answer in TEST_PAIRS:
        assert table.compare("<int-die-num>", stream_token) == answer
