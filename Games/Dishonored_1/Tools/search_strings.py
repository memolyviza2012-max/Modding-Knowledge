import os

files = [
    r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_SF.upk",
    r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files\DisFonts_LCZEHUNPOL_SF.upk"
]

keywords = [b'Eurostile', b'eurostile', b'Dishonored', b'Font', b'font', b'FONT']

for fpath in files:
    print(f"=== {os.path.basename(fpath)} ===")
    with open(fpath, 'rb') as f:
        data = f.read()
    
    for keyword in keywords:
        pos = data.find(keyword)
        if pos != -1:
            print(f"  Found '{keyword.decode()}' at offset {pos} (0x{pos:X})")
            start = max(0, pos-10)
            end = min(len(data), pos+30)
            context = data[start:end]
            printable = ''.join(chr(b) if 32<=b<127 else '.' for b in context)
            print(f"    Context: {printable}")
    
    print()
