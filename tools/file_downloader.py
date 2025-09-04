"""
文件下载工具
支持从Excel文件读取下载链接并批量下载文件
"""
import os
import logging
import requests
import pandas as pd
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
import time

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FileDownloader:
    """文件下载工具类"""
    
    def __init__(self, save_dir: str = "./downloads", timeout: int = 30, max_retries: int = 3):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        self.timeout = timeout
        self.max_retries = max_retries
        
        # 统计信息
        self.downloaded_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        
        # 请求会话，支持连接复用
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def sanitize_filename(self, name: str) -> str:
        """清理文件名中的非法字符"""
        # 移除或替换非法字符
        illegal_chars = r'\/:*?"<>|'
        for char in illegal_chars:
            name = name.replace(char, '_')
        
        # 移除前后空格和点
        name = name.strip('. ')
        
        # 限制长度
        if len(name) > 200:
            name = name[:200]
        
        return name
    
    def extract_filename_from_url(self, url: str) -> str:
        """从URL中提取文件名"""
        try:
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if filename and '.' in filename:
                return filename
        except Exception:
            pass
        
        # 如果无法提取，使用默认名称
        return "downloaded_file"
    
    def get_file_extension_from_url(self, url: str) -> str:
        """从URL中提取文件扩展名"""
        try:
            parsed = urlparse(url)
            path = parsed.path
            if '.' in path:
                return os.path.splitext(path)[1]
        except Exception:
            pass
        return ""
    
    def download_single_file(
        self, 
        url: str, 
        filename: str, 
        custom_filename: Optional[str] = None
    ) -> bool:
        """
        下载单个文件
        
        Args:
            url: 下载链接
            filename: 原始文件名
            custom_filename: 自定义文件名
            
        Returns:
            bool: 是否下载成功
        """
        if not url or url.strip() == "":
            logger.warning("URL为空，跳过")
            return False
        
        url = url.strip()
        
        # 确定最终文件名
        if custom_filename:
            final_filename = self.sanitize_filename(custom_filename)
        else:
            final_filename = self.sanitize_filename(filename)
        
        # 如果文件名没有扩展名，尝试从URL获取
        if not os.path.splitext(final_filename)[1]:
            ext = self.get_file_extension_from_url(url)
            if ext:
                final_filename += ext
        
        filepath = self.save_dir / final_filename
        
        # 检查文件是否已存在
        if filepath.exists():
            logger.info(f"文件已存在，跳过: {final_filename}")
            self.skipped_count += 1
            return True
        
        # 下载文件
        for attempt in range(self.max_retries):
            try:
                logger.info(f"正在下载: {final_filename} (尝试 {attempt + 1}/{self.max_retries})")
                
                response = self.session.get(url, stream=True, timeout=self.timeout)
                response.raise_for_status()
                
                # 获取文件大小
                total_size = int(response.headers.get('content-length', 0))
                
                with open(filepath, "wb") as f:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            
                            # 显示进度（每10MB显示一次）
                            if total_size > 0 and downloaded % (10 * 1024 * 1024) == 0:
                                progress = (downloaded / total_size) * 100
                                logger.info(f"下载进度: {final_filename} - {progress:.1f}%")
                
                file_size = filepath.stat().st_size / (1024 * 1024)  # MB
                logger.info(f"下载完成: {final_filename} ({file_size:.2f} MB)")
                self.downloaded_count += 1
                return True
                
            except requests.exceptions.RequestException as e:
                logger.warning(f"下载失败 (尝试 {attempt + 1}): {final_filename} - {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)  # 指数退避
                else:
                    logger.error(f"下载最终失败: {final_filename}")
                    self.failed_count += 1
                    # 删除可能的不完整文件
                    if filepath.exists():
                        filepath.unlink()
                    return False
            
            except Exception as e:
                logger.error(f"下载异常: {final_filename} - {e}")
                self.failed_count += 1
                if filepath.exists():
                    filepath.unlink()
                return False
        
        return False
    
    def download_from_excel(
        self, 
        excel_path: str, 
        url_column: str = "文件链接",
        name_column: str = "文件名称", 
        status_column: str = "清洗状态",
        skip_cleaned: bool = True
    ) -> Tuple[int, int, int]:
        """
        从Excel文件读取下载列表并批量下载
        
        Args:
            excel_path: Excel文件路径
            url_column: URL列名
            name_column: 文件名列名
            status_column: 状态列名
            skip_cleaned: 是否跳过已清洗的文件
            
        Returns:
            Tuple[int, int, int]: (下载数量, 跳过数量, 失败数量)
        """
        excel_path = Path(excel_path)
        if not excel_path.exists():
            raise FileNotFoundError(f"Excel文件不存在: {excel_path}")
        
        # 重置统计
        self.downloaded_count = 0
        self.skipped_count = 0
        self.failed_count = 0
        
        try:
            # 尝试使用不同的引擎读取Excel
            engines = ['calamine', 'openpyxl', 'xlrd']
            df = None
            
            for engine in engines:
                try:
                    df = pd.read_excel(excel_path, engine=engine)
                    logger.info(f"使用 {engine} 引擎成功读取Excel文件")
                    break
                except Exception as e:
                    logger.warning(f"使用 {engine} 引擎读取失败: {e}")
                    continue
            
            if df is None:
                raise ValueError("无法读取Excel文件，请检查文件格式")
            
            logger.info(f"Excel文件包含 {len(df)} 行数据")
            
            # 检查必需的列
            missing_columns = []
            for col in [url_column, name_column]:
                if col not in df.columns:
                    missing_columns.append(col)
            
            if missing_columns:
                raise ValueError(f"Excel文件缺少必需的列: {missing_columns}")
            
            # 处理每一行
            for idx, row in df.iterrows():
                try:
                    url = str(row[url_column]).strip() if pd.notna(row[url_column]) else ""
                    name = str(row[name_column]).strip() if pd.notna(row[name_column]) else ""
                    status = str(row[status_column]).strip() if pd.notna(row.get(status_column)) else ""
                    
                    if not url or not name:
                        logger.warning(f"第{idx+2}行数据不完整，跳过")
                        continue
                    
                    # 跳过已清洗的文件
                    if skip_cleaned and status == "已清洗":
                        logger.info(f"第{idx+2}行已清洗，跳过: {name}")
                        self.skipped_count += 1
                        continue
                    
                    # 生成文件名
                    status_label = status if status else "未清洗"
                    custom_filename = f"{idx+2}_{name}_{status_label}"
                    
                    # 下载文件
                    self.download_single_file(url, name, custom_filename)
                    
                except Exception as e:
                    logger.error(f"处理第{idx+2}行时出错: {e}")
                    self.failed_count += 1
                    continue
        
        except Exception as e:
            logger.error(f"读取Excel文件失败: {e}")
            raise
        
        return self.downloaded_count, self.skipped_count, self.failed_count
    
    def get_statistics(self) -> Dict[str, int]:
        """获取下载统计信息"""
        total = self.downloaded_count + self.skipped_count + self.failed_count
        return {
            'downloaded': self.downloaded_count,
            'skipped': self.skipped_count,
            'failed': self.failed_count,
            'total': total,
            'success_rate': (self.downloaded_count / max(1, total)) * 100
        }
    
    def close(self):
        """关闭会话"""
        self.session.close()


def main():
    """主函数，用于命令行执行"""
    import argparse
    
    parser = argparse.ArgumentParser(description="文件批量下载工具")
    parser.add_argument("excel_file", help="Excel文件路径")
    parser.add_argument("-d", "--dir", default="./downloads", help="下载目录（默认：./downloads）")
    parser.add_argument("--url-column", default="文件链接", help="URL列名（默认：文件链接）")
    parser.add_argument("--name-column", default="文件名称", help="文件名列名（默认：文件名称）")
    parser.add_argument("--status-column", default="清洗状态", help="状态列名（默认：清洗状态）")
    parser.add_argument("--include-cleaned", action="store_true", help="包括已清洗的文件")
    parser.add_argument("--timeout", type=int, default=30, help="下载超时时间（秒，默认30）")
    parser.add_argument("--max-retries", type=int, default=3, help="最大重试次数（默认3）")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    
    args = parser.parse_args()
    
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
    
    except Exception as e:
        logger.error(f"执行失败: {e}")
        return 1
    
    finally:
        downloader.close()
    
    return 0


if __name__ == "__main__":
    exit(main())
