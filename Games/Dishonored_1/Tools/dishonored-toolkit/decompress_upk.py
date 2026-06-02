#!/usr/bin/env python3
"""
Decompress LZO-compressed Dishonored UPK files.
"""
import sys
import os
import struct
import lzo
from pathlib import Path

def decompress_upk(filepath):
    """Decompress LZO-compressed UPK."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Read header - file is little-endian
    sig = struct.unpack('<I', data[0:4])[0]
    if sig != 0x9E2A83C1:
        raise Exception(f"Bad signature: 0x{sig:08X}")
    
    # Parse header to find compression flags
    offset = 4
    pkgVersion = struct.unpack('<H', data[offset:offset+2])[0]; offset += 2
    pkgLVersion = struct.unpack('<H', data[offset:offset+2])[0]; offset += 2
    headerSize = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    folderLen = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    offset += folderLen  # skip folderStr
    offset += 4  # pkgFlags
    nameCount = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    nameOffset = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    exportCount = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    exportOffset = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    importCount = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    importOffset = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    dependsOffset = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    somedata1 = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    guid = data[offset:offset+16]; offset += 16
    genCount = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    
    for i in range(genCount):
        offset += 12  # 3 x uint32 per gen entry
    
    engineVer = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    cookerVer = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    compFlags = struct.unpack('<I', data[offset:offset+4])[0]; offset += 4
    
    print(f"pkgVersion: {pkgVersion}")
    print(f"headerSize: {headerSize}")
    print(f"compFlags: {compFlags}")
    
    if compFlags == 0:
        print("Not compressed")
        return data
    
    # Find chunk table - after headerSize
    chunkOffset = headerSize
    
    chunks = []
    while chunkOffset < len(data) - 16:
        cSign = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        blockSize = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        cSize = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        uSize = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        
        if cSign == 0 and blockSize == 0 and cSize == 0 and uSize == 0:
            break
        
        if cSign != 0x9E2A83C1:
            break
        
        chunks.append({
            'blockSize': blockSize,
            'cSize': cSize,
            'uSize': uSize,
            'cOffset': chunkOffset,
        })
        
        chunkOffset += cSize
    
    print(f"Found {len(chunks)} chunks")
    
    # Decompress
    total = 0
    for i, chunk in enumerate(chunks):
        cData = data[chunk['cOffset']:chunk['cOffset']+chunk['cSize']]
        try:
            dec = lzo.decompress(cData)
        except:
            # Try skipping different header sizes
            for skip in range(0, 20):
                try:
                    dec = lzo.decompress(cData[skip:])
                    print(f"  Chunk {i}: skip={skip}, got {len(dec)} bytes")
                    break
                except:
                    continue
            else:
                raise Exception(f"Chunk {i} LZO failed")
        
        if len(dec) != chunk['uSize']:
            print(f"  Chunk {i} size mismatch: {len(dec)} vs {chunk['uSize']}")
        total += len(dec)
    
    print(f"Total decompressed: {total}")
    
    # Build decompressed UPK
    # Header stays as-is, then decompressed data
    result = bytearray(data[:headerSize])
    
    # Add all chunks' decompressed data
    for chunk in chunks:
        cData = data[chunk['cOffset']:chunk['cOffset']+chunk['cSize']]
        dec = None
        for skip in range(0, 20):
            try:
                dec = lzo.decompress(cData[skip:])
                break
            except:
                continue
        if dec:
            result.extend(dec)
    
    return bytes(result)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python decompress_upk.py <upk_file>")
        sys.exit(1)
    
    fp = Path(sys.argv[1])
    outDir = Path("_DYuncompressed")
    outDir.mkdir(exist_ok=True)
    outPath = outDir / fp.name
    
    print(f"Decompressing {fp}")
    result = decompress_upk(fp)
    
    with open(outPath, 'wb') as f:
        f.write(result)
    
    print(f"Written: {outPath} ({len(result)} bytes)")
