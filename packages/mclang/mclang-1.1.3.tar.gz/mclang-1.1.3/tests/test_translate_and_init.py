import json
import locale
import pytest
import mclang


def test_set_get_language_and_default(monkeypatch):
    setattr(mclang.lang, "__lang__", None)
    monkeypatch.setattr(locale, "getlocale", lambda: ("en_US", "UTF-8"))
    assert mclang.get_language() == "en_US"

    mclang.set_language("fr_FR")
    assert mclang.get_language() == "fr_FR"


def test_translate_language_with_mock(monkeypatch):
    class FakeGT:
        def __init__(self, target=None, **kw):
            self.target = target

        def translate_batch(self, batch):
            return [f"{t}-translated-to-{self.target}" for t in batch]

    monkeypatch.setattr(mclang.lang, "GoogleTranslator", FakeGT)

    lang = mclang.Lang({"k": "hello", "k2": "bye"})
    out = lang.translate_language(target="fr")
    assert out["k"].endswith("-translated-to-fr")


def test_init_with_bad_languages_json(tmp_path):
    d = tmp_path / "texts"
    d.mkdir()
    (d / "languages.json").write_text(json.dumps({"bad": True}))
    with pytest.raises(TypeError):
        mclang.init(str(d))


def test_translate_without_root_raises(monkeypatch):
    monkeypatch.setattr(mclang.lang, "__root__", None)
    with pytest.raises(mclang.lang.LangError):
        mclang.translate("k")
