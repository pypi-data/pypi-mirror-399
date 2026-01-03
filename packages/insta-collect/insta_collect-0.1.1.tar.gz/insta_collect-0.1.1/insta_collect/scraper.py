from playwright.sync_api import sync_playwright
import time
import random
import re

# ================= UTIL =================
def count_sentences(text):
    if not text:
        return 0
    sentences = re.split(r"[.!?]+", text)
    return len([s for s in sentences if s.strip()])

def extract_hashtags_mentions(text):
    if not text:
        return [], []
    hashtags = re.findall(r"#(\w+)", text)
    mentions = re.findall(r"@(\w+)", text)
    return hashtags, mentions

def is_login_wall(page):
    return (
        page.locator("input[name='username']").count() > 0
        or "login" in page.url
    )

# ================= DETAIL SCRAPER =================
def get_post_details(page, url):
    data = {
        "caption": None,
        "caption_status": None,
        "timestamp": None,
        "is_video": False,
        "hashtags": [],
        "mentions": []
    }

    try:
        print(f"   [..] Visiting: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=20000)

        if is_login_wall(page):
            data["caption_status"] = "login_required"
            return data

        # ---------- META ----------
        caption_text = None
        try:
            meta_desc = page.locator('meta[property="og:description"]').get_attribute("content")
            if meta_desc and ": " in meta_desc:
                caption_text = meta_desc.split(": ", 1)[1].strip().strip('"')
        except:
            pass

        # ---------- DOM FALLBACK ----------
        if not caption_text:
            try:
                candidates = page.locator("article span").all()
                longest = None
                for el in candidates:
                    txt = el.inner_text().strip()
                    if len(txt) < 80:
                        continue
                    if not longest or len(txt) > len(longest):
                        longest = txt
                caption_text = longest
            except:
                pass

        # ---------- VALIDASI ----------
        sentence_count = count_sentences(caption_text)
        if not caption_text or sentence_count < 2:
            data["caption_status"] = "no_text"
            return data

        data["caption"] = caption_text
        data["caption_status"] = "long_text" if sentence_count >= 8 else "short_text"

        # ---------- HASHTAG & MENTION ----------
        hashtags, mentions = extract_hashtags_mentions(caption_text)
        data["hashtags"] = hashtags
        data["mentions"] = mentions

        # ---------- TIMESTAMP ----------
        try:
            time_el = page.locator("time").first
            if time_el.count() > 0:
                data["timestamp"] = time_el.get_attribute("datetime")
        except:
            pass

        # ---------- VIDEO FLAG ----------
        if page.locator("video").count() > 0:
            data["is_video"] = True

    except Exception as e:
        data["caption_status"] = "error"
        print(f"   [!] Error: {e}")

    return data

# ================= HASHTAG SCRAPER =================
def scrape_hashtag(hashtag, limit=10, profile_dir="ig_profile"):
    results = []

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        print(f"[1/3] Scanning hashtag #{hashtag}")
        page.goto(f"https://www.instagram.com/explore/tags/{hashtag}/", wait_until="domcontentloaded")
        time.sleep(3)

        # ---------- LOGIN MANUAL ----------
        if is_login_wall(page):
            print("[!] Login is required. Please log in in an open browser....")
            input("Press Enter after login is complete to continue....")

        collected_links = set()
        while len(collected_links) < limit * 2:
            for a in page.locator("a[href*='/p/']").all():
                href = a.get_attribute("href")
                if href:
                    collected_links.add("https://www.instagram.com" + href)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1.5)

        print(f"[INFO] Found {len(collected_links)} links")

        print("[2/3] Scraping detail posts")
        for i, link in enumerate(collected_links):
            if len(results) >= limit:
                break
            print(f"   -> {i+1}/{len(collected_links)}")
            d = get_post_details(page, link)
            if d["caption_status"] in ("login_required", "error") or d["is_video"]:
                continue
            results.append({"url": link, **d, "source_tag": hashtag})
            time.sleep(random.uniform(1.5, 2.5))

        context.close()

    print(f"[DONE] Collected {len(results)} posts from #{hashtag}")
    return results


