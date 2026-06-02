import os
import codecs

# โฟลเดอร์ที่เก็บไฟล์ภาษาของเกม
loc_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\Localization"
converted_count = 0

print("[Step 1] Starting encoding cleanup operation...")

# สแกนหาทั้งโฟลเดอร์ INT (อังกฤษ) และ THA (ไทย)
for lang in ["INT", "THA"]:
    folder = os.path.join(loc_dir, lang)
    if not os.path.exists(folder):
        print(f"Folder not found: {folder}")
        continue
        
    print(f"\nScanning folder: {lang}")
    for file in os.listdir(folder):
        if file.lower().endswith(f".{lang.lower()}"):
            filepath = os.path.join(folder, file)
            
            # 1. Read file with various encodings
            content = None
            for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'utf-16-le', 'cp1252', 'tis-620']:
                try:
                    with open(filepath, 'r', encoding=enc) as f:
                        content = f.read()
                    break
                except:
                    pass
            
            # 2. Force write with UTF-16 LE + BOM
            if content is not None:
                try:
                    with open(filepath, 'wb') as f:
                        f.write(codecs.BOM_UTF16_LE)
                        f.write(content.encode('utf-16-le'))
                    print(f"Converted: {file}")
                    converted_count += 1
                except Exception as e:
                    print(f"Failed: {file} - {e}")

print("\n========================================")
print(f"Done! Converted {converted_count} files.")
print("Please test the game subtitles!")
print("========================================")
