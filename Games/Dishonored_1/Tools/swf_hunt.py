import os
import shutil

base_dir = r"D:\Mod_Workspace\Tool\UE3\Reverse Engineering"
donor_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\Donor_Fonts_V2"

print("[Step 1] Creating V2 staging area...")
os.makedirs(donor_dir, exist_ok=True)

print("\n[Step 2] Scanning for raw .swf and .gfx files only...")

found_count = 0
for root, dirs, files in os.walk(base_dir):
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        
        if ext in ['.swf', '.gfx']:
            source_path = os.path.join(root, file)
            game_name = os.path.basename(os.path.dirname(root))
            safe_name = f"{game_name}_{file}" 
            dest_path = os.path.join(donor_dir, safe_name)
            
            try:
                shutil.copy2(source_path, dest_path)
                print(f"Found: {file} (from {os.path.basename(root)})")
                found_count += 1
            except:
                pass

print("\n========================================")
if found_count > 0:
    print(f"Found {found_count} raw Flash files!")
    print(f"Location: {donor_dir}")
    print("Open these .swf files in JPEXS to extract fonts!")
else:
    print("No raw .swf or .gfx files found.")
    print("The modder may have deleted the raw files.")
print("========================================")
