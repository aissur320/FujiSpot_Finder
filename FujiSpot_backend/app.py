import os
import numpy as np
from flask import Flask, request, jsonify, render_template
from ultralytics import YOLO
from utils import get_image_gps
from sklearn.cluster import DBSCAN
import random

# Flask初期化
app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'weights', 'best.pt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
CONF_THRESHOLD = 0.15

# DBSCAN 
EPS_KM = 0.5  # 探索半径0.5km
MIN_SAMPLES = 3

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
print(f"Loading YOLO: {MODEL_PATH}")
model = YOLO(MODEL_PATH)
print("Loading complete")

# データベース
valid_spots = []

# --- フロントエンドと連携 ---
@app.route('/')
def index():
    return render_template('index.html')

# --- 富士山検出インターフェース ---
@app.route('/detect', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image'}), 400
    
    file = request.files['image']
    save_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(save_path)
    
    # 入力されたGPSデータを取得
    manual_lat = request.form.get('lat')
    manual_lon = request.form.get('lon')
    
    # YOLO推理
    results = model.predict(save_path, conf=CONF_THRESHOLD, save=False)
    
    is_fuji = len(results[0].boxes) > 0
    
    response_data = {'filename': file.filename, 'is_fuji': is_fuji, 'has_gps': False}

    if is_fuji:
        gps = None
        # 入力されたGPSを最優先
        if manual_lat and manual_lon:
            gps = (float(manual_lat), float(manual_lon))
            print(f"Use externally provided coordinates: {gps}")
        # そうでなければ、EXIFを読み込む
        elif not gps:
            gps = get_image_gps(save_path)
            if gps: print(f"Use EXIF coordinates: {gps}")

        if gps:
            response_data['has_gps'] = True
            response_data['location'] = {'lat': gps[0], 'lon': gps[1]}
            
            # データベースに保存
            valid_spots.append({
                'id': len(valid_spots) + 1,
                'lat': gps[0],
                'lon': gps[1],
                'source': 'upload' if not manual_lat else 'flickr_api',
                'filename': file.filename
            })
    
    return jsonify(response_data)

# --- モックデータインターフェース ---
@app.route('/simulate', methods=['POST'])
def simulate_data():
    # 古いデータを削除（ここは任意）
    # global valid_spots
    # valid_spots = []
    
    # ホットスポットをシミュレート
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
            'filename': None
        })
        count += 1
        
    return jsonify({'message': f'{count} mock data points have been generated'})

# --- DBSCANクラスタリングインターフェース ---
@app.route('/clusters', methods=['GET'])
def get_clusters():
    if len(valid_spots) < MIN_SAMPLES:
        return jsonify({'message': 'Insufficient data', 'clusters': []})
    
    # データの準備
    coords = np.array([[spot['lat'], spot['lon']] for spot in valid_spots])
    coords_rad = np.radians(coords)
    
    # パラメータ計算
    kms_per_radian = 6371.0088
    epsilon = EPS_KM / kms_per_radian
    
    # アルゴリズムの実行
    db = DBSCAN(eps=epsilon, min_samples=MIN_SAMPLES, metric='haversine', algorithm='ball_tree')
    db.fit(coords_rad)
    
    cluster_labels = db.labels_
    n_clusters = len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0)
    
    # 結果を整理
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