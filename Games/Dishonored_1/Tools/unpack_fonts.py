import os, sys
from pathlib import Path
sys.path.insert(0, 'D:/Mod_Workspace/Tool/UE3/dishonored-toolkit-main')
from unpack import unpack

upk = Path(r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\CookedPCConsole\unpacked\DisFonts_SF.upk")
out = Path(r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_working_manual\CookedPCConsole\DisFonts_SF\_DYextracted")

os.makedirs(out, exist_ok=True)
rr = unpack(upk, namefilter=None, split=False, silent=False, dry=False)

print("Done")
print("Objects:", len(rr.get("data", [])))
for obj in rr.get("data", []):
    fname = obj["FileName"].decode("utf-8").replace("\x00", "")
    print(f"  {obj['Type']}: {fname} ({obj['Size']} bytes)")