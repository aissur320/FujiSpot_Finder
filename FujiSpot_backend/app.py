import os
import numpy as np
from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
from utils import get_image_gps
from sklearn.cluster import DBSCAN

app = Flask(__name__)

# ================= 配置区域 =================
# 建议使用相对路径，这样无论你在哪里运行都不会报错
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'weights', 'best.pt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
CONF_THRESHOLD = 0.15

# DBSCAN 参数
EPS_KM = 0.5  # 半径 500米
MIN_SAMPLES = 3

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"正在加载 YOLO 模型: {MODEL_PATH}")
model = YOLO(MODEL_PATH)
print("模型加载完成！")

# 内存数据库
valid_spots = []

# --- 1. 核心修复：加载前端页面 ---
@app.route('/')
def index():
    # Flask 会自动去 'templates' 文件夹找 index.html
    return render_template('index.html')

# --- 2. 图片检测接口 (含 Flickr 支持) ---
@app.route('/detect', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    
    file = request.files['image']
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    
    # 获取手动传入的 GPS (来自 Flickr 爬虫)
    manual_lat = request.form.get('lat')
    manual_lon = request.form.get('lon')
    
    # YOLO 推理
    results = model.predict(save_path, conf=CONF_THRESHOLD, save=False)
    
    is_fuji = len(results[0].boxes) > 0
    
    response_data = {'filename': file.filename, 'is_fuji': is_fuji, 'has_gps': False}

    if is_fuji:
        gps = None
        # 优先使用手动传入的 GPS
        if manual_lat and manual_lon:
            gps = (float(manual_lat), float(manual_lon))
            print(f"📍 使用外部传入坐标: {gps}")
        # 否则尝试读取 EXIF
        elif not gps:
            gps = get_image_gps(save_path)
            if gps: print(f"📍 使用 EXIF 坐标: {gps}")

        if gps:
            response_data['has_gps'] = True
            response_data['location'] = {'lat': gps[0], 'lon': gps[1]}
            
            # 存入数据库 (包含 filename 用于前端显示)
            valid_spots.append({
                'id': len(valid_spots) + 1,
                'lat': gps[0],
                'lon': gps[1],
                'source': 'upload' if not manual_lat else 'flickr_api',
                'filename': file.filename
            })
    
    return jsonify(response_data)

# --- 3. 模拟数据接口 ---
@app.route('/simulate', methods=['POST'])
def simulate_data():
    import random
    # 清空旧数据 (可选)
    # global valid_spots
    # valid_spots = []
    
    # 模拟两个热点: 河口湖大桥, 忠灵塔
    centers = [(35.504, 138.759), (35.500, 138.801)]
    
    count = 0
    for _ in range(50):
        center = random.choice(centers)
        lat = center[0] + random.uniform(-0.005, 0.005)
        lon = center[1] + random.uniform(-0.005, 0.005)
        
        valid_spots.append({
            'id': len(valid_spots) + 1,
            'lat': lat,
            'lon': lon,
            'source': 'simulation',
            'filename': None # 模拟数据没有图片
        })
        count += 1
        
    return jsonify({'message': f'已生成 {count} 个模拟数据'})

# --- 4. DBSCAN 聚类接口 ---
@app.route('/clusters', methods=['GET'])
def get_clusters():
    if len(valid_spots) < MIN_SAMPLES:
        return jsonify({'message': '数据不足', 'clusters': []})
    
    # 准备数据
    coords = np.array([[spot['lat'], spot['lon']] for spot in valid_spots])
    coords_rad = np.radians(coords)
    
    # 计算参数
    kms_per_radian = 6371.0088
    epsilon = EPS_KM / kms_per_radian
    
    # 运行算法
    db = DBSCAN(eps=epsilon, min_samples=MIN_SAMPLES, metric='haversine', algorithm='ball_tree')
    db.fit(coords_rad)
    
    cluster_labels = db.labels_
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    
    # 整理结果
    results = []
    for i, spot in enumerate(valid_spots):
        spot_info = spot.copy()
        spot_info['cluster_id'] = int(cluster_labels[i])
        results.append(spot_info)
        
    return jsonify({
        'total_spots': len(valid_spots),
        'n_clusters_found': n_clusters,
        'data': results
    })

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)