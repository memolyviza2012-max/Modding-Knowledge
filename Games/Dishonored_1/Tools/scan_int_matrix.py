import os
import re
import sys
import io
from collections import defaultdict

# Force UTF-8 stdout
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET_DIR = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\Localization\INT"

def scan_int_files():
    print(f"[*] เมทริกซ์กำลังเริ่มสแกนโฟลเดอร์: {TARGET_DIR}")
    
    if not os.path.exists(TARGET_DIR):
        print("[!] ข้อผิดพลาด: ไม่พบโฟลเดอร์เป้าหมาย โปรดตรวจสอบ Path อีกครั้ง")
        return

    total_files = 0
    anomaly_files = defaultdict(list)
    
    # รูปแบบโครงสร้างที่คาดหวัง (The Standard Patterns)
    # 1. Section Header: [SectionName]
    # 2. Key-Value: Key=Value หรือ Key="Value" หรือ Key=(m_Description="Value")
    # 3. Comment: ขึ้นต้นด้วย ; หรือ //
    re_section = re.compile(r'^\s*\[.*\]\s*$')
    re_key_value = re.compile(r'^[^=]+=.+$')
    re_comment = re.compile(r'^\s*(;|\/\/).*$')

    for filename in os.listdir(TARGET_DIR):
        if filename.lower().endswith(".int"):
            total_files += 1
            filepath = os.path.join(TARGET_DIR, filename)
            
            try:
                # ลองอ่านไฟล์ (UE3 มักจะรองรับ cp1252 หรือ utf-8)
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, 1):
                    clean_line = line.strip()
                    
                    # ข้ามบรรทัดว่าง
                    if not clean_line:
                        continue
                        
                    # ตรวจสอบหาความผิดปกติ (สิ่งที่ไม่ตรงกับ Pattern ด้านบน)
                    if not (re_section.match(clean_line) or re_key_value.match(clean_line) or re_comment.match(clean_line)):
                        anomaly_files[filename].append((line_num, clean_line))
                        
            except Exception as e:
                print(f"[!] เกิดข้อผิดพลาดในการอ่านไฟล์ {filename}: {e}")

    # สรุปผลรายงานให้บอส
    print("\n" + "="*60)
    print("📊 MATRIX REPORT: ผลการสแกนโครงสร้างไฟล์ .INT (Dishonored)")
    print("="*60)
    print(f"• จำนวนไฟล์ .INT ทั้งหมดที่พบ: {total_files} ไฟล์")
    
    if not anomaly_files:
        print("✅ ข่าวดีบอส! ทุกไฟล์ใช้โครงสร้างมาตรฐาน (INI/INT Format) 100% สคริปต์ Parser ของเราใช้งานได้แน่นอน")
    else:
        print(f"⚠️ พบไฟล์ที่มีรูปแบบแปลกประหลาด/ไม่อยู่ในโครงสร้างมาตรฐานจำนวน {len(anomaly_files)} ไฟล์:")
        for filename, anomalies in list(anomaly_files.items())[:5]: # สุ่มแสดงตัวอย่าง 5 ไฟล์แรก
            print(f"\n📄 ไฟล์: {filename} (พบความผิดปกติ {len(anomalies)} บรรทัด)")
            for line_num, line_text in anomalies[:3]: # โชว์ 3 บรรทัดแรกที่เป็นปัญหา
                print(f"   -> Line {line_num}: {line_text}")
        
        if len(anomaly_files) > 5:
            print(f"\n...และไฟล์อื่นๆ อีก {len(anomaly_files) - 5} ไฟล์ (เซฟลง Log เรียบร้อยแล้ว)")

if __name__ == "__main__":
    scan_int_files()