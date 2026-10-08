# UNCHARTED Legacy of Thieves Collection — Persona & Pronoun Calibration Guide
========================================================================================
> **ระบบ:** THub AI Helper Copilot — Persona & Military Voice Calibrator  
> **เกมเป้าหมาย:** UNCHARTED Legacy of Thieves Collection (*Uncharted 4: A Thief's End* & *Uncharted: The Lost Legacy*)  
> **หมวดหมู่:** Games / Localization Persona & Voice Calibration  
> **สถานะ:** ได้รับการตรวจสอบและปรับใช้สมบูรณ์ (Verified & Deployed)  

---

## 1. บทนำและปัญหาที่พบ (Overview & Root Cause)

ในกระบวนการแปลเกมด้วยระบบ Batch อัตโนมัติ (TRun / LLM Translation Engine) เมื่อมีการกำหนด Universe Tone เป็น **Military Tactical & Spec-Ops** มักเกิดผลข้างเคียงคือ:
1. **การเหมารวมสรรพนามเพศชาย (Male Pronoun Flattening):** ตัวละครหญิงถูกใส่สรรพนาม "ผม" หรือลงท้าย "ครับ" ในบทสนทนา (เช่น Chloe Frazer, Elena Fisher, Nadine Ross, Meenu, แม่ค้าในตลาด, แม่ชี)
2. **Ghost Subtitles จาก Cutscene Triggers:** รายการทริกเกอร์เสียงหรือคัตซีนที่มีข้อความต้นฉบับภาษาอังกฤษว่างเปล่า (`source = ""`) ถูกแปลออกมาเป็น `"ครับ"` ทำให้เกมแสดงคำว่า "ครับ" ลอยขึ้นมาบนหน้าจอระหว่างคัตซีน

---

## 2. ทำเนียบตัวละครและตารางสรรพนาม (Character Dossier & Pronoun Matrix)

| ตัวละคร / Speaker Tag | เพศ / บทบาท | สรรพนามตนเอง (1st Person) | สรรพนามเรียกผู้อื่น (2nd Person) | คำลงท้าย & น้ำเสียง (Voice / Tone) |
|---|---|---|---|---|
| **Chloe Frazer** (`CLO`) | หญิง / นักล่าสมบัติ (ตัวเอก Lost Legacy) | ฉัน | นาย (เรียก Nate/Sam)<br>เธอ (เรียก Nadine)<br>คุณ (สุภาพ/คนแปลกหน้า) | กระชับ ไหวพริบดี กวนประสาท ปากไว ไม่ใส่ ครับ/ค่ะ พร่ำเพรื่อ |
| **Nadine Ross** (`NAD`) | หญิง / ผู้บัญชาการทหารรับจ้าง Shoreline | ฉัน (ห้ามใช้ผม) | นาย / พวกนาย (สั่งลูกน้อง)<br>เธอ (เรียก Chloe) | สไตล์ทหารเข้มขรึม เด็ดขาด ละประธานในคำสั่งยุทธวิธี ไม่ใช้คำลงท้ายหวาน |
| **Elena Fisher** (`ELN`) | หญิง / นักข่าวสาว ภรรยานาธาน เดรก | ฉัน | นาย / เนท (เรียกสามี)<br>ซัลลี่ (เรียก Sully) | ฉลาด อบอุ่น เป็นกันเอง น้ำเสียงสามีภรรยาหยอกล้อ |
| **Meenu** (`MNU`) | หญิง / เด็กหญิงชาวอินเดียในตลาด | หนู / ฉัน | พี่ / พี่สาว / คุณน้า / คุณ | ไร้เดียงสา แก่นแก้ว ช่างเจรจา ลงท้าย "ค่ะ/นะคะ" |
| **Elderly / Market Vendors** (`EVF`, `MKTFA`-`E`) | หญิง / แม่ค้าผลไม้และพ่อค้าแม่ค้า | ฉัน / ป้า / ยาย | คุณผู้ชาย / คุณลูกค้า | เชิญชวนซื้อของ ลงท้าย "จ้า / นะจ๊ะ / ค่ะ" |
| **Sister Catherine / Nuns** (`CAS`, `NUN`) | หญิง / แม่ชีในสถานเลี้ยงเด็กกำพร้า | ซิสเตอร์ / ฉัน | เธอ / พวกเธอ / คุณพ่อ | สุภาพ เคร่งขรึม เปี่ยมเมตตา ลงท้าย "ค่ะ" |
| **Shoreline Mercenaries** (`MRC...`, `ORC`) | ชาย / ทหารรับจ้างเอกชน | ผม / ฉัน (หรือละประธาน) | นาย / พวกนาย<br>เรียก Nadine ว่า "หัวหน้า / คุณผู้หญิง (Ma'am)" | สื่อสารวิทยุกระชับ (Radio Brevity) เน้นความชัดเจนในสนามรบ |

---

## 3. สรุปบันทึกการปรับแก้ (Calibration Resolution Log)

ทำการแก้ไขในไฟล์ `02_Translation_Workspace/UNCHARTED_All_Thai.csv` ทั้งหมด **47 แถว**:

### 3.1 กลุ่มตัวละครหญิง (Female Dialogue Fixes)
- **Chloe Frazer (`CLO`)**:
  - `tha.subtitles:da8d2472`: "Thank you, Dr. Freud." ➔ `ขอบใจย่ะ ดร.ฟรอยด์`
  - `tha.subtitles:dbdfad8c`: "Hello, sir." ➔ `สวัสดีค่ะ`
  - `tha.subtitles:3d877b4f`: "Sorry, mum." ➔ `ขอโทษทีนะแม่`
  - `tha.subtitles:8cc5d4bf`: "It hit me!" ➔ `มันชนฉัน!`
  - `tha.subtitles:94091a1c`: "Don't mind me." ➔ `ไม่ต้องสนใจฉันนะ`
  - `tha.subtitles:90c807ab`: "Mind if I just..." ➔ `คงไม่ว่าอะไรถ้าฉันจะ...`
  - `tha.subtitles:994a3cc5`: "Don't mind me." ➔ `ไม่ต้องสนใจฉันนะ`
  - `tha.subtitles:4c930fce`: "Thanks, Dad." ➔ `ขอบคุณนะพ่อ`
  - `tha.subtitles:451134a0`: "Thanks for that, Dad." ➔ `ขอบคุณสำหรับสิ่งนี้นะพ่อ`
  - `tha.subtitles:d8875132`: "Oh. Hello, Mr..." ➔ `โอ้ สวัสดีค่ะ คุณ...`
  - `tha.subtitles:4a6fbe5e`: "Yeah, coming." ➔ `จ้า กำลังไป`

- **Meenu (`MNU`)**:
  - `tha.subtitles:a2499ff8`: "Please, please, sir. Help me find him!" ➔ `ได้โปรดเถอะค่ะคุณน้า ช่วยหนูตามหาเขาหน่อย!`
  - `tha.subtitles:5fda88f2`: "Wait! There he is! There he is! Thank you, sir!" ➔ `เดี๋ยว! เขาอยู่ตรงนั้น! อยู่ตรงนั้นแล้ว! ขอบคุณนะคะคุณน้า!`
  - `tha.subtitles:094a77d6`: "This way, lady." ➔ `ทางนี้ค่ะ พี่สาว`
  - `tha.subtitles:a1c4bbfa`: "Here you go." ➔ `นี่ค่ะ`
  - `tha.subtitles:8c25ba5a`: "Eight hundred rupees, please." ➔ `แปดร้อยรูปีค่ะ`

- **Female Market Vendor (`EVF`)**:
  - `tha.subtitles:c4c82939`: "Apples! Buy my fresh apples! Only fifteen hundred Ariary!" ➔ `แอปเปิ้ลจ้า! ซื้อแอปเปิ้ลสด ๆ ได้นะจ๊ะ! แค่หนึ่งพันห้าร้อยอาเรียรีเท่านั้น!`
  - `tha.subtitles:c98b0fe0`: "Sir! Won't you try an apple? Best apples in the market!" ➔ `คุณผู้ชายคะ! ลองชิมแอปเปิ้ลหน่อยไหมคะ? แอปเปิ้ลที่ดีที่สุดในตลาดเลยนะ!`
  - `tha.subtitles:cd4a1257`: "Sir! You may find other apples here..." ➔ `คุณผู้ชายคะ! คุณอาจจะหาแอปเปิ้ลเจ้าอื่นได้ที่นี่ แต่รับรองไม่เจอที่ดีกว่านี้แน่นอนค่ะ! แค่หนึ่งพันห้าร้อยอาเรียรีเท่านั้น!`
  - `tha.subtitles:d30d4252`: "Sir, you look like you could use an apple..." ➔ `คุณผู้ชายคะ ดูเหมือนคุณอยากทานแอปเปิ้ลนะ แค่หนึ่งพันห้าร้อยอาเรียรีเท่านั้นค่ะ!`
  - `tha.subtitles:d7cc5fe5`: "Ah, thank you very much, sir. Enjoy your apple!" ➔ `ขอบคุณมากนะคะคุณผู้ชาย ทานแอปเปิ้ลให้อร่อยนะคะ!`

- **Catholic Nun (`NUN`)**:
  - `tha.subtitles:349a7f9b`: "(sighs) Good night, Father." ➔ `(ถอนหายใจ) ราตรีสวัสดิ์ค่ะ คุณพ่อ`

- **Elena Fisher (`ELN`)**:
  - `tha.subtitles:96f46f83`: "Yeah." ➔ `อืม`

- **Nadine Ross (`NAD`)**:
  - `tha.subtitles-systemic:96f1823b0c8396c7`: "Any one of you doubt my leadership now? If so, you'd be wise to keep it to yourself." ➔ `มีใครกังขาในความเป็นผู้นำของฉันอีกไหม? ถ้ามี... ก็ฉลาดพอที่จะหุบปากไว้ซะ`

### 3.2 การแก้ไข Ghost Subtitles (23 แถว)
- เคลียร์ค่าสตริงว่างเปล่าให้ตรงกับต้นฉบับ สำหรับคัตซีน `CLO_IGC_RUR_GANESH_...` (เช่น `tha.subtitles:cf6e2cfc`, `4137909d`, `58c8190d` ฯลฯ) ป้องกันคำว่า "ครับ" ปรากฏบนหน้าจอคัตซีนโดยไม่มีเสียงพูด

---

## 4. กฎเหล็กความปลอดภัยของไฟล์ (File Safety Standard)
1. **Schema Preservation**: รักษา 5 คอลัมน์ครบถ้วน (`key,source,translation,context,file_path`)
2. **Context Integrity**: ไม่มีการเขียนทับหรือดัดแปลงคอลัมน์ `context` โดยเด็ดขาด
3. **Encoding & Line Breaks**: ใช้อักขระ `utf-8-sig` (UTF-8 with BOM) และ `newline=''` เพื่อรักษาความเข้ากันได้กับเกมเอนจินของ Naughty Dog
