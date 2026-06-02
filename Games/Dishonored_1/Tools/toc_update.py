import os
import re
import shutil

game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame"
toc_path = os.path.join(game_dir, "PCConsoleTOC.txt")
upk_path = os.path.join(game_dir, "CookedPCConsole", "DisFonts_SF.upk")

print("[Step 1] Checking Thai font file size...")
if not os.path.exists(upk_path):
    print("ERROR: DisFonts_SF.upk not found in game folder!")
    exit()

new_size = os.path.getsize(upk_path)
print(f"   Current file size: {new_size:,} bytes")

print("\n[Step 2] Updating PCConsoleTOC.txt...")
if not os.path.exists(toc_path):
    print("ERROR: PCConsoleTOC.txt not found!")
    exit()

shutil.copy(toc_path, toc_path + ".bak")

with open(toc_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

updated = False
with open(toc_path, 'w', encoding='utf-8') as f:
    for line in lines:
        if "DisFonts_SF.upk" in line:
            old_size_match = re.match(r'^(\d+)', line.strip())
            if old_size_match:
                old_size = old_size_match.group(1)
                new_line = line.replace(f"{old_size} ", f"{new_size} ", 1)
                f.write(new_line)
                updated = True
                print(f"   Updated: {old_size} -> {new_size}")
            else:
                f.write(line)
        else:
            f.write(line)

print("\n========================================")
if updated:
    print("SUCCESS! TOC updated - UE3 Security bypassed!")
else:
    print("WARNING: DisFonts_SF.upk not found in TOC (may not be checked)")
print("========================================")