import json, time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def _score_m3u8(u: str) -> int:
    u = (u or "").lower()
    s = 0
    if u.endswith(".m3u8"): s += 10
    if "master" in u: s += 8
    if "index" in u: s += 4
    if "playlist" in u: s += 4
    if "chunk" in u or "seg" in u: s -= 3
    return s

def sniff_m3u8_g(page_url: str, wait_seconds: float = 6, timeout_seconds: float = 10) -> str:
    opts = Options()
    opts.add_argument("--autoplay-policy=no-user-gesture-required")
    opts.add_argument("--mute-audio")
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    opts.set_capability("pageLoadStrategy", "eager")

    driver = webdriver.Chrome(options=opts)
    try:
        driver.get(page_url)
        time.sleep(wait_seconds)

        best = ""
        seen = set()
        end = time.time() + timeout_seconds

        while time.time() < end:
            for entry in driver.get_log("performance"):
                try:
                    msg = json.loads(entry["message"])["message"]
                except Exception:
                    continue

                if msg.get("method") != "Network.responseReceived":
                    continue

                resp = (msg.get("params") or {}).get("response") or {}
                url = (resp.get("url") or "")
                mime = (resp.get("mimeType") or "").lower()

                if not url:
                    continue

                if url.endswith(".m3u8") or ("mpegurl" in mime):
                    if url in seen:
                        continue
                    seen.add(url)

                    if (not best) or (_score_m3u8(url) > _score_m3u8(best)):
                        best = url

            if best:
                # brief grace to catch a better "master"
                time.sleep(0.6)
                break

            time.sleep(0.8)

        return best
    finally:
        driver.quit()
