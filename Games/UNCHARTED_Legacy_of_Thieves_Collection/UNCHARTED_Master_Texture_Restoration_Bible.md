# UNCHARTED: Legacy of Thieves Collection - Master Texture Restoration & Localization Bible

## 1. Executive Summary & Overview
ในการแปลงภาษาเท็กซ์เจอร์ (Texture Localization) ของเกมระดับ AAA อย่าง **UNCHARTED 4: A Thief's End** และ **UNCHARTED: The Lost Legacy** มีไฟล์ภาพพื้นผิวที่เกี่ยวข้องกับเนื้อเรื่อง บันทึก ป้ายประกาศ และปริศนารวมทั้งสิ้น **234 ภาพ** (ครอบคลุมทั้ง Drake's Journal, เอกสารประวัติศาสตร์, ปริศนาหอนาฬิกา, จดหมายคฤหาสน์, ป้ายถนน, ป้ายคำเตือน, และสมุดบันทึกของแม่ Cassandra Morgan)

เอกสารฉบับนี้สรุปมาตรฐานสูงสุดด้านวิศวกรรมภาพ (Masterpiece Quality Standards), ปัญหาข้อผิดพลาดในอดีต (Root Cause Analysis), สถาปัตยกรรมอัลกอริทึมที่ใช้แก้ไขจริง, และขั้นตอนการแพ็คกลับสู่เกมแบบ Native Bit-Exact Patching

---

## 2. การวิเคราะห์ปัญหาเดิม (Root Cause Analysis of Visual Defects)

### ปัญหาที่ 1: แถบสีดำและรอยตัดสี่เหลี่ยม (Hard Box Cutout Borders & Bleached Patches)
- **สาเหตุรากเหง้า**: 
  1. การใช้สคริปต์รุ่นเก่าที่นำ `draw.rectangle()` หรือ `MaxFilter()` มาถมทับพื้นที่ข้อความ
  2. การใช้ Absolute Threshold เช่น `arr[:, :, 0] < 125` บนพื้นหลังที่มีความมืด เช่น รอยไหม้ของกระดาษ (`a98f03887c84`), เงากระดาษใต้แสงแดด (`c9ec9cc7466d`), หรือกระดานชนวนสีเทาเข้ม (`377caf9d246b`) ทำให้สคริปต์ตรวจจับว่า "ทั้งผืนกระดาษคือหมึก" และทำการลบทั้งผืนจนเกิดรอยตัดสี่เหลี่ยมขอบคม (Cutout Seam)
- **แนวทางแก้ไขถาวร**:
  - เปลี่ยนมาใช้ **Pure Local Relative Median Inpainting** โดยคำนวณ `diff = arr_med - arr[:, :, :3] > 14` จากตัวกรอง Median Filter ขนาด 11 พิกเซล
  - พื้นหลังสีมืด รอยไหม้ และเงาจะมีความแตกต่างจากค่ามัธยฐานในพื้นที่ `diff ~ 0` เสมอ จึงไม่ถูกลบแม้แต่พิกเซลเดียว ลบเฉพาะลายเส้นตัวอักษรที่มีความคมชัดสูงเท่านั้น

