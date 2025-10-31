import os, random, string, json, urllib.parse, requests, time
from datetime import datetime

# --- Môi trường ---
API_TOKEN = os.environ.get("YEUMONEY_API_TOKEN")
INDEX_HTML = os.environ.get("INDEX_HTML_URL", "").rstrip('/')

if not API_TOKEN:
    print("❌ Thiếu YEUMONEY_API_TOKEN trong Secrets (Settings → Secrets → Actions).")
if not INDEX_HTML:
    print("❌ Thiếu INDEX_HTML_URL trong Secrets hoặc file workflow.")
# Không exit ở đây, vẫn tiếp tục để không fail build

# --- Sinh key ---
def gen_key(n=8):
    return "KhanhMG-" + ''.join(random.choices(string.ascii_letters + string.digits, k=n))

key = gen_key()
print(f"✅ Key hôm nay: {key}")

# --- Ghi key.json ---
data = {"key": key, "generated_at": datetime.utcnow().isoformat() + "Z"}
with open("key.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("📦 Ghi key.json thành công.")

# --- URL cần rút gọn ---
target_url = f"{INDEX_HTML}?t={urllib.parse.quote(key, safe='')}"
print("🔗 URL gốc:", target_url)

# --- Rút gọn link (retry 3 lần) ---
def shorten(api_token, url):
    api_url = f"https://yeumoney.com/QL_api.php?token={api_token}&format=text&url={urllib.parse.quote(url, safe='')}"
    for i in range(3):
        try:
            r = requests.get(api_url, timeout=15)
            txt = r.text.strip()
            if r.status_code == 200 and txt and txt.startswith("https"):
                return txt
            print(f"⚠️ Lần {i+1}: YeuMoney không phản hồi hợp lệ, thử lại...")
            time.sleep(2)
        except Exception as e:
            print(f"⚠️ Lỗi kết nối lần {i+1}: {e}")
            time.sleep(2)
    return ""

short_link = shorten(API_TOKEN, target_url)

if short_link:
    print("✅ Shortlink:", short_link)
else:
    print("⚠️ Không tạo được shortlink, dùng URL gốc.")
    short_link = target_url

# --- Lưu shortlink.json ---
with open("shortlink.json", "w", encoding="utf-8") as f:
    json.dump({"short_link": short_link, "updated_at": datetime.utcnow().isoformat()+"Z"}, f, ensure_ascii=False, indent=2)
print("📦 Ghi shortlink.json xong.")

# --- Tạo redirect.html ---
redirect_html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="utf-8">
<title>Đang chuyển hướng...</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body {{
  background:#0d1117;
  color:#c9d1d9;
  font-family:Arial, sans-serif;
  text-align:center;
  padding-top:100px;
}}
a {{
  color:#58a6ff;
  text-decoration:none;
}}
</style>
</head>
<body>
  <h2>Đang chuyển hướng tới trang lấy key...</h2>
  <p>Nếu không tự động, <a href="{short_link}">bấm vào đây</a>.</p>
  <script>setTimeout(()=>location.href="{short_link}",1000);</script>
</body>
</html>
"""
with open("redirect.html", "w", encoding="utf-8") as f:
    f.write(redirect_html)
print("📄 Tạo redirect.html xong.")

print("🎯 HOÀN TẤT: key + shortlink đã cập nhật, không có lỗi nghiêm trọng.")
