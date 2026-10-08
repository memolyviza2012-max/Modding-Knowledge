# TStudio Web: Smart Differential Merge & Recency Matching Guide (ระบบซิงค์แปลแยกประโยคแก้ไข & จับคู่ความใหม่)

> **หมวดหมู่:** Techniques / Collaborative Localization  
> **ไฟล์ต้นฉบับ:** `src/lib/sync/syncEngine.ts`, `src/components/modals/SyncModal.tsx`, `src/lib/moderation/stringStatusHelper.ts`  
> **อัปเดตล่าสุด:** 8 ตุลาคม 2026  

---

## 1. ที่มาและวัตถุประสงค์ (Problem & Objective)

ในโปรเจกต์แปลเกมขนาดใหญ่ที่มีข้อความนับหมื่นบรรทัด ผู้ร่วมแปลมักต้องการ:
1. **ดาวน์โหลดไฟล์แปล (.csv)** ไปเปิดแก้ไขต่อแบบออฟไลน์ด้วยเครื่องมือภายนอก เช่น **Microsoft Excel**, **Google Sheets**, หรือ **VS Code**
2. **อัปโหลดไฟล์ที่แปลเสร็จแล้วกลับเข้าสู่เว็บสตูดิโอ**
3. **เงื่อนไขสำคัญสูงสุด**:
   - **"แทนที่เฉพาะประโยคที่ถูกแก้ไขเท่านั้น"**: ตรวจจับประโยคที่มีการปรับปรุงคำแปลจริง (`incomingText !== existingText`)
   - **"ถ้าตัวไหนเหมือนเดิม มันจะไม่ทับ"**: บรรทัดที่ไม่ได้แก้ไขหรือคำแปลเดิมเหมือนเดิม 100% **จะต้องไม่ถูกทับ ไม่สร้างข้อเสนอซ้ำ และไม่ถูกรีเซ็ตสถานะ** (ประโยคที่ `ตรวจผ่านแล้ว 🟢` จะต้องคงสถานะตรวจผ่านแล้วไว้คงเดิม และประโยคที่ `แปล AI 👑` จะต้องคงสถานะไว้คงเดิม)
   - **"ระบบจับคู่ความใหม่ (Recency & Novelty Matching)"**: ระบุเวลา Timestamp ปัจจุบันให้กับการแก้ไขใหม่ ทำให้ระบบ Moderation ตรวจจับเป็น **ข้อเสนอใหม่รอตรวจ (🔴 สีแดง)** เพื่อให้ผู้ดูแลและม็อดเดอร์เห็นและกดอนุมัติได้อย่างแม่นยำ

---

## 2. สถาปัตยกรรมการจับคู่และเปรียบเทียบ (Diff & Novelty Matching Architecture)

### 2.1 โครงสร้างข้อมูล Diff Report (`SyncDiffReport`)
```typescript
export interface ChangedDiffItem {
  key: string;
  sourceText: string;
  oldTranslation: string;
  newTranslation: string;
  stringId: string;
}

export interface SyncDiffReport {
  totalInNewFile: number;
  newStringsCount: number;
  updatedTranslationsCount: number;
  unchangedCount: number;
  preservedCommunityCount: number;
  changedItems: ChangedDiffItem[];
}
```

### 2.2 อัลกอริทึมการจับคู่คีย์สองชั้น (Two-Tier Key & Source Matching)
เพื่อป้องกันปัญหาชื่อคีย์ผิดพลาดหรือมีการตัดแต่งช่องว่างในโปรแกรมสเปรดชีต:
```typescript
// 1. สร้างดัชนีคีย์และต้นฉบับ
const existingKeyMap = new Map<string, StringEntry>();
const existingSourceMap = new Map<string, StringEntry>();

for (const s of existingStrings) {
  if (s.key) {
    existingKeyMap.set(s.key.trim(), s);
    existingKeyMap.set(s.key.trim().toLowerCase(), s);
  }
  if (s.sourceText) {
    existingSourceMap.set(s.sourceText.trim(), s);
  }
}

// 2. จับคู่ลำดับ: คีย์ตรงกัน -> กรณีไม่พบคีย์ ให้ทดลองจับคู่จาก Source Text ที่ตรงกันทุกประการ
let existing = rawKey ? (existingKeyMap.get(rawKey) || existingKeyMap.get(rawKey.toLowerCase())) : undefined;
if (!existing && rawSource) {
  existing = existingSourceMap.get(rawSource);
}
```

