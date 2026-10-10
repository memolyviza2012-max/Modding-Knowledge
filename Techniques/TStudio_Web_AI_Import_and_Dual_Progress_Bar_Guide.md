# TStudio Web: คู่มือระบบนำเข้าไฟล์เป็นร่างแปล AI และหลอดความคืบหน้าคู่ (Dual Progress Bar: แปล AI vs คนร่วมแปล)

> **Document Type:** Knowledge Item (KI) / Technical Architecture Guide  
> **Target Subsystem:** TStudio Web Portal, CSV Parser, Moderation & Collaboration System  
> **Location:** `E:\Mod_Workspace\Modding-Knowledge\Techniques\TStudio_Web_AI_Import_and_Dual_Progress_Bar_Guide.md`  
> **Last Updated:** ตุลาคม 2026

---

## 1. ที่มาและปรัชญาการออกแบบ (Design Philosophy)

ในกระบวนการแปลเกมคอมมูนิตี้ (Community Crowdsourced Localization):
1. **ไฟล์ตั้งต้น (Initial Import):** บ่อยครั้งที่ผู้สร้างโปรเจกต์ (Host) นำเข้าไฟล์ CSV หรือ JSON ที่ผ่านการแปลหยาบด้วยโมเดล AI (เช่น Claude, GPT, DeepSeek หรือ Gemini) มาก่อนแล้ว
2. **ปัญหาเดิมของระบบเก่า:** ระบบเก่ามองว่าข้อความใดก็ตามที่มีคำแปลภาษาไทยติดมาในไฟล์ ให้ถือว่าเป็นข้อความที่ตรวจผ่านแล้ว (`isApproved = true`, `approvedStrings = translatedStrings`) ส่งผลให้การ์ดแสดงผลความคืบหน้า 100% ตรวจผ่านแล้ว ทั้งที่ยังไม่มีมนุษย์เข้ามาตรวจสอบสำนวนเลย
3. **มาตรฐานใหม่ (AI Draft & Dual Progress):**
   - **เมื่อนำเข้าไฟล์ใหม่:** ข้อความที่มีคำแปลภาษาไทยติดมา จะถูกกำหนดสถานะเป็น **"ร่างแปล AI" (👑 แปล AI)** เสมอ (`isApproved = false`, `isAiGenerated = true`, `userId = 'ai'`)
   - **หน้าการ์ดโปรเจกต์ (Portal Cards & Navbar):** จะต้องแยกหลอดแสดงความคืบหน้าออกเป็น **2 หลอดอย่างชัดเจน**:
     - 🤖 **แปล AI (หลอดสีทอง/Amber):** เปอร์เซ็นต์และจำนวนประโยคที่เป็นร่างแปล AI
     - 👥 **คนร่วมแปล (หลอดสีเขียว/Emerald):** เปอร์เซ็นต์และจำนวนประโยคที่มนุษย์ส่งสำนวนและได้รับการอนุมัติเข้า Master แล้ว
   - **การอัปเกรดสถานะ:** ข้อความจะนับเป็น **"คนร่วมแปล"** ก็ต่อเมื่อมีผู้ส่งคำแปลเข้ามา (Community Submission) และได้รับการตรวจสอบอนุมัติโดย Host/ผู้ตรวจทานแล้วเท่านั้น

---

## 2. โครงสร้างสถานะและวงจรชีวิตข้อความ (String Lifecycle)

```mermaid
flowchart TD
    A["นำเข้าไฟล์ CSV/JSON มีแปลไทย"] -->|csvParser treats as AI| B["ร่างแปล AI (👑 Gold)<br/>isApproved: false, userId: 'ai'"]
    B -->|นับเข้า| B1["หลอดแปล AI 🤖 (สีทอง)"]

    C["นักแปลชุมชนเสนอสำนวนใหม่"] --> D["รออนุมัติ 🔴 (Pending Review)<br/>isApproved: false, userId: human"]
    D -->|นับเข้า| D1["🚨 รออนุมัติ (Pending Badge)"]

    D -->|Host กดอนุมัติ (handleApprove)| E["ตรวจผ่านแล้ว 🟢 (Human Master)<br/>isApproved: true"]
    B -->|Host แปลเองหรืออนุมัติสำนวนมนุษย์| E
    E -->|นับเข้า| E1["หลอดคนร่วมแปล 👥 (สีเขียว)"]
    E -->|หักออกจาก| B1
```

### รายละเอียดการคำนวณสถิติ (Mathematical Integrity)

สำหรับทุกโปรเจกต์:
$$\text{Total} = \text{totalStrings}$$
$$\text{HumanCount} = \text{approvedStrings}$$
$$\text{AiCount} = \max(0, \text{translatedStrings} - \text{approvedStrings})$$
$$\text{AI \%} = \min(100, \text{round}((\text{AiCount} / \text{Total}) \times 100))$$
$$\text{Human \%} = \min(100, \text{round}((\text{HumanCount} / \text{Total}) \times 100))$$

