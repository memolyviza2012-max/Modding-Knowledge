"""
Safe font patch: Only modify the font table at offset 1508776-1514464
which contains the 159 Japanese glyphs.
Change codepoints from Japanese (0x3040+) to Thai (0x0E01+)
but KEEP the original glyph metrics (UV coords pointing to Japanese glyphs in atlas).
This way Thai chars will render using Japanese glyph shapes (test).
"""
import struct
import lz4.frame
import sys

sys.stdout.reconfigure(encoding='utf-8')

VANILLA_DAT = r'E:\Mod_Workspace\TheSurge_Mod_Workspace\test_vanilla_reset\data_bin_0.dat'
GAME_DIR = r'F:\SteamLibrary\steamapps\common\The Surge\data_packages\pc'
ORIG_FNT_OFFSET = 31709755
ORIG_FNT_COMP = 253299

THAI_START = 0x0E01
JAP_START = 0x3040

# Read and decompress vanilla fonts.bin
van_dat = open(VANILLA_DAT, 'rb').read()
van_fnt_comp = van_dat[ORIG_FNT_OFFSET:ORIG_FNT_OFFSET + ORIG_FNT_COMP]
fnt = bytearray(lz4.frame.decompress(van_fnt_comp))
print(f"fonts.bin: {len(fnt):,} bytes")

# ONLY scan the known Japanese glyph region (offset 1508776-1514464)
# with strict 32-byte alignment from the first known entry
REGION_START = 1508776  # First Japanese glyph (ぁ U+3041)
REGION_END = 1514464 + 32  # Last Japanese glyph + one record

patched = 0
i = REGION_START
while i < REGION_END and i < len(fnt) - 32:
    val = struct.unpack_from('>I', fnt, i)[0]
    if JAP_START <= val <= 0x30FF:
        floats = struct.unpack_from('>fffffff', fnt, i + 4)
        if all(-2000 <= f <= 8192 for f in floats):
            # Map to Thai codepoint
            thai_cp = THAI_START + (val - JAP_START)
            if thai_cp <= 0x0E5B:
                # Only change the codepoint, KEEP original UV metrics!
                struct.pack_into('>I', fnt, i, thai_cp)
                patched += 1
                ch_jp = chr(val)
                ch_th = chr(thai_cp)
                if patched <= 5:
                    print(f"  {ch_jp} U+{val:04X} -> {ch_th} U+{thai_cp:04X} (x={floats[0]:.1f} y={floats[1]:.1f} w={floats[2]:.1f} h={floats[3]:.1f})")
    # Step by record size (look for next entry)
    # Records might not be exactly 32 bytes apart - scan by 4
    i += 4

print(f"Patched {patched} Japanese -> Thai codepoints")
print(f"  Region: {REGION_START}-{REGION_END}")

# Compress
mod_comp = lz4.frame.compress(
    bytes(fnt),
    block_size=lz4.frame.BLOCKSIZE_MAX256KB,
    content_checksum=True,
    store_size=False,
    block_linked=True
)

print(f"Compressed: {len(mod_comp):,} / {ORIG_FNT_COMP:,} budget")

if len(mod_comp) <= ORIG_FNT_COMP:
    import os
    game_dat = bytearray(open(os.path.join(GAME_DIR, 'data_bin_0.dat'), 'rb').read())
    game_dat[ORIG_FNT_OFFSET:ORIG_FNT_OFFSET + len(mod_comp)] = mod_comp
    gap = ORIG_FNT_COMP - len(mod_comp)
    game_dat[ORIG_FNT_OFFSET + len(mod_comp):ORIG_FNT_OFFSET + ORIG_FNT_COMP] = b'\x00' * gap
    with open(os.path.join(GAME_DIR, 'data_bin_0.dat'), 'wb') as f:
        f.write(game_dat)
    print(f"Deployed! (gap padded: {gap} bytes)")
else:
    print("OVERFLOW!")
