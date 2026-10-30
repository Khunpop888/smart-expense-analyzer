# -*- coding: utf-8 -*-
import os
import sys
import glob
import json
import base64
import urllib.request
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INDEX_PATH = os.path.join(BASE_DIR, 'index.html')
SHOPEE_DIR = r'C:\Users\napon.su\Downloads\ค่าใช้จ่าย Shopee'

# Fallback API Key
DEFAULT_KEY = base64.b64decode('QVEuQWI4Uk42TE9RTE01XzVJanAzSEVPQWNVelRsYWlFbXBOYjVlbENLMWVoQl85M1hsbFE=').decode('utf-8')

print("=" * 60)
print("🚀 SMART EXPENSE ANALYZER: SHOPEE SCREENSHOT AUTO-SCANNER")
print("=" * 60)

if not os.path.exists(SHOPEE_DIR):
    os.makedirs(SHOPEE_DIR, exist_ok=True)
    print(f"📁 สร้างโฟลเดอร์ให้แล้ว: {SHOPEE_DIR}")

# Find images in folder
image_exts = ('.png', '.jpg', '.jpeg', '.webp')
images = [os.path.join(SHOPEE_DIR, f) for f in os.listdir(SHOPEE_DIR) if f.lower().endswith(image_exts)]

if not images:
    print(f"\nℹ️ ยังไม่พบไฟล์รูปภาพใน: {SHOPEE_DIR}")
    print("👉 วิธีใช้งาน:")
    print("  1. แคปหน้าจอจากแอป Shopee (ประวัติสั่งซื้อ / รายละเอียดบิล SPayLater)")
    print("     (สามารถใช้โหมด 'เลื่อนแคปยาว' หรือแคปทีละภาพก็ได้)")
    print(f"  2. นำไฟล์ภาพมาวางในโฟลเดอร์: {SHOPEE_DIR}")
    print("  3. ดับเบิลคลิกไฟล์นี้อีกครั้ง ระบบจะอ่านชื่อสินค้าและอัปเดตเว็บให้อัตโนมัติทันที!\n")
    input("กด Enter เพื่อปิดหน้าต่างนี้...")
    sys.exit(0)

print(f"\n🔍 พบภาพแคปหน้าจอทั้งหมด {len(images)} ภาพ! กำลังเริ่มประมวลผลด้วย Gemini Vision AI...\n")

