# 英単語・熟語帳Maker
登録した英単語・熟語の意味・類義語・例文を生成し、pdf形式の単語帳を作成してくれる。

## Step 1
OpenAIのAPI_KEYを発行し（URL：[https://platform.openai.com/api-keys]）、取得したAPI_KEYを環境変数に設定する。
```
<例>
export OPENAI_API_KEY="発行したAPI_KEY"
```

## Step 2
filesフォルダ内にword.txtを作成し、ファイル内に英単語・熟語を登録する。
```
<例>
abrogate
act up
imperative
make a fuss
```

## Step 3
appフォルダ内にあるapp.pyを実行すると、filesフォルダ内にwordbook.pdfという単語帳が作成される。



