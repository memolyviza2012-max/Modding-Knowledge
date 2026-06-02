#!/usr/bin/env python3
"""
Patch Thai YAML into extracted DisConv files and repack UPK.
Uses _DYextracted folder and the patch() function from subedit.py.
"""
import os
import sys
import struct
import yaml
from pathlib import Path

sys.path.insert(0, '.')

from upkElements import UpkElements
from binary import BinaryStream
from patch import patch


def patch_and_pack(upkName, yamlPath, langCode="TH"):
    """Patch DisConv files with Thai text and repack UPK."""
    
    extDir = Path(f"_DYextracted/{upkName}")
    
    if not extDir.exists():
        raise Exception(f"_DYextracted/{upkName} not found")
    
    # Load _names.txt for dNames
    namesPath = Path(f"_DYextracted/{upkName}/_names.txt")
    with open(namesPath, 'r', encoding='latin-1') as f:
        dNames = [line.strip() for line in f.readlines()]
    
    # Load YAML
    with open(yamlPath, 'r', encoding='utf-8') as f:
        yod = yaml.safe_load(f)
    
    print(f"Patching {len(yod)} entries...")
    
    # Patch each file in _DYextracted
    isINT = (langCode == "INT")
    patched = 0
    errors = 0
    
    for yamlKey, newText in yod.items():
        disconvFile = extDir / yamlKey
        if not disconvFile.exists():
            print(f"Warning: {yamlKey} not found")
            errors += 1
            continue
        
        fileSize = os.stat(disconvFile).st_size
        
        with open(disconvFile, "r+b") as fileObj:
            reader = BinaryStream(fileObj)
            reader.seek(0)
            e = UpkElements(dNames, reader)
            
            plChoice = False
            if "m_Choices_Static" in e.elements.keys():
                text = e.elements["m_Choices_Static"]
                plChoice = True
            elif "m_Text" in e.elements.keys():
                text = e.elements["m_Text"]
            else:
                errors += 1
                continue
            
            fileData = b''
            
            if isINT:
                textVal = text['value']
                reader.seek(0)
                pStr = newText
                if plChoice:
                    for a in range(len(textVal)):
                        t = textVal[a]['m_ChoiceText'][0]
                        if a == 0:
                            fileData += reader.readBytes(t[1])
                        eStr = pStr[a].encode("utf-16le")
                        lStr = len(pStr[a]) + 1
                        lStr = lStr * -1
                        eStr += b"\x00\x00"
                        fileData += struct.pack("i", lStr)
                        fileData += eStr
                        reader.seek(t[2])
                        if a == len(textVal)-1:
                            fileData += reader.readBytes(fileSize - reader.offset())
                        else:
                            fileData += reader.readBytes(textVal[a+1]['m_ChoiceText'][1] - reader.offset())
                else:
                    fileData += reader.readBytes(textVal[1])
                    try:
                        eStr = pStr.encode("ISO-8859-1")
                        lStr = len(pStr) + 1
                        eStr += b"\x00"
                    except:
                        eStr = pStr.encode("utf-16le")
                        lStr = len(pStr) + 1
                        lStr = lStr * -1
                        eStr += b"\x00\x00"
                    fileData += struct.pack("i", lStr)
                    fileData += eStr
                    cutLen = reader.readInt32()
                    if cutLen < 0:
                        cutLen = cutLen * -2
                    reader.readBytes(cutLen)
                    fileData += reader.readBytes(fileSize - reader.offset())
            else:
                langs = e.resolveLang(e.endOffset)
                if langs[0]['Count'] == 0:
                    errors += 1
                    continue
                textArr = []
                for l in range(len(langs)):
                    textArr.append(langs[l]['langs'][langCode][0])
                
                reader.seek(0)
                pStr = newText
                fileData += reader.readBytes(textArr[0][0])
                for i in range(len(textArr)):
                    if isinstance(pStr, list):
                        eStr = pStr[i].encode("utf-16le")
                        lStr = len(pStr[i]) + 1
                    else:
                        eStr = pStr.encode("utf-16le")
                        lStr = len(pStr) + 1
                    lStr = lStr * -1
                    eStr += b"\x00\x00"
                    fileData += struct.pack("i", lStr)
                    fileData += eStr
                    reader.seek(textArr[i][2])
                    if i == len(textArr)-1:
                        fileData += reader.readBytes(fileSize - reader.offset())
                    else:
                        fileData += reader.readBytes(textArr[i+1][0] - reader.offset())
            
            # Write to _DYpatched
            newFile = str(disconvFile).replace("_DYextracted", "_DYpatched") + "_patched"
            Path(newFile).parent.mkdir(parents=True, exist_ok=True)
            with open(newFile, "wb") as modded:
                modded.write(fileData)
            
            patched += 1
    
    print(f"Patched {patched} files, {errors} errors")
    
    # Now repack using patch()
    # Find original UPK path
    upkPath = None
    for base in [
        "F:/SteamLibrary/steamapps/common/Dishonored/DishonoredGame/CookedPCConsole/",
        "E:/Mod_Workspace/Dishonored_Mod_Workspace/03_working/CookedPCConsole/",
    ]:
        test = Path(base) / f"{upkName}.upk"
        if test.exists():
            upkPath = test
            break
    
    if upkPath is None:
        raise Exception(f"Could not find UPK: {upkName}.upk")
    
    print(f"Packing {upkName}.upk...")
    patch(upkPath, False, addDir=upkName, silent=True, end=True)
    
    print("Done!")
    return patched


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python pack_thai.py <upk_name> <yaml_path> <output_upk> [langCode]")
        sys.exit(1)
    
    upkName = sys.argv[1]
    yamlPath = sys.argv[2]
    outputUpk = sys.argv[3]
    langCode = sys.argv[4] if len(sys.argv) > 4 else "TH"
    
    try:
        patched = patch_and_pack(upkName, yamlPath, langCode)
        print(f"Successfully patched {patched} entries")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
