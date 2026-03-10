"""
本地开发服务器 - 提供二分排序页面，并将排序结果输出到终端
运行: python server.py
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import sys
import urllib.parse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_SRC = os.path.join(SCRIPT_DIR, 'src', 'main', 'python')
if PYTHON_SRC not in sys.path:
    sys.path.insert(0, PYTHON_SRC)

PORT = 3000
# 以 server.py 所在目录为基准
FRONTEND_DIR = os.path.join(SCRIPT_DIR, 'frontend')
SORT_HTML_PATH = os.path.join(FRONTEND_DIR, 'sort-page.html')
ISSUE_QUERY_HTML_PATH = os.path.join(FRONTEND_DIR, 'issue-query.html')
ONLINE_ISSUE_QUERY_HTML_PATH = os.path.join(FRONTEND_DIR, 'online-issue-query.html')
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = os.path.join(os.getcwd(), 'frontend')
    SORT_HTML_PATH = os.path.join(FRONTEND_DIR, 'sort-page.html')
    ISSUE_QUERY_HTML_PATH = os.path.join(FRONTEND_DIR, 'issue-query.html')
    ONLINE_ISSUE_QUERY_HTML_PATH = os.path.join(FRONTEND_DIR, 'online-issue-query.html')

SORT_CONTENT = None
ISSUE_QUERY_CONTENT = None
ONLINE_ISSUE_QUERY_CONTENT = None


def binary_search(arr, target, left, right):
    """二分查找插入位置（与 Java 实现一致）"""
    while left <= right:
        mid = left + (right - left) // 2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return left


def binary_insertion_sort(arr):
    """二分插入排序"""
    result = list(arr)
    for i in range(1, len(result)):
        key = result[i]
        pos = binary_search(result, key, 0, i - 1)
        for j in range(i, pos, -1):
            result[j] = result[j - 1]
        result[pos] = key
    return result


try:
    from issue_query import fetch_issues, fetch_online_issues
except ImportError:
    def fetch_issues(start_date=None, end_date=None):
        return {'error': '问题查询后端未找到，请确认 src/main/python/issue_query.py 存在'}
    def fetch_online_issues(start_date=None, end_date=None):
        return {'error': '问题查询后端未找到，请确认 src/main/python/issue_query.py 存在'}


class SortHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 减少默认日志输出

    def _send_cors(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

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
                sorted_arr = binary_insertion_sort(numbers)
                print('\n========== 二分插入排序 ==========', flush=True)
                print('输入:', numbers, flush=True)
                print('输出:', sorted_arr, flush=True)
                print('================================\n', flush=True)
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self._send_cors()
                self.end_headers()
                self.wfile.write(json.dumps({'sorted': sorted_arr}).encode())
            except Exception as e:
                print('排序错误:', e, flush=True)
                self.send_response(400)
                self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/quit':
            print('\n  收到关闭请求，正在停止服务器...\n', flush=True)
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'Server shutting down...')
            import threading
            threading.Thread(target=self.server.shutdown, daemon=True).start()
            return
        if path == '/api/issues':
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            start_date = query.get('start_date', [None])[0]
            end_date = query.get('end_date', [None])[0]
            data = fetch_issues(start_date=start_date, end_date=end_date)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors()
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        if path == '/api/online-issues':
            query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            start_date = query.get('start_date', [None])[0]
            end_date = query.get('end_date', [None])[0]
            data = fetch_online_issues(start_date=start_date, end_date=end_date)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors()
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
            return
        if path in ('/', '/index.html', '/issue-query', '/issue-query/'):
            content = ISSUE_QUERY_CONTENT
        elif path in ('/online-issue-query', '/online-issue-query/'):
            content = ONLINE_ISSUE_QUERY_CONTENT
        elif path == '/binary-sort' or path.startswith('/binary-sort'):
            content = SORT_CONTENT
        else:
            content = None
        if content is not None:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    # 启动时预加载 HTML
    try:
        with open(os.path.normpath(SORT_HTML_PATH), 'rb') as f:
            sort_raw = f.read()
        with open(os.path.normpath(ISSUE_QUERY_HTML_PATH), 'rb') as f:
            issue_raw = f.read()
        with open(os.path.normpath(ONLINE_ISSUE_QUERY_HTML_PATH), 'rb') as f:
            online_issue_raw = f.read()
        if '二分插入排序'.encode('utf-8') not in sort_raw:
            print('[错误] sort-page.html 校验失败')
            exit(1)
        if '问题查询'.encode('utf-8') not in issue_raw:
            print('[错误] issue-query.html 校验失败')
            exit(1)
        if '线上问题查询'.encode('utf-8') not in online_issue_raw:
            print('[错误] online-issue-query.html 校验失败')
            exit(1)
        SORT_CONTENT = sort_raw
        ISSUE_QUERY_CONTENT = issue_raw
        ONLINE_ISSUE_QUERY_CONTENT = online_issue_raw
        print(f'[OK] 已加载: sort-page.html, issue-query.html, online-issue-query.html')
    except Exception as e:
        print(f'[错误] 无法加载页面: {e}')
        print(f'[目录] {FRONTEND_DIR}')
        exit(1)
    server = HTTPServer(('localhost', PORT), SortHandler)
    print(f'\n  二分排序页面已启动')
    print(f'  在浏览器打开: http://localhost:{PORT}')
    print(f'  按 Ctrl+C 停止服务器\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  正在停止服务器...')
        server.shutdown()
        print('  已停止\n')
