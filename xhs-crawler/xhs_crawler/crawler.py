import csv
import json
import os
import time

import requests

from xhs_crawler.settings import (
    CSV_HEADER, CRAWLER_CFG, SEARCH_API_FALLBACK, FEED_API_FALLBACK, ROOT_DIR
)
from xhs_crawler.utils import convert_date


def fetch_note_desc(auth_data, post_id, xsec_token, cookies):
    headers = dict((auth_data.get('note_detail') or {}).get('headers', {}))
    if not headers:
        return ''
    headers['x-t'] = str(int(time.time() * 1000))
    feed_url = auth_data.get('note_detail', {}).get('url', FEED_API_FALLBACK)
    data = json.dumps({
        'source_note_id': post_id,
        'image_formats': ['jpg', 'webp', 'avif'],
        'extra': {'need_body_topic': '1'},
        'xsec_token': xsec_token,
    }, separators=(',', ':'))
    try:
        resp = requests.post(feed_url, headers=headers, cookies=cookies, data=data)
        items = resp.json().get('data', {}).get('items', [])
        if items:
            return items[0].get('note_card', {}).get('desc', '') or ''
    except Exception:
        pass
    return ''


def run_crawl(keyword, page_count, item_interval, auth_data, stop_event, on_log, on_progress, on_done):
    crawled_count = 0
    suffix = CRAWLER_CFG.get('output_suffix', '_小红书数据.csv')
    csv_path = os.path.join(ROOT_DIR, f"{keyword}{suffix}")
    page_size = CRAWLER_CFG.get('page_size', 20)
    page_delay = CRAWLER_CFG.get('page_delay_seconds', 3)

    search_id = auth_data.get('search', {}).get('search_id')
    if not search_id:
        on_log("鉴权不完整，请先在抓包模式中重新捕获")
        on_done(0)
        return
    if not auth_data.get('note_detail'):
        on_log("缺少帖子详情鉴权，无法获取发布内容，请重新捕获并点击帖子")
        on_done(0)
        return

    if not os.path.exists(csv_path):
        with open(csv_path, mode="w", encoding="utf-8-sig", newline="") as f:
            csv.writer(f).writerow(CSV_HEADER)

    headers = auth_data.get('search', {}).get('headers', {})
    cookies = auth_data.get('cookies', {})
    url = auth_data.get('search', {}).get('url', SEARCH_API_FALLBACK)

    for page in range(1, page_count + 1):
        if stop_event.is_set():
            on_log("爬取已停止")
            break

        on_log(f"正在爬取第 {page} 页...")
        on_progress(int((page / page_count) * 30) + 10, f"第 {page} 页")
        time.sleep(page_delay)

        data = {
            "keyword": keyword,
            "page": page,
            "page_size": page_size,
            "search_id": search_id,
            "sort": "general",
            "note_type": 0,
            "ext_flags": [],
            "geo": "",
            "image_formats": ["jpg", "webp", "avif"]
        }
        try:
            response = requests.post(url, headers=headers, cookies=cookies, data=json.dumps(data, separators=(',', ':')))
            response.raise_for_status()
            post_json = response.json()
        except Exception:
            on_log(f"第 {page} 页搜索请求失败")
            continue

        for post_information in post_json.get("data", {}).get("items", []):
            if stop_event.is_set():
                break
            try:
                main_information = post_information.get("note_card", {})
                if not main_information:
                    continue

                post_title = main_information.get("display_title", "")
                post_writer = main_information.get("user", {}).get("nick_name", "")
                corner_tag_info = main_information.get("corner_tag_info", [])
                post_time = convert_date(corner_tag_info[0].get("text", "") if corner_tag_info else "")
                post_type = main_information.get("type", "")
                interact_info = main_information.get("interact_info", {})
                post_like = str(interact_info.get("liked_count", "0"))
                post_star = str(interact_info.get("collected_count", "0"))
                post_comment = str(interact_info.get("comment_count", "0"))
                post_share = str(interact_info.get("shared_count", "0"))
                hot_value = str(int(post_like) + int(post_star) + int(post_comment) + int(post_share))

                post_id = post_information.get("id", "")
                post_xsec_token = post_information.get("xsec_token", "")
                post_url = f"https://www.xiaohongshu.com/explore/{post_id}?xsec_token={post_xsec_token}"
                post_content = fetch_note_desc(auth_data, post_id, post_xsec_token, cookies)

                image_url_list = []
                for img in main_information.get("image_list", []):
                    if img.get("info_list"):
                        image_url_list.append(img["info_list"][0].get("url", ""))

                with open(csv_path, mode="a", encoding="utf-8-sig", newline="") as f:
                    csv.writer(f).writerow([
                        post_title, post_writer, post_time, post_type, hot_value,
                        post_like, post_star, post_comment, post_share,
                        post_content, post_url, str(image_url_list)
                    ])

                crawled_count += 1
                on_log(f"已保存第 {crawled_count} 条：{post_title[:30]}")
                on_progress(int((crawled_count / (page_count * page_size)) * 100), f"已爬取 {crawled_count} 条")
                if item_interval > 0:
                    time.sleep(item_interval)
            except Exception:
                on_log("处理帖子失败，已跳过")

    on_log(f"爬取完成，共保存 {crawled_count} 条")
    on_progress(100, "完成")
    on_done(crawled_count)
