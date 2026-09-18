# คัมภีร์คลังฟอนต์เกมภาษาไทยและระบบเลื่อนสระ PUA (Thai Game Font & PUA Suite)

## 📌 บทนำ (Introduction)
ในการทำม็อดภาษาไทยสำหรับวิดีโอเกม ปัญหาที่พบบ่อยที่สุดคือ **"สระลอย สระจม วรรณยุกต์ซ้อนทับ หรือตัวอักษรกลายเป็นกล่องสี่เหลี่ยม (Tofu □)"** เนื่องจากเอนจินเกมส่วนใหญ่ถูกออกแบบมาสำหรับระบบอักษรละติน (Latin) และไม่มีระบบ Text Shaper / OpenType Layout Engine อัจฉริยะสำหรับภาษาไทย

เพื่อแก้ปัญหานี้อย่างถาวรและเป็นมาตรฐานเดียวกันทั้งระบบ THub ได้รวบรวม **ชุดฟอนต์มาตรฐาน 15 ตระกูล** พร้อมสร้าง **ชุด Glyph PUA (Private Use Area) 2,208 รูป** บรรจุลงในฟอนต์ล่วงหน้า เชื่อมโยงกับ `Mapping.json` และ `Char.txt` ซึ่งช่วยให้ข้อความภาษาไทยจัดตำแหน่งสระและวรรณยุกต์ได้อย่างสมบูรณ์แบบในทุก Game Engine

---

## 🔤 มาตรฐานระบบ PUA (Private Use Area Standard)

- **ช่วงรหัส Unicode:** `U+F000` ถึง `U+F89F` (รวม 2,208 อักขระ PUA)
- **ไฟล์อักขระแม่แบบ:** `Char.txt` บรรจุอักขระพื้นฐาน (ASCII + Latin Extended + Greek + เลข/เครื่องหมาย + พยัญชนะไทย + PUA 2,208 ตัว)
- **ไฟล์ตารางจับคู่:** `Mapping.json` บรรจุคู่คำระหว่างข้อความไทยปกติ กับรหัส PUA ตัวอย่างเช่น:
  ```json
  "กั": "\uF000",
  "ขั": "\uF001",
  "ปิ่": "\uF123"
  ```
- **สคริปต์แปลงข้อความ:** `thai_font_mapper.py` ทำการแปลงแบบ Longest-Match-First และทำ Unicode NFC Normalization เพื่อความแม่นยำ 100%

---

## 🎮 ตารางฟอนต์มาตรฐาน 15 ตระกูล และการคัดกรองตาม Game Engine

