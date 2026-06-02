import os

game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"

target_files = [
    "DisFonts_LCZEHUNPOL_SF.upk",
    "DisFonts_LRUS_SF.upk",
    "UI_Loading_SF_LOC_INT.upk",
    "UI_Loading_LCZEHUNPOL_SF_LOC_INT.upk",
    "DishonoredGame.upk"
]

print("[Marix Exclusion Protocol] Status Report...\n")

for i, filename in enumerate(target_files):
    path = os.path.join(game_dir, filename)
    disabled_path = path + ".DISABLED"
    
    status = "READY (normal)"
    if os.path.exists(disabled_path):
        status = "DISABLED"
    elif not os.path.exists(path):
        status = "NOT FOUND"
        
    print(f"{i+1}. {filename} -> {status}")

print("\n========================================")
print("To toggle a file, specify the number.")
print("========================================")