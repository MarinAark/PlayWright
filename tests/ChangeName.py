"""
文件重命名工具
用于批量重命名下载文件，整理文件名格式
"""
import os
import re
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileRenamer:
    """文件重命名工具类"""
    
    def __init__(self, folder_path: str):
        self.folder_path = Path(folder_path)
        if not self.folder_path.exists():
            raise ValueError(f"文件夹不存在: {folder_path}")
        
        # 匹配状态后缀（任意中文状态 + 可选数字份）
        self.status_pattern = re.compile(r'_(未清洗|已清洗(，且属于\d+份)?)$')

for filename in os.listdir(folder_path):
    old_path = os.path.join(folder_path, filename)

    if os.path.isdir(old_path):
        continue

    # 尝试从右边找到扩展名
    dot_pos = filename.rfind('.')
    if dot_pos == -1:
        print(f"无法识别扩展名: {filename}, 跳过")
        continue

    name = filename[:dot_pos]
    ext = filename[dot_pos:]

    # 状态后缀可能在扩展名后或扩展名前
    # 先检查扩展名后是否有下划线 + 状态
    status_match = re.search(r'_.*$', ext)
    if status_match:
        status = status_match.group(0)
        ext = ext.replace(status, '')
    else:
        status_match = status_pattern.search(name)
        status = status_match.group(0) if status_match else ''

        if status:
            name = name[:status_match.start()]

    # 重新组合文件名
    new_name = f"{name}{status}{ext}"
    new_path = os.path.join(folder_path, new_name)

    if old_path != new_path:
        os.rename(old_path, new_path)
        print(f"{filename} -> {new_name}")
    else:
        print(f"{filename} 保持不变")
