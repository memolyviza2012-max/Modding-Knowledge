# TStudio Web: Canvas Table Inline Translation & Continuous Enter Auto-Advance Architecture

> **เอกสารคู่มือสถาปัตยกรรม & เทคนิคระบบแปลสดในตาราง (Inline Cell Translation) พร้อมการกด Enter ข้ามบรรทัดอัตโนมัติ**  
> *วันที่อัปเดต: 29 กันยายน 2026*  
> *ตำแหน่งจัดเก็บ: `Modding-Knowledge/Techniques/TStudio_Web_Table_Inline_Translate_and_Continuous_Enter_Navigation_Guide.md`*

---

## 1. ที่มาและความต้องการ (Background & Problem Statement)

ในระบบแปลเกมที่มีปริมาณข้อความเป็นหมื่นแถว รูปแบบการแปลที่รวดเร็วและคล่องตัวที่สุดคือ **การแปลบนตาราง (Spreadsheet/Table-driven localization)** ซึ่งคล้ายกับการกรอกข้อมูลใน Excel / Google Sheets:
- **ปัญหาเดิม**:
  1. การแก้ไขข้อความในตาราง Canvas (`@glideapps/glide-data-grid`) ต้องใช้การ **Double-click** ทำให้เสียจังหวะในการเลื่อนแปลอย่างต่อเนื่อง
  2. เมื่อผู้ใช้พิมพ์คำแปลเสร็จแล้วกด **Enter** ตัว Editor กลับปิดตัวลงและค้างอยู่ที่เดิม ไม่ข้ามไปเปิดแถวถัดไปให้อัตโนมัติ ทำให้ผู้ใช้ต้องเอื้อมเมาส์ไปดับเบิ้ลคลิกแถวใหม่อีกครั้งทุกๆ แถว
  3. `<div id="portal" />` ใน `index.html` ไม่ได้ถูกประกาศไว้ ส่งผลให้ Floating Overlay Editor ของ Glide Data Grid ไม่สามารถ Mount เข้า DOM ได้อย่างสมบูรณ์

---

## 2. สถาปัตยกรรมและโซลูชันทางเทคนิค (Architectural Solution)

เพื่อให้ผู้แปลสามารถ **"คลิกตารางแล้วแปลได้ทันที และกด Enter เพื่อบันทึกพร้อมเปิดแถวถัดไปแบบอัตโนมัติ 100%"** ระบบได้รับการออกแบบกลไกทำงานดังนี้:

```
┌────────────────────────────────────────────────────────┐
│  ผู้ใช้คลิกที่ตาราง (Click on Row / Translation Cell)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (0ms Single-Click Activation)
┌────────────────────────────────────────────────────────┐
│  Glide Data Grid Inline Editor (#portal Floating Input)│
│  - Textarea ขยายตามขนาดข้อความอัตโนมัติ                    │
│  - ดึงคำแปลเดิมหรือคลังศัพท์มาพร้อมแก้ไข                     │
└──────────────────────────┬─────────────────────────────┘
                           │
                           │  พิมพ์คำแปล + กด Enter ↵
                           ▼
┌────────────────────────────────────────────────────────┐
│  1. บันทึกคำแปล (Direct Save / Auto-Approve / Propose)   │
│  2. เลื่อนเคอร์เซอร์ไปแถวถัดไป (Row + 1)                   │
│  3. triggerCellEdit(4, nextRow)                        │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ (Auto-Open Overlay Editor)
┌────────────────────────────────────────────────────────┐
│  เปิดช่องพิมพ์แปลของแถวถัดไปทันที (พร้อมพิมพ์ต่อได้เลย!)     │
│  [Type Thai] ➔ [Enter] ➔ [Type Thai] ➔ [Enter] ...     │
└────────────────────────────────────────────────────────┘
```

---

## 3. รายละเอียดการตั้งค่าและโค้ดหัวใจสำคัญ (Implementation Details)

### 3.1 การประกาศ `#portal` Container ใน `index.html`
Glide Data Grid ใช้ React Portal ในการ Render ตัว Input ลอยเหนือ Canvas Grid:
```html
<body class="bg-[#0f111a] text-[#cdd6f4] antialiased overflow-hidden select-none">
  <div id="root"></div>
  <div id="portal"></div> <!-- สำคัญอย่างยิ่งสำหรับ DataGridOverlayEditor -->
  <script type="module" src="/src/main.tsx"></script>
</body>
```

