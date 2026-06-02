#!/usr/bin/env python3
"""
Build a new uncompressed UPK from _DYextracted DisConv files.
"""
import sys
import struct
import os
from pathlib import Path

TOOLKIT = Path(__file__).parent.parent
sys.path.insert(0, str(TOOLKIT))
sys.path.insert(0, str(TOOLKIT / "_original"))

import yaml
from upkElements import UpkElements
from binary import BinaryStream


def build_uncompressed_upk(upkName, yamlPath, outputUpk, langCode="INT"):
    """
    Build a new uncompressed UPK from extracted DisConv files.
    """
    extDir = Path(f"_DYextracted/{upkName}")
    
    if not extDir.exists():
        raise Exception(f"_DYextracted/{upkName} not found")
    
    # Load YAML
    with open(yamlPath, 'r', encoding='utf-8') as f:
        yamlData = yaml.safe_load(f)
    
    print(f"Building UPK with {len(yamlData)} entries...")
    
    # Load _names.txt
    namesPath = extDir / "_names.txt"
    with open(namesPath, 'r', encoding='latin-1') as f:
        dNames = [line.strip() for line in f.readlines()]
    
    # Load _header
    headerPath = extDir / "_header"
    with open(headerPath, 'rb') as f:
        headerData = f.read()
    
    # Load _objects.txt
    objsPath = extDir / "_objects.txt"
    with open(objsPath, 'r') as f:
        objLines = [line.strip() for line in f.readlines() if line.strip()]
    
    # Parse objects.txt
    objMap = {}
    for line in objLines:
        parts = line.split(';')
        if len(parts) < 5:
            continue
        filename = parts[0].strip()
        sizeOff = int(parts[1].strip())
        size = int(parts[2].strip())
        dataOff = int(parts[3].strip())
        offset = int(parts[4].strip())
        objMap[offset] = (filename, size, dataOff)
    
    # Build new UPK
    newUpk = bytearray(headerData)
    
    patchedCount = 0
    errorCount = 0
    
    for yamlKey, newText in yamlData.items():
        disconvFile = extDir / yamlKey
        if not disconvFile.exists():
            errorCount += 1
            continue
        
        # Find object entry
        objEntry = None
        for offset, (filename, size, dataOff) in objMap.items():
            if filename == yamlKey:
                objEntry = (offset, size, dataOff)
                break
        
        if objEntry is None:
            errorCount += 1
            continue
        
        offset, origSize, dataOff = objEntry
        
        # Parse and patch
        with open(disconvFile, 'r+b') as f:
            reader = BinaryStream(f)
            reader.seek(0)
            e = UpkElements(dNames, reader)
            
            plChoice = False
            if "m_Choices_Static" in e.elements.keys():
                text = e.elements["m_Choices_Static"]
                plChoice = True
            elif "m_Text" in e.elements.keys():
                text = e.elements["m_Text"]
            else:
                errorCount += 1
                continue
            
            isINT = (langCode == "INT")
            fileData = b''
            
            if isINT:
                textVal = text['value']
                if plChoice:
                    for a in range(len(textVal)):
                        t = textVal[a]['m_ChoiceText'][0]
                        if a == 0:
                            fileData += reader.readBytes(t[1])
                        if isinstance(newText, list):
                            eStr = newText[a].encode("ISO-8859-1")
                            lStr = len(newText[a]) + 1
                        else:
                            eStr = newText.encode("ISO-8859-1")
                            lStr = len(newText) + 1
                        eStr += b"\x00"
                        fileData += struct.pack("i", lStr)
                        fileData += eStr
                        reader.seek(t[2])
                        if a == len(textVal)-1:
                            fileData += reader.readBytes(origSize - reader.offset())
                        else:
                            fileData += reader.readBytes(textVal[a+1]['m_ChoiceText'][1] - reader.offset())
                else:
                    fileData += reader.readBytes(textVal[1])
                    eStr = newText.encode("ISO-8859-1")
                    lStr = len(newText) + 1
                    eStr += b"\x00"
                    fileData += struct.pack("i", lStr)
                    fileData += eStr
                    cutLen = reader.readInt32()
                    if cutLen < 0:
                        cutLen = cutLen * -2
                    reader.readBytes(cutLen)
                    fileData += reader.readBytes(origSize - reader.offset())
            else:
                langs = e.resolveLang(e.endOffset)
                if langs[0]['Count'] == 0:
                    errorCount += 1
                    continue
                textArr = []
                for l in range(len(langs)):
                    textArr.append(langs[l]['langs'][langCode][0])
                
                reader.seek(0)
                fileData += reader.readBytes(textArr[0][0])
                for i in range(len(textArr)):
                    if isinstance(newText, list):
                        eStr = newText[i].encode("utf-16le")
                        lStr = len(newText[i]) + 1
                    else:
                        eStr = newText.encode("utf-16le")
                        lStr = len(newText) + 1
                    lStr = lStr * -1
                    eStr += b"\x00\x00"
                    fileData += struct.pack("i", lStr)
                    fileData += eStr
                    reader.seek(textArr[i][2])
                    if i == len(textArr)-1:
                        fileData += reader.readBytes(origSize - reader.offset())
                    else:
                        fileData += reader.readBytes(textArr[i+1][0] - reader.offset())
        
        # Write patched data at offset
        if offset + len(fileData) > len(newUpk):
            newUpk.extend(b'\x00' * (offset + len(fileData) - len(newUpk) + 10000))
        
        for i, b in enumerate(fileData):
            newUpk[offset + i] = b
        
        patchedCount += 1
    
    print(f"Patched {patchedCount} entries, {errorCount} errors")
    
    # Write output
    Path(outputUpk).parent.mkdir(parents=True, exist_ok=True)
    with open(outputUpk, 'wb') as f:
        f.write(bytes(newUpk))
    
    print(f"Written: {outputUpk} ({len(newUpk)} bytes)")
    return len(newUpk)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python build_upk.py <upk_name> <yaml_path> <output_upk> [langCode]")
        sys.exit(1)
    
    upkName = sys.argv[1]
    yamlPath = sys.argv[2]
    outputUpk = sys.argv[3]
    langCode = sys.argv[4] if len(sys.argv) > 4 else "INT"
    
    try:
        build_uncompressed_upk(upkName, yamlPath, outputUpk, langCode)
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
