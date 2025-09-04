import os
import re

# 替换成你的文件夹路径
folder_path = r"/Users/maiqi/PycharmProjects/play_wright/tests/downloads"

# 支持的文件类型
extensions = ['.pptx', '.pdf']

for filename in os.listdir(folder_path):
    for ext in extensions:
        if ext in filename and not filename.endswith(ext):
            # 找到扩展名位置并移动到末尾
            parts = filename.rsplit(ext, 1)
            new_name = f"{parts[0]}{parts[1]}{ext}"
            old_path = os.path.join(folder_path, filename)
            new_path = os.path.join(folder_path, new_name)
            os.rename(old_path, new_path)
            print(f"{filename} => {new_name}")
