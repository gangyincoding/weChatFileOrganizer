#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信文件整理器 - Web服务器
提供Web界面和程序启动功能
"""

import os
import sys
import json
import threading
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import subprocess
import webbrowser
import socket

class OrganizerHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.project_dir = Path(__file__).parent
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理GET请求"""
        parsed_url = urlparse(self.path)

        if parsed_url.path == '/' or parsed_url.path == '/index.html':
            self.serve_file('index.html', 'text/html')
        elif parsed_url.path == '/start':
            self.start_program()
        elif parsed_url.path == '/check':
            self.check_environment()
        else:
            self.serve_404()

    def do_POST(self):
        """处理POST请求"""
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        parsed_url = urlparse(self.path)

        if parsed_url.path == '/start':
            self.start_program()
        else:
            self.serve_404()

    def serve_file(self, filename, content_type='text/html'):
        """提供静态文件"""
        file_path = self.project_dir / filename
        if file_path.exists():
            with open(file_path, 'rb') as f:
                content = f.read()
                self.send_response(200)
                self.send_header('Content-type', f'{content_type}; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
        else:
            self.serve_404()

    def start_program(self):
        """启动程序"""
        try:
            # 切换到项目目录
            os.chdir(self.project_dir)

            # 启动GUI程序
            subprocess.Popen([sys.executable, "gui_organizer.py"])

            # 返回成功响应
            response = {
                "success": True,
                "message": "程序启动成功！",
                "note": "请检查是否弹出程序窗口"
            }

            self.send_json_response(response)

        except Exception as e:
            # 返回错误响应
            response = {
                "success": False,
                "message": f"启动失败: {str(e)}",
                "note": "请检查Python环境和文件完整性"
            }

            self.send_json_response(response)

    def check_environment(self):
        """检查运行环境"""
        checks = {
            "python_version": {
                "status": "unknown",
                "version": f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                "required": "3.6+"
            },
            "tkinter": {
                "status": "unknown"
            },
            "main_script": {
                "status": "unknown",
                "path": str(self.project_dir / "gui_organizer.py")
            }
        }

        # 检查Python版本
        if sys.version_info >= (3, 6):
            checks["python_version"]["status"] = "ok"
        else:
            checks["python_version"]["status"] = "error"

        # 检查tkinter
        try:
            import tkinter
            checks["tkinter"]["status"] = "ok"
        except ImportError:
            checks["tkinter"]["status"] = "error"

        # 检查主程序文件
        main_script_path = self.project_dir / "gui_organizer.py"
        if main_script_path.exists():
            checks["main_script"]["status"] = "ok"
        else:
            checks["main_script"]["status"] = "error"

        self.send_json_response(checks)

    def send_json_response(self, data):
        """发送JSON响应"""
        response_data = json.dumps(data, ensure_ascii=False)
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(response_data.encode('utf-8'))))
        self.end_headers()
        self.wfile.write(response_data.encode('utf-8'))

    def serve_404(self):
        """返回404错误"""
        self.send_response(404)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>404 Not Found</h1>')

def find_free_port(start_port=8000):
    """查找可用端口"""
    for port in range(start_port, start_port + 100):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                s.listen(1)
                return port
        except OSError:
            continue
    return None

def main():
    """主函数"""
    print("微信文件整理器 Web服务器")
    print("=" * 40)

    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # 检查必要文件
    if not (project_dir / "index.html").exists():
        print("错误: 找不到 index.html 文件")
        return

    if not (project_dir / "gui_organizer.py").exists():
        print("错误: 找不到 gui_organizer.py 文件")
        return

    # 查找可用端口
    port = find_free_port()
    if port is None:
        print("错误: 无法找到可用端口")
        return

    print(f"服务器启动中...")
    print(f"本地地址: http://localhost:{port}")
    print("按 Ctrl+C 停止服务器")
    print("-" * 40)

    try:
        # 启动Web服务器
        server_address = ('', port)
        httpd = HTTPServer(server_address, OrganizerHandler)

        # 自动打开浏览器
        def open_browser():
            import time
            time.sleep(1)  # 等待服务器启动
            webbrowser.open(f'http://localhost:{port}')

        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

        # 启动服务器
        httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"启动失败: {e}")

if __name__ == "__main__":
    main()