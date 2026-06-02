import os
import codecs

loc_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\Localization"

print("[Step 1] Starting encoding fix operation...")

for lang in ["INT", "THA"]:
    folder = os.path.join(loc_dir, lang)
    if not os.path.exists(folder):
        continue
        
    print(f"\nScanning folder: {lang}")
    for file in os.listdir(folder):
        if file.lower().endswith(f".{lang.lower()}"):
            filepath = os.path.join(folder, file)
            
            try:
                with open(filepath, 'rb') as f:
                    raw_data = f.read()
                
                text = ""
                if raw_data.startswith(codecs.BOM_UTF16_LE):
                    text = raw_data[2:].decode('utf-16-le')
                elif raw_data.startswith(codecs.BOM_UTF8):
                    text = raw_data[3:].decode('utf-8')
                else:
                    try:
                        text = raw_data.decode('utf-8')
                    except:
                        try:
                            text = raw_data.decode('tis-620')
                        except:
                            text = raw_data.decode('cp1252', errors='ignore')
                
                with open(filepath, 'wb') as f:
                    f.write(codecs.BOM_UTF16_LE)
                    f.write(text.encode('utf-16-le'))
                
                print(f"Converted: {file}")
            except Exception as e:
                print(f"Failed: {file} - {e}")

print("\n========================================")
print("Encoding fix operation complete!")
print("========================================")
