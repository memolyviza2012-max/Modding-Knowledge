#!/usr/bin/env python3
"""
Fixed subedit for Dishonored - uses LITTLE-ENDIAN for ALL header fields (same as original subedit.py).
The fix is in how BinaryStream interacts with file objects.
"""
import os
import sys
import struct
from pathlib import Path

sys.path.insert(0, '.')

import yaml
from upkElements import UpkElements
from binary import BinaryStream

dir = "_DYextracted"


def read_upk(filepath, silent=False, split=False):
    """Read UPK header correctly."""
    from upkCompressor import DYCompressor
    
    if not filepath.is_file():
        raise Exception("File not found")

    sign_upk = 0x9E2A83C1
    
    ff = filepath.stem
    outDir = "_DYextracted"
    if split:
        outDir = f"{outDir}/{ff}"

    with open(filepath, "rb") as f:
        data = bytearray(f.read())
    
    # Signature (bytes 0-3) - LITTLE-ENDIAN
    sig = struct.unpack('<I', data[0:4])[0]
    if sig != sign_upk:
        raise Exception(f"Signature mismatch: got 0x{sig:08X}, expected 0x{sign_upk:08X}")
    
    # After signature: LITTLE-ENDIAN
    o = 4
    pkgVersion = struct.unpack('<H', data[o:o+2])[0]; o += 2
    pkgLVersion = struct.unpack('<H', data[o:o+2])[0]; o += 2
    headerSize = struct.unpack('<I', data[o:o+4])[0]; o += 4
    folderLen = struct.unpack('<I', data[o:o+4])[0]; o += 4
    folderStr = data[o:o+folderLen]; o += folderLen
    o += 4  # pkgFlags
    nameCount = struct.unpack('<I', data[o:o+4])[0]; o += 4
    nameOffset = struct.unpack('<I', data[o:o+4])[0]; o += 4
    exportCount = struct.unpack('<I', data[o:o+4])[0]; o += 4
    exportOffset = struct.unpack('<I', data[o:o+4])[0]; o += 4
    importCount = struct.unpack('<I', data[o:o+4])[0]; o += 4
    importOffset = struct.unpack('<I', data[o:o+4])[0]; o += 4
    dependsOffset = struct.unpack('<I', data[o:o+4])[0]; o += 4
    somedata1 = struct.unpack('<I', data[o:o+4])[0]; o += 4
    
    # UNKNOWN x3 (12 bytes)
    for _ in range(3):
        struct.unpack('<I', data[o:o+4])[0]; o += 4
    
    # GUID x4 (16 bytes)
    for _ in range(4):
        struct.unpack('<I', data[o:o+4])[0]; o += 4
    
    genCount = struct.unpack('<I', data[o:o+4])[0]; o += 4
    
    for i in range(genCount):
        for _ in range(3):
            struct.unpack('<I', data[o:o+4])[0]; o += 4
    
    engineVer = struct.unpack('<I', data[o:o+4])[0]; o += 4
    cookerVer = struct.unpack('<I', data[o:o+4])[0]; o += 4
    compFlags = struct.unpack('<I', data[o:o+4])[0]; o += 4
    
    compressor = DYCompressor(compFlags)
    ctype = compressor.getCompression()
    
    if not silent:
        print(f"Package version: {pkgVersion}")
        print(f"Package License version: {pkgLVersion}")
        print(f"Engine version: {engineVer}")
        print(f"Cooker version: {cookerVer}")
        print(f"Compression: {ctype}")
        print(f"nameCount: {nameCount}, exportCount: {exportCount}, importCount: {importCount}")
        print(f"nameOffset: 0x{nameOffset:08X}, exportOffset: 0x{exportOffset:08X}")
        print(f"headerSize: {headerSize}")
    
    if ctype != "None":
        raise Exception("Compressed files not support yet\nPlease use Unreal Package Decompressor")
    
    # Build name table
    names = []
    namesOffsets = []
    decodedNames = []
    no = nameOffset
    for i in range(nameCount):
        namesOffsets.append(no)
        nameLen = struct.unpack('<I', data[no:no+4])[0]; no += 4
        n = data[no:no+nameLen]; no += nameLen
        names.append(n)
        decodedNames.append(n.decode("ISO-8859-1").replace('\x00', ''))
        # 2 x UNKNOWN
        struct.unpack('<I', data[no:no+4])[0]; no += 4
        struct.unpack('<I', data[no:no+4])[0]; no += 4
    
    names.append(b"NULL\x00")
    
    # Build exports table
    exports = []
    eo = exportOffset
    for i in range(exportCount):
        export = {}
        export["ObjTypeRef"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["ParentClassRef"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["OwnerRef"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["NameListIdx"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field5"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field6"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["PropertyFlags"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field8"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["ObjectFileSizeOff"] = eo; eo += 4
        export["ObjectFileSize"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["DataOffsetOff"] = eo; eo += 4
        export["DataOffset"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field11"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["NumAdditionalFields"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field13"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field14"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field15"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field16"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        export["Field17"] = struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        for j in range(export["NumAdditionalFields"]):
            struct.unpack('<I', data[eo:eo+4])[0]; eo += 4
        exports.append(export)
    
    # Build imports table
    imports = []
    io = importOffset
    for i in range(importCount):
        _import = {}
        _import["PackageID"] = struct.unpack('<I', data[io:io+4])[0]; io += 4
        _import["unknown1"] = struct.unpack('<I', data[io:io+4])[0]; io += 4
        _import["ObjTypeIdx"] = struct.unpack('<I', data[io:io+4])[0]; io += 4
        _import["unknown2"] = struct.unpack('<I', data[io:io+4])[0]; io += 4
        _import["OwnerRef"] = struct.unpack('<I', data[io:io+4])[0]; io += 4
        _import["NameListIdx"] = struct.unpack('<I', data[io:io+4])[0]; io += 4
        _import["unknown3"] = struct.unpack('<I', data[io:io+4])[0]; io += 4
        imports.append(_import)
    
    data_list = []
    for e in exports:
        _objName = names[e["NameListIdx"]]
        _objSize = e["ObjectFileSize"]
        _objOffset = e["DataOffset"]
        _objType = e["ObjTypeRef"]
        
        if _objType < 0:
            _objType = names[imports[-_objType-1]["NameListIdx"]].decode("utf-8").replace("\x00", "")
        elif _objType > 0:
            _objType = names[exports[_objType-1]["NameListIdx"]].decode("utf-8").replace("\x00", "")
        else:
            _objType = "NULL"
        
        data_list.append({
            "FileName": _objName,
            "Type": _objType,
            "Size": _objSize,
            "Offset": _objOffset,
            "SizeOff": e["ObjectFileSizeOff"],
            "DataOff": e["DataOffsetOff"],
        })
    
    data_list.sort(key=lambda item: item["Offset"])
    
    return {
        "data": data_list,
        "imports": imports,
        "exports": exports,
        "dir": outDir,
        "headerSize": headerSize,
        "names": names,
        "dNames": decodedNames,
    }


def unpack_objects(filepath, namefilter=None, split=False, silent=False):
    """Extract objects from UPK."""
    rr = read_upk(filepath, silent, split)
    data = rr["data"]
    outDir = rr["dir"]
    headerSize = rr["headerSize"]
    
    if not silent:
        print("Objects:")
    
    os.makedirs(outDir, exist_ok=True)
    
    if os.path.isfile(f"{outDir}/_objects.txt"):
        os.remove(f"{outDir}/_objects.txt")
    
    # Write header
    with open(filepath, "rb") as f:
        header = f.read(headerSize)
    with open(f"{outDir}/_header", "wb") as hf:
        hf.write(header)
    
    with open(filepath, "rb") as f:
        full_data = f.read()
    
    objid = 0
    for obj in data:
        objFileName = obj["FileName"].decode("utf-8").replace('\x00', '')
        objSize = obj["Size"]
        objOffset = obj["Offset"]
        objType = obj["Type"]
        
        skip = False
        if namefilter is not None:
            if objFileName.find(namefilter) == -1:
                skip = True
        
        objFileName += f".{objid}"
        if not skip:
            p = f"{outDir}/{objFileName}.{objType}"
            if not silent:
                print(f"- {objFileName}\n  type: {objType}\n  size: {objSize}\n  offset: {objOffset}")
            
            with open(p, "wb") as objFile:
                objFile.write(full_data[objOffset:objOffset+objSize])
        
        with open(f"{outDir}/_objects.txt", "a") as objFile:
            objFile.write(f"{objFileName}.{objType}; {obj['SizeOff']}; {objSize}; {obj['DataOff']}; {objOffset}\n")
        
        objid += 1
    
    with open(f"{outDir}/_names.txt", "w") as namesFile:
        for l in rr["names"]:
            namesFile.write(l.decode("ISO-8859-1").replace("\x00", "") + "\n")
    
    return rr


def unpackYaml(fp, outYaml, lang=None):
    print("\x1b[6;30;42m-- Subtitle extractor --\x1b[0m")

    isINT = False
    if lang is None:
        lang = "INT"

    if lang == "INT":
        isINT = True

    if outYaml is None:
        print("\x1b[6;30;41mErr: output yaml not provided\x1b[0m")
        return

    if not os.path.isdir(dir):
        os.mkdir(dir)

    if os.path.isfile(outYaml):
        os.remove(outYaml)

    rr = unpack_objects(fp, "DisConv_", True, True)

    types = ("DisConv_Blurb*", "DisConv_PlayerChoice*", "DisConv_NonWord*")
    files = []
    ff = str(fp).rsplit("/", 1)[1] if "/" in str(fp) else str(fp).rsplit("\\", 1)[1]
    fname = ff.rsplit(".", 1)[0]

    for type in types:
        files.extend(Path(f"_DYextracted/{fname}").glob(type))

    od = {}

    for subFile in files:
        name = os.path.basename(subFile)
        with open(subFile, "r+b") as fileObj:
            reader = BinaryStream(fileObj)
            reader.seek(0)
            e = UpkElements(rr["dNames"], reader)
            plChoice = False

            if "m_Choices_Static" in e.elements.keys():
                text = e.elements["m_Choices_Static"]
                plChoice = True
            elif "m_Text" in e.elements.keys():
                text = e.elements["m_Text"]
            else:
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
                    textVal = textVal[0].replace('\x00', '').strip()
                od[name] = textVal
            else:
                langs = e.resolveLang(e.endOffset)
                if langs[0]["Count"] == 0:
                    continue
                textArr = []
                for l in range(len(langs)):
                    textArr.append(langs[l]["langs"][lang][0][1].replace('\x00', '').strip())
                if len(textArr) == 1:
                    textArr = textArr[0]
                od[name] = textArr

    with open(outYaml, "w", encoding="utf8") as yf:
        yaml.dump(od, yf, allow_unicode=True, width=4096)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Subtitle extractor (Dishonored - Fixed)')
    parser.add_argument("filename", help="File to extract")
    parser.add_argument("-o", "--output", help="Output yaml file")
    parser.add_argument("--langCode", help="Language code", default="INT")
    args = parser.parse_args()

    fp = Path(args.filename)
    outYaml = Path(args.output) if args.output else None

    try:
        unpackYaml(fp, outYaml, args.langCode)
        print("\x1b[6;30;42m-- DONE --\x1b[0m")
    except Exception as e:
        print(f"\x1b[6;30;41mError: {e}\x1b[0m")
        import traceback
        traceback.print_exc()
