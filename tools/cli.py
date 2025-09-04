#!/usr/bin/env python3
"""
工具集命令行入口
提供统一的命令行接口来使用各种工具
"""
import sys
import argparse
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="PlayWright项目工具集",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
可用工具:
  rename        批量重命名文件
  compress      图片压缩工具
  download      文件批量下载工具

示例用法:
  python tools/cli.py rename /path/to/files --dry-run
  python tools/cli.py compress /path/to/images -s 2.0
  python tools/cli.py download data.xlsx -d ./downloads
        """
    )
    
    subparsers = parser.add_subparsers(dest='tool', help='选择要使用的工具')
    
    # 文件重命名工具
    rename_parser = subparsers.add_parser('rename', help='批量重命名文件')
    rename_parser.add_argument('folder', help='要处理的文件夹路径')
    rename_parser.add_argument('--dry-run', action='store_true', help='试运行，不实际重命名')
    rename_parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    # 图片压缩工具
    compress_parser = subparsers.add_parser('compress', help='图片压缩工具')
    compress_parser.add_argument('input', help='输入文件或目录路径')
    compress_parser.add_argument('-o', '--output', help='输出路径（可选）')
    compress_parser.add_argument('-s', '--size', type=float, default=4.9, help='目标大小（MB，默认4.9）')
    compress_parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    compress_parser.add_argument('--min-quality', type=int, default=10, help='最小质量（1-100，默认10）')
    compress_parser.add_argument('--quality-step', type=int, default=5, help='质量递减步长（默认5）')
    compress_parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    # 文件下载工具
    download_parser = subparsers.add_parser('download', help='文件批量下载工具')
    download_parser.add_argument('excel_file', help='Excel文件路径')
    download_parser.add_argument('-d', '--dir', default='./downloads', help='下载目录（默认：./downloads）')
    download_parser.add_argument('--url-column', default='文件链接', help='URL列名（默认：文件链接）')
    download_parser.add_argument('--name-column', default='文件名称', help='文件名列名（默认：文件名称）')
    download_parser.add_argument('--status-column', default='清洗状态', help='状态列名（默认：清洗状态）')
    download_parser.add_argument('--include-cleaned', action='store_true', help='包括已清洗的文件')
    download_parser.add_argument('--timeout', type=int, default=30, help='下载超时时间（秒，默认30）')
    download_parser.add_argument('--max-retries', type=int, default=3, help='最大重试次数（默认3）')
    download_parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    if not args.tool:
        parser.print_help()
        return 1
    
    try:
        if args.tool == 'rename':
            from tools.file_renamer import FileRenamer
            import logging
            
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            
            renamer = FileRenamer(args.folder)
            operations = renamer.rename_files(dry_run=args.dry_run)
            
            print(f"\n总共处理了 {len(operations)} 个文件")
            if args.dry_run:
                print("这是试运行结果，去掉 --dry-run 参数来实际执行重命名")
        
        elif args.tool == 'compress':
            from tools.image_compressor import ImageCompressor
            import logging
            
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            
            input_path = Path(args.input)
            output_path = Path(args.output) if args.output else None
            
            compressor = ImageCompressor()
            
            if input_path.is_file():
                success = compressor.compress_single_image(
                    input_path, output_path, args.size, args.min_quality, args.quality_step
                )
                if success:
                    print("✅ 图片压缩完成")
                else:
                    print("❌ 图片压缩失败")
                    return 1
            
            elif input_path.is_dir():
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
        
        elif args.tool == 'download':
            from tools.file_downloader import FileDownloader
            import logging
            
            if args.verbose:
                logging.getLogger().setLevel(logging.DEBUG)
            
            downloader = FileDownloader(
                save_dir=args.dir,
                timeout=args.timeout,
                max_retries=args.max_retries
            )
            
            try:
                downloaded, skipped, failed = downloader.download_from_excel(
                    excel_path=args.excel_file,
                    url_column=args.url_column,
                    name_column=args.name_column,
                    status_column=args.status_column,
                    skip_cleaned=not args.include_cleaned
                )
                
                stats = downloader.get_statistics()
                
                print(f"\n📊 下载统计:")
                print(f"  总文件数: {stats['total']}")
                print(f"  已下载: {stats['downloaded']}")
                print(f"  已跳过: {stats['skipped']}")
                print(f"  下载失败: {stats['failed']}")
                print(f"  成功率: {stats['success_rate']:.1f}%")
                
                if failed > 0:
                    return 1
            finally:
                downloader.close()
        
        return 0
    
    except Exception as e:
        print(f"❌ 执行失败: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
