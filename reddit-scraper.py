# -*- coding: utf-8 -*-
import csv
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime

SEARCH_QUERY = '绝区零 OR "Zenless Zone Zero" OR ZenlessZoneZero'
SORT = "hot"
TIME_RANGE = "week"
LIMIT = 25
SAVE_CSV = True
CSV_PATH = "zzz_reddit_hot.csv"
USER_AGENT = "ZZZHotPostFetcher/1.0 (student homework; contact: local)"
TIMEOUT_SECONDS = 20


def build_search_url():
    params = {
        "q": SEARCH_QUERY,
        "sort": SORT,
        "t": TIME_RANGE,
        "limit": str(LIMIT),
        "type": "link",
        "raw_json": "1",
    }
    return "https://www.reddit.com/search.json?" + urllib.parse.urlencode(params)


def fetch_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            body = response.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"HTTP 错误 {exc.code}：{exc.reason}\n"
            "可稍等一两分钟再试，或把 USER_AGENT 改成更具体的说明。"
        )
    except urllib.error.URLError as exc:
        raise SystemExit(f"网络错误：{exc.reason}")


def parse_posts(payload):
    children = payload.get("data", {}).get("children", [])
    posts = []
    for item in children:
        data = item.get("data", {})
        title = (data.get("title") or "").strip()
        if not title:
            continue
        posts.append(
            {
                "title": title,
                "score": int(data.get("score") or 0),
                "num_comments": int(data.get("num_comments") or 0),
                "subreddit": data.get("subreddit") or "",
                "permalink": "https://www.reddit.com" + (data.get("permalink") or ""),
            }
        )
    return posts


def print_posts(posts):
    if not posts:
        print("没有抓到帖子。可把 TIME_RANGE 改成 all，或检查网络。")
        return

    print(f"共 {len(posts)} 条（排序={SORT}，时间范围={TIME_RANGE}）")
    print("-" * 80)
    print(f"{'点赞':>6}  {'评论':>6}  标题")
    print("-" * 80)
    for post in posts:
        title = post["title"].replace("\n", " ")
        if len(title) > 70:
            title = title[:67] + "..."
        print(f"{post['score']:>6}  {post['num_comments']:>6}  {title}")
    print("-" * 80)


def save_csv(posts, path):
    with open(path, "w", newline="", encoding="utf-8-sig") as fp:
        writer = csv.DictWriter(
            fp,
            fieldnames=["title", "score", "num_comments", "subreddit", "permalink"],
        )
        writer.writeheader()
        writer.writerows(posts)
    print(f"已写入：{path}")


def main():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 正在请求 Reddit ...")
    url = build_search_url()
    payload = fetch_json(url)
    time.sleep(0.5)

    posts = parse_posts(payload)
    print_posts(posts)
    if SAVE_CSV and posts:
        save_csv(posts, CSV_PATH)


if __name__ == "__main__":
    main()
