import os
import random
import string
import json
import urllib.parse
import requests
from datetime import datetime

# --- Lấy token YeuMoney và URL index từ env ---
API_TOKEN = os.environ.get("YEUMONEY_API_TOKEN")
INDEX_HTML = os.environ.get("INDEX_HTML_URL", "").rstrip('/')

if not API_TOKEN:
    print("ERROR: YEUMONEY_API_TOKEN missing")
    exit(1)
if not INDEX_HTML:
    print("ERROR: INDEX_HTML_URL missing")
    exit(1)

# --- 1) Sinh key mới ---
def gen_key(n=12):
    chars = string.ascii_letters + string.digits
    return "KhanhMG-" + ''.join(random.choices(chars, k=n))

key = gen_key()
print("✅ Key hôm nay:", key)

# --- 2) Ghi key_today.json ---
data = {"key": key, "generated_at": datetime.utcnow().isoformat()+"Z"}
with open("key_today.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("✅ Wrote key_today.json")

# --- 3) Tạo target URL index.html + key ---
target = INDEX_HTML + "?t=" + urllib.parse.quote(key, safe='')

# --- 4) Gọi API YeuMoney ---
api_url = f"https://yeumoney.com/QL_api.php?token={API_TOKEN}&format=text&url={urllib.parse.quote(target, safe='')}"
try:
    r = requests.get(api_url, timeout=15)
    r.raise_for_status()
    short = r.text.strip()
    if not short:
        print("ERROR: YeuMoney trả về rỗng")
        exit(2)

    # --- Lưu shortlink ---
    with open("yeu_shortlink.txt", "w", encoding="utf-8") as f:
        f.write(short + "\n")
    print("✅ Wrote yeu_shortlink.txt ->", short)

    # --- 5) Tạo redirect.html ---
    redirect_html = f"""<!doctype html>
<meta charset="utf-8">
<title>Redirecting...</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
  body{{font-family:Arial;padding:40px;background:#071022;color:#eef3f5;text-align:center}}
</style>
<h2>Chuyển hướng tới trang lấy key...</h2>
<p>Nếu không tự động, <a href="{short}">click vào đây</a>.</p>
<script>
  setTimeout(()=>location.href="{short}",700);
</script>
"""
    with open("redirect.html", "w", encoding="utf-8") as f:
        f.write(redirect_html)
    print("✅ Wrote redirect.html")

except Exception as e:
    print("ERROR khi gọi YeuMoney API:", e)
    exit(3)
