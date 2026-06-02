import os
import shutil
import subprocess

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
tools_dir = os.path.join(workspace_dir, "03_tools")
decompress_exe = os.path.join(tools_dir, "decompress.exe")
game_upk = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole\DisFonts_SF.upk"
work_dir = os.path.join(workspace_dir, "04_output", "Direct_JPEXS_Work")

print("[Step 1] Creating clean workspace...")
if os.path.exists(work_dir):
    shutil.rmtree(work_dir)
os.makedirs(work_dir, exist_ok=True)

print("[Step 2] Restoring original from backup...")
backup_upk = game_upk + ".bak"
src_upk = os.path.join(work_dir, "DisFonts_SF.upk")

if os.path.exists(backup_upk):
    shutil.copy(backup_upk, src_upk)
    print("   Restored!")
else:
    print("   ERROR: No backup found! Verify game files in Steam first.")
    exit()

print("[Step 3] Decompressing...")
os.chdir(work_dir)
subprocess.run([decompress_exe, "DisFonts_SF.upk"])

unpacked_upk = os.path.join(work_dir, "unpacked", "DisFonts_SF.upk")
if os.path.exists(unpacked_upk):
    print(f"\nReady for surgery! File: {unpacked_upk}")
else:
    print("\nDecompress failed")