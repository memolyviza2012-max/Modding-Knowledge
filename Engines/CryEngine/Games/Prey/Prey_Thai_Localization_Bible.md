# Prey (2017) — Thai Localization Modding Bible
### Advanced Deep Analysis Edition (Rivet Engineer)

---

## 1. Overview
Prey (2017) runs on a heavily modified version of CryEngine (often referred to internally as the Void Engine by Arkane Studios). The Thai localization mod utilizes a **File Replacement / Overlay** architecture, taking advantage of the engine's `.pak` patching system to inject Thai fonts and localized XML string databases overriding the base English text.

---

## 2. Technical Stack
| รายการ | รายละเอียด |
|---|---|
| **Game Engine** | CryEngine (Arkane modified) |
| **Developer** | Arkane Studios Austin |
| **Project Codename** | Danielle |
| **Archive Format** | `.pak` (Standard ZIP Archive) |
| **AES Encryption** | No |
| **Compression** | Standard ZIP Deflate |
| **Font System** | Font Swap (TrueType Font inside `.pak` + `.gfx` definitions) |
| **Thai Font Used** | Noto Sans Thai UI (Regular / Bold) |
| **Text System** | XML (`.xml`) |
| **Text Encoding** | UTF-8 |
| **Mod Complexity** | ★★☆☆☆ (Very modder-friendly; standard ZIP and XML formats) |

---

## 3. โครงสร้างไฟล์ (File Architecture)
```
D:\Mods games\Thai Mods\0_Rivet Engineer\Prey\
├── GameSDK\Precache\patch_thai_fonts.pak           [438 KB] - Contains NotoSansThaiUI TTF fonts
├── Localization\English_xml_patch.pak              [1.5 MB] - Main game localized text in XML
└── Whiplash\Localization\English_xml_patch.pak     [100 KB] - DLC (Mooncrash) localized text in XML
```

---

## 4. Font Analysis
- The game uses standard TrueType fonts (`.ttf`) packaged inside `.pak` files.
- The mod introduces `NotoSansThaiUI-Regular.ttf` and `NotoSansThaiUI-Bold.ttf`.
- Because CryEngine's UI often uses Scaleform/GFX, there are also `.gfx` files (e.g. `HUD_Font_LocFont.gfx`) inside the font patch, mapping the TTF fonts to the game's UI elements.
- Thai rendering considerations: Since Scaleform natively supports standard TTFs if configured correctly, basic Thai shaping works, though complex vowel/tone mark alignment (สระลอย) may require pre-shaping or specific font adjustments if the UI engine does not natively support advanced HarfBuzz shaping.

---

## 5. Text Analysis
- Text is stored in standard **XML** files, organized logically into folders (e.g., `ark/player/text_traumas.xml`, `ark/campaign/text_emaillibrary.xml`).
- Encoding is strictly **UTF-8**.
- Our analysis detected over **611,690** Thai UTF-8 characters across hundreds of `.xml` files, indicating a fully translated UI, subtitles, and extensive lore (emails/books).
- Subtitle lines are organized under the `voices/` directory, mapped to specific audio file hashes.

---

## 6. Cross-Engine Comparison
Prey (2017) is extremely accessible for localization compared to other proprietary engines. Because the `.pak` files are simply ZIP archives (similar to **Luminous Engine's** older formats or some **Unreal Engine 3** iterations), modders don't need specialized proprietary unpackers like they do for Unreal Engine 4/5 `.pak` or Crystal Dynamics' `.tiger` files. Any standard ZIP utility can modify the contents, and plain XML allows easy text editing.

---

## 7. Pipeline — ขั้นตอนสร้างม็อด
**Text Pipeline:**
1. Extract `English_xml_patch.pak` using 7-Zip or WinRAR.
2. Edit the `.xml` files in any text editor (VSCode, Notepad++), ensuring UTF-8 encoding without BOM is preserved.
3. Zip the modified `Localization` folder back into an archive and rename the extension to `.pak`.
4. Place it in the game directory. The engine will prioritize files with `patch` in the name.

**Font Pipeline:**
1. Create a `patch_thai_fonts.pak` (ZIP archive) containing the chosen `.ttf` files.
2. Modify or include the corresponding `.gfx` (Scaleform font config) to point to the new TTF filenames.
3. Place in `GameSDK\Precache\`.

---

## 8. Troubleshooting
- **Thai text shows as boxes:** The `patch_thai_fonts.pak` is not loading, or the `.gfx` file inside does not correctly map to the injected `.ttf`.
- **Game hangs on loading screen:** An XML syntax error (e.g., missing closing tag `</Cell>`) will crash the engine parser. Always validate XML before packing.
- **Corrupted characters:** The XML file was accidentally saved in Windows-1252 or UTF-8 with BOM instead of standard UTF-8.

---

## 9. Required Tools
| Tool | Purpose | Source |
|---|---|---|
| 7-Zip / WinRAR | Extracting and repacking `.pak` (ZIP) files | [Download](https://www.7-zip.org/) |
| VSCode / Notepad++ | Editing XML string tables | [Download](https://code.visualstudio.com/) |

---

## 10. Extracted Assets
- [NotoSansThaiUI-Regular.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/CryEngine/Games/Prey/Assets/Fonts/NotoSansThaiUI-Regular.ttf)
- [NotoSansThaiUI-Bold.ttf](file:///E:/Mod_Workspace/Modding-Knowledge/Engines/CryEngine/Games/Prey/Assets/Fonts/NotoSansThaiUI-Bold.ttf)
