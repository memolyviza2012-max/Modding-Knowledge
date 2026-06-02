#!/usr/bin/env python3
"""
Extract DisConv dialogue from _DYextracted binary files.
Uses UpkElements to parse binary data and extract text.
"""
import os
import sys
import struct
from pathlib import Path

sys.path.insert(0, '.')


def extract_from_upk_name(upkName, outputYaml, langCode="INT"):
    """
    Extract all DisConv dialogue from _DYextracted folder to YAML.
    Works by parsing binary files directly using UpkElements.
    """
    import yaml
    from upkElements import UpkElements
    from binary import BinaryStream
    from unpack import unpack
    from upkreader import readerGet
    
    extDir = Path(f"_DYextracted/{upkName}")
    if not extDir.exists():
        raise Exception(f"_DYextracted/{upkName} not found")
    
    print(f"Extracting DisConv from {upkName}...")
    
    # Read header from UPK file (look in known locations)
    upkPath = None
    for base in [
        "F:/SteamLibrary/steamapps/common/Dishonored/DishonoredGame/CookedPCConsole/",
        "E:/Mod_Workspace/Dishonored_Mod_Workspace/03_working/CookedPCConsole/",
    ]:
        testPath = Path(base) / f"{upkName}.upk"
        if testPath.exists():
            upkPath = testPath
            break
    
    if upkPath is None:
        raise Exception(f"Could not find UPK file for {upkName}")
    
    # Get dNames from _names.txt (already extracted from UPK)
    namesPath = Path(f"_DYextracted/{upkName}/_names.txt")
    if namesPath.exists():
        with open(namesPath, 'r', encoding='latin-1') as f:
            rr_dNames = [line.strip() for line in f.readlines()]
        print(f"Loaded {len(rr_dNames)} names from _names.txt")
        rr = {"dNames": rr_dNames}
    else:
        raise Exception(f"_names.txt not found for {upkName}")
    
    # Get all DisConv files
    blurbFiles = sorted(extDir.glob('DisConv_Blurb.*.DisConv_Blurb'))
    choiceFiles = sorted(extDir.glob('DisConv_PlayerChoice.*.DisConv_PlayerChoice'))
    nonWordFiles = sorted(extDir.glob('DisConv_NonWord.*.DisConv_NonWord'))
    
    allFiles = blurbFiles + choiceFiles + nonWordFiles
    print(f"Found {len(blurbFiles)} Blurb, {len(choiceFiles)} PlayerChoice, {len(nonWordFiles)} NonWord")
    
    if len(allFiles) == 0:
        raise Exception("No DisConv files found")
    
    isINT = (langCode == "INT")
    od = {}
    errors = 0
    
    for filepath in allFiles:
        try:
            with open(filepath, 'r+b') as f:
                reader = BinaryStream(f)
                reader.seek(0)
                e = UpkElements(rr["dNames"], reader)
                
                plChoice = False
                if "m_Choices_Static" in e.elements.keys():
                    text = e.elements["m_Choices_Static"]
                    plChoice = True
                elif "m_Text" in e.elements.keys():
                    text = e.elements["m_Text"]
                else:
                    errors += 1
                    continue
                
                if isINT:
                    textVal = text["value"]
                    if plChoice:
                        texVal = []
                        for a in range(len(textVal)):
                            textVal = text["value"]
                            texVal.append(textVal[a]["m_ChoiceText"][0][0].replace('\x00', '').strip())
                        textVal = texVal
                    else:
                        if isinstance(textVal, list):
                            textVal = textVal[0].replace('\x00', '').strip()
                        else:
                            textVal = textVal.replace('\x00', '').strip()
                    od[filepath.name] = textVal
                else:
                    langs = e.resolveLang(e.endOffset)
                    if langs[0]["Count"] == 0:
                        errors += 1
                        continue
                    textArr = []
                    for l in range(len(langs)):
                        textArr.append(langs[l]["langs"][langCode][0][1].replace('\x00', '').strip())
                    if len(textArr) == 1:
                        textArr = textArr[0]
                    od[filepath.name] = textArr
        except Exception as ex:
            errors += 1
            if errors <= 5:
                print(f"  Error: {filepath.name}: {ex}")
    
    print(f"Extracted {len(od)} entries, {errors} errors")
    
    if len(od) == 0:
        raise Exception("No dialogue extracted!")
    
    # Sort
    def sort_key(key):
        parts = key.split('.')
        try:
            t = parts[0]
            idx = int(parts[1])
            order = 0 if 'Blurb' in t else 1 if 'Player' in t else 2
            return (order, idx)
        except:
            return (3, key)
    
    od_sorted = {k: od[k] for k in sorted(od.keys(), key=sort_key)}
    
    # Write
    Path(outputYaml).parent.mkdir(parents=True, exist_ok=True)
    with open(outputYaml, 'w', encoding='utf8') as f:
        yaml.dump(od_sorted, f, allow_unicode=True, width=4096)
    
    print(f"YAML written to {outputYaml} ({len(od_sorted)} entries)")
    return od_sorted


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_from_extracted.py <upk_name> <output_yaml> [langCode]")
        sys.exit(1)
    
    upkName = sys.argv[1]
    outputYaml = sys.argv[2]
    langCode = sys.argv[3] if len(sys.argv) > 3 else "INT"
    
    try:
        extract_from_upk_name(upkName, outputYaml, langCode)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
