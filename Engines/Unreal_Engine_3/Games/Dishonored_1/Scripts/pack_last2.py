import os, subprocess, shutil

SOURCE_DIR = r'F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame'
OUTPUT_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\DLC\DLC'
WORK_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\DLC'
UNPACK_DIR = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working\unpacked_dlc'
TOOL_DECOMPRESS = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\decompress.exe'
TOOL_SUBEDIT = r'D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\dishonored-toolkit\subedit.py'

files = [
    ('DLC06', 'DLC06_DaudBase_Script'),
    ('DLC07', 'DLC07_Twk_Inv_Seekfree_SF'),
]

for dlc_folder, folder in files:
    upk = folder + '.upk'
    th_yaml = os.path.join(WORK_DIR, 'PCConsole', dlc_folder, folder, folder + '_TH.yaml')
    src_dir = os.path.join(SOURCE_DIR, 'DLC', 'PCConsole', dlc_folder)
    out_upk = os.path.join(OUTPUT_DIR, upk)
    
    if os.path.exists(out_upk):
        os.remove(out_upk)
    
    decomp = os.path.join(UNPACK_DIR, upk)
    if os.path.exists(decomp):
        os.remove(decomp)
    
    print('[DECOMPRESS] ' + upk)
    cmd = '"' + TOOL_DECOMPRESS + '" -path="' + src_dir + '" -out="' + UNPACK_DIR + '" "' + upk + '"'
    subprocess.run(cmd, shell=True, capture_output=True)
    
    if os.path.exists(decomp):
        print('[PATCH] ' + upk)
        cmd2 = 'python "' + TOOL_SUBEDIT + '" "' + decomp + '" --input "' + th_yaml + '" --langCode INT'
        r = subprocess.run(cmd2, shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            patched = decomp + '_patched'
            if os.path.exists(patched):
                shutil.copy2(patched, out_upk)
                print('[OK] ' + folder)
            else:
                alt = os.path.join(os.path.dirname(decomp), folder + '_patched.upk')
                if os.path.exists(alt):
                    shutil.copy2(alt, out_upk)
                    print('[OK] ' + folder)
                else:
                    print('[FAIL] No patched file')
        else:
            print('[FAIL] Patch error')
    else:
        print('[FAIL] Decompress')

print('Done!')