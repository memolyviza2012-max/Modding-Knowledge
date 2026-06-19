# 🇹🇭 Space Hulk: Deathwing - Thai Localization Mod (Masterclass Guide)

คัมภีร์ฉบับสมบูรณ์ (Masterclass Grimoire) สำหรับการสร้างม็อดภาษาไทยเกม **Space Hulk: Deathwing - Enhanced Edition** (รันบน Unreal Engine 4.14.3) สอนแบบจับมือทำตั้งแต่เริ่มแกะไฟล์ จนถึงแพ็คเกมเสร็จสมบูรณ์

---

## 🛠️ ขั้นตอนที่ 1: การแกะไฟล์เกมต้นฉบับ (Unpacking)
ก่อนจะเริ่มแปล เราต้องดึงข้อความดั้งเดิมออกจากตัวเกมก่อน
1. **หาไฟล์เป้าหมาย:** เข้าไปที่โฟลเดอร์เกม `F:\SteamLibrary\steamapps\common\Space Hulk Deathwing - Enhanced Edition\SpaceHulkGame\Content\Paks\`
2. **เครื่องมือที่ใช้:** เราใช้โปรแกรม `repak.exe` ในการแกะไฟล์ `SpaceHulkGame-WindowsNoEditor.pak`
3. **คำสั่งแกะไฟล์:**
   ```cmd
   repak.exe unpack SpaceHulkGame-WindowsNoEditor.pak -o Extracted/
   ```
   *ผลลัพธ์:* เราจะได้ไฟล์ทั้งหมดของเกมมาอยู่ในโฟลเดอร์ `Extracted/`

---

## 📝 ขั้นตอนที่ 2: การดึงข้อความ (Export to CSV)
ไฟล์ข้อความของเกม UE4 จะถูกเข้ารหัสไว้ในรูปแบบ `.locres` เราต้องแปลงเป็นไฟล์ตาราง (CSV) ก่อน
1. ค้นหาไฟล์เป้าหมายที่ `Extracted/SpaceHulkGame/Content/Localization/SHDW/en/SHDW.locres`
2. **เครื่องมือที่ใช้:** เราใช้ไลบรารี Python ที่ชื่อว่า `pylocres`
3. **คำสั่งแปลงไฟล์:**
   ```cmd
   pylocres to-csv "Extracted\...\SHDW.locres" "Translation\SHDW.csv"
   ```
   *ผลลัพธ์:* เราจะได้ไฟล์ `SHDW.csv` ที่สามารถเปิดใน Excel หรือให้ AI แปลได้

---

## 🤖 ขั้นตอนที่ 3: การแปลภาษาด้วย AI (DeepSeek & Glossary Injection)
ซีรีส์ Warhammer 40k มีคำศัพท์เฉพาะที่ซับซ้อนมาก การแปลตรงตัวจะทำให้เสียอรรถรส เราจึงเขียนสคริปต์ `run_translation_SHDW.py` ขึ้นมาโดยมีฟีเจอร์เด่นคือ:
1. **Glossary Injection (บังคับคำศัพท์):** ฝังพจนานุกรมเข้าไปใน Prompt เช่น `Space Marine = สเปซมารีน`, `Heretic = พวกนอกรีต`
2. **Tag Masking:** ป้องกัน AI ทำโค้ดพัง โดยแทนที่โค้ดสี `<span color="...">` หรือตัวแปรโค้ดด้วยคำว่า `[TAG_0]` ก่อนส่งให้ AI แล้วค่อยนำโค้ดดั้งเดิมมาสลับกลับเมื่อแปลเสร็จ
3. **Checkpoint System:** สคริปต์จะเซฟไฟล์ทีละบรรทัดลง CSV ทันที ป้องกันปัญหาไฟดับ หรือ API ล่มกลางคัน

---

## 🔤 ขั้นตอนที่ 4: เทคนิคยัดฟอนต์ไทย (Slate Font Fallback Trick)
**นี่คือหัวใจสำคัญของการทำม็อดเกม UE4 รุ่นเก่า!** เพราะการใช้ UE4.14 Editor มา Cook ฟอนต์ทำได้ยากและชอบ Crash เราจึงใช้เทคนิคฟอนต์ตัวแทนแทน
1. **เตรียมฟอนต์:** หาฟอนต์ที่รองรับภาษาไทยสวยๆ มา 1 ตัว แล้วเปลี่ยนชื่อไฟล์ให้เป็นคำว่า **`DroidSansFallback.ttf`** เป๊ะๆ
2. **สร้างโครงสร้างโฟลเดอร์ม็อด (Pack):** 
   ให้สร้างโฟลเดอร์เตรียมแพ็คชื่อ `Pack` และสร้างโฟลเดอร์ย่อยเข้าไปให้ได้โครงสร้างตามนี้:
   ```text
   Pack/
   └── Engine/
       └── Content/
           └── Slate/
               └── Fonts/
                   └── DroidSansFallback.ttf
   ```
3. **ความมหัศจรรย์:** เอนจิ้น UE4 ถูกโปรแกรมไว้ว่า หากตัวอักษรไหนหาไม่เจอในฟอนต์หลัก (เช่น ภาษาไทย) มันจะวิ่งไปดึงไฟล์ `DroidSansFallback.ttf` มาใช้ทันที!

---

## ⚙️ ขั้นตอนที่ 5: นำเข้าข้อความแปลไทย (Import to Locres) และแก้บั๊ก Pylocres
เมื่อแปลไฟล์ `SHDW_th.csv` เสร็จแล้ว เราต้องแปลงกลับเป็น `.locres` เพื่อเอาไปใส่ในเกม
1. **จัดโครงสร้างเตรียมแพ็ค:** นำไฟล์ที่กำลังจะแปลงไปใส่ในโฟลเดอร์ที่จำลองมาจากตัวเกม
   `Pack\SpaceHulkGame\Content\Localization\SHDW\en\SHDW.locres`
2. **คำสั่งแปลงไฟล์:**
   ```cmd
   pylocres from-csv -p "Translation\SHDW_th.csv" -o "Pack\...\SHDW.locres" --ver 0
   ```
3. **🚨 การแก้บั๊ก Integer Hash (Pylocres Bug):**
   หากขึ้น Error `struct.error: required argument is not an integer` ให้ไปแก้ไขไฟล์ `cli.py` ในโฟลเดอร์ที่ติดตั้งไลบรารี `pylocres` บังคับให้ Hash เป็นตัวเลขเสมอ:
   ```python
   # โค้ดที่แก้ไขแล้วใน cli.py
   source_hash = int(row.get("hash", 0)) if row.get("hash") else 0
   ```

---

## 📦 ขั้นตอนที่ 6: แพ็คไฟล์ม็อด (Packing & The _P.pak Trick)
เกม Unreal Engine รุ่นเก่า (4.14) **ไม่รองรับโฟลเดอร์ `~mods`** เราต้องบังคับเกมด้วยระบบ Patch
1. **การเขียนคำสั่งแพ็ค:** ใช้โปรแกรม `repak.exe` บีบอัดโฟลเดอร์ `Pack` ของเรา
   ```cmd
   repak.exe pack Pack SpaceHulkGame-WindowsNoEditor_P.pak --version V3
   ```
   **คำอธิบายเชิงลึก:** 
   - `SpaceHulkGame-WindowsNoEditor_P.pak`: **ต้องตั้งชื่อให้ลงท้ายด้วย `_P`** (`_P` ย่อมาจาก Patch ซึ่งเอนจิ้นจะโหลดไฟล์ที่ลงท้ายด้วย `_P` เป็นลำดับสุดท้ายเพื่อทับไฟล์เกมหลัก)
   - `--version V3`: **จุดชี้เป็นชี้ตาย!** บังคับให้สร้าง Pak เป็นเวอร์ชัน V3 ซึ่งเป็นแพทเทิร์นเก่าที่ UE 4.14 รองรับ หากไม่ใส่ เกมจะอ่านม็อดไม่ออก

---

## 🎮 ขั้นตอนที่ 7: การติดตั้งม็อด
1. นำไฟล์ `SpaceHulkGame-WindowsNoEditor_P.pak` ที่ได้ 
2. ไปวางทับลงในโฟลเดอร์ `SpaceHulkGame\Content\Paks\` ของตัวเกม (วางไว้คู่กับไฟล์ต้นฉบับเลย ห้ามสร้างโฟลเดอร์ย่อย)
3. เข้าเกม และสนุกกับภาษาไทยแบบเต็มรูปแบบ!

---
*Created and optimized for Thai Modding Community by Antigravity (AI Modding Assistant).*
