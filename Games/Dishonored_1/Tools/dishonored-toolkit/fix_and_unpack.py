#!/usr/bin/env python3
"""
Decompress a LZO-compressed UPK and extract DisConv dialogues as YAML.
Fixes upkreader.py to handle compressed files.
"""
import sys
import os
import lzo
from pathlib import Path

sys.path.insert(0, '.')
from binary import BinaryStream
from upkCompressor import DYCompressor

def decompress_upk(filepath):
    """Decompress LZO-compressed UPK to uncompressed bytes."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    sign = int.from_bytes(data[0:4], 'little')
    expected_sign = int.from_bytes(bytes([158, 42, 131, 193]), 'little')
    
    if sign != expected_sign:
        raise Exception(f"Signature mismatch: {hex(sign)} vs {hex(expected_sign)}")
    
    # Parse header to find compression info
    # header layout (after signature):
    # [0:4] signature (already read)
    # [4:6] pkgVersion
    # [6:8] pkgLVersion
    # [8:12] headerSize
    # [12:16] folderLen
    # [16:16+folderLen] folderStr
    # ... rest of header ...
    # At offset ~88: compressionFlags
    
    pkgVersion = int.from_bytes(data[4:6], 'little')
    pkgLVersion = int.from_bytes(data[6:8], 'little')
    headerSize = int.from_bytes(data[8:12], 'little')
    folderLen = int.from_bytes(data[12:16], 'little')
    folderStr = data[16:16+folderLen]
    
    # Find compression flags (after engineVer + cookerVer)
    # Approximate: after signature(4) + pkgVer(2) + pkgLVer(2) + headerSize(4) + folderLen(4) + folder + pkgFlags(4) + nameCount(4) + nameOffset(4) + exportCount(4) + exportOffset(4) + importCount(4) + importOffset(4) + dependsOffset(4) + somedata1(4) + guid(16) + genCount(4) + genArr + engineVer(4) + cookerVer(4)
    # That's roughly 4+2+2+4+4+folderLen+4+4+4+4+4+4+4+4+16+4 = 68+folderLen
    # Then + genArr (each gen entry has 3*4 = 12 bytes)
    
    # Actually let me just search for the compression type marker
    # After signature 0x9e2a83c1, the compression flags are at specific offset
    # Let's use a simpler approach: read from the known position
    
    offset = 4  # after signature
    offset += 2   # pkgVersion
    offset += 2   # pkgLVersion
    offset += 4   # headerSize
    offset += 4   # folderLen
    offset += folderLen
    offset += 4   # pkgFlags
    offset += 4   # nameCount
    offset += 4   # nameOffset
    offset += 4   # exportCount
    offset += 4   # exportOffset
    offset += 4   # importCount
    offset += 4   # importOffset
    offset += 4   # dependsOffset
    offset += 4   # somedata1
    offset += 16  # guid
    offset += 4   # genCount
    
    # Read genArr
    genCount = int.from_bytes(data[offset-4:offset], 'little') if offset >= 4 else 0
    offset += genCount * 12  # 3 int32 per gen entry
    
    offset += 4   # engineVer
    offset += 4   # cookerVer
    compFlags = int.from_bytes(data[offset:offset+4], 'little')
    
    print(f"Compression flags: {compFlags}")
    compressor = DYCompressor(compFlags)
    ctype = compressor.getCompression()
    print(f"Compression type: {ctype}")
    
    if ctype == "None":
        print("File is not compressed, no need to decompress")
        return data
    
    # Find compressed chunks
    # After header, at the offset where data starts
    # In compressed files, the data section has chunk table
    chunkTableOffset = headerSize
    
    reader = BinaryStream(open(filepath, 'rb'))
    reader.seek(chunkTableOffset)
    
    chunks = []
    while True:
        pos = reader.offset()
        if pos >= len(data):
            break
        try:
            uOffset = reader.readInt32()
            uSize = reader.readInt32()
            cOffset = reader.readInt32()
            cSize = reader.readInt32()
            if uOffset == 0 and uSize == 0 and cOffset == 0 and cSize == 0:
                break
            chunks.append({'uOffset': uOffset, 'uSize': uSize, 'cOffset': cOffset, 'cSize': cSize})
            print(f"Chunk: uOffset={uOffset}, uSize={uSize}, cOffset={cOffset}, cSize={cSize}")
        except:
            break
    
    # Reconstruct uncompressed data
    # The uncompressed data starts at headerSize and goes for uSize total
    uncompressed = bytearray(headerSize)  # Start with header
    
    for chunk in chunks:
        cData = data[chunk['cOffset']:chunk['cOffset']+chunk['cSize']]
        try:
            dec = lzo.decompress(cData)
        except Exception as e:
            print(f"LZO decompress failed: {e}")
            # Try with header strip
            cDataStripped = cData[12:] if len(cData) > 12 else cData
            dec = lzo.decompress(cDataStripped)
        uncompressed += dec
    
    print(f"Decompressed {len(uncompressed)} bytes")
    return bytes(uncompressed)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python fix_and_unpack.py <upk_file> <output_yaml> <langCode>")
        sys.exit(1)
    
    fp = Path(sys.argv[1])
    output = sys.argv[2]
    langCode = sys.argv[3] if len(sys.argv) > 3 else "INT"
    
    print(f"Unpacking {fp} -> {output}")
    print(f"Language: {langCode}")
    
    try:
        data = decompress_upk(fp)
        print("Decompression successful!")
        print(f"Output size: {len(data)} bytes")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()
