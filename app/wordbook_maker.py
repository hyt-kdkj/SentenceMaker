import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.units import cm
import os

# --- ディレクトリ設定 ---
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
files_dir = os.path.join(base_dir, "files")
sentence_json_path = os.path.join(files_dir, "sentences.json")

# --- JSON読み込み ---
with open(sentence_json_path, "r", encoding="utf-8") as f:
    words = json.load(f)

# --- 日本語フォント登録（システム標準CIDフォント使用） ---
pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W5"))

# --- PDF作成 ---
pdf_file = os.path.join(files_dir, "wordbook.pdf")
c = canvas.Canvas(pdf_file, pagesize=A4)
width, height = A4

y_position = height - 2*cm  # 上からの開始位置

for entry in words:
    word = entry["word"]
    meanings = entry["meanings"]
    synonyms = entry.get("synonyms", [])
    sentences = [entry["sentence1"], entry["sentence2"], entry["sentence3"]]

    # 単語
    c.setFont("HeiseiKakuGo-W5", 10)
    c.drawString(2*cm, y_position, f"・ {word}")
    y_position -= 0.5*cm

    # 意味
    c.setFont("HeiseiKakuGo-W5", 10)
    c.drawString(2*cm, y_position, f"意味: {meanings}")
    y_position -= 0.5*cm
    
    # 類義語
    if synonyms:
        c.setFont("HeiseiKakuGo-W5", 10)
        c.drawString(2*cm, y_position, f"類義語: {synonyms}")
        y_position -= 0.5*cm

    # 例文
    c.setFont("HeiseiKakuGo-W5", 9)
    for i, sentence in enumerate(sentences, 1):
        c.drawString(2*cm, y_position, f"例文{i}: {sentence}")
        y_position -= 0.5*cm

    y_position -= 0.4*cm  # 単語ごとの余白

    # ページ下まで行ったら改ページ
    if y_position < 3*cm:
        c.showPage()
        y_position = height - 2*cm

# PDF保存
c.save()
print(f"{pdf_file} が作成されました。")
