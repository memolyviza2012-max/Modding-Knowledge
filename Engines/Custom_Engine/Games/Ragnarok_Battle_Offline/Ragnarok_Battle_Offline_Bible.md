# Ragnarok Battle Offline (RBO EX 1-3) — Thai Localization Modding Bible

> **Game:** Ragnarok Battle Offline (Base + Extra Scenario Vol. 1, 2, 3)  
> **Developer:** French-Bread / Shunpu-tei  
> **Original Language:** Japanese  
> **Target Language:** Thai  
> **Engine:** French-Bread Custom 2D Engine (DirectX 8/9)  
> **Author:** Antigravity & THub Modding Team  

---

## 1. Engine & Archive Architecture (.PAC)

### 1.1 Archive Format
The game packages assets inside French-Bread `.PAC` container archives:
- `CG.PAC` (Base game graphics)
- `Ex1Disc.PAC` (Expansion 1 assets)
- `Ex2Disc.PAC` (Expansion 2 assets & Master Title Sheet)
- `Ex3Disc.pac` (Expansion 3 assets)
- `DATA01.PAC`, `DATA02.PAC`, `SE.PAC`, `BGM.PAC`

### 1.2 Cryptography & Structures
- **Header:** 8 bytes
  - `uint32 dummy`
  - `uint32 file_count_enc ^ 0xE3DF59AC`
- **File Record:** 68 bytes per entry
  - `byte[60] filename_enc`: Decrypted using formula:  
    `name[j] ^= (file_index * j * 3 + 61) & 0xFF` (for `j in range(59)`)  
    Encoded as `Shift-JIS`.
  - `uint32 offset`: Absolute byte offset in the archive.
  - `uint32 size_enc`: Decrypted via `size = size_enc ^ 0xE3DF59AC`.
- **Payload:** Raw uncompressed bytes.

### 1.3 Engine File Priority (Loose File Override)
The engine checks the physical filesystem path `DATA/...` before reading from `.PAC` files. Any loose file placed in `F:\Games\RBO EX 1-3\DATA\...` takes 100% precedence, completely eliminating the need to repack giant `.PAC` archives during development.

---

## 2. Graphic Texture Format (.IMG)

### 2.1 File Specification
All textures in `DATA/CG/` use French-Bread's `.IMG` container:
- **Header:** 20 bytes (Little-Endian)
  - `0x00..0x03`: `uint32 magic1 = 0`
  - `0x04..0x07`: `uint32 magic2 = 7`
  - `0x08..0x0B`: `uint32 magic3 = 2`
  - `0x0C..0x0F`: `uint32 width` (e.g. 1024)
  - `0x10..0x13`: `uint32 height` (e.g. 1024)
- **Pixel Data:** `width * height * 4` bytes
  - Uncompressed 32-bit BGRA (Blue, Green, Red, Alpha).
  - Total file size = `20 + (width * height * 4)`.

---

## 3. Title Screen Architecture (TITLE.IMG)

### 3.1 Multi-Executable Discrepancy & Resolution
| Executable | Version | Menu Items on Fresh Game | Button 0 UV Coordinate | Button 0 Source Text |
| :--- | :--- | :--- | :--- | :--- |
| `rbo.exe` | v1.100 | 3 items: `[Start, Ranking, Exit]` | `(0, 176, 208, 32)` | `スタート Start Game` |
| `rbo_ex1.exe` | v2.000 | 3 items: `[Normal, Ranking, Exit]` | `(208, 448, 208, 32)` | `ノーマルモード Normal Mode` |
| `rbo_ex2.exe` | v3.000 | 3 items: `[Normal, Ranking, Exit]` | `(208, 448, 208, 32)` | `ノーマルモード Normal Mode` |
| `rbo_ex3.exe` | v4.000 | 3 items: `[Normal, Ranking, Exit]` | `(208, 448, 208, 32)` | `ノーマルモード Normal Mode` |

> [!IMPORTANT]
> **Master Texture Requirement:**  
> The original `CG.PAC` only contains base game graphics, leaving `(208, 448)` transparent. To support EX1, EX2, and EX3, `TITLE.IMG` MUST be extracted from `Ex2Disc.PAC`.  
> Both `(0, 176)` and `(208, 448)` must be rendered with "เริ่มเกม" to support all 4 executables simultaneously.

