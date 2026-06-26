# AI & Notion News Mailer 📬

毎朝、生成AIおよびNotion関連の最新ニュースを自動収集し、重要度の高い5件を厳選・要約して、Gmailで美しくデザインされたHTMLメールを自動送信するシステムです。

## 🌟 主な機能
- **ニュースの自動検索と収集**:
  Notion公式、OpenAI、Google、Microsoftなどの主要公式情報、およびZenn、AGIラボ、ジェネトピ、Yahoo!ニュース等から自動で直近（過去3日間）のニュースを収集。
- **AIによる自動キュレーションと日本語要約**:
  Gemini API (`gemini-2.5-flash` モデル) の構造化出力（Structured Outputs）を利用し、重要度の高い順に5件を厳選、それぞれ分かりやすい3点箇条書きの日本語要約と選定理由を生成。
- **リッチなHTMLメール配信**:
  Notion風のモダンでクリーンなデザインのHTMLメールを自動で生成し、Gmail経由で指定アドレスに配信。
- **自動スケジュール実行**:
  macOS標準の `launchd` を使用して、毎朝（初期設定は 8:00 AM）自動的に実行。

---

## 🛠️ セットアップ手順

### 1. 初期セットアップの実行
ターミナルで本フォルダに移動し、以下のコマンドを実行します。

```bash
chmod +x setup.sh
./setup.sh
```

これにより、Pythonの仮想環境（`.env`）の構築、必要なライブラリのインストール、および環境変数テンプレートの配置が行われます。

### 2. 環境変数の設定
フォルダ内に `.env` ファイルが自動生成されています。エディタで開き、以下の情報を設定してください。

```ini
# Gemini API Key (https://aistudio.google.com/ で無料取得可能)
GEMINI_API_KEY=your_gemini_api_key_here

# 送信元となるGmailアドレス
GMAIL_ADDRESS=your_gmail_address@gmail.com

# Gmailアプリパスワード (※ 通常のログインパスワードではありません。下記参照)
GMAIL_APP_PASSWORD=xxxx_xxxx_xxxx_xxxx

# 受信先アドレス (空欄の場合は送信元アドレスに自身宛てで送信されます)
RECIPIENT_ADDRESS=

# ニュースの遡り日数 (デフォルトは3日間)
SEARCH_LIMIT_DAYS=3
```

#### 🔑 Gmail「アプリパスワード」の取得方法
GmailのSMTPサーバーを利用してプログラムから安全にメールを送信するために、Googleの「アプリパスワード」が必要です。
1. 送信元のGoogleアカウントの **[セキュリティ設定ページ](https://myaccount.google.com/security)** にアクセスします。
2. アカウントで **「2段階認証プロセス」** が有効になっていることを確認します（無効の場合は有効にしてください）。
3. 2段階認証プロセスの設定内、またはページ下部にある **「アプリ パスワード」** をクリックします。
4. アプリ名に適当な名前（例: `AI News Mailer`）を入力し、**「作成」** をクリックします。
5. 画面に表示される **16文字のパスワード**（例: `abcd efgh ijkl mnop`）をコピーし、`.env` の `GMAIL_APP_PASSWORD` にスペースを詰めて貼り付けます。

---

## 🚀 動作確認（手動実行）

環境変数の設定完了後、実際にスクリプトを起動して、メールが正しく送信されるかテストできます。

```bash
# 仮想環境のPythonを使って実行
./.venv/bin/python main.py
```

実行後、`run.log` を確認し、成功メッセージが表示されること、およびGmailにメールが届いていることを確認してください。

---

## 📅 定期実行のスケジュール設定 (macOS)

macOSの機能である `launchd` を利用して、毎日朝8:00にこのスクリプトを自動実行します。

1. 設定ファイル（`.plist`）をLaunchAgentsフォルダにコピーします：
   ```bash
   mkdir -p ~/Library/LaunchAgents
   cp com.user.ainotionmailer.plist ~/Library/LaunchAgents/
   ```

2. サービスを登録して起動します：
   ```bash
   launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.user.ainotionmailer.plist
   launchctl enable gui/$(id -u)/com.user.ainotionmailer
   ```

3. 登録解除（自動実行を止めたい場合）は以下を実行します：
   ```bash
   launchctl bootout gui/$(id -u) ~/Library/LaunchAgents/com.user.ainotionmailer.plist
   rm ~/Library/LaunchAgents/com.user.ainotionmailer.plist
   ```

### 📝 スケジュール時間の変更方法
実行時間を変更したい場合は、`com.user.ainotionmailer.plist` 内の以下の数値を書き換えてから再登録してください。
```xml
<key>Hour</key>
<integer>8</integer>  <!-- 時間 (24時間表記) -->
<key>Minute</key>
<integer>0</integer>  <!-- 分 -->
```

---

## 📂 ファイル構成
- `main.py`: プロセスの全体制御（メインエントリー）
- `searcher.py`: ニュースのWeb検索・RSSパース・重複排除
- `curator.py`: Gemini APIによる重要度評価・5件厳選・要約生成
- `mailer.py`: HTMLメールの作成とGmail SMTP送信
- `config.py`: 環境変数の管理とバリデーション
- `run.sh`: `launchd` 用の起動シェルスクリプト
- `com.user.ainotionmailer.plist`: macOS用定期実行構成シート
- `setup.sh`: 初期構築用セットアップスクリプト
- `run.log`: 実行履歴ログファイル
