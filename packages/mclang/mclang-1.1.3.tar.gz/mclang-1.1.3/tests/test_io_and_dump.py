from io import StringIO
import mclang


def test_dump_dumps_save_open(tmp_path):
    fp = tmp_path / "t.lang"
    lang = mclang.Lang()
    lang["a"] = "1"
    s = mclang.dumps(lang)
    buf = StringIO()
    mclang.dump(lang, buf)
    assert s == buf.getvalue()

    lang.save(str(fp))
    r = mclang.open(str(fp), "r")
    assert isinstance(r, mclang.Lang)