### ปัญหาที่ 2: จุดฝุ่นประกายดาวบนพื้นหลังสีดำ (Star-dot Noise on Black Decal Masks)
- **สาเหตุรากเหง้า**:
  - ป้ายโลโก้ ป้ายไม้แกะสลัก และป้ายสเตนซิล (เช่น `775894008b04` Parson's Pub, `1a2a1d7d0c1a` Rossi Estate Logo, `0522b752be69` ป้ายคุกปานามา) จัดเก็บเป็น Mask Mode `L` หรือ Decal RGBA
  - เกรนพื้นหลังเดิมมีค่าพิกเซล `1 <= pixel <= 55` ซึ่งเมื่อเกมประมวลผลผ่าน Stencil Shader / Alpha Test จะถูกขยายเป็นจุดแสงระยิบระยับทั่วภาพเหมือนดวงดาวบนท้องฟ้า
- **แนวทางแก้ไขถาวร**:
  - พัฒนาสคริปต์ `clean_all_mask_star_noise.py` สแกนและล้างพิกเซล Noise นอกเขตอักษรให้เป็น **Pure 0 (0x00)** ดำสนิท 100% กวาดล้างพิกเซลแปลกปลอมกว่า 674,000 พิกเซลทั่วทั้งโปรเจกต์

### ปัญหาที่ 3: รอยอักษรเดิมหลงเหลือ (Ghost Text Remnants)
- **สาเหตุรากเหง้า**:
  - อักษรภาษาอังกฤษเดิมมีระยะห่าง (Kerning/Ascender/Descender) ที่กว้างกว่าภาษาไทย หากวางอักษรไทยทับโดยไม่ลบหมึกเดิม หรือลบไม่เต็มก้านอักษร จะมองเห็นหาง 'P', 'b', "'s" โผล่ออกมาด้านหลัง
- **แนวทางแก้ไขถาวร**:
  - ใช้ **Dilation Mask (MaxFilter 5-7)** ครอบคลุมก้านอักษรเดิมให้หมดจด แล้วใช้ **Normalized Convolution** ดึงเนื้อไม้/เนื้อกระดาษรอบข้างเข้ามาสมานแผลแบบไร้รอยต่อ

### ปัญหาที่ 4: การสูญเสียงานศิลปะแท้ของเกม (Accidental Art Overwrite)
- **สาเหตุรากเหง้า**:
  - เท็กซ์เจอร์บางแผ่นไม่ได้มีข้อความจริง แต่เป็นภาพสเก็ตช์หรือภาพสะท้อนด้านหลังกระดาษ เช่น:
    - `41316972d802`: ด้านหลังของบันทึกกระเบื้อง Tew ซึ่งเป็นรอยหมึกซึมย้อนกลับ (Bleed-through) จากด้านหน้า
    - `5c49ab776ca2`: ภาพสเก็ตช์แผนที่ภูเขาไฟมาดากัสการ์
    - `18ae25d4d19b`: ภาพสเก็ตช์โบราณวัตถุในบทส่งท้าย (Epilogue Notebook)
  - สคริปต์รุ่นแรกประเมินผิดพลาด คิดว่าเป็นข้อความภาษาอังกฤษ จึงไปลบทิ้งแล้วพิมพ์ข้อความแต่งเองทับลงไป
- **แนวทางแก้ไขถาวร**:
  - คืนค่า (Restore) ไฟล์ต้นฉบับแท้จากเกม 100% โดยไม่แตะต้องงานศิลป์

---

## 3. สรุปความคืบหน้าการรีมาสเตอร์ครบทุกหมวดหมู่ (234 ไฟล์)

| หมวดหมู่ | จำนวนไฟล์ | อัลกอริทึมที่ใช้ | สถานะการตรวจสอบ |
|---|---|---|---|
| **Drake's Journal (Batches 1-4)** | 78 ไฟล์ | Smart Ink Healing + Hand-drawn Curve Fit (`Mali-Regular`) | สมบูรณ์ 100% ไร้รอยขอบ |
| **Masks & Decals (ป้ายแกะสลัก, คุก, ป้ายกล่อง)** | 66 ไฟล์ | Pure 0 Background Clamping + Normalized Convolution (`Pridi-Regular`, `Sriracha-Regular`) | สมบูรณ์ 100% ไร้ Star Dots |
| **Chapter 11 Tower Puzzles** | 12 ไฟล์ | Selective Cyan/Magenta/Blue Inpainting + Strict Alpha Channel Preservation | สมบูรณ์ 100% ตัวเลขและสีตรงต้นฉบับ |
| **Cassandra Morgan's Journal (Batch 5)** | 12 ไฟล์ | Normalized Convolution + Historical Cursive (`Charmonman-Regular`) + รักษาภาพสเก็ตช์ตราโจรสลัด | สมบูรณ์ 100% ไร้รอยด่างขาว |
| **Historical & Colony Letters (Batch 6)** | 35 ไฟล์ | Pure Relative Median Ink Inpainting + Burnt Edge Protection | สมบูรณ์ 100% ขอบไหม้สมบูรณ์ |
| **Modern & Mansion Letters (Batch 7)** | 19 ไฟล์ | Normalized Convolution + Blue Ink Pen Matching | สมบูรณ์ 100% |
| **Dossiers, Signs & Ephemera (Batches 8-10)** | 12 ไฟล์ | Stencil Typography + Pure Art Protection | สมบูรณ์ 100% |
| **รวมทั้งสิ้น** | **234 ไฟล์** | **Zero-Defect Pipeline** | **ผ่านการตรวจสอบ Native 100%** |

---

## 4. มาตรฐานวิศวกรรมการแพ็คและติดตั้ง (Native PSARC In-Place Patching)

1. **เครื่องมือบีบอัด**:
   - ประมวลผลผ่าน `texconv.exe` ด้วยพารามิเตอร์:
     ```powershell
     texconv.exe -nologo -y -dx10 -nogpu -f <FORMAT> -m <MIPS> -sepalpha -if BOX -o <DEST> <SOURCE>
     ```
   - ฟอร์แมตที่รองรับ: `BC1_UNORM` (71), `BC4_UNORM` (80), `BC5_UNORM` (83), `BC7_UNORM` (98)
2. **การสตรีมและแพ็คลงในคลังเกม**:
   - ดำเนินการผ่าน `05_Scripts_and_Tools/pack_agy_images.py`
   - ทำการแพ็คแบบ In-place Byte Stream ลงใน:
     - `Uncharted4_data/build/pc/uncharted4/texturedict2.psarc`: 128 ranges
     - `Uncharted4_data/build/pc/thelostlegacy/texturedict2.psarc`: 95 ranges
3. **ผลการตรวจสอบ (Audit Verification)**:
   - ตรวจสอบผ่าน `verify_all_234_completed.py`: ขนาดและ Color Mode ตรงกับต้นฉบับ 100% (0 Corrupted, 0 Mismatches)
   - Readback Hash Verification: ผ่านกระบวนการ `installed_native_readback_passed` 100%
