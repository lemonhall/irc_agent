"""
简单的 HTTP 服务器，用于查看新闻网页
"""
import http.server
import socketserver
import webbrowser
from pathlib import Path

PORT = 8000
DIRECTORY = Path(__file__).parent

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

def main():
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print("=" * 60)
        print(f"📰 新闻服务器已启动")
        print(f"🌐 访问地址: http://localhost:{PORT}")
        print("=" * 60)
        print(f"\n按 Ctrl+C 停止服务器\n")
        
        # 自动打开浏览器
        webbrowser.open(f"http://localhost:{PORT}")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n👋 服务器已停止")

if __name__ == "__main__":
    main()
