import json, struct, lz4.frame, os, shutil, sys

sys.stdout.reconfigure(encoding='utf-8')

VANILLA_DAT = r'E:\Mod_Workspace\TheSurge_Mod_Workspace\test_vanilla_reset\data_bin_0.dat'
GAME_DIR = r'F:\SteamLibrary\steamapps\common\The Surge\data_packages\pc'
JSON_FILE = r'E:\Mod_Workspace\TheSurge_Mod_Workspace\json_output\english.json'

ENG_OFFSET = 13786335
ENG_COMP_SIZE = 624743

THAI_START = 0x0E01
JAP_START = 0x3040

def thai_to_japanese(text):
    # Map Thai (0x0E01+) to Japanese (0x3041+)
    return ''.join(chr(JAP_START + (ord(c) - THAI_START)) if THAI_START <= ord(c) <= 0x0E5B else c for c in text)

print("Restoring vanilla data_bin_0.dat...")
dat_path = os.path.join(GAME_DIR, 'data_bin_0.dat')
shutil.copy(VANILLA_DAT, dat_path)

game_dat = bytearray(open(dat_path, 'rb').read())
eng_orig_comp = game_dat[ENG_OFFSET:ENG_OFFSET+ENG_COMP_SIZE]
eng = bytearray(lz4.frame.decompress(eng_orig_comp))
print(f"english.bin decompressed: {len(eng)} bytes")

# Extract strings
pos = 24; eng_strings = []
while pos < len(eng) - 4:
    val = struct.unpack_from('>I', eng, pos)[0]
    if val & 0x80000000:
        slen = val & 0x7FFFFFFF
        if 0 < slen < 100000 and pos + 4 + slen <= len(eng):
            try:
                s = eng[pos+4:pos+4+slen].decode('utf-8')
                eng_strings.append((pos, slen, s))
                pos += 4 + slen + (4 - slen % 4) % 4
                continue
            except: pass
    pos += 1

# Load translations
data = json.load(open(JSON_FILE, 'r', encoding='utf-8'))
trans_map = {}
for entry in data:
    orig = entry.get('original', '')
    trans = entry.get('translation', '')
    if trans and trans != orig:
        trans_map[orig] = thai_to_japanese(trans)

replaced = 0
for pos, slen, s in eng_strings:
    if s in trans_map:
        cipher_bytes = trans_map[s].encode('utf-8')
        if len(cipher_bytes) <= slen:
            eng[pos+4:pos+4+slen] = cipher_bytes + b' ' * (slen - len(cipher_bytes))
            replaced += 1
        else:
            trunc = cipher_bytes[:slen]
            while trunc and (trunc[-1] & 0xC0) == 0x80: trunc = trunc[:-1]
            if trunc and (trunc[-1] & 0xC0) == 0xC0: trunc = trunc[:-1]
            eng[pos+4:pos+4+slen] = trunc + b' ' * (slen - len(trunc))
            replaced += 1

print(f"Injected {replaced} Japanese-encoded Thai strings into english.bin.")

# Compress
comp = lz4.frame.compress(bytes(eng), block_size=lz4.frame.BLOCKSIZE_MAX256KB, content_checksum=True, store_size=False, block_linked=True)
comp_len = len(comp)
print(f"Compressed size: {comp_len} (Budget: {ENG_COMP_SIZE})")

if comp_len <= ENG_COMP_SIZE:
    pad_size = ENG_COMP_SIZE - comp_len
    comp_padded = bytearray(comp)
    
    if pad_size > 0:
        print(f"Padding {pad_size} bytes with ZEROS...")
        comp_padded += (b'\x00' * pad_size)
            
    game_dat[ENG_OFFSET:ENG_OFFSET+ENG_COMP_SIZE] = comp_padded
    with open(dat_path, 'wb') as f:
        f.write(game_dat)
        
    with open(r'F:\SteamLibrary\steamapps\common\The Surge\language.ini', 'w') as f:
        f.write('game_language_text  = english\ngame_language_voice = english\n')
    
    print("DEPLOYED JAPANESE CIPHER TO english.bin SUCCESSFULLY!")
else:
    print("OVERFLOW! We need to blank untranslated strings to save space.")
    
    # Second pass: blank untranslated strings
    eng2 = bytearray(lz4.frame.decompress(eng_orig_comp))
    untranslated = []
    for pos, slen, s in eng_strings:
        if s not in trans_map:
            untranslated.append((slen, pos))
    
    untranslated.sort(reverse=True)
    spaced = 0
    
    for pos, slen, s in eng_strings:
        if s in trans_map:
            cipher_bytes = trans_map[s].encode('utf-8')
            if len(cipher_bytes) <= slen:
                eng2[pos+4:pos+4+slen] = cipher_bytes + b' ' * (slen - len(cipher_bytes))
            else:
                trunc = cipher_bytes[:slen]
                while trunc and (trunc[-1] & 0xC0) == 0x80: trunc = trunc[:-1]
                if trunc and (trunc[-1] & 0xC0) == 0xC0: trunc = trunc[:-1]
                eng2[pos+4:pos+4+slen] = trunc + b' ' * (slen - len(trunc))
                
    for slen, pos in untranslated:
        eng2[pos+4:pos+4+slen] = b' ' * slen
        spaced += 1
        if spaced % 100 == 0:
            c = lz4.frame.compress(bytes(eng2), block_size=lz4.frame.BLOCKSIZE_MAX256KB, content_checksum=True, store_size=False, block_linked=True)
            if len(c) <= ENG_COMP_SIZE:
                break
                
    final_comp = lz4.frame.compress(bytes(eng2), block_size=lz4.frame.BLOCKSIZE_MAX256KB, content_checksum=True, store_size=False, block_linked=True)
    print(f"Second pass compressed size: {len(final_comp)}")
    
    pad = ENG_COMP_SIZE - len(final_comp)
    final_padded = bytearray(final_comp) + (b'\x00' * pad)
    game_dat[ENG_OFFSET:ENG_OFFSET+ENG_COMP_SIZE] = final_padded
    with open(dat_path, 'wb') as f:
        f.write(game_dat)
        
    with open(r'F:\SteamLibrary\steamapps\common\The Surge\language.ini', 'w') as f:
        f.write('game_language_text  = english\ngame_language_voice = english\n')
        
    print("DEPLOYED JAPANESE CIPHER TO english.bin SUCCESSFULLY (with spacing)!")
