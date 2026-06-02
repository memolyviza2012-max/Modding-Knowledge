import os
import subprocess
import shutil

workspace_dir = r"D:\Mod_Workspace\Dishonored_Mod_Workspace"
toolkit_dir = os.path.join(workspace_dir, "03_tools", "dishonored-toolkit")
dy_extracted = os.path.join(toolkit_dir, "_DYextracted")
user_font_dir = os.path.join(workspace_dir, "04_output", "fonts_extracted")
game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"
game_upk = os.path.join(game_dir, "DisFonts_SF.upk")

print("[Step 1] Cleaning up old assembly folders...")
if os.path.exists(dy_extracted):
    shutil.rmtree(dy_extracted)
os.makedirs(dy_extracted, exist_ok=True)

print("[Step 2] Copying real fonts from commander...")
shutil.copy(os.path.join(user_font_dir, "fonts_efigs.swf"), os.path.join(dy_extracted, "fonts_efigs.swf"))
shutil.copy(os.path.join(user_font_dir, "gfxfontlib.swf"), os.path.join(dy_extracted, "gfxfontlib.swf"))

print("[Step 3] Running patch.py to reassemble...")
os.chdir(toolkit_dir)
output_upk = os.path.join(workspace_dir, "04_output", "DisFonts_SF_THAI.upk")
subprocess.run(["python", "patch.py", dy_extracted, output_upk])

final_file = output_upk
if not os.path.exists(output_upk) and os.path.exists(output_upk + "_patched"):
    final_file = output_upk + "_patched"

if os.path.exists(final_file):
    print("[Step 4] Installing to game folder...")
    if os.path.exists(game_upk):
        os.remove(game_upk)
    shutil.copy(final_file, game_upk)
    print("SUCCESS! DisFonts_SF.upk installed with Thai fonts!")
else:
    print("FAILED: Assembly did not produce output")