# Restore English original first (previous run corrupted it)
import shutil

src = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\Localization\INT\Twk_InGameUI.int"
dst = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Twk_InGameUI.int"
shutil.copy2(src, dst)
print("Restored original EN file")

# Now run Shield Engine V.2
import subprocess
result = subprocess.run(
    ["python", r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\translate_shield_v2.py"],
    capture_output=True, text=True
)
print(result.stdout)
print(result.stderr if result.stderr else "")