import requests
import os

# 1. 设定服务器地址 (本机)
url = 'http://127.0.0.1:5000/detect'

# 2. 设定测试图片路径 (确保你的文件夹里有这张图！)
img_path = 'test.jpg' 

if not os.path.exists(img_path):
    print(f"❌ 错误: 找不到 {img_path}，请找一张图片放进来并改名。")
    exit()

# 3. 发送 POST 请求
print(f"📤 正在上传 {img_path} 到服务器...")
try:
    with open(img_path, 'rb') as f:
        # 'image' 对应 app.py 里 request.files['image'] 的名字
        response = requests.post(url, files={'image': f})

    # 4. 打印结果
    print(f"📥 服务器状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ 返回数据 (JSON):")
        print(response.json())
    else:
        print("❌ 请求失败:", response.text)

except requests.exceptions.ConnectionError:
    print("❌ 无法连接服务器。请检查 app.py 那个黑色窗口是不是被关掉了？")