def call_gemini(b64_data):
    prompt_text = """คุณคือระบบแกะไส้ในใบแจ้งหนี้และภาพแคปหน้าจอแอปมือถือ (Shopee, SPayLater, ShopeePay, Grab)
คำสั่งเข้มงวดที่สุด (STRICT RULES):
1. หากเป็นภาพจากแอป Shopee (ประวัติการซื้อ My Purchases, รายละเอียดบิล SPayLater, ShopeePay, สั่งอาหาร ShopeeFood):
   - สกัดชื่อสินค้าจริง หรือชื่อร้านค้า เป็นภาษาไทยที่กระชับ ชัดเจน (clean_name_th) เช่น "เคสไอโฟน", "หูฟังไร้สาย", "ช้อปปี้", "อาหาร ShopeeFood"
   - ดึงงวดผ่อนถ้ามี เช่น (1/3), (2/6), (1/1)
   - ดึงวันที่ทำรายการ (date YYYY-MM-DD หากในภาพระบุปี 2569 หรือ 2026 ให้ใช้ 2026)
   - ดึงจำนวนเงินบาทที่จ่ายจริง (amount) ให้ตรงแถว
   - กำหนด bank: "SHOPEE"
   - กำหนดหมวดหมู่ category: "shopping", "food", "installment", "utilities"
2. ห้ามดึงแถวยอดรวม เช่น "TOTAL BALANCE", "ยอดรวม", "ยอดชำระเดือนนี้", "ปุ่มชำระเงิน"
ตอบกลับเป็น JSON array เท่านั้น:
[{"date":"YYYY-MM-DD","clean_name_th":"...","amount":123.45,"category":"shopping|food|installment","payment_type":"full|01/03","bank":"SHOPEE"}]"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-lite-latest:generateContent?key={DEFAULT_KEY}"
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": "image/jpeg", "data": b64_data}}
            ]
        }],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0}
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        txt = res.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '[]')
        return json.loads(txt)

all_extracted = []

for idx, img_path in enumerate(images):
    fname = os.path.basename(img_path)
    print(f"[{idx+1}/{len(images)}] กำลังวิเคราะห์: {fname} ...")
    
    im = Image.open(img_path)
    w, h = im.size
    
    # Slice tall images
    if h > 2000:
        slice_h = 1600
        overlap = 200
        sy = 0
        s_idx = 1
        while sy < h:
            cur_h = min(slice_h, h - sy)
            box = (0, sy, w, sy + cur_h)
            slice_im = im.crop(box)
            if slice_im.mode in ('RGBA', 'P'):
                slice_im = slice_im.convert('RGB')
            from io import BytesIO
            buf = BytesIO()
            slice_im.save(buf, format='JPEG', quality=88)
            b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
            print(f"   -> ตัดวิเคราะห์ท่อนที่ {s_idx} (พิกเซล {sy} ถึง {sy+cur_h})...")
            try:
                items = call_gemini(b64)
                all_extracted.extend(items)
            except Exception as e:
                print(f"      ข้อผิดพลาด: {e}")
            sy += (slice_h - overlap)
            s_idx += 1
            if sy + 100 >= h:
                break
    else:
        if im.mode in ('RGBA', 'P'):
            im = im.convert('RGB')
        from io import BytesIO
        buf = BytesIO()
        im.save(buf, format='JPEG', quality=88)
        b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        try:
            items = call_gemini(b64)
            all_extracted.extend(items)
        except Exception as e:
            print(f"   ข้อผิดพลาด: {e}")

print(f"\n✅ AI แกะรายการได้ทั้งหมด {len(all_extracted)} รายการ!")

# Deduplicate
dedup = []
for it in all_extracted:
    amt = float(it.get('amount', 0))
    name = it.get('clean_name_th', '')
    if amt <= 0:
        continue
    exists = any(abs(d['amount'] - amt) < 0.05 and d['clean_name_th'] == name for d in dedup)
    if not exists:
        dedup.append(it)

print(f"✨ คัดกรองรายการซ้ำซ้อนจากรอยต่อภาพ เหลือ {len(dedup)} รายการจริง")

# Update index.html
with open(INDEX_PATH, 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('const PRELOADED_KTC_TRANSACTIONS = [') + len('const PRELOADED_KTC_TRANSACTIONS = ')
end = html.find('];\n', start) + 1
curr_txs = json.loads(html[start:end])

# Match with Shopee items and enrich
updated_count = 0
for it in dedup:
    amt = float(it.get('amount', 0))
    name = it.get('clean_name_th', '')
    # find matching shopee item in curr_txs
    for t in curr_txs:
        if t.get('source') == 'SHOPEE' and abs(t.get('amount', 0) - amt) < 0.05:
            if 'ช้อปปี้' in t.get('name', '') and name:
                t['name'] = f"{name} ({t['name']})"
                updated_count += 1
                break

if updated_count > 0:
    print(f"🎯 อัปเดตผสานชื่อสินค้าจริงเข้ากับรายการ SPayLater สำเร็จ {updated_count} รายการ!")
    # Update STORE_KEY to trigger refresh in browser
    import time
    new_v = f"smart_expense_tx_v{int(time.time())}"
    html = re.sub(r"const STORE_KEY = '.*?';", f"const STORE_KEY = '{new_v}';", html)
    new_json_str = json.dumps(curr_txs, ensure_ascii=False)
    html = html[:start] + new_json_str + html[end:]
    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(html)
    print("💾 บันทึกไฟล์ index.html เรียบร้อยแล้ว!")
    
    # Auto push to GitHub
    git_cmd = r'C:\Users\napon.su\AppData\Local\GitHubDesktop\app-3.6.5\resources\app\git\cmd\git.exe'
    if os.path.exists(git_cmd):
        print("☁️ กำลังซิงค์ขึ้น GitHub Pages...")
        import subprocess
        subprocess.run([git_cmd, 'add', '.'], cwd=BASE_DIR)
        subprocess.run([git_cmd, 'commit', '-m', f"Auto-enrich Shopee items from screenshots ({updated_count} items)"], cwd=BASE_DIR)
        subprocess.run([git_cmd, 'push', 'origin', 'clean_main:main', '--force'], cwd=BASE_DIR)
        print("🎉 ซิงค์ขึ้น GitHub สำเร็จ! เปิดดูบนมือถือได้ทันที")
else:
    print("ℹ️ สแกนเรียบร้อย แต่ไม่พบยอดที่ตรงกับรายการเดิม หรือยอดตรงกันอยู่แล้ว")

print("\n" + "=" * 60)
input("กด Enter เพื่อเสร็จสิ้น...")
