import hashlib
import os

def remove_duplicates(directory):
    # 存储图片hash值的字典
    hashes = {}
    duplicates = []
    
    print(f"正在扫描重复图片: {directory} ...")
    
    file_list = sorted(os.listdir(directory)) # 排序保证删除顺序一致
    
    for filename in file_list:
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue
            
        filepath = os.path.join(directory, filename)
        
        try:
            # 计算文件的MD5哈希
            with open(filepath, 'rb') as f:
                filehash = hashlib.md5(f.read()).hexdigest()
            
            if filehash in hashes:
                duplicates.append(filepath)
                print(f"🗑️ 发现重复: {filename} (与 {hashes[filehash]} 重复)")
                os.remove(filepath) # 自动删除
            else:
                hashes[filehash] = filename
        except Exception as e:
            print(f"Error processing {filename}: {e}")

    print(f"✅ 清理完成! 共删除了 {len(duplicates)} 张重复图片。\n")

if __name__ == "__main__":
    # 这里填你下载图片的路径
    remove_duplicates("./raw_datasets/positive")
    remove_duplicates("./raw_datasets/negative")