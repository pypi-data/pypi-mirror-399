import pytest
import mclang


def test_format_edge_cases():
    lang = mclang.Lang()
    assert lang.format("a %1 b %2 c", "X") == "a X b  c"
    assert lang.format("%s %s", "A") == "A A"
    assert lang.format("hello", "x") == "hello"


def test_comments_setter_and_operations():
    lang = mclang.Lang()
    with pytest.raises(TypeError):
        lang.comments = "not a list"
    lang.insert_comment(0, "c1")
    lang.insert_comment(1, "c2", inline=True)
    assert len(lang.comments) == 2
    lang.remove_comment(5)
    lang.remove_comment(1)
    assert len(lang.comments) == 1
    lang.clear_comments()
    assert lang.comments == []


def test_copy_preserves_comments():
    lang = mclang.Lang({"a": "1"})
    lang.insert_comment(0, "c")
    c = lang.copy()
    assert isinstance(c, mclang.Lang)
    assert c.comments[0].text == "c"


def test_update_merges_comments():
    a = mclang.Lang({"a": "1"})
    b = mclang.Lang({"b": "2"})
    b.insert_comment(0, "c")
    a.update(b)
    assert len(a.comments) == 1
