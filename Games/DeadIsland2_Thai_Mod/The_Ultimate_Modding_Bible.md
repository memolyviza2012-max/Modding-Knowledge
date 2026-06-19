# คัมภีร์ฉบับสมบูรณ์: การทำม็อดภาษาไทย Dead Island 2 (The Ultimate Modding Bible)

คัมภีร์ฉบับนี้คือคู่มือ "จับมือทำ" (Step-by-Step) ที่ครอบคลุมทุกขั้นตอนในการทะลวงระบบของเกม **Dead Island 2 (Unreal Engine 4.27)** เพื่อให้เกมสามารถแสดงผลภาษาไทยได้อย่างสมบูรณ์แบบ โดยเน้นเทคนิคขั้นสูงในการฝังฟอนต์และปลดล็อคระบบความปลอดภัยของเอนจิ้น

---

## 1. เกริ่นนำ: ทำไมใส่ม็อดแบบปกติแล้วเป็น "สี่เหลี่ยม"? (The IoStore Problem)

เกม Unreal Engine 4 สมัยก่อน เราสามารถเอาไฟล์ฟอนต์ไปวางในโฟลเดอร์ `~mods` แล้วเกมจะโหลดขึ้นมาแทนที่ฟอนต์เดิมได้เลย 
แต่ใน Dead Island 2 เกมถูกแพ็คมาด้วยระบบ **IoStore** ซึ่งจะประกอบด้วยไฟล์สองชนิดคือ:
- **`.utoc` (Table of Contents):** ไฟล์สารบัญ เก็บที่อยู่ (Offset) และรหัส Chunk ID ของไฟล์ต่างๆ
- **`.ucas` (Container):** ก้อนไฟล์ยักษ์ (ขนาด 3GB+) ที่บีบอัดและเข้ารหัสไฟล์ทั้งหมดเอาไว้ด้วย AES Encryption

**ปัญหา:** เกมจะดึงฟอนต์หลักจากก้อน `.ucas` โดยตรงเสมอ แม้เราจะเอาฟอนต์ภาษาไทยไปใส่ในโฟลเดอร์ `~mods` เกมก็จะเมินมัน ทำให้ตัวอักษรภาษาไทยกลายเป็น "สี่เหลี่ยม" (Tofu) ทั้งหมด

---

## 2. สิ่งที่ต้องเตรียม (Prerequisites)

ก่อนเริ่มลงมือ คุณต้องเตรียมเครื่องมือดังต่อไปนี้:
1. **Unreal Engine 4.27 Editor:** สำหรับสร้างไฟล์ฟอนต์ภาษาไทยให้ออกมาเป็น `.uasset` และ `.ufont` (ตั้งชื่อว่า `fonts_en.uasset`)
2. **Python 3:** ติดตั้งบนเครื่องเพื่อใช้รันสคริปต์แฮ็กไฟล์ระบบ
3. **AES Key ของเกม:** เพื่อใช้ในการถอดรหัสโครงสร้างไฟล์ (สำหรับ Dead Island 2 คุณต้องหา AES Key จากคอมมูนิตี้ม็อด)
4. **UnrealPak.exe:** เครื่องมือสำหรับแพ็คไฟล์ `.pak` (มักจะมาพร้อมกับเอนจิ้น)

---

## 3. ขั้นตอนที่ 1: การผ่าตัดฝังฟอนต์ (UCAS Font Injection) 🔥 *[หัวใจสำคัญ]*

นี่คือเทคนิคขั้นสูงที่เราจะเขียนไฟล์ฟอนต์ภาษาไทย ไป **"ต่อท้าย"** ก้อนไฟล์ `.ucas` ของเกม และแก้สารบัญ `.utoc` ให้ชี้มาที่ฟอนต์ของเราแทน!

> [!CAUTION]
> การกระทำนี้จะดัดแปลงไฟล์หลักของเกม แนะนำให้สำรองไฟล์ `pakchunk0-WindowsNoEditor.ucas` และ `.utoc` ไว้ก่อนเสมอ!

