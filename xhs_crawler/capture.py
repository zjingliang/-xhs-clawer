import json
import time

from DrissionPage import ChromiumOptions, ChromiumPage

from xhs_crawler.auth import save_auth_data
from xhs_crawler.browser import find_chrome_path
from xhs_crawler.settings import CAPTURE_TARGETS, AUTH_HEADER_KEYS, CAPTURE_CFG


def extract_headers(req):
    headers = {}
    if not req:
        return headers
    h = getattr(req, 'headers', {}) or {}
    for key in AUTH_HEADER_KEYS:
        for k in h.keys():
            if k.lower() == key.lower():
                headers[key] = h[k]
                break
    return headers


def extract_search_id(req):
    if not req:
        return None
    body = getattr(req, 'postData', None) or getattr(req, 'body', None)
    if not body:
        return None
    if isinstance(body, dict):
        return body.get('search_id')
    if isinstance(body, bytes):
        body = body.decode('utf-8', errors='ignore')
    if isinstance(body, str):
        try:
            return json.loads(body).get('search_id')
        except (json.JSONDecodeError, TypeError):
            return None
    return None


def run_capture(on_log, on_progress, on_done):
    auth_data = {
        'search': None,
        'note_detail': None,
        'cookies': {},
        'save_time': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    browser = None
    max_wait = CAPTURE_CFG.get('max_wait_seconds', 300)
    log_interval = CAPTURE_CFG.get('log_interval_seconds', 10)
    site_url = CAPTURE_CFG.get('site_url', 'https://www.xiaohongshu.com')

    try:
        on_log("启动浏览器...")
        on_progress(10, "启动浏览器")

        chrome_path = find_chrome_path()
        if not chrome_path:
            on_log("找不到 Google Chrome，请确认已安装")
            on_done(auth_data)
            return

        co = ChromiumOptions()
        co.set_browser_path(chrome_path)
        co.set_argument('--disable-blink-features=AutomationControlled')
        co.set_argument('--disable-gpu')
        co.set_argument('--start-maximized')

        browser = ChromiumPage(addr_or_opts=co)
        on_log("开始监听...")
        on_progress(20, "开始监听")
        browser.listen.start()
        try:
            browser.listen.clear()
        except Exception:
            pass

        on_log("打开小红书，请登录后搜索并点击帖子")
        on_progress(30, "等待操作")
        browser.get(site_url)
        time.sleep(2)

        captured = {}
        start_time = time.time()
        last_log_time = start_time

        while len(captured) < len(CAPTURE_TARGETS):
            if time.time() - start_time > max_wait:
                on_log("等待超时，请重新捕获")
                break
            if time.time() - last_log_time > log_interval:
                if captured:
                    labels = [t['label'] for t in CAPTURE_TARGETS if t['name'] in captured]
                    on_log(f"等待中… 已捕获：{'、'.join(labels)}")
                else:
                    on_log("等待中… 尚未捕获鉴权")
                last_log_time = time.time()

            try:
                entry = browser.listen.wait(timeout=2)
            except Exception:
                continue
            if entry is None:
                continue

            url = getattr(entry, 'url', '') or ''
            method = getattr(entry, 'method', '') or ''
            if not url or not method:
                continue

            req = getattr(entry, 'request', None)
            for target in CAPTURE_TARGETS:
                if target['name'] in captured:
                    continue
                if target['pattern'] in url and method.upper() == target['method'].upper():
                    info = {'url': url, 'headers': extract_headers(req)}
                    if target['name'] == 'search':
                        search_id = extract_search_id(req)
                        if search_id:
                            info['search_id'] = search_id
                    captured[target['name']] = info
                    on_log(f"已捕获{target['label']}")
                    on_progress(60 if target['name'] == 'search' else 80, target['label'])
                    break

        cookies = {}
        try:
            for cookie in browser.cookies():
                cookies[cookie['name']] = cookie['value']
        except Exception:
            pass

        auth_data['search'] = captured.get('search')
        auth_data['note_detail'] = captured.get('note_detail')
        auth_data['cookies'] = cookies
        auth_data['save_time'] = time.strftime('%Y-%m-%d %H:%M:%S')

        save_auth_data(auth_data)

        on_log("搜索鉴权：已保存" if auth_data['search'] else "搜索鉴权：未捕获")
        on_log("帖子详情鉴权：已保存" if auth_data['note_detail'] else "帖子详情鉴权：未捕获")
        on_log(f"鉴权信息已保存（{len(cookies)} 项 Cookie）")
        on_progress(100, "完成")
        on_done(auth_data)
    except Exception:
        on_log("捕获失败，请重试")
        on_done(auth_data)
    finally:
        if browser:
            try:
                browser.listen.stop()
                browser.quit()
            except Exception:
                pass