### 3.2 Full Button UV Table (Table 5 in Executable)
All buttons have standard dimensions `width = 208`, `height = 32`:
- `TITLE_MAIN_001`: `(0, 176, 208, 32)` — เริ่มเกม (Base Game)
- `TITLE_MAIN_001_EX`: `(208, 448, 208, 32)` — เริ่มเกม (Normal Mode EX1-3)
- `TITLE_MAIN_002`: `(0, 208, 208, 32)` — ตั้งค่า Option
- `TITLE_MAIN_003`: `(0, 240, 208, 32)` — ออกจากเกม
- `TITLE_MAIN_004`: `(0, 272, 208, 32)` — ต้องการออกจากเกมหรือไม่?
- `TITLE_MAIN_005`: `(0, 304, 112, 32)` — ออก
- `TITLE_MAIN_006`: `(112, 304, 96, 32)` — ยกเลิก
- `TITLE_MAIN_007`: `(0, 336, 208, 32)` — โหมดประลอง PVP
- `TITLE_MAIN_008`: `(0, 368, 208, 32)` — ดูอันดับ Ranking
- `TITLE_MAIN_009`: `(0, 448, 208, 32)` — โหมดประลอง Arena
- `TITLE_MAIN_010`: `(0, 480, 208, 32)` — ยูทิลิตี้ Utility
- `TITLE_MAIN_011`: `(0, 512, 208, 32)` — อ่านจดหมาย Vol.1
- `TITLE_MAIN_012`: `(0, 544, 208, 32)` — อ่านจดหมาย Vol.2
- `TITLE_MAIN_013`: `(0, 576, 208, 32)` — อ่านจดหมาย Vol.3
- `TITLE_MAIN_014`: `(0, 608, 208, 32)` — ตอบคำถาม RBO Quiz
- `TITLE_MAIN_015`: `(0, 640, 208, 32)` — มินิเกม MiniRBO
- `TITLE_MAIN_016`: `(0, 672, 208, 32)` — ร้านไอเทมเวทมนตร์ Wiz

---

## 4. Typography & Thai Rendering Pipeline

- **Font Family:** `Prompt-Bold` with Custom PUA Remapping (`Prompt-Bold_PUA.ttf`).
- **Color Palette:**
  - Fill: Crisp White `(255, 255, 255, 255)`
  - Stroke: Deep Crimson Brown `(88, 11, 0, 255)`, width = 2px
- **Dynamic Centering Algorithm:**
  ```python
  bbox = font.getbbox(render_text)
  tw = bbox[2] - bbox[0]
  th = bbox[3] - bbox[1]
  dx = bx + (bw - tw) // 2 - bbox[0]
  dy = by + (bh - th) // 2 - bbox[1]
  ```

---

## 5. System Configuration Tweaks

Files located in `DATA/SaveData/SystemConfig.*` (`.cnf`, `.v2`, `.v3`, `.v4`):
- **Fullscreen / Windowed Toggle:** Byte offset `0x04`
  - `0x01`: Fullscreen (Forces display mode change)
  - `0x00`: Windowed Mode (Standard desktop window)

---

## 6. Executable Binary Patching (Window Title & Launchers)

### 6.1 Root Cause of Mojibake (ภาษาต่างดาว)
The game and launcher executables invoke `CreateWindowExA` and `RegisterClassA` with hardcoded Shift-JIS strings (`ラグナロクバトルオフライン...`). On non-Japanese Windows operating systems (English, Thai), Windows decodes ANSI strings using the local system code page (CP1252, CP874), causing the title bar to display mojibake characters like `f%ofOfiffNfofgf<flftf%ofCf"`.

### 6.2 Binary Patch Offsets
In-place string replacements with null-padding:

