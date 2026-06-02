#!/usr/bin/env python3
"""
LZO Decompressor for Dishonored UPK files.
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
      cSign (4 bytes): 0x9E2A83C1 (signature marker)
      blockSize (4 bytes): compression block size (usually 131072)
      cSize (4 bytes): compressed size
      uSize (4 bytes): uncompressed size
      cData (cSize bytes): LZO compressed data
    
    Chunks are consecutive. End marker: all zeros or invalid values.
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    sig = struct.unpack('<I', data[0:4])[0]
    if sig != 0x9E2A83C1:
        raise Exception(f"Bad signature: 0x{sig:08X}")
    
    # Get headerSize (at offset 8-11, LE)
    headerSize = struct.unpack('<I', data[8:12])[0]
    
    print(f"File size: {len(data)}")
    print(f"Header size: {headerSize} (0x{headerSize:08X})")
    
    # Find chunks starting at headerSize
    chunkOffset = headerSize
    
    chunks = []
    while chunkOffset < len(data) - 16:
        cSign = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        blockSize = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        cSize = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        uSize = struct.unpack('<I', data[chunkOffset:chunkOffset+4])[0]; chunkOffset += 4
        
        # Check for end marker
        if cSign == 0 and blockSize == 0 and cSize == 0 and uSize == 0:
            print(f"End marker at 0x{chunkOffset-16:08X}")
            break
        
        # Validate chunk
        if cSign != 0x9E2A83C1:
            print(f"Warning: Invalid chunk signature at 0x{chunkOffset-16:08X}: 0x{cSign:08X}")
            # Try to re-sync by looking for next signature
            break
        
        if cSize < 100 or uSize < cSize:
            print(f"Warning: Invalid chunk at 0x{chunkOffset-16:08X}: cSize={cSize}, uSize={uSize}")
            break
        
        # Data starts after the chunk header (16 bytes)
        chunks.append({
            'cSign': cSign,
            'blockSize': blockSize,
            'cSize': cSize,
            'uSize': uSize,
            'cOffset': chunkOffset,  # cData starts here
        })
        
        # Move to next chunk (after cData)
        chunkOffset += cSize
        
        if len(chunks) <= 5 or len(chunks) % 5 == 0:
            print(f"  Chunk {len(chunks)}: cOffset=0x{chunkOffset-cSize:08X}, cSize={cSize}, uSize={uSize}")
    
    print(f"Total chunks found: {len(chunks)}")
    
    if len(chunks) == 0:
        raise Exception("No valid chunks found!")
    
    # Build uncompressed UPK
    # Start with header (bytes 0 to headerSize)
    uncompressed = bytearray(data[:headerSize])
    
    for i, chunk in enumerate(chunks):
        cData = data[chunk['cOffset']:chunk['cOffset']+chunk['cSize']]
        
        # Try LZO decompress
        dec = None
        error_msg = None
        for skip in range(20):
            try:
                dec = lzo.decompress(cData[skip:])
                print(f"  Chunk {i}: decompressed {len(dec)} bytes (skip={skip})")
                break
            except:
                continue
        
        if dec is None:
            # Try with different buffer sizes
            try:
                dec = lzo.decompress(cData, False)  # LZO1Z mode
                print(f"  Chunk {i}: decompressed {len(dec)} bytes (LZO1Z mode)")
            except Exception as e:
                error_msg = str(e)
                print(f"  Chunk {i}: LZO FAILED - {error_msg}")
                print(f"    cOffset=0x{chunk['cOffset']:08X}, cSize={chunk['cSize']}")
                print(f"    First 20 bytes: {cData[:20].hex()}")
                raise Exception(f"Chunk {i} LZO decompress failed: {error_msg}")
        
        if len(dec) != chunk['uSize']:
            print(f"  Warning: Chunk {i} size mismatch: got {len(dec)}, expected {chunk['uSize']}")
        
        uncompressed += dec
    
    print(f"Total decompressed: {len(uncompressed)} bytes")
    
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
        print("Usage: python decompress_lzo.py <upk_file> [output_dir]")
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
