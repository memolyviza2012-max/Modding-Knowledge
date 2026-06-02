import os
import subprocess
import shutil

# --- Paths ---
base_dir = r"D:\Mod_Workspace\Tool\UE3\Reverse Engineering"
tools_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools"
umodel_exe = os.path.join(tools_dir, "umodel.exe")
donor_swf_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\Donor_Fonts_Extracted"

print("[Step 1] Creating extraction staging area...")
os.makedirs(donor_swf_dir, exist_ok=True)

print("\n[Step 2] Locating target UPK files...")
target_upks = []
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file.lower() in ['gfxui.upk', 'startup.upk', 'ui_shared.upk'] or file.lower().startswith('ui_'):
            target_upks.append(os.path.join(root, file))

if not target_upks:
    print("No primary targets found, scanning for any .upk files...")
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.lower().endswith('.upk'):
                target_upks.append(os.path.join(root, file))

print(f"Found {len(target_upks)} target files!")

found_swf_count = 0
for upk_path in target_upks[:5]: 
    game_name = os.path.basename(os.path.dirname(os.path.dirname(upk_path)))
    if not game_name or game_name == "Reverse Engineering":
        game_name = os.path.basename(os.path.dirname(upk_path))
        
    print(f"Extracting from: {os.path.basename(upk_path)} (from {game_name})")
    
    temp_dir = os.path.join(donor_swf_dir, "temp_extract")
    os.makedirs(temp_dir, exist_ok=True)
    subprocess.run([umodel_exe, "-export", f"-out={temp_dir}", upk_path], capture_output=True)
    
    for r, d, f in os.walk(temp_dir):
        for file in f:
            if file.lower().endswith('.swf') or file.lower().endswith('.gfx'):
                new_name = f"{game_name}_{file}"
                shutil.copy2(os.path.join(r, file), os.path.join(donor_swf_dir, new_name))
                print(f"   Extracted: {new_name}")
                found_swf_count += 1
                
    shutil.rmtree(temp_dir, ignore_errors=True)

print("\n========================================")
print(f"Extraction complete! Found {found_swf_count} Flash files.")
print(f"Location: {donor_swf_dir}")
print("========================================")
