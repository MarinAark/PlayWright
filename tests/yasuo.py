from PIL import Image
import os

def compress_image(input_path, output_path, target_size=4.9*1024*1024):
    """
    将图片压缩到 target_size (默认3MB) 以下
    """
    img = Image.open(input_path)

    # 转换为 RGB，避免部分 PNG 保存时报错
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # 初始质量
    quality = 95

    # 先保存一次
    img.save(output_path, format="JPEG", quality=quality)
    while os.path.getsize(output_path) > target_size and quality > 10:
        quality -= 5
        img.save(output_path, format="JPEG", quality=quality)

    final_size = os.path.getsize(output_path) / 1024 / 1024
    print(f"压缩完成，最终大小: {final_size:.2f} MB (quality={quality})")

if __name__ == "__main__":
    input_file = "11.jpg"   # 原图路径
    output_file = "111.jpg" # 压缩后保存路径
    compress_image(input_file, output_file)
