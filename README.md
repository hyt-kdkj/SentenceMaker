# 英単語・熟語帳Maker
英単語・熟語を登録することで意味・類義語・例文を生成し、pdf形式の単語帳を作成してくれるツールです。<br>
生成AIにはOpenAIのAPIを使用しています。<br>
## Step 1
OpenAIのAPI_KEYを発行し（URL：[https://platform.openai.com/api-keys]）、取得したAPI_KEYを環境変数に設定する。.bashrcや.zshrcなどに追記しておくと便利かもしれません。
```
<例>
export OPENAI_API_KEY="発行したAPI_KEY"
```

## Step 2
filesフォルダ内にword.txtを作成し、word.txtファイル内に英単語・熟語を登録する。
```
<例>
abrogate
act up
imperative
make a fuss
```

## Step 3
appフォルダ内にあるapp.pyを実行すると、filesフォルダ内にwordbook.pdfという単語帳が作成されます。


## 補足
英単語帳をアルファベット順に並び替えたい場合は、appフォルダ内にあるapp.py内4行目のコメントアウトを解除してください。
```
<例>
#subprocess.run(["python3","json_sort.py"])
↓
subprocess.run(["python3","json_sort.py"])
```
生成AIのモデルの変更を行いたい方は、appフォルダ内にあるsentence_maker.py内11行目部分で希望するモデル名に変更してください。初期設定では"gpt-4o-mini"が設定されています。
```
<例>
MODEL = "gpt-4o-mini"   # 利用可能なモデルに合わせて変更してください
↓
MODEL = "gpt-4o"   # 利用可能なモデルに合わせて変更してください
```

## 注意
OpenAIのAPI_KEYを使用するため、API使用料が発生します。使用料については、OpenAIの公式サイトをご確認ください。<br>




