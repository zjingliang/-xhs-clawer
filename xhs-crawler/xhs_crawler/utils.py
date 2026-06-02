import re
from datetime import datetime, timedelta

from xhs_crawler.settings import TARGET_DATE_FORMAT


def convert_date(date_str):
    if not date_str or str(date_str).strip() == "":
        return ""
    date_str = str(date_str).strip()

    if re.match(r"^\d{4}-\d{1,2}-\d{1,2}$", date_str):
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date().strftime(TARGET_DATE_FORMAT)
        except ValueError:
            return date_str
    if re.match(r"^\d{4}/\d{1,2}/\d{1,2}$", date_str):
        try:
            return datetime.strptime(date_str, "%Y/%m/%d").date().strftime(TARGET_DATE_FORMAT)
        except ValueError:
            return date_str
    if re.match(r"^\d{1,2}-\d{1,2}$", date_str):
        try:
            month, day = date_str.split("-")
            return datetime(datetime.now().year, int(month), int(day)).date().strftime(TARGET_DATE_FORMAT)
        except ValueError:
            return date_str
    cn_match = re.search(r"(\d+)月(\d+)日", date_str)
    if cn_match:
        try:
            return datetime(datetime.now().year, int(cn_match.group(1)), int(cn_match.group(2))).date().strftime(TARGET_DATE_FORMAT)
        except ValueError:
            return date_str
    if "昨天" in date_str:
        return (datetime.now().date() - timedelta(days=1)).strftime(TARGET_DATE_FORMAT)
    day_match = re.search(r"(\d+)天前", date_str)
    if day_match:
        return (datetime.now().date() - timedelta(days=int(day_match.group(1)))).strftime(TARGET_DATE_FORMAT)
    return date_str