### 2.3 การตรวจจับความแตกต่าง (Novelty & Change Detection)
```typescript
const activeOldTrans = (approvedSugg?.translationText || topSugg?.translationText || existing.targetText || '').trim();
const newTrans = (incomingSuggs[0]?.translationText || incomingStr.translation || '').trim();

// กฎที่ 1: ถ้าในไฟล์ใหม่ไม่มีคำแปล หรือมีคำแปลเหมือนกับคำแปลปัจจุบันทุกตัวอักษร
if (!newTrans || newTrans === activeOldTrans) {
  unchangedCount++; // "ถ้าตัวไหนเหมือนเดิม มันจะไม่ทับ" -> ข้ามการแก้ไข 100%
} else {
  // กฎที่ 2: มีการแก้ไขประโยคจริง -> นับเป็นคำแปลอัปเดตใหม่ และบันทึกลง changedItems
  updatedTranslationsCount++;
  changedItems.push({
    key: existing.key,
    sourceText: existing.sourceText,
    oldTranslation: activeOldTrans,
    newTranslation: newTrans,
    stringId: existing.id,
  });
}
```

---

## 3. กลยุทธ์การผสานคำแปล (Merge Strategies)

ระบบรองรับ 2 โหมดหลักที่ปรับให้เหมาะกับบทบาทผู้ใช้งาน (User Role):

| กลยุทธ์ (Strategy) | เหมาะสำหรับ | พฤติกรรมต่อประโยคที่แก้ไข | พฤติกรรมต่อประโยคเดิมที่เหมือนเดิม | สถานะใน Moderation |
| :--- | :--- | :--- | :--- | :--- |
| **`smart_differential` / `overwrite_master`** | แอดมิน / หัวหน้าโปรเจกต์ (Lead) | แทนที่และอนุมัติเป็น Master ทันที (`isApproved: true`) | **ไม่ทับ ข้าม 100%** (คงสถานะตรวจผ่านแล้ว 🟢 เดิมไว้) | 🟢 ตรวจผ่านแล้ว (Verified) |
| **`safe_merge`** | ผู้ร่วมแปลทั่วไป (Contributor / Translator / Guest) | สร้างเป็นข้อเสนอใหม่พร้อมประทับเวลาปัจจุบัน (`nowIso`) | **ไม่ทับ ไม่สร้างข้อเสนอซ้ำ 100%** | 🔴 รอตรวจ (Pending Review) |

### 3.1 การผสานเวลา (ISO Timestamp Recency)
เมื่อสร้างข้อเสนอจากการอัปโหลด ระบบจะประทับเวลาด้วย ISO 8601 String:
```typescript
const nowIso = new Date().toISOString();
const updateSugg: Suggestion = {
  id: `sugg_sync_${Date.now()}_${Math.random().toString(36).substring(2, 6)}`,
  stringId: existing.id,
  userId: authorId,
  authorName,
  authorRole,
  translationText: newTrans,
  isAiGenerated: false,
  score: isMasterOverwrite ? 10 : 1,
  upvotes: isMasterOverwrite ? 10 : 1,
  downvotes: 0,
  isApproved: isMasterOverwrite,
  createdAt: nowIso, // ประทับเวลาล่าสุด
};
```
ฟังก์ชัน `getStringReviewStatus()` ใน `stringStatusHelper.ts` จะเปรียบเทียบ:
$$t_{\text{proposal}} > t_{\text{approved}}$$
หากพบว่ามีข้อเสนอใหม่ที่ถูกเสนอเข้ามาทีหลัง ระบบจะแสดงเป็น **🔴 มีคำใหม่ / รอตรวจ** ทันที พร้อมส่งการแจ้งเตือนไปยังหน้าต่างตรวจคำแปลยอดนิยม (Consensus Review Modal 🚨)