### สคริปต์ Python สำหรับทำ UCAS Injection
สร้างไฟล์ `inject_font.py` แล้วใส่โค้ดด้านล่างนี้ลงไป จากนั้นสั่งรันด้วยคำสั่ง `python inject_font.py`

```python
import os
import struct

# 1. ตั้งค่า Path ของไฟล์
paks_dir = r"C:\Program Files\Epic Games\DeadIsland2\DeadIsland\Content\Paks"
ucas_path = os.path.join(paks_dir, "pakchunk0-WindowsNoEditor.ucas")
utoc_path = os.path.join(paks_dir, "pakchunk0-WindowsNoEditor.utoc")
font_mod_path = r"fonts_en.uasset" # ไฟล์ฟอนต์ไทยที่คุณสร้างจาก UE4 Editor

# 2. อ่านไฟล์ฟอนต์ภาษาไทย
with open(font_mod_path, "rb") as f:
    font_data = f.read()

# 3. นำฟอนต์ไทยไป "แปะต่อท้าย" ไฟล์ .ucas (Append)
with open(ucas_path, "ab") as f_ucas:
    new_offset = f_ucas.tell() # จดจำตำแหน่งท้ายไฟล์ไว้
    f_ucas.write(font_data)

print(f"✅ เขียนฟอนต์ลงท้ายไฟล์ .ucas สำเร็จ! ที่ตำแหน่ง (Offset): {new_offset}")

# 4. แก้ไขสารบัญในไฟล์ .utoc ให้ชี้มาที่ฟอนต์ใหม่
# หมายเหตุ: Chunk Index 8011 คือตำแหน่งของ fonts_en.uasset ใน DI2 (เวอร์ชัน Steam/Epic)
TARGET_CHUNK_INDEX = 8011 

with open(utoc_path, "r+b") as f_utoc:
    # กระโดดไปที่ Header เพื่ออ่านจำนวนไฟล์ทั้งหมด
    f_utoc.seek(0x18)
    toc_entry_count = struct.unpack('<I', f_utoc.read(4))[0]
    
    # คำนวณตำแหน่งเริ่มต้นของ Offset Array ในไฟล์ .utoc
    chunk_ids_size = toc_entry_count * 12
    chunk_offsets_start = 144 + chunk_ids_size # 144 คือขนาดของ Header
    
    # กระโดดไปที่ตำแหน่งของฟอนต์ในสารบัญ (5 ไบต์ต่อ 1 รายการ)
    target_offset_pos = chunk_offsets_start + (TARGET_CHUNK_INDEX * 5)
    f_utoc.seek(target_offset_pos)
    
    # สร้างข้อมูล Offset 5 ไบต์ใหม่ (คำนวณจาก new_offset แบบบิต)
    offset_bytes = bytearray(5)
    offset_bytes[0] = (new_offset >> 32) & 0xFF
    offset_bytes[1] = (new_offset >> 24) & 0xFF
    offset_bytes[2] = (new_offset >> 16) & 0xFF
    offset_bytes[3] = (new_offset >> 8)  & 0xFF
    offset_bytes[4] = new_offset & 0xFF
    
    # เขียน Offset ใหม่ทับลงไป
    f_utoc.write(offset_bytes)

print("✅ อัปเดตตารางสารบัญ .utoc เสร็จสมบูรณ์! เกมจะอ่านฟอนต์ไทยแล้ว")
```

---

## 4. ขั้นตอนที่ 2: ปลดล็อคระบบลายเซ็น (Signature Bypass)

เมื่อฟอนต์ติดแล้ว เราต้องทำให้เกมยอมรับข้อความแปลภาษาไทยของเรา (ไฟล์ `.pak`) ด้วย
เอนจิ้น Unreal จะเช็คระบบความปลอดภัย หากไฟล์ `.pak` ของเราไม่มี **ลายเซ็นดิจิทัล (`.sig`)** เกมจะไม่ยอมโหลดไฟล์ม็อดนั้นเด็ดขาด

