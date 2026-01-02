import time, re, subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

IPHONE_SAFARI_UA = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
    "Mobile/15E148 Safari/604.1"
)

M3U8P_END = re.compile(r"https?://[^\s\"\\]+?\.m3u8\?p$", re.I)

def _kill_leftovers():
    subprocess.run(["pkill", "-9", "-f", "chromedriver"], check=False)

def _extract_m3u8p(driver, keyword: str, seconds: int) -> str:
    end = time.time() + seconds
    seen = set()
    kw = (keyword or "").lower()

    while time.time() < end:
        for entry in driver.get_log("performance"):
            raw = (entry.get("message") or "")
            if not raw or raw in seen:
                continue
            seen.add(raw)

            raw = raw.replace("\\/", "/")
            for url in re.findall(r"https?://[^\"\\\s]+", raw):
                url = url.rstrip('",\'')
                if kw in url.lower() and M3U8P_END.search(url):
                    return url
        time.sleep(0.25)
    return ""

def okru_m3u8p(
    input_url: str,
    *,
    keyword: str = "okcdn",
    timeout: int = 25,
    headless: bool = False,
) -> str:
    """Return the first URL that ends exactly with '.m3u8?p' from OK.ru playback."""
    _kill_leftovers()

    opts = Options()
    opts.set_capability("goog:loggingPrefs", {"performance": "ALL"})
    if headless:
        opts.add_argument("--headless=new")

    driver = None
    try:
        driver = webdriver.Chrome(options=opts)
        driver.execute_cdp_cmd("Network.enable", {})
        driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {"userAgent": IPHONE_SAFARI_UA, "platform": "iPhone"},
        )
        driver.get(input_url)
        time.sleep(2)
        return _extract_m3u8p(driver, keyword, timeout)
    finally:
        try:
            if driver:
                driver.quit()
        except Exception:
            pass
        _kill_leftovers()
