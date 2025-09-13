import os
import json
import sys
import time
from openai import OpenAI


client = OpenAI()

# === 設定 ===
MODEL = "gpt-4o-mini"   # 利用可能なモデルに合わせて変更してください
TEMPERATURE = 0.2
MAX_TOKENS = 300

def call_openai_chat(prompt):
    """
    OpenAI ChatCompletion を呼ぶ簡易ラッパー。
    openai パッケージがないか API キーが無い場合は None を返す。
    """

    try:
        resp = client.chat.completions.create(model=MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that returns ONLY valid JSON objects (no extra text)."},
            {"role": "user", "content": prompt}
        ],
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS)
        # ChatCompletion のレスポンスからテキストを取り出す
        text = resp.choices[0].message.content
        return text
    except Exception as e:
        print(f"OpenAI API error: {e}", file=sys.stderr)
        return None

def build_prompt(word):
    # JSON出力と各フィールドの要件のみを簡潔に指示
    return (
        f"Word: {word}\n"
        "Return ONLY one JSON object with these string fields:"
        " word, meanings (Japanese), synonyms (English - comma-separated single string), sentence1, sentence2, sentence3.\n"
        "For 'synonyms' return a comma-separated string (no arrays).\n"
        "Use natural idiomatic English for example sentences (business/daily TOEIC contexts).\n"
        "Do NOT add any extra text, explanation, or markdown."
    )


def ensure_valid_json(text):
    """
    受け取ったテキストを JSON に変換して検証する試み。
    モデルが余計なテキストを付けてしまった場合でも
    最初に見つかった JSON オブジェクト部分を取り出す処理を行う。
    """
    # まず直接パースを試す
    try:
        obj = json.loads(text)
        return obj
    except Exception:
        pass

    # 簡易的に最初の "{" から最後の "}" を抜き取りパースを試みる
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start:end+1]
        try:
            obj = json.loads(candidate)
            return obj
        except Exception:
            pass

    return None

def normalize_synonyms_field(obj, max_items=5):
    """
    synonyms フィールドを安定化して文字列にする。
    - obj が dict でなければそのまま返す
    - synonyms が list/tuple の場合は英単語らしい部分を抽出してカンマ区切りにする
    - synonyms が文字列でカンマやセミコロンで区切られている場合は整形して返す
    - max_items は保持する最大語数（余分は切る）
    """
    if not isinstance(obj, dict):
        return obj

    syn = obj.get("synonyms") or obj.get("synonym")
    if syn is None:
        # 何もない場合は空文字列をセット
        obj["synonyms"] = ""
        return obj

    items = []
    # リストやタプルなら直接各要素を文字列化
    if isinstance(syn, (list, tuple)):
        for v in syn:
            if isinstance(v, str):
                items.extend([s.strip() for s in v.replace(';', ',').split(',') if s.strip()])
            else:
                # dict などが混ざる場合は文字列化して追加
                try:
                    items.append(json.dumps(v, ensure_ascii=False))
                except Exception:
                    items.append(str(v))

    elif isinstance(syn, str):
        # 文字列ならカンマやセミコロン、改行で分割
        parts = [p.strip() for p in syn.replace(';', ',').replace('\n', ',').split(',')]
        items = [p for p in parts if p]

    else:
        # その他の型は文字列化して1要素に
        items = [str(syn)]

    # 英単語らしいトークンのみを残す（簡易フィルタ）
    cleaned = []
    for tok in items:
        # 括弧や引用を削除
        t = tok.strip().strip('"\'')
        # 簡易的に英文字が含まれるものを優先
        if any(c.isalpha() for c in t):
            cleaned.append(t)
        else:
            # 英文字がない場合でも短い説明文などはそのまま候補に入れる
            cleaned.append(t)

    # 重複を取り除き、最大数に切る
    seen = []
    for c in cleaned:
        if c not in seen:
            seen.append(c)
        if len(seen) >= max_items:
            break

    obj["synonyms"] = ", ".join(seen)
    return obj

def normalize_fields_to_strings(obj):
    """
    トップレベルのすべてのフィールドを文字列に変換する簡易関数。
    - list/tuple はカンマ区切りで結合
    - dict や複雑な要素は JSON 表現で文字列化
    - None は空文字列に変換
    """
    if not isinstance(obj, dict):
        return obj

    out = {}
    for k, v in obj.items():
        if v is None:
            out[k] = ""
        elif isinstance(v, (list, tuple)):
            parts = []
            for item in v:
                if isinstance(item, (dict, list, tuple)):
                    try:
                        parts.append(json.dumps(item, ensure_ascii=False))
                    except Exception:
                        parts.append(str(item))
                else:
                    parts.append(str(item))
            out[k] = ", ".join(parts)
        else:
            out[k] = str(v)

    return out

def main():

    # words.txtのパス
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    files_dir = os.path.join(base_dir, "files")
    words_path = os.path.join(files_dir, "words.txt")
    sentence_json_path = os.path.join(files_dir, "sentences.json")

    # words.txtから単語/熟語を取得
    if not os.path.isfile(words_path):
        print(f"words.txt not found: {words_path}", file=sys.stderr)
        return
    with open(words_path, "r", encoding="utf-8") as wf:
        words = [line.strip() for line in wf if line.strip()]
    words_set = set(words)
    if not words:
        print("words.txt is empty.", file=sys.stderr)
        return

    # sentence.jsonの既存データをロード（なければ空リスト）
    if os.path.isfile(sentence_json_path):
        try:
            with open(sentence_json_path, "r", encoding="utf-8") as sf:
                sentences = json.load(sf)
            if not isinstance(sentences, list):
                sentences = []
        except Exception:
            sentences = []
    else:
        sentences = []

    # 各単語/熟語についてAIに投げて結果をsentence.jsonに追加
    for word in words:
        print(f"Processing: {word}")
        prompt = build_prompt(word)
        response = call_openai_chat(prompt)
        if response:
            obj = ensure_valid_json(response)
            if obj is None:
                print(f"Warning: API returned non-JSON or malformed JSON for '{word}'. Fallback parsing.", file=sys.stderr)
            else:
                # synonyms フィールドを安定化
                obj = normalize_synonyms_field(obj)
                # 他のフィールドはトップレベル文字列化（既存 safeguard があればそちらを使う）
                try:
                    # もし既に normalize_fields_to_strings があれば使う
                    obj = normalize_fields_to_strings(obj)
                except NameError:
                    pass
                sentences.append(obj)
                words_set.discard(word)
        else:
            print(f"OpenAI API not available for '{word}' — using fallback.", file=sys.stderr)

        # 0.5秒待機（API制限対策、必要に応じて調整）
        time.sleep(0.5)

    # sentence.jsonに保存
    try:
        with open(sentence_json_path, "w", encoding="utf-8") as sf:
            json.dump(sentences, sf, ensure_ascii=False, indent=2)
        print(f"Saved all results to {sentence_json_path}")
    except Exception as e:
        print(f"Could not save sentence.json: {e}", file=sys.stderr)
    
    # 処理できなかった単語/熟語はwords.txtに再保存
    try:
        with open(words_path, "w", encoding="utf-8") as wf:
            for w in words_set:
                wf.write(w + "\n")
        print(f"Updated words.txt with unprocessed words only.")
    except Exception as e:
        print(f"Could not update words.txt: {e}", file=sys.stderr)
            
if __name__ == "__main__":
    main()
