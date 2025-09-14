import json
import os

# --- ディレクトリ設定 ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files_dir = os.path.join(base_dir, "files")
sentence_json_path = os.path.join(files_dir, "sentences.json")

# JSON読み込み
if os.path.isfile(sentence_json_path):
    try:
        with open(sentence_json_path, "r", encoding="utf-8") as sf:
            sentences = json.load(sf)
        if not isinstance(sentences, list):
            sentneces = []
    except Exception:
        sentences = []
else:
    sentences = []
    

# 単語でソート
sentences.sort(key=lambda x: x.get("word", "").lower())
with open(sentence_json_path, "w", encoding="utf-8") as sf:
    json.dump(sentences, sf, ensure_ascii=False, indent=2)
print(f"Sorted JSON saved to: {sentence_json_path}")