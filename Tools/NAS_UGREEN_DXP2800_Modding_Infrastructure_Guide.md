# คู่มือการบริหารจัดการ NAS UGREEN DXP2800 สำหรับสตูดิโองานม็อดและ TStudio Web

เอกสารนี้ระบุสถาปัตยกรรมโครงสร้างระบบ เครือข่าย การจัดสรรพื้นที่จัดเก็บข้อมูล (Storage Layout) คอนเทนเนอร์ Docker ความเร็วสูง และระบบสำรองข้อมูลอัตโนมัติ (Automated Backup Engine) สำหรับสตูดิโอ Modder และ TStudio Web

---

## 1. ข้อมูลฮาร์ดแวร์และระบบเครือข่าย (System & Network Profile)

* **รุ่นอุปกรณ์:** UGREEN NASync DXP2800 (Hostname: `HSH-DXP2800`)
* **หน่วยประมวลผล (CPU):** Intel® Processor N100 (4 Cores / 4 Threads, สูงสุด 3.4 GHz, สถาปัตยกรรม x86_64)
* **หน่วยความจำ (RAM):** 8GB DDR5 4800MHz
* **พอร์ตเครือข่าย (LAN):** 2.5GbE High-Speed LAN
* **ระบบปฏิบัติการ:** UGOS Pro (Linux Kernel 6.18.x บนฐาน Debian)
* **IP Address ประจำเครื่อง:** `192.168.1.102`
* **การเชื่อมต่อระยะไกล (Remote Access):**
  * SSH Key Authentication: `ssh -i C:\Users\Danaiwit.WiT\.ssh\id_ed25519 crysers@192.168.1.102`
  * เข้าถึงแบบ Passwordless ไม่ต้องกรอกรหัสผ่านทุกครั้ง
  * บัญชีผู้ใช้หลัก: `crysers` (อยู่ในกลุ่ม `admin`, `users`, `docker`)

---

## 2. การจัดสรรพื้นที่จัดเก็บข้อมูล (Tiered Storage Topology)

ระบบถูกจัดแบ่งแบบ **Tiered Storage Architecture** ตามระดับความเร็วและความเหมาะสมของงาน:

| Volume | ชนิดสื่อบันทึก | ความจุ | เส้นทางบน NAS (Path) | Shared Folders | หน้าที่และการใช้งาน |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Volume 1** | **HDD 8TB** (พร้อม bcache) | **7.3 TB** | `/volume1` | `0_BackUp`<br>`02_Source`<br>`03_Movie` | **Cold & Large Storage:** สำรองข้อมูลโปรเจกต์ม็อดจากเครื่อง PC, เก็บไฟล์ติดตั้งเกมก้อนใหญ่, Raw Game Assets, และมีเดีย |
| **Volume 2** | **NVMe SSD 1TB** | **901 GB** | `/volume2` | `01_Work`<br>`docker` | **Hot Storage (High IOPS):** รัน Live Database, Redis Cache, Docker Containers, และงานอ่านเขียนความเร็วสูงระดับไมโครวินาที |

---

## 3. บริการ Docker Stack บน SSD Volume 2 (`/volume2/docker`)

คอนเทนเนอร์ทั้งหมดถูกรันอยู่บน SSD M.2 NVMe เพื่อให้ได้ค่า Input/Output Operations Per Second (IOPS) สูงสุด และตอบสนองต่อคำขอฐานข้อมูลในระดับ **1–5 มิลลิวินาที**

### รายการ Services ที่ติดตั้ง:

