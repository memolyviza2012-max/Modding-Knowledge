import sys
sys.stdout.reconfigure(encoding='utf-8')

# Check original file
with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Twk_UI_MainMenu.int', 'rb') as f:
    raw = f.read(100)
print("First 100 bytes (hex):", raw.hex())
print("BOM check:", raw[:2].hex())

# Check what's in the translated file
with open(r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Twk_UI_MainMenu.int', 'rb') as f:
    raw2 = f.read(200)
print("\nTranslated first 200 bytes:", raw2[:200])
