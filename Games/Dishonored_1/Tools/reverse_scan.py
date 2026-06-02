import os
import binascii

base_dir = r"D:\Mod_Workspace\Tool\UE3\Reverse Engineering"

font_keywords = [
    b'Chalet', b'Emerge', b'Tahoma', b'Cordia', b'IBM Plex', b'Noto Sans', 
    b'DB ', b'Supermarket', b'PS ', b'Boon', b'Sarabun'
]

text_extensions = ['.int', '.tha', '.loc', '.txt', '.csv']
ui_extensions = ['.swf', '.gfx', '.upk']

print("[Marix Reverse Engineering Protocol] Starting scan...")
print(f"Target: {base_dir}\n")

for root, dirs, files in os.walk(base_dir):
    for file in files:
        filepath = os.path.join(root, file)
        ext = os.path.splitext(file)[1].lower()
        
        if ext in text_extensions:
            try:
                with open(filepath, 'rb') as f:
                    raw_bytes = f.read(4)
                
                encoding_type = "Unknown"
                if raw_bytes.startswith(b'\xff\xfe'):
                    encoding_type = "UTF-16 LE (with BOM) - UE3 Standard"
                elif raw_bytes.startswith(b'\xef\xbb\xbf'):
                    encoding_type = "UTF-8 (with BOM)"
                
                print(f"[TEXT] {file}")
                print(f"   -> Encoding: {encoding_type}")
            except Exception as e:
                pass

        elif ext in ui_extensions:
            try:
                found_fonts = set()
                with open(filepath, 'rb') as f:
                    content = f.read(5242880) 
                    
                    for keyword in font_keywords:
                        if keyword.lower() in content.lower():
                            found_fonts.add(keyword.decode('utf-8', errors='ignore'))
                
                if found_fonts:
                    print(f"[UI/FONT] {file}")
                    print(f"   -> Detected font names: {', '.join(found_fonts)}")
            except Exception as e:
                pass

print("\n========================================")
print("Scan complete!")
print("========================================")
