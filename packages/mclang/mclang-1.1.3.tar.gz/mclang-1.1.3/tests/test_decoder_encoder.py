import pytest
import mclang


def test_loads_type_and_decoder_errors():
    with pytest.raises(TypeError):
        mclang.loads(123)

    with pytest.raises(mclang.LANGDecoderError):
        mclang.loads("continued line without key\n")


def test_decoder_bytes_and_multiline():
    s = b"a=1\nb=multi\nline\n"
    doc = mclang.loads(s)
    assert doc.tl("a") == "1"
    assert "multi\nline" in doc.tl("b")


def test_langencoder_errors_and_encode_comments():
    with pytest.raises(TypeError):
        mclang.LANGEncoder().encode(object())

    lang = mclang.Lang()
    lang["x"] = "y"
    lang.insert_comment(0, "block")
    out = mclang.dumps(lang)
    assert "##block" in out