### 3.2 การเปิดโหมด Single-Click บน DataEditor
ตั้งค่า `cellActivationBehavior="single-click"` บนคอมโพเนนต์ `<DataEditor>` และระบุ `activationBehaviorOverride: 'single-click'` บนคอลัมน์คำแปลภาษาไทย (Col 4):
```tsx
<DataEditor
  ref={gridRef}
  rows={filteredStrings.length}
  columns={columns}
  getCellContent={getCellContent}
  onCellClicked={handleCellClicked}
  onCellActivated={handleCellActivated}
  onCellEdited={handleCellEdited}
  onFinishedEditing={handleFinishedEditing}
  cellActivationBehavior="single-click"
  ...
/>
```

### 3.3 ฟังก์ชัน Programmatic Cell Trigger (`triggerCellEdit`)
สั่งเปิดโหมดแก้ไขเซลล์ผ่านการ Dispatch คีย์อีเวนต์ `Enter` ส่งตรงไปยัง Canvas Element:
```tsx
const triggerCellEdit = useCallback((col: number, row: number) => {
  if (!gridContainerRef.current) return;

  gridRef.current?.scrollTo(col, row, 'vertical', 0, 0, { vAlign: 'center' });
  gridRef.current?.focus();

  const canvas =
    (gridContainerRef.current.querySelector('canvas[data-testid="data-grid-canvas"]') as HTMLCanvasElement) ||
    (gridContainerRef.current.querySelector('canvas') as HTMLCanvasElement);

  if (canvas) {
    canvas.focus();
    const enterEvent = new KeyboardEvent('keydown', {
      key: 'Enter',
      code: 'Enter',
      keyCode: 13,
      which: 13,
      bubbles: true,
      cancelable: true,
    });
    canvas.dispatchEvent(enterEvent);
  }
}, []);
```

### 3.4 การสลับแถวอัตโนมัติเมื่อกด Enter (`handleFinishedEditing`)
เมื่อผู้ใช้กด `Enter` ในช่องพิมพ์ของตาราง Glide Data Grid จะส่ง `movement: [0, 1]` มายัง `onFinishedEditing`:
```tsx
const handleFinishedEditing = useCallback(
  (_newValue: GridCell | undefined, movement: Item) => {
    const activeCell = activeEditingCellRef.current;
    const editedRow = activeCell ? activeCell[1] : (gridSelection?.current?.cell[1] ?? -1);
    activeEditingCellRef.current = null;

    // movement[1] === 1 คือการกด Enter เพื่อเลื่อนลงแถวถัดไป
    if (movement && movement[1] === 1) {
      const nextRow = editedRow + 1;
      if (nextRow >= 0 && nextRow < filteredStrings.length) {
        const nextStr = filteredStrings[nextRow];
        if (nextStr) {
          onSelectString(nextStr.id);
        }
        setGridSelection({
          current: {
            cell: [4, nextRow],
            range: { x: 0, y: nextRow, width: 6, height: 1 },
            rangeStack: [],
          },
          rows: CompactSelection.fromSingleSelection(nextRow),
          columns: CompactSelection.empty(),
        });
        setTimeout(() => {
          triggerCellEdit(4, nextRow);
        }, 45);
      }
    }
  },
  [gridSelection, filteredStrings, onSelectString, triggerCellEdit]
);
```

### 3.5 คีย์ลัดสากล (Universal Navigation Rules)
- **Enter**: บันทึกคำแปลแถวปัจจุบัน และเลื่อนไปเปิดช่องพิมพ์แถวถัดไปทันที
- **Shift + Enter**: ขึ้นบรรทัดใหม่ (`\n`) ในกรณีที่ประโยคเกมต้องการตัดขึ้นบรรทัดใหม่
- **Escape**: ยกเลิกการแก้ไขและปิด Overlay
- **คลิกแถวใดๆ**: สลับโฟกัสไปยังคอลัมน์คำแปลและเปิดช่องพิมพ์ให้พร้อมกรอกทันที

---

## 4. ผลลัพธ์ในระบบจริง (Production Release)
- **Repo Commit**: `47f762c`
- **Deploy Target**: UGREEN NAS Docker (`192.168.1.102:3001`), โฟลเดอร์ `/volume2/docker/tstudio-web/dist/`
- **User Experience**: แปลต่อเนื่องแบบ Rapid-Fire ไหลลื่นระดับ 60 FPS ปราศจากการสะดุด
