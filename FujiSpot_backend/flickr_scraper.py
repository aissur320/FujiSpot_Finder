import flickrapi
import requests
import os
import time
import random

# ================= 配置エリア =================
API_KEY = '**********************'
API_SECRET = '****************'

BACKEND_URL = 'http://127.0.0.1:5000/detect'
TEMP_DIR = './temp_flickr_images'
os.makedirs(TEMP_DIR, exist_ok=True)
# ===========================================

def get_flickr_photos(keyword, max_count=50):
    print(f"\n📡 Flickrで検索: '{keyword}' (目標: {max_count}枚)...")
    try:
        flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')
        photos = flickr.photos.search(
            text=keyword,
            has_geo=1,
            accuracy=11, 
            content_type=1,
            media='photos',
            per_page=max_count,
            # 画質の確保
            extras='geo,url_m,url_l,url_o',
            sort='relevance'
        )
        return photos['photos']['photo']
    except Exception as e:
        print(f"❌ API接続に失敗しました: {e}")
        return []

def process_photo(photo):
    """
    写真の処理
    戻り値: True (ダウンロードを実行したため、休憩が必要)、False (キャッシュを使用したため、休憩は不要)
    """
    # 利用可能な任意のURLを取得
    url = photo.get('url_m') or photo.get('url_l') or photo.get('url_o')
    if not url: return False

    lat = photo['latitude']
    lon = photo['longitude']
    title = photo['title'] if photo['title'] else f"fuji_{photo['id']}"
    
    # ファイル名の整理
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ','-','_')]).strip()
    if len(safe_title) > 30: safe_title = safe_title[:30]
    filename = f"{safe_title}_{photo['id']}.jpg"
    save_path = os.path.join(TEMP_DIR, filename)

    is_new_download = False

    # --- 1. ローカルキャッシュの確認 ---
    if os.path.exists(save_path):
        # ✅ キャッシュあり
        print(f"   🚀 [キャッシュあり] {filename[:15]}... -> バックエンドへ送信")
    else:
        # 📥 新画像をダウンロード
        print(f"   📥 [新画像をダウンロード] {filename[:15]}... (Lat:{lat}, Lon:{lon})")
        try:
            img_data = requests.get(url, timeout=10).content
            with open(save_path, 'wb') as f:
                f.write(img_data)
            is_new_download = True
        except Exception as e:
            print(f"     ❌ ダウンロード失敗: {e}")
            return False

    # --- 2. バックエンドへ送信 ---
    try:
        with open(save_path, 'rb') as f:
            files = {'image': f}
            data = {'lat': lat, 'lon': lon}
            resp = requests.post(BACKEND_URL, files=files, data=data)
            
        if resp.status_code != 200:
            print(f"     ❌ バックエンドエラー: {resp.status_code}")

    except Exception as e:
        print(f"     ❌ バックエンド接続に失敗しました: {e}")

    return is_new_download

def main():
    # キーワードを網羅的にカバー
    keywords = [
        # --- 北侧 ---
        "Lake Kawaguchiko Mt Fuji",   # 河口湖
        "Lake Yamanaka Mt Fuji",      # 山中湖
        "Lake Motosu Mt Fuji",        # 本栖湖
        "Lake Shoji Mt Fuji",         # 精進湖
        "Lake Saiko Mt Fuji",         # 西湖
        
        # --- 有名なランドマーク ---
        "Chureito Pagoda",            # 新倉山浅間公園
        "Oshino Hakkai",              # 忍野八海
        "Lake Tanuki Mt Fuji",        # 田贯湖
        "Shiraito Falls",             # 白糸の滝
        
        # --- 都市視点 ---
        "Fujinomiya Mt Fuji",         # 富士宫市
        "Gotemba Mt Fuji",            # 御殿场
        "Mishima Skywalk"             # 三岛
    ]
    
    # 各単語につき50枚ずつダウンロード
    target_per_keyword = 50 
    
    print(f"🚀 クローリングタスクを開始: {len(keywords)} キーワード x {target_per_keyword} 枚/ワード")
    print("----------------------------------------------------")

    for kw in keywords:
        photos = get_flickr_photos(kw, max_count=target_per_keyword)
        print(f"🔍 キーワード '{kw}' で {len(photos)}　枚見つかった")
        
        for photo in photos:
            did_download = process_photo(photo)
            
            if did_download:
                # ダウンロードした後は休憩し、アカウント停止を防ぐ
                sleep_time = random.uniform(1.5, 3.0)
                print(f"     💤 休憩 {sleep_time:.1f} 秒...")
                time.sleep(sleep_time)
            else:
                # キャッシュヒット
                pass

    print("\nデータのインポートが完了しました")

if __name__ == '__main__':
    main()