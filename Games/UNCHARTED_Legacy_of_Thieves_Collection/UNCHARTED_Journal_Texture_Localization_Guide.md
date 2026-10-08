# คู่มือกระบวนการแปลภาพสมุดบันทึก UNCHARTED 4 (Journal Texture Localization Guide)

## 1. บทนำและโครงสร้างเท็กซ์เจอร์สมุดบันทึก (Drake's Journal)
ในเกม *UNCHARTED 4: A Thief's End* (UNCHARTED: Legacy of Thieves Collection) สมุดบันทึกของ Nathan Drake ไม่ได้แสดงผลด้วยภาพหน้าสมุดธรรมดา แต่ประกอบขึ้นด้วยระบบ Shader แบบหลายเลเยอร์:
1. **Background Shader / Paper Base**: พื้นผิวสมุดและสีกระดาษ
2. **Blend Texture (RGBA)**: เลเยอร์หมึก ภาพสเก็ตช์ และบันทึกข้อความ ซึ่งเก็บในรูปของ Mask แยกช่องสี
3. **Color Props**: ภาพถ่าย ตราสัญลักษณ์ หรือแผ่นแผนที่ที่แปะลงบนหน้าสมุด

---

## 2. โครงสร้างช่องสี (Channel Masks) และข้อควรระวังสำคัญ
แต่ละช่องของ Blend Texture มีหน้าที่เฉพาะตัว:
- **R Channel (Red)**: หมึกดำหลัก (ลายมือจดบันทึกของ Drake, ภาพสเก็ตช์หลัก เช่น หัวกะโหลก ดาบไขว้ ไม้กางเขน)
- **G Channel (Green)**: หมึกเสริม ลำดับขั้นตอน หรือสเก็ตช์ปริศนาเพิ่มเติม (เช่น แผนปฏิบัติการสีน้ำเงิน, ปริศนาก้อนหินถังน้ำ)
- **B Channel (Blue)**: ขอบหน้ากากแผนที่ หรือเงาขอบกระดาษ
- **A Channel (Alpha)**: เงาและรอยนิ้วมือขอบสมุด

### กฎเหล็กด้านเทคนิค
1. **ขนาดพิกเซลต้องเท่าเดิม 100% (Strict Resolution Preservation)**:
   - ห้ามขยายหรือลดขนาดพิกเซลของภาพโดยเด็ดขาด (เช่น 1024x1024 ต้องเป็น 1024x1024 เท่านั้น)
   - หากความละเอียดเปลี่ยน จะทำให้ไม่สามารถแพ็คกลับเข้าสู่ PSARC/PAK ได้เนื่องจาก descriptor offset, mipmap level, และ block size จะไม่ตรงกัน
2. **การกลับแนวแกนตั้ง (Vertical Flip)**:
   - Native Texture ภายในไฟล์เกมถูกจัดเก็บแบบกลับหัว (Upside Down) ตามแนวแกน V ของ UV
   - เวลาแก้ไขหรือสร้างภาพด้วย AI/โปรแกรมวาดภาพ ต้องทำงานในแนวตั้งตรง (Upright)
   - เมื่อประกอบกลับเข้าเป็นไฟล์ Blend Texture เพื่อใช้งานในเกม **ต้องทำการกลับหัว (Vertical Flip)** ด้วย `np.flipud()` ก่อนใส่ลงใน R/G channel
3. **ความบริสุทธิ์ของพื้นหลัง (White Background Purity)**:
   - ในระบบ Mask ค่าพิกเซล 255 คือพื้นหลังสีขาว (ไม่มีหมึก)
   - หากพื้นหลังมีสีเทาหรือรอยเปื้อน (เช่น 200–230) เกมจะเรนเดอร์เป็นคราบหมึกดำเปรอะเปื้อน จึงต้อง Normalize ให้พื้นหลังเป็นสีขาวล้วน 255 (Pure White) เสมอ

---

## 3. สรุปผลงานแปลชุด Priority_Three_Screens

### ชุดที่ 1: `01_Henrys_Gravery`
- **หน้าซ้าย (`sco-avery-grave-1-blend`)**:
  - `HENRY'S GRAVERY` ➔ **สุสานของเฮนรี่**
  - `NEEDS TO HAVE:` ➔ **ต้องมี:**
  - `<- Skull and crossbones` ➔ **<- หัวกะโหลกไขว้**
  - `<- Crossed Swords (pointed down)` ➔ **ดาบไขว้ (ชี้ลง)**
  - `1659 . 1699 <- dates.` ➔ **1659 . 1699 <- ปี ค.ศ.**
  - สเก็ตช์หีบสมบัติ กะโหลกไขว้ และดาบไขว้คงความสมบูรณ์ 100%
