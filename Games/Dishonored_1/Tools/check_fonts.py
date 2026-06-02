import os

font_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\fonts_extracted"

for fname in ["fonts_efigs.swf", "gfxfontlib.swf"]:
    fpath = os.path.join(font_dir, fname)
    with open(fpath, 'rb') as f:
        header = f.read(3)
    print(f"{fname}:")
    print(f"  Size: {os.path.getsize(fpath):,} bytes")
    print(f"  Header: {header}")
    print()
