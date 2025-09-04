"""
文件重命名工具
用于批量重命名下载文件，整理文件名格式
"""
import os
import re
import logging
from pathlib import Path
from typing import List, Tuple, Optional

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
    
    def analyze_filename(self, filename: str) -> Tuple[str, str, str]:
        """
        分析文件名，提取名称、扩展名和状态
        
        Args:
            filename: 原始文件名
            
        Returns:
            tuple: (名称, 扩展名, 状态)
        """
        # 尝试从右边找到扩展名
        dot_pos = filename.rfind('.')
        if dot_pos == -1:
            logger.warning(f"无法识别扩展名: {filename}")
            return filename, "", ""
        
        name = filename[:dot_pos]
        ext = filename[dot_pos:]
        
        # 状态后缀可能在扩展名后或扩展名前
        # 先检查扩展名后是否有下划线 + 状态
        status_match = re.search(r'_.*$', ext)
        if status_match:
            status = status_match.group(0)
            ext = ext.replace(status, '')
        else:
            status_match = self.status_pattern.search(name)
            status = status_match.group(0) if status_match else ''
            
            if status:
                name = name[:status_match.start()]
        
        return name, ext, status
    
    def generate_new_filename(self, name: str, ext: str, status: str) -> str:
        """
        生成新的文件名
        
        Args:
            name: 文件名（不含扩展名）
            ext: 扩展名
            status: 状态后缀
            
        Returns:
            str: 新的文件名
        """
        return f"{name}{status}{ext}"
    
    def rename_files(self, dry_run: bool = True) -> List[Tuple[str, str]]:
        """
        批量重命名文件
        
        Args:
            dry_run: 是否为试运行（不实际重命名）
            
        Returns:
            List[Tuple[str, str]]: 重命名操作列表 [(原文件名, 新文件名)]
        """
        rename_operations = []
        
        for filename in os.listdir(self.folder_path):
            old_path = self.folder_path / filename
            
            if old_path.is_dir():
                continue
            
            name, ext, status = self.analyze_filename(filename)
            if not ext:  # 跳过无法识别扩展名的文件
                continue
            
            new_filename = self.generate_new_filename(name, ext, status)
            new_path = self.folder_path / new_filename
            
            if old_path != new_path:
                rename_operations.append((filename, new_filename))
                
                if not dry_run:
                    try:
                        old_path.rename(new_path)
                        logger.info(f"重命名: {filename} -> {new_filename}")
                    except Exception as e:
                        logger.error(f"重命名失败 {filename}: {e}")
                else:
                    logger.info(f"[试运行] {filename} -> {new_filename}")
            else:
                logger.info(f"文件名无需更改: {filename}")
        
        return rename_operations


def main():
    """主函数，用于命令行执行"""
    import argparse
    
    parser = argparse.ArgumentParser(description="批量重命名文件工具")
    parser.add_argument("folder", help="要处理的文件夹路径")
    parser.add_argument("--dry-run", action="store_true", help="试运行，不实际重命名")
    parser.add_argument("--verbose", "-v", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        renamer = FileRenamer(args.folder)
        operations = renamer.rename_files(dry_run=args.dry_run)
        
        print(f"\n总共处理了 {len(operations)} 个文件")
        if args.dry_run:
            print("这是试运行结果，使用 --dry-run=false 来实际执行重命名")
        
    except Exception as e:
        logger.error(f"执行失败: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