---

## 4. ส่วนติดต่อผู้ใช้ (UI Components & Workflows)

### 4.1 แถบเมนูด้านบน (Navbar Actions)
- **`📥 โหลดไฟล์แปล (CSV)`**: ให้ผู้ร่วมแปลทุกคนสามารถกดส่งออกไฟล์ CSV พร้อมหัวคอลัมน์มาตรฐาน `key,source,translation,context` ไปเปิดแปลใน Excel ได้ทันที
- **`📤 อัปโหลดคำแปล`**: เปิดหน้าต่าง Sync Modal ให้ผู้ร่วมแปลนำไฟล์หรือก๊อปปี้ข้อความมาวางผสาน

### 4.2 หน้าต่างวิเคราะห์และผสาน (SyncModal)
1. **การ์ดเวิร์กโฟลว์แปลออฟไลน์**: แนะนำขั้นตอนการดาวน์โหลดไฟล์ไปแปลใน Excel และมีปุ่มดาวน์โหลดด่วน
2. **กล่องสถิติ Diff 4 รูปแบบ**:
   - 🔄 **ประโยคที่แก้ไขใหม่**: แสดงจำนวนบรรทัดที่จะนำเข้าแทนที่
   - ⏸️ **เหมือนเดิม (ไม่ทับ)**: แสดงจำนวนบรรทัดที่ข้ามการทับ เพื่อคงสถานะเดิม 100%
   - ➕ **ข้อความใหม่ในไฟล์**: จำนวนข้อความใหม่ที่เพิ่มเข้ามาต่อท้าย
   - 🛡️ **ระบบจับคู่ความใหม่**: รับรองความปลอดภัยของงานแปลเดิม
3. **Interactive Diff Inspector (กล่องตรวจสอบประโยคที่แก้ไข)**:
   - ผู้ใช้สามารถกดคลี่ดูรายการเปรียบเทียบแบบละเอียด:
     - `คีย์ / ข้อความต้นฉบับ`
     - `เดิม (Old)` ➔ `ใหม่ที่จะนำเข้า (New)`
4. **ตัวเลือกโหมดการผสาน**:
   - ⚡ แทนที่เฉพาะประโยคที่แก้ (Master ทันที - สำหรับแอดมิน)
   - 🔴 ส่งเป็นข้อเสนอใหม่เฉพาะที่แก้ (รอตรวจ - สำหรับผู้ร่วมแปล)

---

## 5. ผลการทดสอบ (Verification & Testing)

ระบบผ่านการทดสอบอัตโนมัติด้วยชุดข้อมูลจำลอง (Mock test):
- **กรณี 1 (ประโยคเดิมเหมือนเดิม)**: ข้ามการประมวลผล ไม่สร้างข้อเสนอซ้ำ คงสถานะ `verified (🟢)` หรือ `ai_translated (👑)` ไว้ 100%
- **กรณี 2 (ประโยคที่มีการแก้ไข)**: ตรวจจับได้แม่นยำ และเมื่อเลือกโหมดส่งเป็นข้อเสนอ ระบบเปลี่ยนสถานะเป็น `pending_review (🔴)` พร้อมแสดงในหน้าต่างตรวจคำแปลทันที
- **การคอมไพล์โปรดักชัน**: ผ่านการทดสอบ `npm run build` (Vite + TypeScript) ปราศจากข้อผิดพลาด 100%
