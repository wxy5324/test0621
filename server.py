"""
本地开发服务器 - 仅负责启动
运行: python server.py
"""
import os
import sys
from http.server import HTTPServer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_SRC = os.path.join(SCRIPT_DIR, 'src', 'main', 'python')
if PYTHON_SRC not in sys.path:
    sys.path.insert(0, PYTHON_SRC)

PORT = 3000
FRONTEND_DIR = os.path.join(SCRIPT_DIR, 'frontend')
if not os.path.exists(FRONTEND_DIR):
    FRONTEND_DIR = os.path.join(os.getcwd(), 'frontend')

HTML_FILES = [
    ('sort-page.html', '二分插入排序'),
    ('issue-query.html', '问题查询'),
    ('online-issue-query.html', '线上问题查询'),
    ('url-encrypt-decrypt.html', 'URL 加解密'),
    ('timestamp-convert.html', '时间戳转换'),
    ('json-parse.html', 'JSON 在线解析'),
    ('data-process.html', '数据处理'),
    ('mobile-cipher.html', '手机号加解密'),
    ('test-cases.html', '测试用例'),
]


def load_html_contents():
    """预加载所有 HTML 并构建路由映射"""
    contents = {}
    raw = {}

    for filename, check_str in HTML_FILES:
        path = os.path.join(FRONTEND_DIR, filename)
        with open(os.path.normpath(path), 'rb') as f:
            data = f.read()
        if check_str.encode('utf-8') not in data:
            print(f'[错误] {filename} 校验失败')
            sys.exit(1)
        raw[filename] = data

    #  路由映射
    contents['/'] = raw['issue-query.html']
    contents['/index.html'] = raw['issue-query.html']
    contents['/issue-query'] = raw['issue-query.html']
    contents['/issue-query/'] = raw['issue-query.html']
    contents['/online-issue-query'] = raw['online-issue-query.html']
    contents['/online-issue-query/'] = raw['online-issue-query.html']
    contents['*binary-sort'] = raw['sort-page.html']
    contents['/url-encrypt-decrypt'] = raw['url-encrypt-decrypt.html']
    contents['/url-encrypt-decrypt/'] = raw['url-encrypt-decrypt.html']
    contents['/timestamp-convert'] = raw['timestamp-convert.html']
    contents['/timestamp-convert/'] = raw['timestamp-convert.html']
    contents['/json-parse'] = raw['json-parse.html']
    contents['/json-parse/'] = raw['json-parse.html']
    contents['/data-process'] = raw['data-process.html']
    contents['/data-process/'] = raw['data-process.html']
    contents['/mobile-cipher'] = raw['mobile-cipher.html']
    contents['/mobile-cipher/'] = raw['mobile-cipher.html']
    contents['/test-cases'] = raw['test-cases.html']
    contents['/test-cases/'] = raw['test-cases.html']

    return contents


def main():
    from app_handlers import create_handler

    try:
        html_contents = load_html_contents()
        print('[OK] 已加载:', ', '.join(f for f, _ in HTML_FILES))
    except Exception as e:
        print(f'[错误] 无法加载页面: {e}')
        print(f'[目录] {FRONTEND_DIR}')
        sys.exit(1)

    try:
        import openpyxl  # noqa: F401
    except ImportError:
        py_path = sys.executable
        print('[提示] 当前 Python 未安装 openpyxl，正在尝试自动安装...')
        import subprocess
        try:
            r = subprocess.run(
                [py_path, '-m', 'pip', 'install', 'openpyxl', '-q'],
                capture_output=True,
                text=True,
                timeout=120,
                cwd=SCRIPT_DIR,
            )
            if r.returncode == 0:
                print('[OK] openpyxl 安装成功')
            else:
                raise RuntimeError(r.stderr or r.stdout or '安装失败')
        except Exception as e:
            print('[失败] 自动安装失败，请手动执行:')
            print(f'       "{py_path}" -m pip install openpyxl')
            print(f'       错误: {e}')

    handler = create_handler(html_contents)
    server = HTTPServer(('127.0.0.1', PORT), handler)
    print(f'\n  系统已启动')
    print(f'  在浏览器打开: http://127.0.0.1:{PORT} 或 http://localhost:{PORT}')
    print(f'  按 Ctrl+C 停止服务器\n')

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n  正在停止服务器...')
        server.shutdown()
        print('  已停止\n')


if __name__ == '__main__':
    main()
