# flickr_scraper.py (安全版)

import flickrapi
import requests
import os
import time
import random

# ================= 最终配置区域 =================
# 🔴 请再次确认 Key 是否正确
API_KEY = '**********************'
API_SECRET = '****************'

BACKEND_URL = 'http://127.0.0.1:5000/detect'
TEMP_DIR = './temp_flickr_images'
os.makedirs(TEMP_DIR, exist_ok=True)
# ===========================================

def get_flickr_photos(keyword, max_count=50):
    print(f"\n📡 连接 Flickr 搜索: '{keyword}' (目标: {max_count}张)...")
    try:
        flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')
        photos = flickr.photos.search(
            text=keyword,
            has_geo=1,
            accuracy=11, 
            content_type=1,
            media='photos',
            per_page=max_count,
            # 请求原图(url_o)和中大图，保证画质
            extras='geo,url_m,url_l,url_o',
            sort='relevance' # 或者 'interestingness-desc'
        )
        return photos['photos']['photo']
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return []

def process_photo(photo):
    """
    处理单张照片
    返回: True (进行了下载，需要休息), False (使用了缓存，不需要休息)
    """
    # 尝试获取任意可用的 URL
    url = photo.get('url_m') or photo.get('url_l') or photo.get('url_o')
    if not url: return False

    lat = photo['latitude']
    lon = photo['longitude']
    title = photo['title'] if photo['title'] else f"fuji_{photo['id']}"
    
    # 清理文件名
    safe_title = "".join([c for c in title if c.isalnum() or c in (' ','-','_')]).strip()
    if len(safe_title) > 30: safe_title = safe_title[:30]
    filename = f"{safe_title}_{photo['id']}.jpg"
    save_path = os.path.join(TEMP_DIR, filename)

    is_new_download = False

    # --- 1. 检查本地缓存 ---
    if os.path.exists(save_path):
        # ✅ 命中缓存
        print(f"   🚀 [缓存命中] {filename[:15]}... -> 发送后端")
    else:
        # 📥 下载新图
        print(f"   📥 [下载新图] {filename[:15]}... (Lat:{lat}, Lon:{lon})")
        try:
            img_data = requests.get(url, timeout=10).content
            with open(save_path, 'wb') as f:
                f.write(img_data)
            is_new_download = True
        except Exception as e:
            print(f"     ❌ 下载失败: {e}")
            return False

    # --- 2. 发送给后端 ---
    try:
        with open(save_path, 'rb') as f:
            files = {'image': f}
            data = {'lat': lat, 'lon': lon}
            resp = requests.post(BACKEND_URL, files=files, data=data)
            
        if resp.status_code != 200:
            print(f"     ❌ 后端报错: {resp.status_code}")

    except Exception as e:
        print(f"     ❌ 后端连接失败: {e}")

    return is_new_download

def main():
    # 全方位覆盖关键词
    keywords = [
        # --- 北侧 (经典湖景) ---
        "Lake Kawaguchiko Mt Fuji",   # 河口湖 (量大)
        "Lake Yamanaka Mt Fuji",      # 山中湖 (东侧大湖，可以看到很大的富士山)
        "Lake Motosu Mt Fuji",        # 本栖湖 (1000日元纸币背后的风景)
        "Lake Shoji Mt Fuji",         # 精进湖 (较小，但安静)
        "Lake Saiko Mt Fuji",         # 西湖
        
        # --- 著名地标 ---
        "Chureito Pagoda",            # 新仓山浅间公园 (忠灵塔 - 必杀机位！)
        "Oshino Hakkai",              # 忍野八海 (著名的涌泉群)
        "Lake Tanuki Mt Fuji",        # 田贯湖 (西侧，非常有名的“钻石富士”倒影点)
        "Shiraito Falls",             # 白丝瀑布 (瀑布+富士山)
        
        # --- 城市视角 ---
        "Fujinomiya Mt Fuji",         # 富士宫市 (南侧，巨大而震撼的山体)
        "Gotemba Mt Fuji",            # 御殿场 (东南侧，奥特莱斯附近)
        "Mishima Skywalk"             # 三岛 (远眺)
    ]
    
    # 🔥 最终设定: 每个词抓 50 张
    target_per_keyword = 50 
    
    print(f"🚀 开始最终爬取任务: {len(keywords)} 个关键词 x {target_per_keyword} 张/词")
    print("----------------------------------------------------")

    for kw in keywords:
        photos = get_flickr_photos(kw, max_count=target_per_keyword)
        print(f"🔍 关键词 '{kw}' 找到 {len(photos)} 张图片...")
        
        for photo in photos:
            did_download = process_photo(photo)
            
            if did_download:
                # 新图下载后休息，防止封号
                sleep_time = random.uniform(1.5, 3.0)
                print(f"     💤 休息 {sleep_time:.1f} 秒...")
                time.sleep(sleep_time)
            else:
                # 缓存命中，极速处理
                pass

    print("\n🎉🎉🎉 最终数据导入完成！请去前端见证奇迹时刻！ 🎉🎉🎉")

if __name__ == '__main__':
    main()