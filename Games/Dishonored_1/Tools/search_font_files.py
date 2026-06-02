"""
DISHONORED-007 (Phase 1): Font Files Scanner
"""
import os
import glob

source_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"
patterns = ["*GFxUI*.upk", "*UI_Fonts*.upk", "*Startup*.upk", "*Font*.upk"]

print("DISHONORED-007: Font Files Scanner")
print("=" * 60)
print(f"Source: {source_dir}")
print()

results = []

for pattern in patterns:
    search_path = os.path.join(source_dir, pattern)
    files = glob.glob(search_path)
    
    for file_path in files:
        file_name = os.path.basename(file_path)
        file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        results.append({
            "Filename": file_name,
            "SizeMB": file_size_mb,
            "MatchPattern": pattern
        })

# Sort: GFxUI first, then Startup, then by size
def sort_key(x):
    fname = x["Filename"]
    gfxi_first = fname.find("GFxUI") == -1  # True=sort later, False=sort first
    startup_second = fname.find("Startup") == -1
    return (gfxi_first, startup_second, -x["SizeMB"])

results.sort(key=sort_key)

print(f"Found {len(results)} matching files:\n")
print(f"{'Rank':<5} {'Filename':<45} {'Size (MB)':>10} {'Pattern':<20}")
print("-" * 85)
for i, res in enumerate(results, 1):
    print(f"{i:<5} {res['Filename']:<45} {res['SizeMB']:>10.2f} {res['MatchPattern']:<20}")

print()
print("=" * 60)
print("TOP 5 PRIORITY FILES:")
print("=" * 60)
for i, res in enumerate(results[:5], 1):
    print(f"  {i}. {res['Filename']} ({res['SizeMB']:.2f} MB)")
