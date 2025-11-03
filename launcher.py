#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信文件整理器 - 启动器
可以从Web界面启动主程序
"""

import os
import sys
import subprocess
import webbrowser
from pathlib import Path
import json

def create_launcher_config():
    """创建启动器配置"""
    config = {
        "version": "1.0.0",
        "main_script": "gui_organizer.py",
        "requirements": ["python >= 3.6", "tkinter"],
        "description": "微信文件整理器启动器"
    }

    config_path = Path(__file__).parent / "launcher_config.json"
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

    return config_path

def check_environment():
    """检查运行环境"""
    # 检查Python版本
    if sys.version_info < (3, 6):
        return False, f"Python版本过低：{sys.version}，需要3.6+"

    # 检查tkinter
    try:
        import tkinter
        tkinter.Tk().withdraw()  # 测试tkinter是否可用
    except ImportError:
        return False, "未找到tkinter模块，请安装Python的tkinter支持"

    # 检查主程序文件
    main_script = Path(__file__).parent / "gui_organizer.py"
    if not main_script.exists():
        return False, f"找不到主程序文件：{main_script}"

    return True, "环境检查通过"

def start_main_program():
    """启动主程序"""
    try:
        # 切换到脚本所在目录
        script_dir = Path(__file__).parent
        os.chdir(script_dir)

        # 启动GUI程序
        subprocess.run([sys.executable, "gui_organizer.py"], check=True)
        return True, "程序启动成功"

    except subprocess.CalledProcessError as e:
        return False, f"启动失败：{e}"
    except Exception as e:
        return False, f"未知错误：{e}"

def main():
    """主函数"""
    print("微信文件整理器启动器")
    print("=" * 30)

    # 检查环境
    success, message = check_environment()
    if not success:
        print(f"环境检查失败: {message}")
        input("按回车键退出...")
        return

    print(f"环境检查通过: {message}")

    # 尝试启动程序
    print("正在启动微信文件整理器...")
    success, message = start_main_program()

    if success:
        print(f"{message}")
    else:
        print(f"启动失败: {message}")
        input("按回车键退出...")

if __name__ == "__main__":
    main()