| ID | ชื่อฟอนต์ | รูปแบบ/น้ำหนัก | สไตล์ / Typography | จุดเด่นและแนวเกมที่แนะนำ | Engine แนะนำ |
|---|---|---|---|---|---|
| **prompt** | Prompt (พร้อม) | **18 รูปแบบ** (Thin-Black + Italic) | Modern Loopless Sans | ฟอนต์ไร้หัวเรขาคณิต คมชัดสูงบนจอภาพ AAA เมนูทันสมัย | **Unreal Engine**, Unity, RE Engine |
| **kanit** | Kanit (คณิต) | **18 รูปแบบ** (Thin-Black + Italic) | Athletic Geometric Sans | ตัวหนา คมชัด ดุดัน อ่านง่ายที่สุดในสนามรบและเกมแอ็กชัน | **RE Engine (Capcom)**, Unity, Unreal Engine |
| **bai_jamjuree** | Bai Jamjuree (ใบจามจุรี) | **12 รูปแบบ** (ExtraLight-Bold + Italic) | Square Terminal Sans | ทรงเหลี่ยมมน สไตล์ไซไฟ ไฮเทค แข็งแกร่ง บันทึกยาวๆ อ่านสบาย | **Unreal Engine**, RE Engine, Unity |
| **google_sans** | Google Sans (กูเกิล แซนส์) | **18 รูปแบบ** (Normal/17pt + Italic) | Geometric Product Sans | คลีนระดับสากล สัดส่วนสมบูรณ์แบบ หรูหรา เรียบง่าย พรีเมียม | **Unreal Engine**, Unity, Godot |
| **ibm_plex_sans_thai** | IBM Plex Sans Thai | **7 รูปแบบ** (Thin-Bold) | Neo-Grotesque Industrial | สไตล์วิศวกรรม อุตสาหกรรม ชัดเจนในระบบสถิติ ตาราง และ Inventory | **Unity**, **C_Engine**, Godot |
| **noto_sans_thai** | Noto Sans Thai | **37 รูปแบบ** (Normal, Condensed, ExtraCondensed) | Universal Standard Sans | มีน้ำหนักครบที่สุด ใช้เป็นฟอนต์สำรอง (Universal Fallback) ปลอดภัยสุด | ทุก Engine (Universal Fallback) |
| **sarabun** | Sarabun (สารบรรณ) | **16 รูปแบบ** (Thin-ExtraBold + Italic) | Standard Looped Thai | ฟอนต์ทางการมีหัวมาตรฐาน อ่านง่ายที่สุดสำหรับบทสนทนายาวๆ จดหมาย คัมภีร์ | **Visual Novels**, RPG, Unity |
| **pridi** | Pridi (ปรีดี) | **6 รูปแบบ** (ExtraLight-Bold) | Slab Serif Narrative | มีเชิงหนักแน่น ให้บรรยากาศวรรณกรรม สืบสวน ย้อนยุค หรือแฟนตาซี | **Fantasy RPG**, Mystery, Lore |
| **chonburi** | Chonburi (ชลบุรี) | **1 รูปแบบ** (Regular Display) | High-Contrast Display Serif | เส้นหนาตัดบาง Didone หรูหรา อลังการ สำหรับโลโก้ ไตเติล และหัวเรื่อง | **Title Screen**, Headers, Posters |
| **itim** | Itim (ไอติม) | **1 รูปแบบ** (Regular Casual) | Friendly Rounded Casual | หัวกลมน่ารัก สดใส เป็นมิตร สำหรับเกมทำฟาร์ม แคชชวล หรือ Cozy Game | **Cozy Games**, Farming Sims, Unity |
| **sriracha** | Sriracha (ศรีราชา) | **1 รูปแบบ** (Regular Handwriting) | Casual Marker Handwriting | ลายมือปากกาเมจิก มีชีวิตชีวา เหมาะกับสมุดบันทึก ไดอารี่ผู้รอดชีวิต | **Survival Notes**, Diaries |
| **charm** | Charm (ชาม) | **2 รูปแบบ** (Regular, Bold) | Elegant Script Handwriting | ลายมือปลายพู่กันอ่อนช้อย สำหรับเกมโรแมนติก แฟนตาซี เวทมนตร์ หรือจดหมายรัก | **Romance RPG**, Spells, Scrolls |
| **charmonman** | Charmonman (ชาร์มอนแมน) | **2 รูปแบบ** (Regular, Bold) | Ornate Calligraphy Script | ลายมือประดิษฐ์วิกตอเรียน สำหรับคัมภีร์เวท จดหมายโบราณ และพระราชโองการ | **Grimoires**, Royal Edicts, Gothic |
| **cts_rattikal** | CTS Rattikal (รัตติกาล) | **2 รูปแบบ** (Regular PUA/Shifted) | Horror Stylized Gothic | โกธิกหลอน มืดมน ลึกลับ สำหรับเกมสยองขวัญ สุสาน และดาร์กแฟนตาซี | **Survival Horror**, Dark Fantasy |
| **niramit** | Niramit (นิรมิต) | **12 รูปแบบ** (ExtraLight-Bold + Italic) | Contemporary Looped Serif | ดีไซน์ร่วมสมัย มั่นคง สง่างาม สำหรับการเมือง ประวัติศาสตร์ และผจญภัย | **Adventure**, Narrative Lore |

