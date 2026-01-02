"""
Converts a .lang string to a Lang.
"""

import mclang


def test_loads():
    lang = """
    # Single comment
    ## Block comment
    test=This is cool!
    test2=It worked!    ## Inline comment
    key=va
    lue
    """

    doc = mclang.loads(lang)

    assert doc.tl("test") == "This is cool!"
    assert doc.tl("key") == "va\nlue"
    assert doc.comments[0].text == " Single comment"
    assert doc.comments[1].text == " Block comment"
