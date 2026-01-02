"""
Writes and reads a .lang file.
"""

import mclang

test = "§cThis is cool!"
test2 = "§aIt worked!"
block_comment = " Block comment"
inline_comment = "Inline comment"


def test_write_file():
    obj = mclang.Lang()
    obj.insert_comment(0, block_comment)
    obj["test"] = test
    obj["test2"] = test2

    with mclang.open("tests/en_US.lang", "w") as lang:
        lang.update(obj)


def test_read_file():
    with mclang.open("tests/en_US.lang", "r") as lang:
        assert lang.tl("test") == test
        assert lang.tl("test2") == test2
        assert lang.comments[0].text == block_comment


def test_rw_file():
    with mclang.open("tests/en_US.lang", "rw") as lang:
        lang["added"] = "§cUpdated!"


test_write_file()
test_read_file()
test_rw_file()