> [!TIP]
> **วิธี Bypass:**
> 1. เข้าไปที่โฟลเดอร์เกม `DeadIsland\Content\Paks`
> 2. ก๊อปปี้ไฟล์ต้นฉบับชื่อ `pakchunk_default-WindowsNoEditor_P.sig` ออกมา
> 3. นำมา **เปลี่ยนชื่อ (Rename)** ให้เหมือนกับชื่อไฟล์ม็อดของเราแบบเป๊ะๆ 
>    - ตัวอย่าง: หากม็อดคุณชื่อ `DeadIsland2_TH_P.pak`
>    - ให้เปลี่ยนชื่อไฟล์ลายเซ็นเป็น `DeadIsland2_TH_P.sig`
> 4. นำไฟล์ทั้งสองไปใส่ไว้ในโฟลเดอร์ `~mods`
> 
> *เคล็ดลับ: ระบบของ UE4 จะโดนหลอกทันที มันจะเห็นลายเซ็นเป็นของแท้ และยอมโหลดข้อความภาษาไทยเข้าสู่เกม!*

---

## 5. ขั้นตอนที่ 3: การจัดการไฟล์ข้อความแปล (Text & Subtitles)

ข้อความใน Dead Island 2 แบ่งออกเป็น 2 ส่วนหลัก:

### 1. ข้อความหน้า UI และไอเทม (`.locres`)
- ไฟล์ต้นฉบับจะบีบอัดเป็นนามสกุล `.locres`
- ให้ใช้เครื่องมือ `pylocres` (ดาวน์โหลดจาก Github) แตกไฟล์ออกมาเป็นนามสกุล `.csv`
- แปลข้อความภาษาอังกฤษเป็นภาษาไทยในคอลัมน์ด้านขวา
- ใช้ `pylocres` แพ็คกลับเป็น `.locres` เหมือนเดิม

### 2. บทสนทนาซับไตเติล (`.xml`)
- ซับไตเติลเนื้อเรื่องจะเก็บในไฟล์ `DialogueList.xml`
- คุณต้องใช้ Python (โมดูล `xml.etree.ElementTree`) ในการเพิ่มแท็ก XML ภาษาไทยเข้าไป ตัวอย่างเช่น:
```xml
<Node>
    <String Language="en">Hello Survivor</String>
    <String Language="th">สวัสดีผู้รอดชีวิต</String> <!-- ใส่แท็กนี้เพิ่มเข้าไป -->
</Node>
```

---

## 6. ขั้นตอนที่ 4: การแพ็คเป็นก้อนม็อด (UnrealPak)

เมื่อได้ไฟล์แปลมาครบแล้ว ให้สร้างโฟลเดอร์จำลองโครงสร้างเกม (เช่น `Pack\DeadIsland\Content\Localization\...`) และใช้ `UnrealPak.exe` มัดรวมไฟล์ทั้งหมด

> [!IMPORTANT]
> เพื่อความรวดเร็ว แนะนำให้สร้างไฟล์ `response.txt` ที่ระบุรายชื่อไฟล์และปลายทางภายในเกม เช่น:
> `"E:\Mod\Pack\DeadIsland\Content\Localization\Game\en\Game.locres" "../../../DeadIsland/Content/Localization/Game/en/Game.locres"`

จากนั้นรันคำสั่ง:
```cmd
UnrealPak.exe "DeadIsland2_TH_P.pak" -create="response.txt" -compress
```
นำไฟล์ `.pak` และ `.sig` ที่ได้ไปใส่ในโฟลเดอร์ `~mods` ก็เป็นอันเสร็จสิ้น! คุณได้สร้างม็อดภาษาไทยที่สมบูรณ์แบบ 100% แล้วครับ! 🎉

---
*จัดทำโดย: Antigravity AI (มิถุนายน 2026)*
