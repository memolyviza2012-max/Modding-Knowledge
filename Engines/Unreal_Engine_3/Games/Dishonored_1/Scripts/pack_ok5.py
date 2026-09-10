import os, subprocess, shutil

ok_files = [
    ('DLC06', 'L_DLC07_Brig_Ext_P'),
    ('DLC07', 'L_DLC07_BaseIntro_Script'),
    ('DLC07', 'L_DLC07_Brig_Ext_Loot'),
    ('DLC07', 'L_DLC07_Brigmore_Void_Script'),
    ('DLC07', 'L_DLC07_Coldridge_P'),
]

SOURCE_DIR = r'F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame'
OUTPUT_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\DLC\DLC'
WORK_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC'
UNPACK_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\unpacked_dlc'
TOOL_DECOMPRESS = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\decompress.exe'
TOOL_SUBEDIT = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored-toolkit\subedit.py'

for dlc_folder, folder in ok_files:
    upk_name = f'{folder}.upk'
    th_yaml = os.path.join(WORK_DIR, 'PCConsole', dlc_folder, folder, f'{folder}_TH.yaml')
    src_dir = os.path.join(SOURCE_DIR, 'DLC', 'PCConsole', dlc_folder)
    out_upk = os.path.join(OUTPUT_DIR, upk_name)
    
    if os.path.exists(out_upk):
        os.remove(out_upk)
    
    decomp_path = os.path.join(UNPACK_DIR, upk_name)
    if os.path.exists(decomp_path):
        os.remove(decomp_path)
    
    os.makedirs(UNPACK_DIR, exist_ok=True)
    print(f'[DECOMPRESS] {upk_name}')
    subprocess.run(f'"{TOOL_DECOMPRESS}" -path="{src_dir}" -out="{UNPACK_DIR}" "{upk_name}"', shell=True, capture_output=True)
    
    if os.path.exists(decomp_path):
        print(f'[PATCH] {upk_name}')
        result = subprocess.run(f'python "{TOOL_SUBEDIT}" "{decomp_path}" --input "{th_yaml}" --langCode INT', shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            patched = f'{decomp_path}_patched'
            if os.path.exists(patched):
                shutil.copy2(patched, out_upk)
                print(f'[OK] {folder}')
            else:
                alt = os.path.join(os.path.dirname(decomp_path), f'{folder}_patched.upk')
                if os.path.exists(alt):
                    shutil.copy2(alt, out_upk)
                    print(f'[OK] {folder}')
                else:
                    print(f'[FAIL] No patched file')
        else:
            print(f'[FAIL] Patch error')
    else:
        print(f'[FAIL] Decompress')

print('Done!')