---

## 3. สถาปัตยกรรมโค้ดและการนำไปใช้ (Implementation Architecture)

### 3.1 การปรับปรุง CSV Parser (`src/lib/parsers/csvParser.ts`)
เมื่อผู้ใช้อัปโหลดไฟล์ CSV สร้างโปรเจกต์ใหม่:
- กำหนด `treatTranslationsAsAi: true` เป็นค่าเริ่มต้น
- แปลงข้อความที่มีคำแปลภาษาไทยให้มี:
  ```ts
  isApproved: false, // ยังไม่ถือว่ามนุษย์อนุมัติ
  isAiGenerated: true,
  userId: 'ai',
  authorName: 'แปล AI',
  createdAt: 'นำเข้าเป็นร่างแปล AI'
  ```

### 3.2 ตัวช่วยคำนวณและไมเกรตระบบ (`src/lib/moderation/projectStatsHelper.ts`)
ประกอบด้วย 2 ฟังก์ชันหลัก:

1. **`getDualProjectProgress(project)`**:
   - คำนวณเปอร์เซ็นต์และจำนวนของทั้งสองหลอด
   - รองรับ **Auto-Fallback สำหรับโปรเจกต์รุ่นเก่า**:
     ```ts
     if (project.approvedStrings === project.translatedStrings && project.translatedStrings > 0) {
       aiCount = project.translatedStrings;
       humanCount = 0;
     }
     ```
     ทำให้โปรเจกต์เดิมทั้งหมดบน Cloud Database ถูกแสดงผลเป็น **แปล AI ทันที** โดยไม่ต้องรันสคริปต์แก้ฐานข้อมูลล่วงหน้า

2. **`migrateProjectStringsToAi(strings, suggestions)`**:
   - ตรวจสอบประโยคในโปรเจกต์เมื่อเปิดขึ้นมา:
     - หากเป็นข้อความจากไฟล์ต้นฉบับดั้งเดิม ปรับเป็น `isApproved = false` (ร่างแปล AI)
     - **เว้นแต่** มีผู้ส่งคำแปลเข้ามาจริง (`userId !== 'ai'`):
       - หากได้รับการอนุมัติแล้ว: คงสถานะ `isApproved = true` (คนร่วมแปล)
       - หากยังไม่อนุมัติ: ให้อยู่ในสถานะ **รออนุมัติ 🔴** (`pending_review`)
   - คำนวณและส่งคืนสถิติ `stats: { totalStrings, translatedStrings, aiStrings, approvedStrings, pendingStrings }`

### 3.3 การแสดงผลบนการ์ดใน Portal (`src/components/portal/PortalView.tsx`)
1. **การ์ดโปรเจกต์ขนาดใหญ่ (Main Project Card):**
   - มีหลอดสีทอง **🤖 แปล AI (XX% • X,XXX บรรทัด)**
   - มีหลอดสีเขียว **👥 คนร่วมแปล (YY% • Y,YYY บรรทัด)**
   - หากมีรายการรออนุมัติ จะแสดง Badge สีแดงเตือนชัดเจน `🚨 Z รออนุมัติ`
2. **การ์ดประวัติแปลต่อ (Continue Translating Strip):**
   - แสดงสัญลักษณ์คู่ `🤖 AI {aiPercent}% • 👥 คน {humanPercent}%`

### 3.4 การแสดงผลบนแถบ Navbar (`src/components/layout/Navbar.tsx`)
Project Capsule ด้านบนซ้ายแสดง:
- แถบความคืบหน้าแบบสองสี (Dual Stacked Progress Bar: สีทองต่อด้วยสีเขียว)
- ป้ายบอกเปอร์เซ็นต์คู่: `🤖 AI {aiPercent}% • 👥 คน {humanPercent}%`

### 3.5 ระบบจับคู่สองไฟล์ (Dual File Selection: Origin EN + ไฟล์ใหม่) & ตัวเลือกระบุประเภทคำแปล
ในเวอร์ชันล่าสุด ระบบนำเข้าไฟล์ถูกยกระดับเพื่อรองรับ Workflow ของม็อดเดอร์เกมจริง ที่มักแยกดัมป์ไฟล์ภาษาอังกฤษ (Original Dump) และไฟล์คำแปล (Translated Dump) เป็น 2 ไฟล์คนละชุด:

