"""
图片压缩工具
支持批量压缩图片到指定大小
"""
import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from PIL import Image

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ImageCompressor:
    """图片压缩工具类"""
    
    SUPPORTED_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    
    def __init__(self):
        self.processed_count = 0
        self.failed_count = 0
    
    def get_file_size_mb(self, file_path: Path) -> float:
        """获取文件大小（MB）"""
        return file_path.stat().st_size / (1024 * 1024)
    
    def is_supported_format(self, file_path: Path) -> bool:
        """检查是否为支持的图片格式"""
        return file_path.suffix.lower() in self.SUPPORTED_FORMATS
    
    def compress_single_image(
        self, 
        input_path: Path, 
        output_path: Optional[Path] = None,
        target_size_mb: float = 4.9,
        min_quality: int = 10,
        quality_step: int = 5
    ) -> bool:
        """
        压缩单个图片
        
        Args:
            input_path: 输入图片路径
            output_path: 输出图片路径（为None时覆盖原文件）
            target_size_mb: 目标文件大小（MB）
            min_quality: 最小质量（1-100）
            quality_step: 质量递减步长
            
        Returns:
            bool: 是否成功
        """
        if not input_path.exists():
            logger.error(f"文件不存在: {input_path}")
            return False
        
        if not self.is_supported_format(input_path):
            logger.warning(f"不支持的图片格式: {input_path}")
            return False
        
        if output_path is None:
            output_path = input_path
        
        try:
            # 检查原文件大小
            original_size_mb = self.get_file_size_mb(input_path)
            target_size_bytes = target_size_mb * 1024 * 1024
            
            if original_size_mb <= target_size_mb:
                logger.info(f"文件已满足大小要求: {input_path.name} ({original_size_mb:.2f}MB)")
                if input_path != output_path:
                    # 如果输出路径不同，复制文件
                    import shutil
                    shutil.copy2(input_path, output_path)
                return True
            
            # 打开并转换图片
            with Image.open(input_path) as img:
                # 转换为 RGB，避免部分 PNG 保存时报错
                if img.mode in ("RGBA", "P"):
                    img = img.convert("RGB")
                
                # 初始质量
                quality = 95
                
                # 尝试不同质量设置
                while quality >= min_quality:
                    # 保存到临时路径
                    temp_path = output_path.with_suffix('.tmp.jpg')
                    img.save(temp_path, format="JPEG", quality=quality, optimize=True)
                    
                    # 检查文件大小
                    if temp_path.stat().st_size <= target_size_bytes:
                        # 达到目标大小，移动到最终位置
                        temp_path.rename(output_path)
                        final_size_mb = self.get_file_size_mb(output_path)
                        
                        logger.info(
                            f"压缩完成: {input_path.name} "
                            f"({original_size_mb:.2f}MB -> {final_size_mb:.2f}MB, "
                            f"质量={quality})"
                        )
                        self.processed_count += 1
                        return True
                    
                    # 删除临时文件，降低质量重试
                    temp_path.unlink()
                    quality -= quality_step
                
                # 如果最低质量仍然过大，使用最低质量
                img.save(output_path, format="JPEG", quality=min_quality, optimize=True)
                final_size_mb = self.get_file_size_mb(output_path)
                
                logger.warning(
                    f"使用最低质量压缩: {input_path.name} "
                    f"({original_size_mb:.2f}MB -> {final_size_mb:.2f}MB, "
                    f"质量={min_quality})"
                )
                self.processed_count += 1
                return True
                
        except Exception as e:
            logger.error(f"压缩失败 {input_path.name}: {e}")
            self.failed_count += 1
            return False
    
    def compress_directory(
        self,
        input_dir: Path,
        output_dir: Optional[Path] = None,
        target_size_mb: float = 4.9,
        recursive: bool = True
    ) -> Tuple[int, int]:
        """
        批量压缩目录中的图片
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录（为None时覆盖原文件）
            target_size_mb: 目标文件大小（MB）
            recursive: 是否递归处理子目录
            
        Returns:
            Tuple[int, int]: (成功数量, 失败数量)
        """
        if not input_dir.exists():
            raise ValueError(f"输入目录不存在: {input_dir}")
        
        if output_dir is None:
            output_dir = input_dir
        else:
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # 重置计数器
        self.processed_count = 0
        self.failed_count = 0
        
        # 获取所有图片文件
        pattern = "**/*" if recursive else "*"
        image_files = [
            f for f in input_dir.glob(pattern)
            if f.is_file() and self.is_supported_format(f)
        ]
        
        logger.info(f"找到 {len(image_files)} 个图片文件")
        
        for image_file in image_files:
            # 计算相对路径，保持目录结构
            relative_path = image_file.relative_to(input_dir)
            output_path = output_dir / relative_path.with_suffix('.jpg')  # 统一输出为jpg
            
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.compress_single_image(image_file, output_path, target_size_mb)
        
        return self.processed_count, self.failed_count
    
    def get_statistics(self) -> dict:
        """获取处理统计信息"""
        return {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'total': self.processed_count + self.failed_count,
            'success_rate': self.processed_count / max(1, self.processed_count + self.failed_count) * 100
        }


def main():
    """主函数，用于命令行执行"""
    import argparse
    
    parser = argparse.ArgumentParser(description="图片压缩工具")
    parser.add_argument("input", help="输入文件或目录路径")
    parser.add_argument("-o", "--output", help="输出路径（可选）")
    parser.add_argument("-s", "--size", type=float, default=4.9, help="目标大小（MB，默认4.9）")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归处理子目录")
    parser.add_argument("--min-quality", type=int, default=10, help="最小质量（1-100，默认10）")
    parser.add_argument("--quality-step", type=int, default=5, help="质量递减步长（默认5）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else None
    
    compressor = ImageCompressor()
    
    try:
        if input_path.is_file():
            # 单文件处理
            success = compressor.compress_single_image(
                input_path, output_path, args.size, args.min_quality, args.quality_step
            )
            if success:
                print("✅ 图片压缩完成")
            else:
                print("❌ 图片压缩失败")
                return 1
        
        elif input_path.is_dir():
            # 目录处理
            processed, failed = compressor.compress_directory(
                input_path, output_path, args.size, args.recursive
            )
            
            stats = compressor.get_statistics()
            print(f"\n📊 处理统计:")
            print(f"  总文件数: {stats['total']}")
            print(f"  成功: {stats['processed']}")
            print(f"  失败: {stats['failed']}")
            print(f"  成功率: {stats['success_rate']:.1f}%")
            
            if failed > 0:
                return 1
        
        else:
            print(f"❌ 路径不存在: {input_path}")
            return 1
    
    except Exception as e:
        logger.error(f"执行失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
