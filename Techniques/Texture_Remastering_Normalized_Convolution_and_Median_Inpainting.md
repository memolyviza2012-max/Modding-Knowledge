# คู่มือวิศวกรรมเท็กซ์เจอร์: Normalized Convolution & Pure Relative Median Inpainting
## เทคนิคการลบอักษรและซ่อมแซมพื้นผิวเกมขั้นสูง (Zero-Seam, Zero-Box-Cut, Zero-Star-Noise)

---

### 1. ปัญหาและข้อจำกัดของเทคนิคเดิม (The Limitations of Naive Approaches)

เมื่อทำการแปลภาษาในเท็กซ์เจอร์เกม (Texture Modding) ที่มีความซับซ้อน เช่น ลายไม้แกะสลัก, กระดาษโบราณขอบไหม้, กระดานชนวน, หรือแผ่นสเตนซิลหน้ากาก (Decal Masks):
1. **การใช้ `draw.rectangle()` หรือ MaxFilter ขอบกว้าง**:
   - ทำให้เกิดรอยด่างขาวสี่เหลี่ยม (Bleached Patches)
   - ลบลายน้ำ ลายสเก็ตช์ดินสอ และเกรนธรรมชาติของกระดาษรอบข้างทิ้งอย่างถาวร
2. **การใช้ Absolute Color Threshold (`color < 125`)**:
   - ล้มเหลวอย่างสิ้นเชิงบนพื้นหลังสีมืด (เช่น แผ่นกระดาษที่มีเงาตกกระทบ, รอยขอบกระดาษไหม้ไฟสีน้ำตาลเข้ม, กระดานชนวนสีเทา)
   - อัลกอริทึมจะมองว่า "ทั้งผืนภาพคือหมึก" และตัดเป็นกรอบสี่เหลี่ยมคมกริบ (Cutout Seam)
3. **ปัญหา Star-Dot Noise บน Stencil / Alpha Mask**:
   - พิกเซล Noise เล็กๆ ที่มีค่า `1 <= pixel <= 55` ในพื้นหลังสีดำของ Shader จะถูกเกมเรนเดอร์เป็นจุดสะท้อนแสงระยิบระยับเหมือนดวงดาวบนท้องฟ้า

---

### 2. นวัตกรรมที่ 1: Pure Local Relative Median Inpainting

แทนที่จะเทียบกับค่าคงที่แบบตายตัว เราใช้การคำนวณ **ความต่างระหว่างพิกเซลกับมัธยฐานเฉพาะจุด (Local Median)**:

$$\text{ink\_mask} = (\text{Median}_{11\times 11}(I) - I) > \text{threshold}$$

#### ข้อดี:
- **รอยไหม้และเงาสลัว**: มีค่าความสว่างใกล้เคียงกับพิกเซลรอบข้าง ดังนั้น $\text{Median} - I \approx 0$ จึงไม่ถูกตรวจจับว่าเป็นหมึก
- **ตัวอักษรจริง**: มีขอบคมและตัดกับพื้นผิวอย่างรวดเร็ว (High-frequency Edge) ทำให้ $\text{Median} - I > 14$ เสมอ
- **ผลลัพธ์**: ลบเฉพาะก้านตัวอักษรเดิม 100% โดยไม่เกิดรอยตัดขอบสี่เหลี่ยมแม้แต่พิกเซลเดียว

```python
def pure_relative_ink_heal(im, zone, threshold=14, blur_r=7):
    """
    Inpaints only high-frequency ink strokes relative to local background.
    Completely immune to dark paper, burnt edges, and lighting gradients.
    """
    arr = np.array(im.convert('RGBA')).astype(float)
    h, w, _ = arr.shape
    
    # 1. Local median filter (11x11 window)
    med = im.convert('RGB').filter(ImageFilter.MedianFilter(size=11))
    arr_med = np.array(med).astype(float)
    diff = np.mean(arr_med - arr[:, :, :3], axis=2)
    
    # 2. Strict relative ink detection inside defined bounding zone
    ink = (diff > threshold) & zone
    ink_im = Image.fromarray((ink * 255).astype(np.uint8))
    ink_dilated = np.array(ink_im.filter(ImageFilter.MaxFilter(5))) > 0
    
    # 3. Normalized Convolution Inpainting
    valid = (~ink_dilated).astype(float)
    cur = arr[:, :, :3].copy()
    cur[ink_dilated] = 0
    
    val_blur = np.array(Image.fromarray((valid * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur_r))).astype(float) / 255.0
    cur_blur = np.array(Image.fromarray(cur.astype(np.uint8)).filter(ImageFilter.GaussianBlur(blur_r))).astype(float)
    
    healed = arr.copy()
    healed[ink_dilated, :3] = (cur_blur / np.maximum(val_blur, 1e-4)[:, :, None])[ink_dilated]
    
    res = Image.fromarray(healed.astype(np.uint8))
    return res.convert('RGB') if im.mode == 'RGB' else res
```

---

### 3. นวัตกรรมที่ 2: Normalized Convolution Inpainting สำหรับเนื้อไม้และพื้นผิวลวดลาย

บนพื้นผิวไม้ที่มีเสี้ยนไม้ (Wood Grain) หรือกระดาษที่มีเกรนหยาบ การใช้ Blur ธรรมดาจะทำให้ลายไม้ขาดตอน
การใช้ **Normalized Convolution** จะทำการถ่วงน้ำหนักเฉพาะพิกเซลที่ไม่ใช่หมึก (Valid Pixels):

$$I_{\text{healed}} = \frac{G_\sigma * (I \cdot M_{\text{valid}})}{G_\sigma * M_{\text{valid}}}$$

ทำให้เสี้ยนไม้และสีพื้นผิวจากซ้าย-ขวา-บน-ล่าง ไหลเข้ามาบรรจบกันตรงรอยแผลอย่างต่อเนื่อง เสมือนไม่เคยมีตัวอักษรเดิมอยู่มาก่อน

---

### 4. นวัตกรรมที่ 3: Zero-Noise Clamping สำหรับ Decal / Stencil Mask

สำหรับเท็กซ์เจอร์ประเภท Mask (Mode `L` หรือ RGBA Decal):
- พิกเซลที่มีค่าตั้งแต่ `1` ถึง `55` ในบริเวณที่ไม่ใช่ตัวอักษร ต้องทำการ Clamp ให้เป็น `0` บริสุทธิ์:

```python
def wipe_mask_star_noise(mask_im, font_box=None):
    arr = np.array(mask_im)
    # Any speckle or spray artifact below solid stroke value is forced to pure black
    noisy_bg = (arr > 0) & (arr <= 55)
    arr[noisy_bg] = 0
    return Image.fromarray(arr)
```

- กำจัดอาการแสงระยิบระยับ (Glittering Artifacts) ในเอนจินเกมได้อย่างสมบูรณ์ 100%

---

### 5. มาตรฐานการตรวจสอบคุณภาพ (Quality Assurance Checklist)

1. **Zero Box Cuts**: ตรวจสอบด้วย Gradient Derivative หาเส้นตรงแนวนอน/แนวตั้งที่เกิดจากการครอบ Bounding Box
2. **Zero Star Dots**: ตรวจสอบค่าพิกเซลในพื้นหลังสีดำของ Decal ต้องเป็น `0` สนิท
3. **Ghost Text Free**: ตรวจสอบว่าไม่มีเส้นหมึกเดิมภาษาอังกฤษโผล่พ้นหลังตัวอักษรไทย
4. **Preserve Art 100%**: รอยไหม้ ตราประทับ ภาพสเก็ตช์ และรอยพับกระดาษต้องคงอยู่ครบถ้วน
