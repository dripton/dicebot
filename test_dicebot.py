import pytest

from dicebot import roll_inner

def test_empty():
    with pytest.raises(TypeError):
        roll_inner()

def test_nds():
    result = roll_inner("3d1")
    assert result == "1 + 1 + 1 = 3"

def test_0ds():
    result = roll_inner("0d1")
    assert result == ""
