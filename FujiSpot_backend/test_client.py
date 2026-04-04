import requests
import os

# 1. サーバーアドレスの設定（ローカル）
url = 'http://127.0.0.1:5000/detect'

# 2. テスト画像のパスを設定
img_path = 'test.jpg' 

if not os.path.exists(img_path):
    print(f"❌ エラー: {img_path}を見つかりません")
    exit()

# 3. POSTリクエストを送信
print(f"📤 {img_path} をサーバーにアップロード中です...")
try:
    with open(img_path, 'rb') as f:
        response = requests.post(url, files={'image': f})

    # 4. 結果の印刷
    print(f"📥 サーバーステータスコード: {response.status_code}")
    if response.status_code == 200:
        print("✅ 取得データ (JSON):")
        print(response.json())
    else:
        print("❌ リクエストが失敗しました:", response.text)

except requests.exceptions.ConnectionError:
    print("❌ サーバーに接続できません。黒いウィンドウ（app.py）が閉じられていないか確認してください。")