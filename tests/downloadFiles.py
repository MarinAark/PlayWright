import os
import requests
import pandas as pd

# Excel 文件路径
EXCEL_FILE = "./downloads.xlsx"

# 保存目录
SAVE_DIR = "./downloads"
os.makedirs(SAVE_DIR, exist_ok=True)

# 读取 Excel（用 calamine 避免 openpyxl 样式报错）
# 安装：pip install calamine
df = pd.read_excel(EXCEL_FILE, engine="calamine")

def sanitize_filename(name: str) -> str:
    """清理文件名中的非法字符"""
    return "".join(c for c in name if c not in r'\/:*?"<>|')

def download_file(url: str, filename: str):
    filepath = os.path.join(SAVE_DIR, filename)
    if os.path.exists(filepath):
        print(f"已存在，跳过: {filename}")
        return

    print(f"正在下载: {filename} ...")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        print(f"下载完成: {filename}")
    except Exception as e:
        print(f"下载失败 {filename}: {e}")

if __name__ == "__main__":
    for idx, row in df.iterrows():
        url = str(row["文件链接"]).strip()
        name = str(row["文件名称"]).strip()
        status = str(row["清洗状态"]).strip() if pd.notna(row["清洗状态"]) else ""

        # 跳过已清洗
        if status == "已清洗":
            print(f"第{idx+2}行 已清洗，跳过")
            continue

        safe_name = sanitize_filename(name)

        # 如果 Excel 没有扩展名，就从 URL 里取
        if not os.path.splitext(safe_name)[1]:
            ext = os.path.splitext(url)[1]
            safe_name += ext

        # 空状态填充为 "未清洗"
        status_label = status if status else "未清洗"

        # 最终文件名 = 行号_文件名_状态
        final_name = f"{idx+2}_{safe_name}_{status_label}"

        download_file(url, final_name)
