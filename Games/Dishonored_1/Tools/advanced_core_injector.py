import os
import subprocess
import shutil
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

tools_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools"
sys.path.append(tools_dir)

decompress_exe = os.path.join(tools_dir, "decompress.exe")
if not os.path.exists(decompress_exe):
    print("❌ หยุดปฏิบัติการ! ไม่พบ decompress.exe ใน 03_tools!")
    sys.exit(1)

try:
    from swf_repacker import SimpleUPKRepacker
except ImportError:
    print("❌ ไม่พบ swf_repacker.py!")
    sys.exit(1)

game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"
startup_game_path = os.path.join(game_dir, "Startup.upk")

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\upk_files"
startup_workspace = os.path.join(workspace_dir, "Startup.upk")
unpacked_startup = os.path.join(workspace_dir, "Startup.upk.uncompressed")

output_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\04_output"
extracted_dir = os.path.join(output_dir, "unpacked_upk", "Startup")
output_startup = os.path.join(output_dir, "Startup_THAI.upk")

user_font_dir = os.path.join(output_dir, "fonts_extracted")
thai_efigs = os.path.join(user_font_dir, "fonts_efigs.swf")
thai_fontlib = os.path.join(user_font_dir, "gfxfontlib.swf")

print("🚀 [Step 1] ดึง Startup.upk และ Decompress...")
os.makedirs(workspace_dir, exist_ok=True)
shutil.copy(startup_game_path, startup_workspace)
os.chdir(workspace_dir)
result = subprocess.run([decompress_exe, "Startup.upk"], capture_output=True, text=True)
print(result.stdout)
print(result.stderr if result.stderr else "")

print("\n🧹 [Step 2] สกัดโครงสร้างด้วย upk_unpacker.py...")
os.chdir(tools_dir)
subprocess.run(["python", "upk_unpacker.py"], capture_output=True)

print("\n🚀 [Step 3] แอบสอดไส้ภาษาไทย...")
search_path = os.path.join(output_dir, "unpacked_upk")
injected = 0
for root, dirs, files in os.walk(search_path):
    for file in files:
        if file.lower() == "fonts_efigs.swf":
            shutil.copy(thai_efigs, os.path.join(root, file))
            print(f"  ✅ เสียบ {file} ที่ {root}")
            injected += 1
        elif file.lower() == "gfxfontlib.swf":
            shutil.copy(thai_fontlib, os.path.join(root, file))
            print(f"  ✅ เสียบ {file} ที่ {root}")
            injected += 1

print(f"  → สอดไส้ได้ {injected} ไฟล์")

print("\n🚀 [Step 4] ประกอบร่างขั้นสูง...")
split_dir = None
for root, dirs, files in os.walk(search_path):
    if "_objects.txt" in files:
        split_dir = root
        break

if split_dir:
    repacker = SimpleUPKRepacker(unpacked_startup, output_startup)
    repacker.repack(split_dir)
    if os.path.exists(output_startup):
        print(f"✅ ประกอบร่างสำเร็จ! ({os.path.getsize(output_startup):,} bytes)")
    else:
        print("❌ Repack ล้มเหลว!")
        sys.exit(1)
else:
    print("❌ หาโฟลเดอร์สำหรับ Repack ไม่เจอ!")
    sys.exit(1)

print("\n🚀 [Step 5] ติดตั้งลงเกม...")
backup_startup = startup_game_path + ".bak"
if not os.path.exists(backup_startup):
    shutil.move(startup_game_path, backup_startup)
    print(f"  📦 Backup เก่าไว้ที่ {backup_startup}")
else:
    os.remove(startup_game_path)
    print(f"  🗑️ ลบตัวเก่า (backup มีอยู่แล้ว)")

shutil.copy(output_startup, startup_game_path)
print("🎉 ติดตั้ง Startup.upk ลงเกมเรียบร้อย!")
print("=" * 50)
print("ทดสอบในเกมได้เลยครับท่าน!")
print("=" * 50)
