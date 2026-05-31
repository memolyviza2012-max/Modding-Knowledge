# 🤖 AI Agent Workflow: Modding Knowledge Upload Protocol (KI)

**Knowledge Item (KI):** มาตรฐานการทำงาน (SOP) สำหรับ AI Assistant ในการอัปโหลดข้อมูลเทคนิคการทำม็อด (Modding Knowledge) ขึ้น GitHub ของคุณ `memolyviza2012-max` เมื่อโปรเจคเกมใดๆ เสร็จสิ้น

## 🎯 จุดประสงค์
เพื่อให้ AI ทราบขั้นตอนที่ชัดเจนในการรวบรวมไฟล์อธิบายเทคนิค (README), สคริปต์ AI แปลภาษา (Python), และ Batch Scripts ต่างๆ นำไปจัดเก็บใน Repository `Modding-Knowledge` อย่างเป็นระเบียบ โดยที่ผู้ใช้ไม่ต้องสั่งการทีละขั้นตอน

## 🛠️ ขั้นตอนปฏิบัติการสำหรับ AI (AI Action Plan)

เมื่อผู้ใช้พิมพ์คำสั่งในทำนองว่า: *"อัพขึ้น github ได้เลย"*, *"บันทึก KI ลง Github"*, หรือ *"จบโปรเจค อัพข้อมูลได้"* ให้ AI ทำตามขั้นตอนดังนี้ทันที:

1. **เตรียม Repository ปลายทาง:**
   - เช็คว่าโฟลเดอร์ `E:\Mod_Workspace\Modding-Knowledge` มีอยู่แล้วหรือไม่
   - หากไม่มี ให้รันคำสั่ง `git clone https://github.com/memolyviza2012-max/Modding-Knowledge.git E:\Mod_Workspace\Modding-Knowledge`
   - หากมีอยู่แล้ว ให้ `cd` เข้าไปแล้วรันคำสั่ง `git pull` เพื่ออัปเดตข้อมูลล่าสุด

2. **จัดโครงสร้างโฟลเดอร์สำหรับเกมใหม่:**
   - สร้างโฟลเดอร์ใหม่ภายใต้ `Games/[ชื่อเกม_แบบไม่มีเว้นวรรค]` (เช่น `Games/SpaceHulk_Deathwing`) 

3. **คัดลอกไฟล์ความรู้และสคริปต์ (Knowledge Extraction):**
   - คัดลอกไฟล์ต่อไปนี้จากโฟลเดอร์ Workspace ของโปรเจคเกมนั้นๆ มายังโฟลเดอร์ใหม่ที่เพิ่งสร้าง:
     - `README.md` (ที่สรุปเทคนิค KI ทั้งหมดที่ค้นพบในโปรเจค)
     - `*.bat` (สคริปต์ Workflow เช่น 1_export, 2_import, 3_pack เท่าที่ปลอดภัยและไม่มีรหัสลับ)
   - **🛑 กฎเหล็กความปลอดภัยสูงสุด (CRITICAL SECURITY RULE):** ห้ามคัดลอกหรืออัปโหลดสคริปต์รันการทำงานหลัก (Execution Scripts) โดยเฉพาะสคริปต์เชื่อมต่อ API (เช่น `*.py`, `run_translation_*.py`) ขึ้นสู่ GitHub หรืออินเทอร์เน็ตเด็ดขาด! เพื่อป้องกัน API Key หลุด
   - **ข้อควรระวังเพิ่มเติม:** ห้ามคัดลอกไฟล์ขนาดใหญ่ เช่น โฟลเดอร์ `Extracted`, ไฟล์ `.pak`, `.locres` หรือไฟล์ภาพขนาดใหญ่เด็ดขาด

4. **ตั้งค่าบัญชี (หากจำเป็น):**
   - รันคำสั่ง `git config user.name "Antigravity"` และ `git config user.email "antigravity@gemini.com"` (หรือใช้ของระบบหากตั้งค่าไว้แล้ว)

5. **Commit & Push:**
   - รันคำสั่ง:
     ```bash
     git add .
     git commit -m "Add [ชื่อเกม] modding techniques and scripts"
     git push
     ```

6. **รายงานผลผู้ใช้:**
   - แจ้งผู้ใช้ว่าการจัดเก็บ Knowledge Item (KI) ลงในคลังแสง GitHub เรียบร้อยแล้ว พร้อมแนบ URL หากเป็นไปได้
