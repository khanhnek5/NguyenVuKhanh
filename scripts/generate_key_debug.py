import os
import json
import requests
from datetime import datetime

print("=== START generate.py ===")

api_token = os.getenv("YEUMONEY_API_TOKEN", "").strip()
index_url = os.getenv("INDEX_HTML_URL", "").strip()

print(f"[DEBUG] YEUMONEY_API_TOKEN: {'SET' if api_token else 'MISSING'}")
print(f"[DEBUG] INDEX_HTML_URL: {index_url or '(missing)'}")

today = datetime.now().strftime("%Y-%m-%d")
key = f"K-{today.replace('-', '')}"

# Ghi file key.json
try:
    with open("key.json", "w", encoding="utf-8") as f:
        json.dump({"date": today, "key": key}, f, ensure_ascii=False, indent=2)
    print("[OK] key.json created.")
except Exception as e:
    print("[ERR] Cannot write key.json:", e)

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

# Ghi redirect.html
try:
    html = f"""<html>
<head><meta http-equiv="refresh" content="0;url={shortlink or '#'}"></head>
<body><p>Redirecting to YeuMoney...</p></body>
</html>"""
    with open("redirect.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("[OK] redirect.html created.")
except Exception as e:
    print("[ERR] Cannot write redirect.html:", e)

print("=== END generate.py ===")with open("redirect.html", "w", encoding="utf-8") as f:
    f.write(redirect_html)
print("📄 Tạo redirect.html xong.")

print("🎯 HOÀN TẤT: key + shortlink đã cập nhật, không có lỗi nghiêm trọng.")
