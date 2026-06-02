import os
import shutil

base_dir = r"D:\Mod_Workspace\Tool\UE3\Reverse Engineering"
donor_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\Donor_Fonts"

print("[Step 1] Creating temporary staging area...")
os.makedirs(donor_dir, exist_ok=True)

print("\n[Step 2] Scanning for high-value target files...")

keywords = ['ui', 'font', 'startup', 'hud', 'menu']
found_count = 0

for root, dirs, files in os.walk(base_dir):
    for file in files:
        file_lower = file.lower()
        if file_lower.endswith('.upk') or file_lower.endswith('.swf'):
            if any(kw in file_lower for kw in keywords):
                source_path = os.path.join(root, file)
                game_name = os.path.basename(os.path.dirname(root))
                safe_name = f"{game_name}_{file}" 
                dest_path = os.path.join(donor_dir, safe_name)
                
                try:
                    shutil.copy2(source_path, dest_path)
                    print(f"Copied: {file}")
                    print(f"   From: {os.path.basename(root)}")
                    found_count += 1
                    
                    if found_count >= 6:
                        break
                except Exception as e:
                    pass
    if found_count >= 6:
        break

print("\n========================================")
print(f"Done! Copied {found_count} files to Donor_Fonts.")
print(f"Location: {donor_dir}")
print("========================================")
