import os
import subprocess
import shutil

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
tools_dir = os.path.join(workspace_dir, "03_tools")
toolkit_dir = os.path.join(tools_dir, "dishonored-toolkit")
decompress_exe = os.path.join(tools_dir, "decompress.exe")
dy_extracted = os.path.join(toolkit_dir, "_DYextracted")
dy_patched = os.path.join(toolkit_dir, "_DYpatched")
game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"

target_upk_name = "Startup.upk"
game_upk = os.path.join(game_dir, target_upk_name)
work_upk = os.path.join(workspace_dir, "01_source", "upk_files", target_upk_name)

print(f"[Step 1] Copying and decompressing {target_upk_name}...")
os.makedirs(os.path.dirname(work_upk), exist_ok=True)
shutil.copy(game_upk, work_upk)

os.chdir(os.path.dirname(work_upk))
subprocess.run([decompress_exe, target_upk_name])
unpacked_upk = os.path.join(os.path.dirname(work_upk), "unpacked", target_upk_name)

print("\n[Step 2] Unpacking SwfMovie from Startup...")
if os.path.exists(dy_extracted):
    shutil.rmtree(dy_extracted)
if os.path.exists(dy_patched):
    shutil.rmtree(dy_patched)
os.makedirs(dy_patched, exist_ok=True)
os.chdir(toolkit_dir)
subprocess.run(["python", "unpack.py", "-f", "SwfMovie", unpacked_upk])

print("\n[Step 3] Injecting Batman fonts into _DYpatched...")
user_font_dir = os.path.join(workspace_dir, "04_output", "fonts_extracted")

# Read _objects.txt to find the correct object IDs
objects_file = os.path.join(dy_extracted, "_objects.txt")
if os.path.exists(objects_file):
    with open(objects_file, "r") as f:
        for line in f:
            parts = line.replace(" ", "").replace("\n", "").split(";")
            if len(parts) >= 5:
                name = parts[0]
                obj_id = parts[1]
                obj_type = parts[2]
                
                if "fonts_efigs" in name:
                    # Copy with proper naming: name.objectId.type_patched
                    new_name = f"{name}.{obj_id}.{obj_type}_patched"
                    shutil.copy(os.path.join(user_font_dir, "fonts_efigs.swf"), 
                               os.path.join(dy_patched, new_name))
                    print(f"  Patched: {new_name}")
                elif "gfxfontlib" in name:
                    new_name = f"{name}.{obj_id}.{obj_type}_patched"
                    shutil.copy(os.path.join(user_font_dir, "gfxfontlib.swf"), 
                               os.path.join(dy_patched, new_name))
                    print(f"  Patched: {new_name}")

print("\n[Step 4] Repacking Startup.upk...")
os.chdir(toolkit_dir)
result = subprocess.run(["python", "patch.py", unpacked_upk], capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print(result.stderr)

# Check for _patched output
final_output = unpacked_upk + "_patched"
if os.path.exists(final_output):
    print(f"Repacked successfully! Installing...")
    if not os.path.exists(game_upk + ".bak"):
        shutil.move(game_upk, game_upk + ".bak")
    else:
        os.remove(game_upk)
    shutil.copy(final_output, game_upk)
    print("SUCCESS! Startup.upk Thai version installed!")
else:
    print("FAILED: Startup.upk could not be repacked")