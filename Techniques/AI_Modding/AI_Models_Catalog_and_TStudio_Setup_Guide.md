# คู่มือแคตตาล็อกโมเดล AI ล่าสุด & การตั้งค่าใน TStudio และ TRun (AI Models Catalog & Setup Guide)

## 1. บทนำ (Introduction)
เอกสารนี้รวบรวมรายชื่อโมเดล AI ยุคล่าสุด (Frontier, Reasoning, Open-Weights, และ OpenRouter) พร้อมแนวทางการตั้งค่าใช้งานร่วมกับเครื่องมือแปลเกมภาษาไทย **TStudio**, **TRun**, และ **TSub** ในระบบ THub

---

## 2. หมวดหมู่โมเดลและการเลือกใช้งานสำหรับงานแปลเกม (Model Selection by Use Case)

### 🥇 สายคุ้มค่า ประหยัดงบ และแปลมหาศาล (High-Volume Bulk Translation)
* **โมเดลแนะนำ**: `deepseek-chat` (DeepSeek-V3)
* **ข้อดี**: ราคาต่อโทเค็นถูกที่สุดในกลุ่มโมเดลระดับท็อป (ล้านละไม่กี่สตางค์) ความเร็วสูง สำนวนภาษาไทยเป็นธรรมชาติ
* **ข้อควรระวัง**: โมเดล DeepSeek อาจมีคอมเมนต์ภาษาจีนหลุดมาบางครั้ง (ระบบ TStudio และ TRun มีฟิลเตอร์ CJK Leak ช่วยตัดให้อัตโนมัติแล้ว)

### 🥇 สายสำนวนวรรณศิลป์ & ซับซ้อนสูง (Narrative & Literary Translation)
* **โมเดลแนะนำ**: `claude-3-7-sonnet-20250219` (Claude 3.7 Sonnet) หรือ `claude-3-5-sonnet-20241022`
* **ข้อดี**: เข้าใจบริบท มุกตลก คำสแลง และอารมณ์ตัวละครได้ดีที่สุดในตลาด ไม่แปลแบบทื่อๆ
* **การตั้งค่า**: รองรับทั้ง Direct API จาก Anthropic หรือเรียกผ่าน OpenRouter (`anthropic/claude-3.7-sonnet`)

### 🥇 สาย Context ขนาดยักษ์ & โหลดคลังศัพท์ทั้งเกม (Massive Lore & Glossary Consistency)
* **โมเดลแนะนำ**: `gemini-2.0-flash` หรือ `gemini-1.5-pro`
* **ข้อดี**: รองรับ Context Window ระดับ 1M ถึง 2M Tokens สามารถยัดคลังคำศัพท์ (Glossary) หลายพันคำพร้อมประวัติศาสตร์เกมลงไปในพรอมต์ได้ทั้งหมดโดยที่โมเดลไม่หลงลืม

### 🥇 สายคิดวิเคราะห์ & ตรรกะแม่นยำ (CoT / Reasoning)
* **โมเดลแนะนำ**: `o3-mini` (OpenAI), `deepseek-reasoner` (DeepSeek-R1), `gemini-2.0-flash-thinking-exp-01-21`
* **ข้อดี**: มีกระบวนการคิดในหัวก่อนตอบ เหมาะมากกับการถอดรหัสโค้ด, ตรวจสอบความถูกต้องของสคริปต์, หรือแปลประโยคที่มีตัวแปรแทรกซับซ้อน

### 🥇 สายออฟไลน์ / ปลอดภัยในเครื่อง (Local / Offline Translation)
* **โมเดลแนะนำ**: `qwen2.5:14b`, `qwen2.5:32b`, `qwq:32b`, `llama3.3:70b`
* **ข้อดี**: ใช้งานฟรี รันผ่าน Ollama หรือ LM Studio ในเครื่อง ไม่ต้องต่ออินเทอร์เน็ต

---

## 3. ตารางโมเดลที่มีใน TStudio Settings

| AI Provider | Model Name (Identifier) | หมายเหตุ / จุดเด่น |
|---|---|---|
| **DeepSeek** | `deepseek-chat` | DeepSeek-V3 โมเดลหลัก แนะนำสำหรับงานแปลทั่วไป |
| | `deepseek-reasoner` | DeepSeek-R1 โมเดลคิดวิเคราะห์ (CoT) |
| **Anthropic Claude** | `claude-3-7-sonnet-20250219` | Claude 3.7 Sonnet ตัวท็อปล่าสุด สำนวนยอดเยี่ยม |
| | `claude-3-5-sonnet-20241022` | Claude 3.5 Sonnet v2 |
| | `claude-3-5-haiku-20241022` | Claude 3.5 Haiku เร็วและประหยัด |
| | `claude-3-opus-20240229` | Claude 3 Opus |
| **Google Gemini** | `gemini-2.0-flash` | Gemini 2.0 เร็วสุดขีด 1M Context |
| | `gemini-2.0-flash-thinking-exp-01-21` | Gemini 2.0 โหมดคิดก่อนตอบ |
| | `gemini-2.0-pro-exp-02-05` | Gemini 2.0 Pro Experimental |
| | `gemini-1.5-pro` | Gemini 1.5 Pro รองรับ 2M Tokens |
| | `gemini-1.5-flash` | Gemini 1.5 Flash |
| **OpenAI** | `gpt-4o` | GPT-4o Flagship |
| | `gpt-4o-mini` | GPT-4o mini เร็วและประหยัด |
| | `o3-mini` | o3-mini โมเดลใช้เหตุผลความเร็วสูง |
| | `o1` | o1 โมเดลใช้เหตุผลเต็มรูปแบบ |
| **OpenRouter** | `anthropic/claude-3.7-sonnet` | รวมทุกค่ายใน API Key เดียว (sk-or-...) |
| | `deepseek/deepseek-chat` | OpenRouter DeepSeek V3 |
| | `deepseek/deepseek-r1` | OpenRouter DeepSeek R1 |
| | `google/gemini-2.0-flash-001` | OpenRouter Gemini 2.0 Flash |
| | `qwen/qwen-2.5-72b-instruct` | OpenRouter Qwen 2.5 72B |
| | `meta-llama/llama-3.3-70b-instruct` | OpenRouter Llama 3.3 70B |
| **Local LLM** | `qwen2.5:14b` / `qwen2.5:32b` | Ollama Local LLM (พอร์ต 11434) |
| | `llama3.3:70b` | Ollama Llama 3.3 |
| | `custom-local-llm` | LM Studio (พอร์ต 1234) |

---

## 4. วิธีการตั้งค่าในโปรแกรม (How to Configure)

1. เปิด **TStudio Desktop** หรือ **TRun**
2. ไปที่เมนู **Settings -> Global Settings (⚙️)**
3. เลือก **1. AI Provider**:
   - หากมีคีย์ DeepSeek: เลือก `DeepSeek`
   - หากใช้คีย์รวมของ OpenRouter: เลือก `OpenRouter`
   - หากใช้ Claude: เลือก `Anthropic Claude`
   - หากใช้ Gemini: เลือก `Google Gemini`
   - หากรันในเครื่อง: เลือก `Local LLM`
4. กรอก **2. API Key** ของผู้ให้บริการนั้นๆ
5. เลือกหรือพิมพ์ **3. Model Name** จากรายการ
6. กด **Save Settings** ระบบจะจดจำคีย์แยกค่ายไว้อย่างอิสระ สามารถสลับไปมาได้ตลอดเวลา
