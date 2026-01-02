"""
Converts a dict to a .lang string.
"""

import mclang


def test_dumps_object():
    obj = {
        "test": "This is cool!",
        "test2": "It worked!",
        "newline": "va\nlue",
    }

    mclang.dumps(obj)


def test_dumps_lang():
    obj = mclang.Lang()
    obj.insert_comment(0, "Block comment")
    obj["test"] = "This is cool!"
    obj["test2"] = "It worked!"
    obj["newline"] = "va\nlue"

    mclang.dumps(obj)
