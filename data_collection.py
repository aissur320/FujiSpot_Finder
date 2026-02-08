import os
from icrawler.builtin import BingImageCrawler

def download_images(keyword, save_dir, max_num=100):
    """
    使用Bing图片搜索下载图片
    """
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    print(f"🚀 开始下载: {keyword} -> {save_dir}")
    
    crawler = BingImageCrawler(storage={'root_dir': save_dir})
    
    # filters参数可以过滤图片类型，这里我们尽量要照片(photo)
    crawler.crawl(keyword=keyword, max_num=max_num, filters=None)
    
    print(f"✅ 完成: {keyword}\n")

def main():
    # 根目录
    base_dir = "./raw_datasets"
    
    # 1. 正样本 (Positive Samples): 富士山的多样化场景
    # 我们不仅要“完美的富士山”，还要各种角度、遮挡、天气的
    # 替换之前的 positive_keywords
    positive_keywords = [
        "Mt Fuji", 
        "Mount Fuji sunny", 
        "Mount Fuji cloudy", 
        "Mount Fuji from city",   # 城市背景
        "Mount Fuji aerial view", # 航拍
        "富士山", 
        "富士山 遠景",
        "富士山 街並み"
        # 1. 富士五湖视角 (经典倒影和湖景)
        "Lake Kawaguchiko Mt Fuji",  # 河口湖 (最常见，可能有重叠，但量大)
        "Lake Yamanaka Mt Fuji",     # 山中湖
        "Lake Motosu Mt Fuji",       # 本栖湖 (千元纸币背后的视角)
        "Lake Tanuki Mt Fuji",       # 田贯湖
        
        # 2. 著名地标视角 (具有独特的前景特征)
        "Chureito Pagoda Mt Fuji",   # 忠灵塔 (非常重要！红塔+富士山)
        "Oshino Hakkai Mt Fuji",     # 忍野八海 (村落+富士山)
        "Shiraito Falls Mt Fuji",    # 白丝瀑布
        "Miho no Matsubara Mt Fuji", # 三保松原 (海边+松树)
        
        # 3. 城市与交通视角 (系统实际会遇到的数据)
        "Shinkansen Mt Fuji",        # 新干线车窗视角
        "Gotemba Outlets Mt Fuji",   # 御殿场奥特莱斯
        "Fuji City factory view",    # 富士市工厂夜景 (赛博朋克风)
        "Enoshima Mt Fuji",          # 江之岛 (海景远眺)
        "Tokyo Tower Mt Fuji",       # 东京远眺 (极小目标检测)
        
        # 4. 特殊天象 (增加颜色鲁棒性)
        "Red Fuji",                  # 赤富士 (夏末早晨，红色山体)
        "Diamond Fuji",              # 钻石富士 (太阳在山顶)
        "Pearl Fuji"                 # 珍珠富士 (月亮在山顶)
    ]
    
    for kw in positive_keywords:
        # 全部存入 positive 文件夹
        download_images(kw, os.path.join(base_dir, "positive"), max_num=200)

    # 2. 负样本 (Negative Samples): 长得像富士山的山 (Hard Negatives)
    # 这些图片在标注时不要画框，或者专门设为"negative"类（通常YOLOv8建议直接留空作为背景）
    negative_keywords = [
        "Mount Yotei",      # 羊蹄山 (北海道的富士山)
        "Mount Kaimon",     # 开闻岳 (萨摩富士)
        "Mount Daisen",     # 大山 (伯耆富士)
        "Mount Nantai",     # 男体山
        "Stratovolcano",    # 成层火山 (通用的火山锥形状)
        "Blue sky with clouds", # 容易被误检的云
        "City skyline no mountain" # 纯城市背景
        "Mount Taranaki",      # 新西兰的塔拉纳基山 (最像富士山的山，一定要有！)
        "Mount Mayon",         # 菲律宾的马荣火山 (完美的圆锥体)
        "Mount Rainier",       # 美国的雷尼尔山 (也是巨大的雪山，但山体更宽大)
        "Mount Osorno",        # 智利的奥索尔诺火山
        "Mount Kronotsky",     # 俄罗斯的克罗诺基火山
        "Cotopaxi volcano"     # 厄瓜多尔的科托帕希火山
        "Mount Iwate",         # 岩手山 (南部富士，形状略有不同但很像)
        "Mount Iwaki",         # 岩木山 (津轻富士)
        "Mount Chokai",        # 鸟海山 (出羽富士)
        "Mount Rishiri",       # 利尻山 (利尻富士，在海上)
        "Mount Nantai"         # 男体山 (日光地区的圆锥形山)
        "Swiss Alps peaks",    # 瑞士阿尔卑斯山 (连绵的尖峰，用来教模型“连绵山脉”不是“独立峰”)
        "Rocky Mountains",     # 落基山脉 (石头质感更多)
        "Pyramids of Giza",    # 金字塔 (纯粹的三角形几何体)
        "White teepee tent",   # 白色圆锥形帐篷 (近景误检高发区)
        "Snowy roof triangular" #同样是白色三角形的屋顶
    ]
    
    for kw in negative_keywords:
        # 全部存入 negative 文件夹
        download_images(kw, os.path.join(base_dir, "negative"), max_num=100)

if __name__ == "__main__":
    main()