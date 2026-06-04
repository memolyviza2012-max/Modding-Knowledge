import os
import subprocess

workspace = r"."
pack_dir = os.path.join(workspace, "Pack")
unrealpak_exe = r"E:\Mod_Workspace\Tool\UE4\Unreal\UnrealPak-841\Engine\Binaries\Win64\UnrealPak.exe"
output_pak = os.path.join(workspace, "DeadIsland2_TH_P.pak")
response_file = os.path.join(workspace, "response.txt")

if not os.path.exists(pack_dir):
    print(f"[ERROR] โฟลเดอร์ Pack ไม่พบที่: {pack_dir}")
    exit(1)

if not os.path.exists(unrealpak_exe):
    print(f"[ERROR] เครื่องมือ UnrealPak.exe ไม่พบที่: {unrealpak_exe}")
    exit(1)

print("กำลังสร้างไฟล์ response.txt สำหรับ UnrealPak...")

file_list = []
for root, dirs, files in os.walk(pack_dir):
    for file in files:
        abs_path = os.path.abspath(os.path.join(root, file))
        # หา relative path จากโฟลเดอร์ Pack
        rel_path = os.path.relpath(abs_path, pack_dir)
        # แปลงเป็น virtual path ในเกมโดยใช้ prefix ../../../
        virtual_path = "../../../" + rel_path.replace(os.path.sep, "/")
        file_list.append(f'"{abs_path}" "{virtual_path}"')

if not file_list:
    print("[ERROR] ไม่มีไฟล์ใดๆ ในโฟลเดอร์ Pack!")
    exit(1)

with open(response_file, "w", encoding="utf-8") as f:
    for line in file_list:
        f.write(line + "\n")

print(f"เขียนไฟล์ response.txt เรียบร้อย (จำนวน {len(file_list)} ไฟล์)")
print("กำลังเรียกใช้งาน UnrealPak.exe เพื่อทำม็อด (.pak + .sig)...")

# รัน UnrealPak.exe
# รูปแบบ: UnrealPak.exe <OutputPak> -Create=<ResponseFile> -sign
cmd = [unrealpak_exe, output_pak, f"-Create={response_file}", "-sign"]
try:
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    print("สำเร็จ!")
    print(f"ไฟล์ม็อดที่สร้างเสร็จแล้ว:")
    print(f"  - {output_pak}")
    print(f"  - {output_pak.replace('.pak', '.sig')}")
    
    # พัดโฟลเดอร์เกมเป้าหมาย
    game_mods_dir = r"F:\Epic Games\DeadIsland2\DeadIsland\Content\Paks\~mods"
    print(f"\nกำลังก๊อปปี้ไฟล์ม็อดไปที่โฟลเดอร์เกม: {game_mods_dir}")
    os.makedirs(game_mods_dir, exist_ok=True)
    
    # ล้างไฟล์ม็อดชื่อซ้ำตัวเก่าใน ~mods ป้องกันปัญหาทับซ้อน
    old_mod_path = os.path.join(game_mods_dir, "pakchunk_default-WindowsNoEditor_P.pak")
    old_sig_path = os.path.join(game_mods_dir, "pakchunk_default-WindowsNoEditor_P.sig")
    if os.path.exists(old_mod_path):
        os.remove(old_mod_path)
    if os.path.exists(old_sig_path):
        os.remove(old_sig_path)
        
    import shutil
    game_pak_name = "pakchunk_default-WindowsNoEditor_Thai_P.pak"
    shutil.copy2(output_pak, os.path.join(game_mods_dir, game_pak_name))
    print(f"คัดลอกไฟล์ม็อด {game_pak_name} สำเร็จ")
    
    # คัดลอกและเปลี่ยนชื่อ .sig จากไฟล์หลักของเกมเพื่อหลอกระบบ Signature Check
    orig_sig_path = r"F:\Epic Games\DeadIsland2\DeadIsland\Content\Paks\pakchunk_default-WindowsNoEditor_P.sig"
    target_sig_path = os.path.join(game_mods_dir, "pakchunk_default-WindowsNoEditor_Thai_P.sig")
    if os.path.exists(orig_sig_path):
        shutil.copy2(orig_sig_path, target_sig_path)
        print("คัดลอกไฟล์ .sig จากเกมหลักและเปลี่ยนชื่อเป็นของม็อดสำเร็จ")
    else:
        print("[WARNING] ไม่พบไฟล์ .sig หลักของเกมสำหรับคัดลอก")
        
    print("คัดลอกไฟล์ Mod เข้าสู่เกมสำเร็จแล้ว! บอสสามารถเปิดเกมทดสอบได้เลยครับ")
    
except subprocess.CalledProcessError as e:
    print(f"[ERROR] เกิดข้อผิดพลาดในระว่างรัน UnrealPak.exe:")
    print(e.stderr)
    exit(1)

