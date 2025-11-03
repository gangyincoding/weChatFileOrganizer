#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信文件整理器 - 图形界面版本
使用tkinter创建友好的用户界面
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
from file_organizer import WeChatFileOrganizer


class WeChatOrganizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("微信文件整理器")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # 变量
        self.source_dir = tk.StringVar()
        self.target_dir = tk.StringVar()
        self.organizer = None
        self.is_running = False

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # 标题
        title_label = ttk.Label(main_frame, text="微信文件整理器", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # 源目录选择
        ttk.Label(main_frame, text="微信文件夹:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.source_entry = ttk.Entry(main_frame, textvariable=self.source_dir, width=50)
        self.source_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_source).grid(row=1, column=2, padx=5, pady=5)

        # 目标目录选择
        ttk.Label(main_frame, text="目标文件夹:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.target_entry = ttk.Entry(main_frame, textvariable=self.target_dir, width=50)
        self.target_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_target).grid(row=2, column=2, padx=5, pady=5)

        # 分类预览
        preview_frame = ttk.LabelFrame(main_frame, text="文件分类预览", padding="10")
        preview_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        main_frame.columnconfigure(1, weight=1)

        categories = [
            "图片: jpg, png, gif, bmp, webp",
            "视频: mp4, avi, mov, mkv, flv",
            "音频: mp3, wav, flac, aac, m4a",
            "文档: pdf, doc, docx, txt, xlsx",
            "压缩包: zip, rar, 7z, tar",
            "程序: exe, msi, apk",
            "其他: 未识别格式的文件"
        ]

        for i, category in enumerate(categories):
            ttk.Label(preview_frame, text=category).grid(row=i//2, column=i%2, sticky=tk.W, padx=5, pady=2)

        # 操作说明
        instruction_frame = ttk.LabelFrame(main_frame, text="使用说明", padding="10")
        instruction_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))

        instruction_text = "📋 简单操作：选择文件夹 → 点击「开始整理」，程序会自动扫描并整理文件"
        instruction_label = ttk.Label(instruction_frame, text=instruction_text, foreground="#666666")
        instruction_label.pack()

        # 操作按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)

        self.organize_button = ttk.Button(button_frame, text="🚀 开始整理", command=self.start_organizing)
        self.organize_button.pack(side=tk.LEFT, padx=5)

        self.stop_button = ttk.Button(button_frame, text="⏹ 停止", command=self.stop_organizing, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame, text="🗑️ 清空日志", command=self.clear_log).pack(side=tk.LEFT, padx=5)

        # 进度信息框架
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100, length=400)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        progress_frame.columnconfigure(0, weight=1)

        # 进度百分比标签
        self.progress_percent_label = ttk.Label(progress_frame, text="0%", width=8)
        self.progress_percent_label.grid(row=0, column=1)

        # 进度详情标签
        self.progress_detail_label = ttk.Label(main_frame, text="等待开始...", foreground="gray")
        self.progress_detail_label.grid(row=7, column=0, columnspan=3, pady=2)

        # 状态标签
        self.status_label = ttk.Label(main_frame, text="就绪")
        self.status_label.grid(row=8, column=0, columnspan=3, pady=5)

        # 日志文本框
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="5")
        log_frame.grid(row=9, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(9, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

    def browse_source(self):
        """浏览源目录"""
        directory = filedialog.askdirectory(title="选择微信文件夹")
        if directory:
            self.source_dir.set(directory)
            self.log_message(f"选择源目录: {directory}")

    def browse_target(self):
        """浏览目标目录"""
        directory = filedialog.askdirectory(title="选择目标文件夹")
        if directory:
            self.target_dir.set(directory)
            self.log_message(f"选择目标目录: {directory}")

    def log_message(self, message):
        """在日志框中显示消息"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)

    def update_progress(self, current, total, filename):
        """更新进度显示"""
        if not self.is_running:
            return

        # 计算百分比
        if total > 0:
            progress_percent = (current / total) * 100
            self.progress_var.set(progress_percent)
            self.progress_percent_label.config(text=f"{progress_percent:.1f}%")

            # 更新进度详情
            try:
                # 安全地显示文件名，避免特殊字符问题
                safe_filename = filename.encode('ascii', 'ignore').decode('ascii')
                if not safe_filename:
                    safe_filename = "[特殊字符文件名]"

                # 根据操作类型显示不同的状态
                if "扫描" in filename:
                    self.progress_detail_label.config(
                        text=f"🔍 扫描中: {safe_filename} ({current}/{total})"
                    )
                elif "整理完成" in filename:
                    self.progress_detail_label.config(text="✅ 整理完成！")
                elif "收到停止信号" in filename:
                    self.progress_detail_label.config(text="⏹ 正在停止...")
                    self.status_label.config(text="用户取消操作")
                else:
                    self.progress_detail_label.config(
                        text=f"📁 整理中: {safe_filename} ({current}/{total})"
                    )
            except:
                self.progress_detail_label.config(text=f"正在处理文件 {current}/{total}")

        # 更新界面
        self.root.update_idletasks()

    def reset_progress(self):
        """重置进度显示"""
        self.progress_var.set(0)
        self.progress_percent_label.config(text="0%")
        self.progress_detail_label.config(text="等待开始...")

    
    def start_organizing(self):
        """开始整理文件（包含自动扫描）"""
        source = self.source_dir.get()
        target = self.target_dir.get()

        if not source or not target:
            messagebox.showerror("错误", "请选择源目录和目标目录")
            return

        if not os.path.exists(source):
            messagebox.showerror("错误", "源目录不存在")
            return

        # 简单确认
        if not messagebox.askyesno("确认整理",
            f"即将整理文件到以下位置：\n\n"
            f"源目录：{source}\n"
            f"目标目录：{target}\n\n"
            f"程序会自动扫描并整理所有文件，不会删除原始文件。\n\n"
            f"确认继续吗？"):
            return

        self.is_running = True
        self.organize_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.reset_progress()
        self.status_label.config(text="正在整理文件...")

        def organize_task():
            try:
                self.log_message("开始整理文件...")
                self.log_message(f"源目录: {source}")
                self.log_message(f"目标目录: {target}")
                self.log_message("=" * 50)

                # 创建整理器，传入进度回调函数
                self.organizer = WeChatFileOrganizer(source, target, self.update_progress)

                # 重定向日志输出
                original_print = print
                def custom_print(*args, **kwargs):
                    message = " ".join(str(arg) for arg in args)
                    self.log_message(message)
                    original_print(*args, **kwargs)

                # 临时替换print函数
                import builtins
                builtins.print = custom_print

                # 执行整理（包含自动扫描）
                self.organizer.organize_files()

                # 恢复print函数
                builtins.print = original_print

                self.progress_var.set(100)
                self.progress_percent_label.config(text="100%")
                self.progress_detail_label.config(text="整理完成！")
                self.status_label.config(text="整理完成")
                self.log_message("文件整理完成！")

                messagebox.showinfo("完成", "文件整理完成！")

            except Exception as e:
                self.log_message(f"整理出错: {e}")
                self.status_label.config(text="整理失败")
                self.progress_detail_label.config(text=f"整理失败: {str(e)}")
                messagebox.showerror("错误", f"整理失败: {e}")

            finally:
                self.is_running = False
                self.organize_button.config(state=tk.NORMAL)
                self.stop_button.config(state=tk.DISABLED)

        # 在新线程中执行整理
        threading.Thread(target=organize_task, daemon=True).start()

    def stop_organizing(self):
        """停止整理"""
        if self.is_running:
            self.is_running = False
            self.status_label.config(text="正在停止...")
            self.progress_detail_label.config(text="正在停止操作...")
            self.log_message("用户请求停止操作")

            # 向整理器发送停止信号
            if hasattr(self, 'organizer') and self.organizer:
                self.organizer.stop_organizing()


def main():
    """主函数"""
    root = tk.Tk()
    app = WeChatOrganizerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()