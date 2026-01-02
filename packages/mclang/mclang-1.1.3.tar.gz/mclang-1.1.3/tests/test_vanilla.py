import requests
import mclang


def fetch_text(filename: str) -> requests.Response:
    url = f"https://raw.githubusercontent.com/Mojang/bedrock-samples/refs/heads/main/resource_pack/texts/{filename}"
    res = requests.get(url)
    res.raise_for_status()
    return res


def test_vanilla():
    for lang in fetch_text("languages.json").json():
        print(lang)
        res = fetch_text(f"{lang}.lang")
        mclang.loads(res.text)
