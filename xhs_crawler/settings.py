import os
import json

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT_DIR, 'config', 'config.json')

CAPTURE_TARGETS = [
    {'name': 'search', 'pattern': 'so.xiaohongshu.com/api/sns/web/v2/search/notes', 'method': 'POST', 'label': '搜索鉴权'},
    {'name': 'note_detail', 'pattern': 'edith.xiaohongshu.com/api/sns/web/v1/feed', 'method': 'POST', 'label': '帖子详情鉴权'},
]

AUTH_HEADER_KEYS = [
    'x-s', 'x-s-common', 'x-t', 'x-b3-traceid', 'x-xray-traceid',
    'x-rap-param', 'xy-direction', 'Content-Type', 'Referer',
    'User-Agent', 'origin', 'accept',
]

CSV_HEADER = [
    "发布标题", "发布作者", "发布时间", "发布类型", "热力值",
    "点赞量", "收藏量", "评论数量", "分享数量",
    "发布内容", "发布链接", "图片链接",
]

TARGET_DATE_FORMAT = "%Y/%m/%d"


def load_config():
    with open(CONFIG_PATH, encoding='utf-8') as f:
        return json.load(f)


_cfg = load_config()
AUTH_FILE = os.path.join(ROOT_DIR, _cfg.get('auth_file', 'xhs_auth.json'))
CAPTURE_CFG = _cfg.get('capture', {})
CRAWLER_CFG = _cfg.get('crawler', {})
SEARCH_API_FALLBACK = _cfg.get('search_api_fallback', 'https://so.xiaohongshu.com/api/sns/web/v2/search/notes')
FEED_API_FALLBACK = _cfg.get('feed_api_fallback', 'https://edith.xiaohongshu.com/api/sns/web/v1/feed')
