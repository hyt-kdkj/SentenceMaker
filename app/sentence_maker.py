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
        " word, meanings (Japanese), synonyms (English), sentence1, sentence2, sentence3.\n"
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
