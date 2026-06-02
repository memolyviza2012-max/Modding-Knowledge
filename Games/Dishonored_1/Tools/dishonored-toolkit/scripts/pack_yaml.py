#!/usr/bin/env python3
"""
Pack Thai YAML back into UPK.
Uses _DYextracted folder (already extracted) and _names.txt.
"""
import os
import sys
import struct
import yaml
from pathlib import Path

sys.path.insert(0, '.')

from upkElements import UpkElements
from binary import BinaryStream


def pack_yaml(upkName, yamlPath, outputUpk, langCode="TH"):
    """Pack Thai YAML into UPK using extracted files."""
    from patch import patch
    from upkreader import readerGet
    
    extDir = Path(f"_DYextracted/{upkName}")
    
    if not extDir.exists():
        raise Exception(f"_DYextracted/{upkName} not found")
    
    # Load _names.txt for dNames
    namesPath = Path(f"_DYextracted/{upkName}/_names.txt")
    with open(namesPath, 'r', encoding='latin-1') as f:
        dNames = [line.strip() for line in f.readlines()]
    
    # Load YAML
    with open(yamlPath, 'r', encoding='utf-8') as f:
        yamlData = yaml.safe_load(f)
    
    print(f"Packing {len(yamlData)} entries from {yamlPath}")
    
    # For each DisConv file, patch the Thai text
    patched = 0
    errors = 0
    
    for yamlKey, thText in yamlData.items():
        disconvFile = extDir / yamlKey
        if not disconvFile.exists():
            print(f"Warning: {yamlKey} not found in _DYextracted")
            errors += 1
            continue
        
        # Read the binary file
        with open(disconvFile, 'r+b') as f:
            reader = BinaryStream(f)
            reader.seek(0)
            
            # Parse with UpkElements
            e = UpkElements(dNames, reader)
            
            if "m_Text" in e.elements:
                # Simple text - patch it
                try:
                    e.elements["m_Text"]["value"] = [thText + "\x00"]
                    e.apply()
                    patched += 1
                except Exception as ex:
                    print(f"Error patching {yamlKey}: {ex}")
                    errors += 1
            elif "m_Choices_Static" in e.elements:
                # Player choice - handle list
                try:
                    orig = e.elements["m_Choices_Static"]["value"]
                    if isinstance(orig, list) and len(orig) > 0:
                        if isinstance(thText, list):
                            for i, txt in enumerate(thText):
                                if i < len(orig):
                                    orig[i]["m_ChoiceText"][0][0] = txt + "\x00"
                        else:
                            orig[0]["m_ChoiceText"][0][0] = thText + "\x00"
                        e.elements["m_Choices_Static"]["value"] = orig
                        e.apply()
                        patched += 1
                except Exception as ex:
                    print(f"Error patching choices {yamlKey}: {ex}")
                    errors += 1
            else:
                errors += 1
    
    print(f"Patched {patched} entries, {errors} errors")
    
    # Now repack into UPK
    # Load original UPK header
    upkPath = Path(f"_DYextracted/{upkName}/_header")
    if not upkPath.exists():
        raise Exception(f"_header not found for {upkName}")
    
    with open(upkPath, 'rb') as f:
        header = f.read()
    
    # Load full original UPK for export data
    origUpkPath = None
    for base in [
        "F:/SteamLibrary/steamapps/common/Dishonored/DishonoredGame/CookedPCConsole/",
    ]:
        test = Path(base) / f"{upkName}.upk"
        if test.exists():
            origUpkPath = test
            break
    
    if origUpkPath is None:
        raise Exception(f"Could not find original UPK for {upkName}")
    
    with open(origUpkPath, 'rb') as f:
        origData = f.read()
    
    # Build new UPK: header + patched objects + original compressed data
    # For compressed UPKs, we need to keep the compressed chunks
    # The _DYextracted folder has the individual object files
    
    # Read header info
    sig = struct.unpack('<I', header[0:4])[0]
    if sig != 0x9E2A83C1:
        raise Exception(f"Bad signature: 0x{sig:08X}")
    
    # Parse header to get exportCount, exportOffset, etc.
    o = 4
    pkgVersion = struct.unpack('<H', header[o:o+2])[0]; o += 2
    pkgLVersion = struct.unpack('<H', header[o:o+2])[0]; o += 2
    headerSize = struct.unpack('<I', header[o:o+4])[0]; o += 4
    
    print(f"Header size: {headerSize}")
    
    # For compressed UPKs, we need to decompress first, then recompress
    # But we don't have working LZO decompressor...
    # Instead, let's use the _DYextracted folder directly
    
    # Build new UPK from extracted files
    # Read _objects.txt to understand the structure
    objsPath = Path(f"_DYextracted/{upkName}/_objects.txt")
    if objsPath.exists():
        with open(objsPath, 'r') as f:
            objLines = [line.strip() for line in f.readlines() if line.strip()]
    
    # The output will be a COPY of the original UPK with patched DisConv files
    # Read the original UPK
    with open(origUpkPath, 'rb') as f:
        upkData = bytearray(f.read())
    
    # We need to find the DataOffset for each DisConv object and replace
    # Each object in _DYextracted was extracted from the UPK
    # We need to find its offset in the original UPK
    
    # Parse _objects.txt format:
    # filename.ObjType; SizeOff; Size; DataOff; Offset
    
    replacements = {}
    for line in objLines:
        parts = line.split(';')
        if len(parts) < 5:
            continue
        
        filename = parts[0].strip()
        sizeOff = int(parts[1].strip())
        size = int(parts[2].strip())
        dataOff = int(parts[3].strip())
        offset = int(parts[4].strip())
        
        # Check if this is a DisConv file we have patched
        if filename in yamlData:
            extFile = extDir / filename
            if extFile.exists():
                newData = extFile.read_bytes()
                if len(newData) <= size:
                    replacements[offset] = (newData, size, offset)
    
    print(f"Found {len(replacements)} objects to replace")
    
    # Apply replacements
    for offset, (newData, origSize, off) in replacements.items():
        if offset < len(upkData):
            # Copy new data into UPK
            for i, b in enumerate(newData):
                upkData[offset + i] = b
            # Pad remaining space with zeros
            for i in range(len(newData), origSize):
                if offset + i < len(upkData):
                    upkData[offset + i] = 0
    
    # Write output
    Path(outputUpk).parent.mkdir(parents=True, exist_ok=True)
    with open(outputUpk, 'wb') as f:
        f.write(upkData)
    
    print(f"Packed UPK written to: {outputUpk} ({len(upkData)} bytes)")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python pack_yaml.py <upk_name> <yaml_path> <output_upk> [langCode]")
        sys.exit(1)
    
    upkName = sys.argv[1]
    yamlPath = sys.argv[2]
    outputUpk = sys.argv[3]
    langCode = sys.argv[4] if len(sys.argv) > 4 else "TH"
    
    try:
        pack_yaml(upkName, yamlPath, outputUpk, langCode)
        print("Done!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
