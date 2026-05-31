"""
V15: Save compression space by targeting specific safe strings (e.g., credits) 
instead of nulling out thousands of strings.
"""
import lz4.frame
import struct
import json
import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

VANILLA_DAT = r'E:\Mod_Workspace\TheSurge_Mod_Workspace\test_vanilla_reset\data_bin_0.dat'
VANILLA_TOC = r'E:\Mod_Workspace\TheSurge_Mod_Workspace\test_vanilla_reset\data_bin.toc'
ORIG_ENG_OFFSET = 13786335
ORIG_ENG_COMP = 624743

with open(VANILLA_DAT, 'rb') as f:
    f.seek(ORIG_ENG_OFFSET)
    orig_comp = f.read(ORIG_ENG_COMP)
orig_eng = bytearray(lz4.frame.decompress(orig_comp))

with open(r'E:\Mod_Workspace\TheSurge_Mod_Workspace\json_output\english.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

trans_map = {}
for e in data:
    if e.get('translation',''):
        trans_map[e['original']] = e['translation']

# Create base with Thai that fits, keep English for others
new_eng = bytearray(orig_eng)
thai_count = 0

pos = 24
while pos < len(new_eng) - 4:
    val = struct.unpack_from('>I', new_eng, pos)[0]
    if val & 0x80000000:
        str_len = val & 0x7FFFFFFF
        if 0 < str_len < 100000 and pos + 4 + str_len <= len(new_eng):
            try:
                text = new_eng[pos+4:pos+4+str_len].decode('utf-8')
                pad = (4 - str_len % 4) % 4
                
                if text in trans_map:
                    thai_bytes = trans_map[text].encode('utf-8')
                    if len(thai_bytes) <= str_len:
                        new_eng[pos+4:pos+4+len(thai_bytes)] = thai_bytes
                        if len(thai_bytes) < str_len:
                            # Use space for padding instead of null to be safe
                            new_eng[pos+4+len(thai_bytes):pos+4+str_len] = b' ' * (str_len - len(thai_bytes))
                        thai_count += 1
                    else:
                        # Thai doesn't fit, try truncation
                        trunc = thai_bytes[:str_len]
                        while trunc and (trunc[-1] & 0xC0) == 0x80:
                            trunc = trunc[:-1]
                        if trunc and len(trunc) >= 3:
                            try:
                                trunc.decode('utf-8')
                                new_eng[pos+4:pos+4+len(trunc)] = trunc
                                if len(trunc) < str_len:
                                    new_eng[pos+4+len(trunc):pos+4+str_len] = b' ' * (str_len - len(trunc))
                                thai_count += 1
                            except:
                                pass # Keep English
                pos += 4 + str_len + pad
                continue
            except:
                pass
    pos += 1

base_comp = lz4.frame.compress(
    bytes(new_eng),
    block_size=lz4.frame.BLOCKSIZE_MAX256KB,
    content_checksum=True,
    store_size=False,
    block_linked=True,
)
print(f"Base size with Thai: {len(base_comp):,} (Budget: {ORIG_ENG_COMP:,})")
print(f"Need to save: {len(base_comp) - ORIG_ENG_COMP:,} bytes")

# First, gather all untranslated strings
untranslated = []
pos = 24
while pos < len(new_eng) - 4:
    val = struct.unpack_from('>I', new_eng, pos)[0]
    if val & 0x80000000:
        str_len = val & 0x7FFFFFFF
        if 0 < str_len < 100000 and pos + 4 + str_len <= len(new_eng):
            try:
                text = new_eng[pos+4:pos+4+str_len].decode('utf-8')
                if text not in trans_map:
                    untranslated.append((str_len, pos))
                pad = (4 - str_len % 4) % 4
                pos += 4 + str_len + pad
                continue
            except:
                pass
    pos += 1

# Sort by length descending, space out the longest ones first
untranslated.sort(reverse=True)
spaced_strings = 0

for str_len, pos in untranslated:
    new_eng[pos+4:pos+4+str_len] = b' ' * str_len
    spaced_strings += 1
    if spaced_strings % 100 == 0:
        temp_comp = lz4.frame.compress(bytes(new_eng), block_size=lz4.frame.BLOCKSIZE_MAX256KB, content_checksum=True, store_size=False, block_linked=True)
        if len(temp_comp) <= ORIG_ENG_COMP:
            break

final_comp = lz4.frame.compress(
    bytes(new_eng),
    block_size=lz4.frame.BLOCKSIZE_MAX256KB,
    content_checksum=True,
    store_size=False,
    block_linked=True,
)

print(f"Final size: {len(final_comp):,} (Budget: {ORIG_ENG_COMP:,})")
print(f"Spaced out {spaced_strings} untranslated strings.")
if len(final_comp) <= ORIG_ENG_COMP:
    import shutil
    GAME_DIR = r'F:\SteamLibrary\steamapps\common\The Surge\data_packages\pc'
    game_dat = bytearray(open(VANILLA_DAT, 'rb').read())
    game_dat[ORIG_ENG_OFFSET:ORIG_ENG_OFFSET + len(final_comp)] = final_comp
    gap_start = ORIG_ENG_OFFSET + len(final_comp)
    gap_end = ORIG_ENG_OFFSET + ORIG_ENG_COMP
    game_dat[gap_start:gap_end] = b'\x00' * (gap_end - gap_start)
    
    with open(os.path.join(GAME_DIR, 'data_bin_0.dat'), 'wb') as f:
        f.write(game_dat)
    shutil.copy2(VANILLA_TOC, os.path.join(GAME_DIR, 'data_bin.toc'))
    print("Deployed V15 to game dir.")

