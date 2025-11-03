#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信文件整理器
自动扫描微信文件夹，将文件按类型分类整理到指定目录
"""

import os
import sys
import shutil
from pathlib import Path
from typing import Dict, List, Tuple
import hashlib
from datetime import datetime

# 设置控制台编码支持特殊字符
try:
    if sys.platform == 'win32':
        # Windows系统设置UTF-8编码
        os.system('chcp 65001 >nul')
except:
    pass


def safe_print(text):
    """安全的打印函数，处理特殊字符"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果有编码问题，尝试ASCII编码
        try:
            print(text.encode('ascii', 'ignore').decode('ascii'))
        except:
            # 最后的备选方案
            print("[无法显示的特殊字符]")

class WeChatFileOrganizer:
    def __init__(self, source_dir: str, target_dir: str, progress_callback=None):
        """
        初始化文件整理器

        Args:
            source_dir: 微信文件夹路径
            target_dir: 目标整理路径
            progress_callback: 进度回调函数，接收(current, total, filename)参数
        """
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.progress_callback = progress_callback
        self.file_categories = {
            '图片': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico', '.tiff'],
            '视频': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp'],
            '音频': ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.amr'],
            '文档': ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx'],
            '压缩包': ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'],
            '程序': ['.exe', '.msi', '.dmg', '.pkg', '.deb', '.rpm', '.apk'],
            '其他': []
        }
        self.processed_files = []
        self.skipped_files = []
        self.total_files = 0
        self.stop_requested = False

    def create_target_directories(self):
        """创建目标目录结构"""
        safe_print("正在创建目标目录结构...")
        for category in self.file_categories.keys():
            category_dir = self.target_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            safe_print(f"创建目录: {category_dir}")

    def get_file_category(self, file_path: Path) -> str:
        """根据文件扩展名确定文件类别"""
        suffix = file_path.suffix.lower()

        for category, extensions in self.file_categories.items():
            if category != '其他' and suffix in extensions:
                return category

        return '其他'

    def calculate_file_hash(self, file_path: Path) -> str:
        """计算文件MD5哈希值，用于检测重复文件"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            safe_print(f"计算文件哈希失败 {file_path}: {e}")
            return ""

    def is_duplicate_file(self, source_file: Path, target_file: Path) -> bool:
        """检查是否为重复文件"""
        if not target_file.exists():
            return False

        # 计算源文件和目标文件的哈希值
        source_hash = self.calculate_file_hash(source_file)
        target_hash = self.calculate_file_hash(target_file)

        return source_hash == target_hash and source_hash != ""

    def generate_unique_filename(self, target_dir: Path, filename: str) -> Path:
        """生成唯一的文件名，避免重名覆盖"""
        target_path = target_dir / filename
        stem = target_path.stem
        suffix = target_path.suffix
        counter = 1

        while target_path.exists():
            new_filename = f"{stem}_{counter}{suffix}"
            target_path = target_dir / new_filename
            counter += 1

        return target_path

    def scan_files(self) -> List[Path]:
        """扫描源目录中的所有文件"""
        safe_print(f"正在扫描目录: {self.source_dir}")
        all_files = []

        try:
            # 先获取所有文件列表，用于进度计算
            file_list = list(self.source_dir.rglob('*'))
            total_items = len(file_list)

            for i, item in enumerate(file_list):
                # 更新扫描进度
                if self.progress_callback:
                    self.progress_callback(i + 1, total_items, f"扫描: {item.name}")

                if item.is_file():
                    all_files.append(item)

        except Exception as e:
            safe_print(f"扫描文件时出错: {e}")

        safe_print(f"找到 {len(all_files)} 个文件")
        return all_files

    def organize_files(self):
        """整理文件的主要方法"""
        safe_print(f"开始整理文件...")
        safe_print(f"源目录: {self.source_dir}")
        safe_print(f"目标目录: {self.target_dir}")
        safe_print("-" * 50)

        # 创建目标目录
        self.create_target_directories()

        # 扫描所有文件
        all_files = self.scan_files()

        if not all_files:
            safe_print("没有找到任何文件！")
            return

        # 设置总文件数
        self.total_files = len(all_files)

        # 按类别统计文件
        category_stats = {category: 0 for category in self.file_categories.keys()}
        total_size = 0

        for i, file_path in enumerate(all_files, 1):
            try:
                # 检查是否收到停止信号
                if hasattr(self, 'stop_requested') and self.stop_requested:
                    safe_print("收到停止信号，正在停止整理...")
                    break

                # 更新进度回调
                if self.progress_callback:
                    self.progress_callback(i, self.total_files, file_path.name)

                # 获取文件类别
                category = self.get_file_category(file_path)

                # 目标路径
                target_category_dir = self.target_dir / category
                target_file_path = target_category_dir / file_path.name

                # 检查重复文件
                if self.is_duplicate_file(file_path, target_file_path):
                    safe_print(f"跳过重复文件: {file_path.name}")
                    self.skipped_files.append(file_path)
                    continue

                # 生成唯一文件名（如果需要）
                unique_target_path = self.generate_unique_filename(target_category_dir, file_path.name)

                # 复制文件
                shutil.copy2(file_path, unique_target_path)

                # 更新统计信息
                file_size = file_path.stat().st_size
                total_size += file_size
                category_stats[category] += 1
                self.processed_files.append(unique_target_path)

                safe_print(f"已复制: {file_path.name} -> {category}/{unique_target_path.name}")

            except Exception as e:
                safe_print(f"处理文件失败 {file_path}: {e}")
                self.skipped_files.append(file_path)

        # 完成进度回调
        if self.stop_requested:
            self.progress_callback(self.total_files, self.total_files, "收到停止信号")
            safe_print("\n整理已被用户停止")
            safe_print(f"已处理文件: {len(self.processed_files)} 个")
            safe_print(f"跳过文件: {len(self.skipped_files)} 个")
        else:
            self.progress_callback(self.total_files, self.total_files, "整理完成")
            # 显示统计信息
            self.show_statistics(category_stats, total_size)

    def show_statistics(self, category_stats: Dict[str, int], total_size: int):
        """显示整理统计信息"""
        safe_print("\n" + "=" * 50)
        safe_print("文件整理完成！")
        safe_print("=" * 50)

        safe_print("\n分类统计:")
        for category, count in category_stats.items():
            if count > 0:
                safe_print(f"  {category}: {count} 个文件")

        safe_print(f"\n总计:")
        safe_print(f"  成功处理: {len(self.processed_files)} 个文件")
        safe_print(f"  跳过文件: {len(self.skipped_files)} 个文件")
        safe_print(f"  总大小: {self.format_size(total_size)}")

        safe_print(f"\n目标目录: {self.target_dir}")

    def stop_organizing(self):
        """请求停止整理"""
        self.stop_requested = True
        safe_print("正在发送停止信号...")

    def format_size(self, size_bytes: int) -> str:
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"

        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024.0 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1

        return f"{size_bytes:.2f} {size_names[i]}"


def main():
    """主函数"""
    safe_print("微信文件整理器")
    safe_print("=" * 30)

    # 获取用户输入
    source_dir = input("请输入微信文件夹路径: ").strip()
    target_dir = input("请输入目标整理路径: ").strip()

    # 验证路径
    if not os.path.exists(source_dir):
        safe_print(f"错误: 源目录不存在 - {source_dir}")
        return

    if not os.path.exists(target_dir):
        safe_print(f"目标目录不存在，将自动创建 - {target_dir}")
        os.makedirs(target_dir, exist_ok=True)

    # 确认操作
    safe_print(f"\n即将整理文件从: {source_dir}")
    safe_print(f"到: {target_dir}")
    confirm = input("确认继续？(y/n): ").strip().lower()

    if confirm != 'y':
        safe_print("操作已取消")
        return

    # 创建整理器并执行
    organizer = WeChatFileOrganizer(source_dir, target_dir)
    organizer.organize_files()


if __name__ == "__main__":
    main()