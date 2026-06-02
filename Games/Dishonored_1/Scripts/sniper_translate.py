# sniper_translate.py (V4.0)
import sys, os, re, time
from openai import OpenAI

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# --- [CONFIG] ---
LM_STUDIO_URL   = "http://localhost:1234/v1"
LM_STUDIO_MODEL = "qwen/qwen3-14b"
WORK_DIR        = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\CookedPCConsole"
TARGET_MAX_LINES = 200

client = OpenAI(base_url=LM_STUDIO_URL, api_key="lm-studio", timeout=120.0)

RE_THAI = re.compile(r'[\u0e00-\u0e7f]')
RE_ENG  = re.compile(r'[a-zA-Z]')

# /no_think บรรทัดแรก — ปิด Thinking Mode ทันที
SYSTEM_PROMPT = """/no_think
You translate video game dialogue from English to Thai.
Keep the EXACT key (e.g. DisConv_Blurb.4084.DisConv_Blurb) unchanged — output: "KEY: Thai translation"
Exact line count required. Preserve %s %d {0} \\n <font...>
Examples:
Input:  DisConv_Blurb.4084.DisConv_Blurb: Very well.
Output: DisConv_Blurb.4084.DisConv_Blurb: ดีมากเลย
Input:  Guard_Bark.12: Open fire!
Output: Guard_Bark.12: ยิงได้!
Glossary: Corvo Attano=คอร์โว อัตตาโน|Emily Kaldwin=เอมิลี่ คาลด์วิน|The Outsider=ดิ เอาท์ไซเดอร์|Lord Regent=อัครมหาเสนาบดี|Overseer=โอเวอร์เซียร์|Weepers=วีปเปอร์|Blink=บลิงก์|Dunwall=ดันวอลล์"""

def read_yaml(path):
    for enc in ('utf-8-sig', 'utf-8', 'utf-16-le', 'utf-16-be', 'cp1252'):
        try:
            data = {}
            with open(path, 'r', encoding=enc) as f:
                for line in f:
                    if ': ' in line:
                        k, v = line.split(': ', 1)
                        data[k.strip()] = v.strip()
            if data:
                return data
        except Exception:
            continue
    return {}

def translate_batch(lines):
    prompt = "".join(lines) + "\n[OUTPUT TRANSLATED LINES ONLY]"
    for attempt in range(3):
        try:
            res = client.chat.completions.create(
                model=LM_STUDIO_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            return res.choices[0].message.content
        except Exception as e:
            print(f"  [!] Attempt {attempt+1}/3 fail: {e}")
            time.sleep(2 ** attempt)
    return ""

def snipe_file(int_path):
    th_path  = int_path.replace('_INT.yaml', '_TH.yaml')
    int_data = read_yaml(int_path)
    if not int_data:
        return

    th_data = read_yaml(th_path) if os.path.exists(th_path) else {}

    keys_to_fix = [
        k for k, v_int in int_data.items()
        if RE_ENG.search(v_int)
        and (k not in th_data or th_data[k] == v_int or not RE_THAI.search(th_data.get(k, "")))
    ]

    if not keys_to_fix or len(keys_to_fix) > TARGET_MAX_LINES:
        return

    print(f"\n  🎯 {os.path.basename(int_path)} — ค้าง {len(keys_to_fix)} บรรทัด")

    res = translate_batch([f"{k}: {int_data[k]}\n" for k in keys_to_fix])
    if not res:
        print("  [✗] แปลล้มเหลว")
        return

    # กรองเฉพาะ key ที่ถูกต้อง ป้องกัน AI ตอบเกิน
    valid_keys = set(keys_to_fix)
    parsed = {}
    for line in res.split('\n'):
        line = line.strip()
        if ': ' not in line:
            continue
        k, v = line.split(': ', 1)
        v = v.strip()
        # ป้องกันเขียนค่าว่างทับ English — เช็คว่าผลแปลไม่ว่างและมีตัวอักษรจริง
        if k.strip() in valid_keys and v and len(v) > 0:
            parsed[k.strip()] = v

    print(f"  [✓] {len(parsed)}/{len(keys_to_fix)} บรรทัด")

    th_data.update(parsed)
    with open(th_path, 'w', encoding='utf-8-sig') as f:
        for k in int_data:
            v_th = th_data.get(k, "")
            # ถ้าค่า TH ว่าง ใช้ค่า INT แทน (กันกรณี model ไม่ตอบ)
            final = v_th if v_th and v_th.strip() else int_data[k]
            f.write(f"{k}: {final}\n")
    print("  [💾] Saved")

def main():
    print("=== Sniper Translate V4.0 ===\n")
    for root, _, files in os.walk(WORK_DIR):
        for f in files:
            if f.endswith('_INT.yaml'):
                snipe_file(os.path.join(root, f))
    print("\n=== เสร็จสิ้น ===")

if __name__ == "__main__":
    main()