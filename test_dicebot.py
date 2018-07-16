import pytest

import dicebot


def test_to_postfix():
    assert dicebot.to_postfix([]) == []
    assert dicebot.to_postfix(["1"]) == ["1"]
    assert dicebot.to_postfix(["1", "2"]) == ["1", "2"]
    assert dicebot.to_postfix(["1", "+", "2"]) == ["1", "2", "+"]


def test_empty():
    with pytest.raises(TypeError):
        dicebot.roll_inner()


def test_nds():
    result = dicebot.roll_inner("3d1")
    assert result == ([[1, 1, 1]], 3)
    result = dicebot.roll_inner("3D1")
    assert result == ([[1, 1, 1]], 3)


def test_bogus_function():
    with pytest.raises(Exception):
        dicebot.roll_inner("3q1")


def test_0ds():
    result = dicebot.roll_inner("0d1")
    assert result == ([[]], 0)


def test_gen_tokens():
    assert list(dicebot.gen_tokens("")) == []
    assert list(dicebot.gen_tokens("1")) == ["1"]
    assert list(dicebot.gen_tokens("d")) == ["d"]
    assert list(dicebot.gen_tokens("abc")) == ["abc"]
    assert list(dicebot.gen_tokens("7.5")) == ["7.5"]
    assert list(dicebot.gen_tokens("3d6")) == ["3", "d", "6"]
    assert list(dicebot.gen_tokens("3d6 + 5")) == ["3", "d", "6", " ", "+", " ", "5"]
    assert list(dicebot.gen_tokens("18d6*3+5")) == ["18", "d", "6", "*", "3", "+", "5"]


def test_addition():
    result = dicebot.roll_inner("1 + 1")
    assert result[1] == 2
    result = dicebot.roll_inner("1 + 1 + 2")
    assert result[1] == 4


def test_subtraction():
    result = dicebot.roll_inner("1 - 1")
    assert result[1] == 0


def test_multiplication():
    result = dicebot.roll_inner("2 * 3")
    assert result[1] == 6


def test_division():
    result = dicebot.roll_inner("8 / 4")
    assert result[1] == 2
    result = dicebot.roll_inner("10 / 4")
    assert result[1] == 2.5


def test_adding_dice():
    result = dicebot.roll_inner("1d1 + 1d1")
    assert result == ([[1], [1]], 2)


def test_parenthesis():
    result = dicebot.roll_inner("(1 + 2) * 3")
    assert result == ([], 9)


def test_dice_plus_operators():
    result = dicebot.roll_inner("1d1 + 100")
    assert result[1] == 101
    result = dicebot.roll_inner("1d1 - 100")
    assert result[1] == -99
    result = dicebot.roll_inner("1d1 * 100")
    assert result[1] == 100
    result = dicebot.roll_inner("1d1 / 100")
    assert result[1] == 0.01
    result = dicebot.roll_inner("100d1 / 10")
    assert result[1] == 10
    result = dicebot.roll_inner("100d1 / 10")
    assert result[1] == 10


def test_add_missing_numbers():
    assert dicebot.add_missing_numbers(["d"]) == ["1", "d", "6"]
    assert dicebot.add_missing_numbers(["2", "d"]) == ["2", "d", "6"]
    assert dicebot.add_missing_numbers(["d", "20"]) == ["1", "d", "20"]
    assert dicebot.add_missing_numbers(["5", "d", "20"]) == ["5", "d", "20"]
