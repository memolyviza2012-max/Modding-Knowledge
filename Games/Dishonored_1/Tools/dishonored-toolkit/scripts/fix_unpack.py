#!/usr/bin/env python3
"""
Decompress a LZO-compressed UPK file and write decompressed version to _DYuncompressed/.
Then extract DisConv dialogue as YAML.
"""
import sys
import os
import lzo
from pathlib import Path

sys.path.insert(0, '.')
from binary import BinaryStream

def decompress_upk(filepath):
    """Decompress LZO-compressed UPK to uncompressed bytes."""
    with open(filepath, 'rb') as f:
        raw = f.read()
    
    sign_be = int.from_bytes(raw[0:4], 'big')
    sign_le = int.from_bytes(raw[0:4], 'little')
    expected = 0x9e2a83c1
    
    is_be = (sign_be == expected)
    is_le = (sign_le == expected)
    
    if not is_be and not is_le:
        raise Exception(f"Signature mismatch: {hex(sign_be)}/{hex(sign_le)} vs {hex(expected)}")
    
    if is_le:
        # File is little-endian, byteswap everything
        data = bytearray(raw)
        for i in range(0, len(data), 4):
            data[i:i+4] = data[i:i+4][::-1]
        raw = bytes(data)
        sign = sign_be  # After byteswap, read as big-endian
    else:
        sign = sign_be
    
    # Parse header (big-endian)
    pos = 4
    pkgVersion = int.from_bytes(raw[pos:pos+2], 'big'); pos += 2
    pkgLVersion = int.from_bytes(raw[pos:pos+2], 'big'); pos += 2
    headerSize = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    folderLen = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    folderStr = raw[pos:pos+folderLen]; pos += folderLen
    pkgFlags = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    nameCount = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    nameOffset = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    exportCount = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    exportOffset = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    importCount = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    importOffset = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    dependsOffset = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    somedata1 = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    guid = raw[pos:pos+16]; pos += 16
    genCount = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    for _ in range(genCount):
        pos += 12  # 3 x uint32
    engineVer = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    cookerVer = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    compFlags = int.from_bytes(raw[pos:pos+4], 'big'); pos += 4
    
    # Determine compression type
    # compFlags value for LZO is typically 2
    ctype_map = {0: "None", 1: "ZLIB", 2: "LZO", 4: "LZX"}
    ctype = ctype_map.get(compFlags & 0xF, f"Unknown({compFlags})")
    
    print(f"  Package version: {pkgVersion}")
    print(f"  Header size: {headerSize}")
    print(f"  Compression: {ctype} (flags={compFlags})")
    
    if ctype == "None":
        print("  File is not compressed")
        return raw
    
    # Find chunk table after header
    chunkStart = headerSize
    reader_pos = chunkStart
    chunks = []
    
    while reader_pos < len(raw) - 16:
        uOffset = int.from_bytes(raw[reader_pos:reader_pos+4], 'big')
        uSize = int.from_bytes(raw[reader_pos+4:reader_pos+8], 'big')
        cOffset = int.from_bytes(raw[reader_pos+8:reader_pos+12], 'big')
        cSize = int.from_bytes(raw[reader_pos+12:reader_pos+16], 'big')
        reader_pos += 16
        
        if uOffset == 0 and uSize == 0 and cOffset == 0 and cSize == 0:
            break
        if uOffset >= len(raw) or cOffset >= len(raw):
            break
        chunks.append({'uOffset': uOffset, 'uSize': uSize, 'cOffset': cOffset, 'cSize': cSize})
    
    print(f"  Found {len(chunks)} compressed chunks")
    
    # Build uncompressed data
    uncompressed = bytearray(headerSize)  # header stays as-is (raw)
    
    for chunk in chunks:
        cData = raw[chunk['cOffset']:chunk['cOffset']+chunk['cSize']]
        try:
            dec = lzo.decompress(cData)
        except Exception as e:
            print(f"  LZO failed for chunk at cOffset={chunk['cOffset']}: {e}")
            # Try with header stripped (first 12 bytes)
            if len(cData) > 12:
                dec = lzo.decompress(cData[12:])
            else:
                dec = lzo.decompress(cData)
        uncompressed += dec
    
    return bytes(uncompressed)


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python fix_unpack.py <upk_file> <output_yaml> <langCode>")
        sys.exit(1)
    
    fp = Path(sys.argv[1])
    output = Path(sys.argv[2])
    langCode = sys.argv[3]
    
    print(f"Unpacking {fp}")
    print(f"Language: {langCode}")
    
    # Step 1: Decompress if needed
    data = decompress_upk(fp)
    
    # Step 2: Write decompressed UPK
    outDir = Path("_DYuncompressed")
    outDir.mkdir(exist_ok=True)
    decompPath = outDir / fp.name
    with open(decompPath, 'wb') as f:
        f.write(data)
    print(f"  Decompressed UPK written to: {decompPath} ({len(data)} bytes)")
    
    # Step 3: Now unpack the decompressed UPK
    print(f"  Extracting DisConv to YAML...")
    os.chdir(Path(sys.argv[0]).parent)
    
    from subedit import unpackYaml
    
    # Extract
    upkName = fp.stem
    rr = unpack(decompPath, "DisConv_", True, True)
    
    from pathlib import Path
    types = ('DisConv_Blurb*', 'DisConv_PlayerChoice*', 'DisConv_NonWord*')
    files = []
    for fp_t in types:
        files.extend(Path(f"_DYextracted/{upkName}").glob(fp_t))
    
    od = {}
    from upkElements import UpkElements
    
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
                print(f"  Notice: {name} has no text")
                continue
            
            if langCode == "INT":
                textVal = text['value']
                if plChoice:
                    texVal = []
                    for a in range(len(textVal)):
                        textVal = text['value']
                        texVal.append(textVal[a]['m_ChoiceText'][0][0].replace('\x00', '').strip())
                    textVal = texVal
                else:
                    textVal = textVal[0].replace('\x00', '').strip()
                od[name] = textVal
            else:
                langs = e.resolveLang(e.endOffset)
                if langs[0]['Count'] == 0:
                    print(f"  Notice: {name} has no translateble text")
                    continue
                textArr = []
                for l in range(len(langs)):
                    textArr.append(langs[l]['langs'][langCode][0][1].replace('\x00','').strip())
                if len(textArr) == 1:
                    textArr = textArr[0]
                od[name] = textArr
    
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf8") as yf:
        import yaml
        yaml.dump(od, yf, allow_unicode=True, width=4096)
    
    print(f"  YAML written to: {output}")
    print("Done!")
