import os

game_dir = r"F:\SteamLibrary\steamapps\common\Dishonored\DishonoredGame\CookedPCConsole"

search_terms = {
    b'fonts_efigs': 'Found fonts_efigs.swf',
    b'gfxfontlib': 'Found gfxfontlib.swf',
    b'ChaletComprime': 'Found Chalet font (main subtitle)',
    b'Emerge BF': 'Found Emerge font (headline)'
}

print("[Step 1] Starting Radar Sweep...")
print(f"Target: {game_dir}\n")

found_files = {}
total_scanned = 0

for root, dirs, files in os.walk(game_dir):
    for file in files:
        if file.lower().endswith('.upk'):
            filepath = os.path.join(root, file)
            total_scanned += 1
            
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                    
                    hits = []
                    for term, desc in search_terms.items():
                        if term.lower() in content.lower():
                            hits.append(desc)
                    
                    if hits:
                        found_files[file] = hits
                        print(f"LOCKED: {file}")
                        for hit in hits:
                            print(f"   -> {hit}")
                            
            except Exception as e:
                pass

print("\n========================================")
print(f"Radar sweep complete! Scanned {total_scanned} files")
if found_files:
    print(f"Found {len(found_files)} files with font references!")
else:
    print("No font references found in this folder.")
print("========================================")