- **หน้าขวา (`sco-avery-grave-right-blend`)**:
  - `CELTIC KNOTS` ➔ **ปมเคลติก**
  - `really?` ➔ **จริงดิ?**
  - `Scottish Gravestone` ➔ **ป้ายหลุมศพสก็อต**
  - `I'M Knot Patient enough for this.` ➔ **ฉันทนกับปมพวกนี้ไม่ไหวแล้ว**
  - `<- or` ➔ **<- หรือ**
  - `Still nope.` ➔ **ยังไม่ใช่อยู่ดี**

### ชุดที่ 2: `02_Auction_Plan`
- **หน้าซ้าย (`start-auction-info-left-blend`)**:
  - `"A crow will not pluck out the eye of another crow" -> Honor Among Thieves.`
  - แปลเป็น: **"อีกาจะไม่จิกตาของอีกาด้วยกัน" ➔ เกียรติในหมู่โจร**
- **หน้าขวา (`start-auction-info-right-blend`)**:
  - **R Channel (หมึกดำ/ขีดฆ่า)**:
    - `Sullivan Contact - Hotel de Fiorentino` ➔ **คนติดต่อของซัลลิแวน - โรงแรม เดอ ฟิโอเรนติโน**
    - `power` (ขีดฆ่า) ➔ **ตัดไฟ** (ขีดฆ่า) ➔ `4. Get chucked out a window...` ➔ **4. โดน เนดีน รอสส์ โยนออกนอกหน้าต่าง ยิงกันในห้องบอลรูม**
    - `very very fast` ➔ **เร็วมากๆ** (ขีดเส้นใต้คู่)
    - `IBUPROFEN` (ขีดฆ่า) ➔ **ไอบูโพรเฟน** (ขีดฆ่า)
    - `7. I think I'm also getting too old for this, kid.` ➔ **7. ฉันคิดว่าฉันเริ่มแก่เกินไปสำหรับเรื่องนี้แล้วเหมือนกัน เจ้าหนู**
  - **G Channel (รายการแผนปฏิบัติการสีน้ำเงิน)**:
    - 1. ไปยังจุดสังเกตการณ์
    - 2. รวมพลกับซัลลี่
    - 3. มุ่งหน้าไปห้องเก็บของ
    - 4. เจอซัลลี่ที่รถ
    - 5. ขับรถหนีพร้อมไม้กางเขน
    - 6. ราวิโอลีสอดไส้ล็อบสเตอร์เป็นมื้อค่ำ

### ชุดที่ 3: `03_Three_Crosses`
- **หน้าซ้าย (`sco-3-crosses-stage-2-left-blend`)**:
  - Dismas Speech: `We recieve the due reward of our deeds` ➔ **เราได้รับผลกรรมอันสมควรแก่การกระทำของเรา**
  - Dismas Label: `DISMAS (GOOD THIEF)` ➔ **ดิสมาส (โจรผู้กลับใจ)**
  - Jesus Speech: `TODAY YOU WILL JOIN ME IN PARADISE` ➔ **วันนี้เจ้าจะได้อยู่กับเราในสรวงสวรรค์**
  - Jesus Label: `JESUS (JESUS)` ➔ **เยซู (พระเยซู)**
- **หน้าขวา (`sco-3-crosses-center-blend`)**:
  - Gestas Speech: `COOL. I'll JUST hang here. You guys have fun...` ➔ **เจ๋งเลย งั้นฉันห้อยอยู่ตรงนี้ละกัน พวกนายสนุกกันไปนะ...**
  - Gestas Label: `GESTAS (JERK THIEF)` ➔ **เกสตัส (โจรชั่ว)**

---

## 4. โครงสร้างโฟลเดอร์ไฟล์งานที่พร้อมใช้งาน
ในแต่ละโฟลเดอร์ของ `Priority_Three_Screens/`:
- `Localized_Thai/`: รวบรวมไฟล์ Mask และ Texture แปลไทยที่พร้อมสำหรับทดสอบและแพ็คเข้าเกม
- `Channel_Masks/`: บรรจุ Mask ภาษาไทยต่อท้ายชื่อด้วย `_TH.png`
- `Ink_Preview_TH.png`: ภาพพรีวิวสมุดบันทึกภาษาไทย (ขนาด 1000x750 เท่าต้นฉบับ)