| บริการ (Service) | คอนเทนเนอร์ | พอร์ตภายนอก : ภายใน | โฟลเดอร์เก็บข้อมูล (SSD Data Mount) | คำอธิบาย |
| :--- | :--- | :--- | :--- | :--- |
| **Portainer CE** | `portainer` | `9000:9000` (HTTP)<br>`9444:9443` (HTTPS) | `/volume2/docker/portainer_data` | หน้าเว็บ GUI สำหรับบริหารจัดการ ดูสถานะ ดู Log และควบคุมคอนเทนเนอร์ Docker ทั้งหมด |
| **PostgreSQL 16** | `tstudio-postgres` | `5434:5432` | `/volume2/docker/database/postgres_data` | ฐานข้อมูลเชิงสัมพันธ์ความเร็วสูงสำหรับ TStudio Web (Local Replica & Snapshot) |
| **Redis 7 Stack** | `tstudio-redis` | `6380:6379` | `/volume2/docker/database/redis_data` | ระบบ In-memory Data Cache สำหรับเร่งความเร็วการประมวลผลคำแปลและ Realtime |

> [!NOTE]
> **ทำไมจึงเลือกพอร์ต `5434` และ `6380`?**
> เนื่องจากระบบ UGOS Pro มีบริการภายในของตัวระบบปฏิบัติการดักฟังอยู่ที่ `127.0.0.1:5432` (Internal Postgres) และ `127.0.0.1:6379` (Internal Redis) รวมถึงพอร์ต `9443` สำหรับหน้าจัดการ HTTPS การเลือกพอร์ต `5434`, `6380`, และ `9444` จึงช่วยป้องกันการชนกันของพอร์ต (Port Conflict) ได้อย่างสมบูรณ์แบบ 100%

### การเข้าใช้งาน Web GUI ของ Portainer:
* **URL:** `http://192.168.1.102:9000` หรือ `https://192.168.1.102:9444`
* เปิดครั้งแรก ระบบจะให้ตั้งรหัสผ่าน Admin สำหรับการจัดการผ่านเบราว์เซอร์

---

## 4. ระบบสำรองข้อมูลอัตโนมัติ (Automated Backup Engine)

เครื่องมือสำรองข้อมูลถูกจัดเก็บไว้ที่ `E:\Mod_Workspace\scripts\`:

### 1. `backup_to_nas.ps1` (สำรองไฟล์งานม็อด)
* ใช้คำสั่ง `Robocopy` พร้อมมัลติเธรด 16 ท่อ (`/MT:16`) รองรับแบนด์วิดท์ 2.5GbE
* กรองและตัดโฟลเดอร์ขยะ/แคชที่ไม่จำเป็นออกอัตโนมัติ:
  * โฟลเดอร์: `node_modules`, `.git`, `.venv`, `__pycache__`, `DerivedDataCache`, `TempMessage`, `TempUnpack`, `scratch`, `build`, `dist`
  * ไฟล์: `*.tmp`, `*.log`, `Thumbs.db`, `desktop.ini`
* โหมดทดสอบ: `powershell.exe -File E:\Mod_Workspace\scripts\backup_to_nas.ps1 -DryRun`
* บันทึก Log การสำรองข้อมูลไว้ที่: `E:\Mod_Workspace\scripts\logs\`

### 2. `backup_supabase_to_nas.cjs` (สำรองฐานข้อมูล Cloud สู่ NAS)
* ดึงข้อมูลทั้งหมดจาก Supabase Cloud (`projects`, `strings`, `suggestions`, `glossary_terms`, `comments`, `audit_logs`)
* บันทึกเป็นไฟล์ JSON พร้อม Timestamp ลงใน `\\192.168.1.102\0_BackUp\Database_Backups\`
* อัปเดตไฟล์ `tstudio_backup_latest.json` อัตโนมัติทุกครั้งที่รัน

---

## 5. การตั้งเวลาทำงานอัตโนมัติ (Windows Task Scheduler)

สามารถตั้งให้ Windows รันสำรองข้อมูลอัตโนมัติทุกวันเวลา 02:00 น. ด้วยคำสั่ง PowerShell:

```powershell
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File E:\Mod_Workspace\scripts\backup_to_nas.ps1"
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM
Register-ScheduledTask -TaskName "TStudio_ModWorkspace_NAS_Backup" -Action $action -Trigger $trigger -Description "สำรองข้อมูลงานม็อดและฐานข้อมูล TStudio สู่ NAS UGREEN DXP2800"
```