> 🏷️ **รวมไฟล์ฟอนต์ทั้งหมดในคลัง:** 15 ตระกูล รวม **153 รูปแบบไฟล์** คลอบคลุมน้ำหนักตั้งแต่ Thin (100) จนถึง Black (900) พร้อมตัวเอียง (Italic) และ Condensed

---

## 🎚️ ระบบเลือกรุ่น/น้ำหนักฟอนต์ (Font Weight & Style Selector)
ผู้พัฒนาสามารถเลือกระดับความหนาของตัวอักษรให้เหมาะสมกับประเภท UI ในเกมได้โดยตรงผ่าน AI Helper และคลังฟอนต์:
1. **Thin (100) / ExtraLight (200) / Light (300):** เหมาะกับ Subtitle เล็กๆ ลอเรลแคร์ หรือเครดิตท้ายเกม
2. **Regular (400) [ปกติ]:** เหมาะกับข้อความบทสนทนายาวๆ และ UI มาตรฐาน
3. **Medium (500) / SemiBold (600):** เหมาะกับเมนูย่อย ชื่อไอเทม และปุ่มคำสั่ง
4. **Bold (700) [หนา]:** เหมาะกับ UI หน้าจอต่อสู้ ค่าดาเมจ และหัวข้อ (Default แนะนำสำหรับเกมส่วนใหญ่)
5. **ExtraBold (800) / Black (900) [หนาสุด]:** เหมาะกับตัวเลขไตเติล แจ้งเตือนบอส และหน้าไตเติล

เมื่อเลือกสไตล์ใด ระบบจะ:
- อัปเดต Master Prompt ให้ระบุชื่อสไตล์และพาร์ทไฟล์ TTF ที่ตรงรุ่น
- คัดลอกและบันทึกสไตล์ที่เลือกลงใน `03_Font_and_UI` ของโปรเจกต์เมื่อกดติดตั้ง
- อัปเดตภาพประกอบตัวอย่างระดับ Full HD ให้ตรงตามสไตล์ที่เลือกแบบเรียลไทม์

### 🖼️ ระบบภาพตัวอย่างคมชัดระดับ Full HD ครบทุกขนาดตัวอักษร (Multi-Size Specimen Edition)
ภาพตัวอย่างของทุกฟอนต์และทุกน้ำหนัก (ครบทั้ง 153 ไฟล์) ถูกสร้างขึ้นในขนาด Full HD (1920x1080) โดยแสดงข้อความตัวอย่าง **ครบทุกขนาดพิกเซลที่ใช้งานจริงในเกม**:
- **ขนาด 64pt (Title / ไตเติลเกม):** แสดงความสง่างามและความคมชัดของตัวหนังสือขนาดใหญ่พิเศษบนหน้าไตเติล
- **ขนาด 44pt (Heading / เมนูหลัก):** แสดงการจัดวางระดับหัวข้อเควสต์และชื่อบทตอน
- **ขนาด 32pt (In-Game Buttons / ปุ่มคำสั่ง):** จำลองปุ่มกดเมนูจริง (เริ่มเกมใหม่, ดำเนินการต่อ, การตั้งค่า, ออกจากเกม)
- **ขนาด 24pt (Dialogue & Subtitles / บทสนทนาและซับไตเติล):** แสดงการอ่านง่ายของประโยคยาวและสระลอย/สระจม
- **ขนาด 18pt (Tooltips & Notes / คำอธิบายไอเทมขนาดเล็ก):** ทดสอบความชัดเจนของตัวอักษรขนาดจิ๋ว ไม่เบลอ ไม่ทับซ้อน
- **English & Numerals:** แสดงตัวอักษรภาษาอังกฤษ ตัวเลข และสัญลักษณ์ครบถ้วน

---

## 🛠️ คู่มือการนำฟอนต์ไปติดตั้งในแต่ละ Engine (Engine Integration Guides)