| Executable | Offset | Max Cap | Original String (Shift-JIS) | Clean Replacement (ASCII) |
| :--- | :--- | :--- | :--- | :--- |
| `rbo.exe` | `0x893E8` | 27 | `ラグナロクバトルオフライン` (Class) | `Ragnarok Battle Offline` |
| `rbo.exe` | `0x89404` | 27 | `ラグナロクバトルオフライン` (Title) | `Ragnarok Battle Offline` |
| `rbo_ex1.exe` | `0x93CA8` | 40 | `ラグナロクバトルオフライン追加シナリオ1` (Class) | `Ragnarok Battle Offline - Extra 1` |
| `rbo_ex1.exe` | `0x93CD0` | 40 | `ラグナロクバトルオフライン追加シナリオ1` (Title) | `Ragnarok Battle Offline - Extra 1` |
| `rbo_ex2.exe` | `0x970F0` | 40 | `ラグナロクバトルオフライン追加シナリオ2` (Class) | `Ragnarok Battle Offline - Extra 2` |
| `rbo_ex2.exe` | `0x97118` | 40 | `ラグナロクバトルオフライン追加シナリオ2` (Title) | `Ragnarok Battle Offline - Extra 2` |
| `RBO_Ex3.exe` | `0x97518` | 40 | `ラグナロクバトルオフライン追加シナリオ3` (Class) | `Ragnarok Battle Offline - Extra 3` |
| `RBO_Ex3.exe` | `0x97540` | 40 | `ラグナロクバトルオフライン追加シナリオ3` (Title) | `Ragnarok Battle Offline - Extra 3` |
| `RBOConfig.exe` | `0xC4B4` | 35 | `RAGNAROK BATTLE OFFLINE コンフィグ1` | `RBO Configuration Utility 1` |
| `RBOEx2Config.exe` | `0xC4B4` | 35 | `RAGNAROK BATTLE OFFLINE コンフィグ2` | `RBO Configuration Utility 2` |
| `RBOEx3Config.exe` | `0xC4B4` | 35 | `RAGNAROK BATTLE OFFLINE コンフィグ3` | `RBO Configuration Utility 3` |

---

## 7. Launcher & Parody Patch Client Architecture

### 7.1 Overview
Upon executing any of the game executables (`rbo.exe`, `rbo_ex1.exe`, `rbo_ex2.exe`, `RBO_Ex3.exe`), the engine immediately invokes `DialogBoxParamA` using **Resource ID 109 (`0x6D`)** before initializing DirectX. This dialog simulates the official Ragnarok Online patch updater client as an in-game parody.

### 7.2 Root Cause of Launcher Mojibake
1. **Dialog Template Encoding Mismatch:** The dialog resources in `.rsrc` contain Japanese Shift-JIS/Unicode strings (`†Patch★Client†`, `ラグナロクバトルオフライン公知事項`, `パッチ作業はしておりません。`). Because the engine calls ANSI `DialogBoxParamA`, Windows uses `WideCharToMultiByte(CP_ACP, ...)` to convert the template text. Under non-Japanese Windows (where ACP is 1252 or 874), unconvertible characters are replaced with question marks (`?????????????????`).
2. **Dynamic Button Text (`ゲーム開始`):** When the progress timer finishes, the code invokes `SetDlgItemTextA(hDlg, 1, "\x83Q\x81[\x83\x80\x8aJ\x8en")`. Interpreted as CP1252, this produces the garbled string `ƒQ[ƒ€ŠJŽn`.
3. **Announcement Notice (`_notice.txt`):** Loaded via the engine's internal file loader from `.\Data\_notice.txt` (or extracted from `.PAC` archives) and fed into the multiline EDIT control (ID 1002) as Shift-JIS bytes, resulting in full-text mojibake.

### 7.3 Binary Patch Offsets & Fixes

#### A. Win32 Dialog Resource ID 109 (358 bytes)
Reconstructed using clean ASCII in UTF-16LE with standard `Tahoma` font:
- Window Title: `RBO Patch Client`
- Button 1 (ID 1): `Cancel` (50x16 units)
- Button 2 (ID 2): `Exit` (50x16 units)
- Static 1 (ID 65535): `RBO Notice`
- Static 2 (ID 1003): `Patch complete.`

| Executable | Dialog 109 Offset | Size | Status |
| :--- | :--- | :--- | :--- |
| `rbo.exe` | `0x95D08` | 358 bytes | Patched |
| `rbo_ex1.exe` | `0x9FD68` | 358 bytes | Patched |
| `rbo_ex2.exe` | `0xA3D68` | 358 bytes | Patched |
| `RBO_Ex3.exe` | `0xA3D68` | 358 bytes | Patched |

