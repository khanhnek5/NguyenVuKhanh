import os
import json
import requests
from datetime import datetime
import random  # Add: Import random

print("=== START generate.py ===")

api_token = os.getenv("YEUMONEY_API_TOKEN", "").strip()
index_url = os.getenv("INDEX_HTML_URL", "").strip()

print(f"[DEBUG] YEUMONEY_API_TOKEN: {'SET' if api_token else 'MISSING'}")
print(f"[DEBUG] INDEX_HTML_URL: {index_url or '(missing)'}")

today = datetime.now().strftime("%Y-%m-%d")
date_part = today.replace('-', '')  # YYYYMMDD
random_suffix = ''.join(random.choices('ABCDEF123456', k=6))  # Add: Random 6 ký tự (A-F0-6)
key = f"K-{date_part}-{random_suffix}"  # e.g., K-20251031-ABC123

print(f"[DEBUG] Generated key: {key}")  # Add: Debug để check

# Ghi file key.json (và copy to key_today.json cho index.html)
try:
    data = {"date": today, "key": key}
    with open("key.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    with open("key_today.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("[OK] key.json & key_today.json created.")
except Exception as e:
    print("[ERR] Cannot write key files:", e)

# ... (giữ nguyên phần API YeuMoney, shortlink.json, yeu_shortlink.txt, redirect.html)
# Gọi API YeuMoney
shortlink = None
if api_token:
    try:
        resp = requests.post(
            "https://yeumoney.com/api/link",
            data={"api": api_token, "url": index_url},
            timeout=15
        )
        print("[DEBUG] YeuMoney status:", resp.status_code)
        print("[DEBUG] YeuMoney raw response:", resp.text[:200])
        data = resp.json()
        if data.get("shortenedUrl"):
            shortlink = data["shortenedUrl"]
            print("[OK] Shortlink:", shortlink)
        else:
            print("[WARN] No shortenedUrl in response.")
    except Exception as e:
        print("[ERR] YeuMoney API error:", e)
else:
    print("[WARN] Missing YeuMoney API token, skipping shortlink.")

# Ghi file shortlink.json
try:
    with open("shortlink.json", "w", encoding="utf-8") as f:
        json.dump({"date": today, "shortlink": shortlink}, f, ensure_ascii=False, indent=2)
    print("[OK] shortlink.json created.")
except Exception as e:
    print("[ERR] Cannot write shortlink.json:", e)

# Append to yeu_shortlink.txt (log history)
try:
    with open("yeu_shortlink.txt", "a", encoding="utf-8") as f:
        f.write(f"{today}: {shortlink or 'N/A'}\n")
    print("[OK] Appended to yeu_shortlink.txt.")
except Exception as e:
    print("[WARN] Cannot append to yeu_shortlink.txt:", e)

# Ghi redirect.html
try:
    redirect_to = shortlink or index_url or '#'
    html = f"""<html>
<head><meta http-equiv="refresh" content="0;url={redirect_to}"></head>
<body><p>Redirecting to YeuMoney...</p></body>
</html>"""
    with open("redirect.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] redirect.html created (redirects to: {redirect_to})")
except Exception as e:
    print("[ERR] Cannot write redirect.html:", e)

print("=== END generate.py ===")
