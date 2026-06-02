"""
DISHONORED-018: Setup Dishonored Toolkit & Decompress
"""
import os
import subprocess

tools_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools"
toolkit_dir = os.path.join(tools_dir, "dishonored-toolkit")
upk_source = os.path.join(tools_dir, "..", "01_source", "upk_files", "DisFonts_SF.upk")
upk_source = os.path.normpath(upk_source)

print("DISHONORED-018: Toolkit Setup")
print("=" * 60)

# Step 1: Check for decompress.exe in tools
decompress_exe = os.path.join(tools_dir, "decompress.exe")
print(f"[CHECK] decompress.exe at: {decompress_exe}")
print(f"        Exists: {os.path.exists(decompress_exe)}")

# Check UE3 tools folder
ue3_tools = r"D:\Mod_Workspace\Tool\UE3"
ue3_exes = []
if os.path.exists(ue3_tools):
    for root, dirs, files in os.walk(ue3_tools):
        for f in files:
            if f.endswith('.exe'):
                ue3_exes.append(os.path.join(root, f))

print(f"[INFO] Found {len(ue3_exes)} .exe files in UE3 tools:")
for exe in ue3_exes:
    print(f"       {exe}")

# Step 2: Check/Clone dishonored-toolkit
print(f"\n[CHECK] dishonored-toolkit at: {toolkit_dir}")
print(f"        Exists: {os.path.exists(toolkit_dir)}")

if not os.path.exists(toolkit_dir):
    print("\n[ACTION] Cloning dishonored-toolkit...")
    try:
        result = subprocess.run(
            ["git", "clone", "https://github.com/deadYokai/dishonored-toolkit.git", toolkit_dir],
            capture_output=True, text=True, timeout=60
        )
        print(f"Clone result: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout[:500]}")
        if result.stderr:
            print(f"Stderr: {result.stderr[:500]}")
    except Exception as e:
        print(f"Clone failed: {e}")
else:
    print("  Toolkit already exists")

# Step 3: Look for decompress tool in toolkit
if os.path.exists(toolkit_dir):
    print(f"\n[SCAN] Checking toolkit contents...")
    for root, dirs, files in os.walk(toolkit_dir):
        for f in files:
            if 'decompress' in f.lower() or 'compress' in f.lower():
                print(f"  Found: {os.path.join(root, f)}")

print("\n" + "=" * 60)
print("SETUP COMPLETE - Check above for details")
