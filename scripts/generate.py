import os, random, string, json, urllib.parse, requests, time
from datetime import datetime

# --- Biến môi trường ---
API_TOKEN = os.environ.get("YEUMONEY_API_TOKEN")
INDEX_HTML = os.environ.get("INDEX_HTML_URL", "").rstrip('/')

if not API_TOKEN:
    print("❌ Thiếu YEUMONEY_API_TOKEN trong Secrets.")
    exit(1)
if not INDEX_HTML:
    print("❌ Thiếu INDEX_HTML_URL trong Secrets.")
    exit(1)

# --- Sinh key ---
def gen_key(n=8):
    chars = string.ascii_letters + string.digits
    return "KhanhMG-" + ''.join(random.choices(chars, k=n))

key = gen_key()
print("✅ Key hôm nay:", key)

# --- Ghi file key.json ---
data = {"key": key, "generated_at": datetime.utcnow().isoformat() + "Z"}
with open("key.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("📦 Đã lưu key.json")

# --- Tạo URL để rút gọn ---
target_url = f"{INDEX_HTML}?t={urllib.parse.quote(key, safe='')}"
print("🔗 Gốc:", target_url)

# --- Gọi API YeuMoney (retry tối đa 3 lần) ---
def shorten_url(api_token, url):
    api_url = f"https://yeumoney.com/QL_api.php?token={api_token}&format=text&url={urllib.parse.quote(url, safe='')}"
    for i in range(3):
        try:
            r = requests.get(api_url, timeout=15)
            if r.status_code == 200 and r.text.strip():
                return r.text.strip()
            print(f"⚠️ Lần thử {i+1} thất bại, thử lại sau...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Lỗi kết nối ({i+1}/3):", e)
            time.sleep(2)
    return ""

short_link = shorten_url(API_TOKEN, target_url)

if not short_link:
    print("❌ Không tạo được shortlink. Dùng URL gốc tạm thời.")
    short_link = target_url

# --- Ghi shortlink.json ---
link_data = {"short_link": short_link, "updated_at": datetime.utcnow().isoformat() + "Z"}
with open("shortlink.json", "w", encoding="utf-8") as f:
    json.dump(link_data, f, ensure_ascii=False, indent=2)
print("📦 Đã lưu shortlink.json:", short_link)

# --- Ghi redirect.html ---
redirect_html = f"""<!DOCTYPE html>
<meta charset="utf-8">
<title>Đang chuyển hướng...</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body {{
  font-family: Arial, sans-serif;
  background: #090f1a;
  color: #e8f0ff;
  text-align: center;
  padding-top: 100px;
}}
a {{ color: #4db2ff; }}
</style>
<h2>Đang chuyển hướng tới trang lấy key...</h2>
<p>Nếu không tự động, <a href="{short_link}">bấm vào đây</a>.</p>
<script>
setTimeout(()=>location.href="{short_link}",1000);
</script>
"""
with open("redirect.html", "w", encoding="utf-8") as f:
    f.write(redirect_html)
print("📄 Đã tạo redirect.html")

print("🎯 Hoàn tất: key + shortlink đã được cập nhật thành công!")
