import os
import subprocess

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
tools_dir = os.path.join(workspace_dir, "03_tools")
decompress_exe = os.path.join(tools_dir, "decompress.exe")
game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"

# Paths
backup_in_game = os.path.join(game_dir, "DisFonts_SF_BACKUP.upk")
work_dir = os.path.join(workspace_dir, "04_output", "Direct_JPEXS_Work")
work_upk = os.path.join(work_dir, "DisFonts_SF.upk")
unpacked_dir = os.path.join(work_dir, "unpacked")
unpacked_upk = os.path.join(unpacked_dir, "DisFonts_SF.upk")

print(f"Source backup: {backup_in_game}")
print(f"Exists: {os.path.exists(backup_in_game)}")
print(f"Size: {os.path.getsize(backup_in_game):,} bytes")

# Clean and copy
if os.path.exists(work_dir):
    import shutil
    shutil.rmtree(work_dir)
os.makedirs(unpacked_dir, exist_ok=True)

shutil.copy(backup_in_game, work_upk)
print(f"Copied to: {work_upk}")

# Run decompress from the work_dir
os.chdir(work_dir)
print(f"\nRunning decompress from: {os.getcwd()}")
result = subprocess.run([decompress_exe, "DisFonts_SF.upk"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

if os.path.exists(unpacked_upk):
    print(f"\nSUCCESS! File ready: {unpacked_upk}")
    print(f"Size: {os.path.getsize(unpacked_upk):,} bytes")
else:
    print("\nDecompress may have failed - checking file...")
    if os.path.exists(work_upk):
        print(f"Working file still exists: {work_upk}")