1. **สล็อตเลือกไฟล์อิสระ 2 ช่อง (`CreateProjectModal.tsx`):**
   - 🇬🇧 **ไฟล์ต้นฉบับ Origin EN:** ดึง Key และ Source Text ภาษาอังกฤษ
   - 🇹🇭 **ไฟล์ใหม่ / ไฟล์แปล:** นำคำแปลมาจับคู่เข้ากับประโยคต้นฉบับ
   - **ความยืดหยุ่นของโหมดการจับคู่ (Pairing Modes):**
     - **Dual Paired:** อัปโหลดทั้งสองไฟล์ ระบบจับคู่ข้ามไฟล์อัตโนมัติ
     - **Origin Only:** อัปโหลดเฉพาะไฟล์ Origin EN อย่างเดียว (ตั้งต้นโปรเจกต์ 0% แปล)
     - **New Only / Single File:** อัปโหลดเฉพาะไฟล์เดียวที่มีทั้งคอลัมน์อังกฤษและไทย
2. **ตัวเลือกระบุประเภทคำแปลสำหรับไฟล์ใหม่ (Translation Source Type Toggle):**
   - 🤖 **เป็นร่างแปล AI (AI Draft):** คำแปลที่นำเข้าจะได้รับสถานะ `isApproved: false, isAiGenerated: true, userId: 'ai'` และนับเข้า **หลอดสีทอง 👑 แปล AI**
   - 👥 **แปลคน (Human Verified):** คำแปลที่นำเข้าจะได้รับสถานะ `isApproved: true, isAiGenerated: false, userId: 'host_danaiwit'` และนับเข้า **หลอดสีเขียว 🟢 คนร่วมแปล**
3. **เอนจินจับคู่อัจฉริยะ (`src/lib/parsers/dualFileImporter.ts`):**
   - **Key-based Matching:** จับคู่ผ่าน `key`, `id`, `name`, หรือ `hash`
   - **Index Fallback:** หากโครงสร้างไม่มี Key แต่จำนวนบรรทัดเท่ากัน จะจับคู่ตามลำดับแถว (Row index) ทันที
   - รองรับฟอร์แมตไฟล์หลากหลาย: `.csv`, `.json`, `.srt`
4. **การเชื่อมโยงกับระบบ Sync / อัปเดตไฟล์ออฟไลน์ (`SyncModal.tsx` & `syncEngine.ts`):**
   - เมื่อม็อดเดอร์นำไฟล์ที่ดาวน์โหลดไปแปลข้างนอกมาอัปโหลด Sync กลับเข้าโปรเจกต์ สามารถเลือกระบุได้เช่นกันว่าเป็น **🤖 แปล AI** หรือ **👥 แปลคน**
   - หากเลือก "แปล AI": ประโยคที่ถูกแก้ไขจะเข้าสู่ระบบเป็นร่าง AI โดยไม่ทับประโยคที่มนุษย์เคยตรวจผ่านแล้ว
   - หากเลือก "แปลคน": ประโยคที่ถูกแก้ไขจะได้รับการรับรองเข้าสู่ Master ทันที

---

## 4. มาตรการความปลอดภัยของข้อมูล (Data Loss Prevention)

- **ไม่ลบคำแปลของผู้ใช้:** การไมเกรตตรวจสอบเฉพาะคำแปลที่เกิดจากการ Import อัตโนมัติเท่านั้น คำแปลที่ผู้ใช้งานพิมพ์ส่งเข้ามาจะไม่มีการสูญหาย
- **Cloud Stats Synchronous Update:** เมื่อเปิดโปรเจกต์หรือมีการอนุมัติคำแปล ระบบจะซิงค์ตัวเลขสถิติใหม่ขึ้น Supabase `projects` ทันทีผ่าน `updateProjectStatsCloud`
- **Smart Differential Merge:** การอัปโหลดไฟล์ใหม่จะไม่ทับประโยคที่เหมือนเดิม และคัดกรองประโยคที่ถูกแก้ไขตามระดับความน่าเชื่อถือ

---

## 5. การทดสอบและการยืนยันผล (Verification & Validation)

1. **TypeScript Type Safety:** รัน `npm run build` ตรวจสอบผ่าน 100% ไม่มีข้อผิดพลาด TS6133 หรือ TS2339
2. **Rollup Production Build:** สร้าง Bundled Assets ผ่านเรียบร้อย
3. **Portal Preview Consistency:** ทั้งตอนสร้างโปรเจกต์ใหม่และตอนดูรายการโปรเจกต์เดิม ข้อมูลความคืบหน้าแสดงผลตรงกันทั้งสองหลอด
4. **Dual Import Validation:** ทดสอบโหลด Origin EN ควบคู่กับ New TH ทั้งกรณีเลือก AI และเลือก แปลคน สถิติหลอดความคืบหน้าตรงตามที่เลือกทันทีตั้งแต่ขั้นตอนสร้างโปรเจกต์