#### B. Dynamic Start Button String (`ゲーム開始`)
In-place ASCII replacement: `Start\0\0\0\0` (9 bytes):
| Executable | File Offset | Original String | Replacement |
| :--- | :--- | :--- | :--- |
| `rbo.exe` | `0x82AE8` | `\x83Q\x81[\x83\x80\x8aJ\x8en\0` | `Start\0\0\0\0` |
| `rbo_ex1.exe` | `0x8C9C8` | `\x83Q\x81[\x83\x80\x8aJ\x8en\0` | `Start\0\0\0\0` |
| `rbo_ex2.exe` | `0x8F9D8` | `\x83Q\x81[\x83\x80\x8aJ\x8en\0` | `Start\0\0\0\0` |
| `RBO_Ex3.exe` | `0x8F9D8` | `\x83Q\x81[\x83\x80\x8aJ\x8en\0` | `Start\0\0\0\0` |

#### C. Win32 Dialog Resource ID 122 (Save Splash, 156 bytes)
- Static (ID 65535): `  Preparing RBO save data...\r\rPlease wait...`
- Font: `Tahoma` 9pt

| Executable | Dialog 122 Offset | Size | Status |
| :--- | :--- | :--- | :--- |
| `rbo_ex1.exe` | `0x9FED0` | 156 bytes | Patched |
| `rbo_ex2.exe` | `0xA3ED0` | 156 bytes | Patched |
| `RBO_Ex3.exe` | `0xA3ED0` | 156 bytes | Patched |

#### D. Clean Announcement File (`_notice.txt`)
Placed at `DATA/_notice.txt` (overriding packed `.PAC` version). Formatted with CRLF newlines and clean text, explaining windowed mode settings, Thai mod features, and launch instructions.

---

## 8. Script File & Bytecode Architecture (.FOB)

### 8.1 Overview
French-Bread Watanabe Seisakujo engine compiles stage logic, NPC chat bubbles, and character skill voice calls into binary `.FOB` files.
- **Stage Scripts:** `STAGE01.FOB` – `STAGE12.FOB`
- **Character Scripts:** `NOVICE_M/F.FOB`, `SWORDMAN_M/F.FOB`, `ACOLYTE_M/F.FOB`, `MAGICIAN_M/F.FOB`, `ARCHER_M/F.FOB`, `MERCHANT_M/F.FOB`, `THIEF_M/F.FOB`
- **Omake & Utility:** `READMAIL.FOB`, `READMAIL2.FOB`, `READMAIL3.FOB`

### 8.2 String Literal Bytecode Structure
1. **Type A: Opcode `0x00010000` (Compiled String Literal):**
   - `0x00..0x03`: `uint32 opcode = 0x00010000` (`\x00\x00\x01\x00`)
   - `0x04..0x07`: `uint32 dword_count = ceil((strlen + 1) / 4)`
   - `0x08..`: Null-terminated string encoded in Shift-JIS, padded to 4-byte boundary.
2. **Type B: String Tables (Character Victory Shouts):**
   - Header with `string_count` followed by total `dword_count`, followed by contiguous null-terminated strings (e.g. `清算\0`, `せいさーん\0`, `おつかれさまでした\0`).

### 8.3 Translation Workspace Categorization (Step 4 Inventory)
| Category | File | Translatable Strings | Pre-Translated | Status |
| :--- | :--- | :---: | :---: | :--- |
| `01_UI_Menu` | `01_title_menu.csv` | 45 | 45 | Verified (Step 3) |
| `01_UI_Menu` | `02_system_hud.csv` | 20 | 0 | Ready for Step 5 |
| `01_UI_Menu` | `03_lobby_select.csv` | 12 | 0 | Ready for Step 5 |
| `02_Stage_Story` | `stage_prologue_and_base.csv` | 1,173 | 0 | Ready for Step 5 |
| `02_Stage_Story` | `stage_extra_scenarios.csv` | 1,163 | 0 | Ready for Step 5 |
| `03_Character_Shouts` | `character_skills_and_shouts.csv` | 953 | 0 | Ready for Step 5 |
| `04_Arena_and_System` | `arena_and_system_messages.csv` | 554 | 0 | Ready for Step 5 |
| `05_Developer_Letters` | `developer_mail_vol1.csv` | 95 | 0 | Ready for Step 5 |
| `05_Developer_Letters` | `developer_mail_vol2.csv` | 270 | 0 | Ready for Step 5 |
| `05_Developer_Letters` | `developer_mail_vol3.csv` | 584 | 0 | Ready for Step 5 |
| **Total Master** | **`rbo_tstudio_master.csv`** | **4,859** | **45** | **Ready for Batch Translation** |

