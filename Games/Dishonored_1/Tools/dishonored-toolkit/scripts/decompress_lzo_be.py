#!/usr/bin/env python3
"""
LZO Decompressor for Dishonored UPK files - FIXED Big-Endian chunk headers.
Reads chunk table from UPK and decompresses each LZO chunk.
"""
import sys
import os
import struct
import lzo
from pathlib import Path


def decompress_upk(filepath, output_dir=None):
    """
    Decompress an LZO-compressed Dishonored UPK file.
    
    Chunk table format (at headerSize):
      cSign (4 bytes, BIG-ENDIAN): 0x9E2A83C1 (signature marker)
      blockSize (4 bytes, BIG-ENDIAN): compression block size (usually 131072)
      cSize (4 bytes, BIG-ENDIAN): compressed size
      uSize (4 bytes, BIG-ENDIAN): uncompressed size
      cData (cSize bytes): LZO compressed data
    
    Chunks are consecutive. End marker: all zeros or invalid values.
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    sig = struct.unpack('<I', data[0:4])[0]
    if sig != 0x9E2A83C1:
        raise Exception(f"Bad signature: 0x{sig:08X}")
    
    # Get headerSize (at offset 8-11, LITTLE-ENDIAN)
    headerSize = struct.unpack('<I', data[8:12])[0]
    
    print(f"File size: {len(data)} ({len(data)/1024/1024:.1f} MB)")
    print(f"Header size: {headerSize} ({headerSize/1024:.1f} KB)")
    print(f"Data region starts at: 0x{headerSize:08X}")
    
    # Find chunks starting at headerSize
    # Chunk headers are BIG-ENDIAN
    chunkOffset = headerSize
    
    chunks = []
    while chunkOffset < len(data) - 16:
        # Read chunk header in BIG-ENDIAN
        cSign = struct.unpack('>I', data[chunkOffset:chunkOffset+4])[0]
        blockSize = struct.unpack('>I', data[chunkOffset+4:chunkOffset+8])[0]
        cSize = struct.unpack('>I', data[chunkOffset+8:chunkOffset+12])[0]
        uSize = struct.unpack('>I', data[chunkOffset+12:chunkOffset+16])[0]
        
        # Check for end marker
        if cSign == 0 and blockSize == 0 and cSize == 0 and uSize == 0:
            print(f"End marker at 0x{chunkOffset-16:08X}")
            break
        
        # Validate chunk
        if cSign != 0x9E2A83C1:
            print(f"Warning: Invalid chunk signature at 0x{chunkOffset:08X}: 0x{cSign:08X}")
            break
        
        if cSize < 100 or cSize > len(data):
            print(f"Warning: Invalid chunk at 0x{chunkOffset:08X}: cSize={cSize}, uSize={uSize}")
            break
        
        chunks.append({
            'cSign': cSign,
            'blockSize': blockSize,
            'cSize': cSize,
            'uSize': uSize,
            'cOffset': chunkOffset + 16,  # cData starts after 16-byte header
        })
        
        if len(chunks) <= 5 or len(chunks) % 10 == 0:
            print(f"  Chunk {len(chunks)}: cDataOffset=0x{chunks[-1]['cOffset']:08X}, cSize={cSize}, uSize={uSize}")
        
        # Move to next chunk
        chunkOffset += 16 + cSize
        
        if len(chunks) >= 1000:
            break
    
    print(f"Total chunks found: {len(chunks)}")
    
    if len(chunks) == 0:
        raise Exception("No valid chunks found!")
    
    # Build uncompressed UPK
    # Start with header (bytes 0 to headerSize)
    uncompressed = bytearray(data[:headerSize])
    
    for i, chunk in enumerate(chunks):
        cData = data[chunk['cOffset']:chunk['cOffset']+chunk['cSize']]
        
        # Try LZO decompress with various skips
        dec = None
        for skip in range(32):
            try:
                dec = lzo.decompress(cData[skip:], False, original_size=chunk['uSize'])
                if len(dec) == chunk['uSize']:
                    print(f"  Chunk {i}: decompressed {len(dec)} bytes (skip={skip}) OK")
                    break
            except:
                continue
        
        if dec is None or len(dec) != chunk['uSize']:
            print(f"  Chunk {i}: LZO FAILED - tried skip 0-{skip}")
            print(f"    cData[:32]: {cData[:32].hex()}")
            raise Exception(f"Chunk {i} LZO decompress failed")
        
        uncompressed += dec
    
    print(f"Total decompressed: {len(uncompressed)} bytes ({len(uncompressed)/1024/1024:.1f} MB)")
    
    # Write to output
    if output_dir is None:
        output_dir = Path("_DYuncompressed")
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    outPath = output_dir / Path(filepath).name
    
    with open(outPath, 'wb') as f:
        f.write(uncompressed)
    
    print(f"Written: {outPath} ({len(uncompressed)} bytes)")
    return outPath


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python decompress_lzo_be.py <upk_file> [output_dir]")
        sys.exit(1)
    
    filepath = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None
    
    print(f"Decompressing {filepath}")
    
    try:
        outPath = decompress_upk(filepath, output_dir)
        print(f"Success! Decompressed UPK: {outPath}")
    except Exception as e:
        print(f"Failed: {e}")
        import traceback
        traceback.print_exc()