### 1. Unity Engine (TextMeshPro / UGUI)
1. **การสร้าง SDF Font Asset ด้วย TextMeshPro:**
   - คัดลอกฟอนต์ (เช่น `Kanit-Bold_PUA.ttf`) เข้า Unity Assets
   - เปิดเมนู: `Window` > `TextMeshPro` > `Font Asset Creator`
   - **Source Font File:** เลือกไฟล์ฟอนต์ PUA
   - **Sampling Point Size:** `Auto Sizing`
   - **Padding:** `5` หรือ `6` (ป้องกันขอบตัวอักษรเบลอหรือชนกัน)
   - **Atlas Resolution:** `4096 x 4096`
   - **Character Set:** เลือก `Custom Characters`
   - เปิดไฟล์ `Char.txt` จากโปรเจกต์ คัดลอกข้อความทั้งหมดมาวางในช่อง `Custom Character List`
   - กด **Generate Font Atlas** แล้วกด **Save** เป็น `.asset`
2. **การแปลงข้อความ:**
   - รันสคริปต์ `thai_font_mapper.py` กับไฟล์บทสนทนาภาษาไทยก่อนนำเข้าเกม เพื่อเปลี่ยนรหัสเป็น PUA

### 2. Unreal Engine (UE4 / UE5 - Slate & UMG)
1. **การตั้งค่า Font Face ใน Content Browser:**
   - นำไฟล์ฟอนต์ (เช่น `Prompt-Bold_PUA.ttf`) ไปวางในโปรเจกต์
   - ดับเบิลคลิกเปิด Font Asset ของเกม (หรือสร้างขึ้นใหม่)
   - ในส่วน **Font Faces** ให้ชี้ Source Font File ไปที่ไฟล์ TTF ที่มี PUA
   - FreeType Shaper ของ Unreal Engine จะเรนเดอร์ Glyph PUA ได้อย่างคมชัดและไม่ตกขอบ
2. **การทำ Pak Mod:**
   - แพ็ค Font Asset ลงใน `~mods` โฟลเดอร์ของเกม

### 3. RE Engine (Capcom / Resident Evil / Monster Hunter)
1. **การแทนที่ฟอนต์:**
   - RE Engine ใช้ฟอนต์แบบ OpenType/TrueType หรือ Sprite Atlas `.tex`
   - เลือกใช้ `Kanit-Bold_PUA.ttf` หรือ `Prompt-Bold_PUA.ttf` เพื่อให้ความหนาของตัวอักษรอ่านง่ายขณะต่อสู้
   - แปลงข้อความแปลด้วย `thai_font_mapper.py` ก่อนแพ็คกลับเข้าไฟล์ `.pak`

---

## 📁 โครงสร้างไฟล์ใน THub (`tools/fonts/`)
```
modder-hub/
└── tools/
    └── fonts/
        ├── catalog.json              # ฐานข้อมูลและระบบจับคู่ Engine Score
        ├── library/                  # คลังไฟล์ TTF 15 ตระกูล (แยกโฟลเดอร์)
        │   ├── Prompt/
        │   ├── Kanit/
        │   ├── Bai_Jamjuree/
        │   └── ...
        ├── mapping/                  # ชุดเครื่องมือ PUA มาตรฐาน
        │   ├── Mapping.json          # 2,208 PUA entries
        │   ├── Char.txt              # รายการ Glyph ครบชุด
        │   ├── thai_font_mapper.py   # สคริปต์แปลงข้อความ Longest-Match
        │   └── validate_mapping.py   # สคริปต์ตรวจความถูกต้อง
        └── previews/                 # รูปภาพการ์ดตัวอย่าง 16:9 ของทุกฟอนต์
            ├── prompt_preview.png
            ├── kanit_preview.png
            └── ...
```

---
*จัดทำและซิงค์ความรู้โดย: THub 2.0 Engineering Team (NodNuatTranslator)*
