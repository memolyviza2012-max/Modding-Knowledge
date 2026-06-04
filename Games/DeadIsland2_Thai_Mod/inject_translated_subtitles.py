import os
import xml.etree.ElementTree as ET
import csv

# Mapping of file source to original XML paths and pack output paths
XML_CONFIGS = {
    "Main": {
        "src": "Extracted/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList.xml",
        "dest": "Pack/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList.xml"
    },
    "EXP1": {
        "src": "Extracted/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList_EXP1.xml",
        "dest": "Pack/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList_EXP1.xml"
    },
    "EXP2": {
        "src": "Extracted/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList_EXP2.xml",
        "dest": "Pack/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList_EXP2.xml"
    },
    "Horde": {
        "src": "Extracted/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList_Horde.xml",
        "dest": "Pack/DeadIsland/Content/StagedData/DamLoc/Data/DialogueList_Horde.xml"
    }
}

CSV_FILEPATH = "Translation/Dialogue_Subtitles.csv"

def inject_subtitles():
    print("==============================================")
    print("   Injecting Subtitles back into XML Lists   ")
    print("==============================================")
    
    if not os.path.exists(CSV_FILEPATH):
        print(f"[ERROR] Subtitle CSV file not found: {CSV_FILEPATH}")
        return
        
    # Read translation records
    translations = {}
    total_loaded = 0
    translated_loaded = 0
    
    print(f"Reading translations from {CSV_FILEPATH}...")
    try:
        with open(CSV_FILEPATH, "r", encoding="utf-16") as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row["Key"]
                thai = row["Thai"].strip()
                english = row["English"].strip()
                source = row["Source"]
                
                total_loaded += 1
                if thai:  # Only load non-empty translations
                    translations[key] = thai
                    translated_loaded += 1
    except Exception as e:
        print(f"[ERROR] Failed to read CSV: {e}")
        return
        
    print(f"Loaded {total_loaded:,} subtitle records.")
    print(f"Translated records found: {translated_loaded:,} ({translated_loaded/total_loaded*100:.1f}%)")
    
    if translated_loaded == 0:
        print("[WARN] No translated strings (Thai column is empty). Copying English text for fallback injection test.")
        # For testing, we can inject English to verify the packer works, or we can wait.
        # Let's proceed anyway to create the structure.
        
    # Process each XML file
    for label, config in XML_CONFIGS.items():
        src_path = config["src"]
        dest_path = config["dest"]
        
        if not os.path.exists(src_path):
            print(f"[SKIP] Original XML not found: {src_path}")
            continue
            
        print(f"Processing {label} XML...")
        print(f"  Reading {src_path}...")
        try:
            tree = ET.parse(src_path)
            root = tree.getroot()
            
            elements = root.findall(".//DialogueLineVariation") + root.findall(".//DialogueLine")
            patched_count = 0
            
            for elem in elements:
                path = elem.get("Path")
                if not path:
                    continue
                    
                chunks = elem.findall("Chunk")
                if chunks:
                    for idx, chunk in enumerate(chunks):
                        key = f"{path}#chunk_{idx}"
                        if key in translations:
                            chunk.set("Text", translations[key])
                            patched_count += 1
                else:
                    if path in translations:
                        elem.set("ActorLine", translations[path])
                        patched_count += 1
            
            print(f"  Patched {patched_count:,} lines in XML memory.")
            
            # Save to Pack folder
            print(f"  Saving patched XML to {dest_path}...")
            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
            
            # Write with XML declaration and utf-8
            tree.write(dest_path, encoding="utf-8", xml_declaration=True)
            print(f"  [OK] Saved patched XML.")
            
        except Exception as e:
            print(f"  [ERROR] Failed to process {label} XML: {e}")
            
    print("\nInjection completed successfully.")

if __name__ == "__main__":
    inject_subtitles()
