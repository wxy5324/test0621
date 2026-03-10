"""
HTTP 请求处理 - 路由与业务调用
"""
import json
import os
import threading
import urllib.parse
from http.server import BaseHTTPRequestHandler

# 业务模块导入（带降级）
try:
    from issue_query import fetch_issues, fetch_online_issues
except ImportError:
    def fetch_issues(start_date=None, end_date=None):
        return {'error': '问题查询后端未找到，请确认 src/main/python/issue_query.py 存在'}

    def fetch_online_issues(start_date=None, end_date=None):
        return {'error': '问题查询后端未找到'}

try:
    from data_process import generate_random_contacts
except ImportError:
    def generate_random_contacts(n):
        return {'error': '数据处理模块未找到，请确认 src/main/python/data_process.py 存在'}

try:
    from binary_sort import binary_insertion_sort
except ImportError:
    def binary_insertion_sort(arr):
        return {'error': '排序模块未找到，请确认 src/main/python/binary_sort.py 存在'}

try:
    from mobile_cipher import generate_and_encrypt_mobiles
except ImportError:
    def generate_and_encrypt_mobiles(mobile, n):
        return {'error': '手机号加解密模块未找到，请确认 src/main/python/mobile_cipher.py 存在'}


def create_handler(html_contents: dict):
    """
    创建 HTTP 处理器，注入预加载的 HTML 内容
    :param html_contents: 各路由对应的 HTML 字节内容，key 为 path 或 '*binary-sort' 表示 /binary-sort 及子路径
    """

    class AppHandler(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _send_cors(self):
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')

        def _json_response(self, data):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors()
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))

        def do_OPTIONS(self):
            self.send_response(204)
            self._send_cors()
            self.end_headers()

        def do_POST(self):
            if self.path == '/sort':
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length)
                try:
                    data = json.loads(body)
                    numbers = [float(x) for x in data['numbers']]
                    result = binary_insertion_sort(numbers)
                    if isinstance(result, dict) and 'error' in result:
                        self.send_response(400)
                        self.end_headers()
                        self.wfile.write(json.dumps(result).encode('utf-8'))
                        return
                    print('\n========== 二分插入排序 ==========', flush=True)
                    print('输入:', numbers, flush=True)
                    print('输出:', result, flush=True)
                    print('================================\n', flush=True)
                    self._json_response({'sorted': result})
                except Exception as e:
                    print('排序错误:', e, flush=True)
                    self.send_response(400)
                    self.end_headers()
                return
            self.send_response(404)
            self.end_headers()

        def do_GET(self):
            path = self.path.split('?')[0]
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)

            if path == '/quit':
                print('\n  收到关闭请求，正在停止服务器...\n', flush=True)
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain; charset=utf-8')
                self.end_headers()
                self.wfile.write(b'Server shutting down...')
                threading.Thread(target=self.server.shutdown, daemon=True).start()
                return

            if path == '/api/issues':
                start_date = query.get('start_date', [None])[0]
                end_date = query.get('end_date', [None])[0]
                self._json_response(fetch_issues(start_date=start_date, end_date=end_date))
                return

            if path == '/api/online-issues':
                start_date = query.get('start_date', [None])[0]
                end_date = query.get('end_date', [None])[0]
                self._json_response(fetch_online_issues(start_date=start_date, end_date=end_date))
                return

            if path == '/api/random-contacts':
                try:
                    n = int(query.get('n', [10])[0])
                except (ValueError, TypeError):
                    n = 10
                result = generate_random_contacts(n)
                data = result if (isinstance(result, dict) and 'error' in result) else {'list': result}
                self._json_response(data)
                return

            if path == '/api/mobile-cipher':
                mobile = (query.get('mobile', [''])[0] or '').strip()
                try:
                    n = max(1, min(500, int(query.get('n', [1])[0])))
                except (ValueError, TypeError):
                    n = 1
                if not mobile or not mobile.isdigit() or len(mobile) != 11:
                    data = {'error': '请输入有效的11位手机号'}
                else:
                    data = generate_and_encrypt_mobiles(mobile, n)
                self._json_response(data)
                return

            #  静态页面路由
            content = html_contents.get(path)
            if content is None and (path == '/binary-sort' or path.startswith('/binary-sort/')):
                content = html_contents.get('*binary-sort')
            if content is None and path.endswith('/'):
                content = html_contents.get(path[:-1])
            if content is None and path != '/':
                content = html_contents.get(path + '/')
            if content is not None:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html')
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_response(404)
                self.end_headers()

    return AppHandler
