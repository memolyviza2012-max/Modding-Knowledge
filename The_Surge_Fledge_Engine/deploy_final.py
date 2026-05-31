import json, struct, lz4.frame, os, shutil, sys

sys.stdout.reconfigure(encoding='utf-8')

VANILLA_DAT = r'E:\Mod_Workspace\TheSurge_Mod_Workspace\test_vanilla_reset\data_bin_0.dat'
GAME_DIR = r'F:\SteamLibrary\steamapps\common\The Surge\data_packages\pc'
JSON_FILE = r'E:\Mod_Workspace\TheSurge_Mod_Workspace\json_output\english.json'

RUS_OFFSET = 24988133
RUS_COMP_SIZE = 767898

THAI_START = 0x0E01
CYRILLIC_START = 0x0400

def thai_to_cyrillic(text):
    return ''.join(chr(CYRILLIC_START + (ord(c) - THAI_START)) if THAI_START <= ord(c) <= 0x0E5B else c for c in text)

print("Restoring vanilla data_bin_0.dat...")
dat_path = os.path.join(GAME_DIR, 'data_bin_0.dat')
shutil.copy(VANILLA_DAT, dat_path)

game_dat = bytearray(open(dat_path, 'rb').read())
rus_orig_comp = game_dat[RUS_OFFSET:RUS_OFFSET+RUS_COMP_SIZE]
rus = bytearray(lz4.frame.decompress(rus_orig_comp))
print(f"russian.bin decompressed: {len(rus)} bytes")

# Extract strings
pos = 0; rus_strings = []
while pos < len(rus) - 4:
    val = struct.unpack_from('>I', rus, pos)[0]
    if val & 0x80000000:
        slen = val & 0x7FFFFFFF
        if 0 < slen < 5000:
            try:
                s = rus[pos+4:pos+4+slen].decode('utf-8')
                rus_strings.append((pos, slen, s))
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
        trans_map[orig] = thai_to_cyrillic(trans)

replaced = 0
blanked = 0
for pos, slen, s in rus_strings:
    # Blank existing Russian to save space (replaced with English if untranslated)
    if any(0x0400 <= ord(c) <= 0x04FF for c in s) and s not in trans_map:
        rus[pos+4:pos+4+slen] = b' ' * slen
        blanked += 1

for pos, slen, s in rus_strings:
    if s in trans_map:
        cipher_bytes = trans_map[s].encode('utf-8')
        if len(cipher_bytes) <= slen:
            rus[pos+4:pos+4+slen] = cipher_bytes + b' ' * (slen - len(cipher_bytes))
            replaced += 1
        else:
            trunc = cipher_bytes[:slen]
            while trunc and (trunc[-1] & 0xC0) == 0x80: trunc = trunc[:-1]
            if trunc and (trunc[-1] & 0xC0) == 0xC0: trunc = trunc[:-1]
            rus[pos+4:pos+4+slen] = trunc + b' ' * (slen - len(trunc))
            replaced += 1

print(f"Blanked {blanked} old Russian strings.")
print(f"Injected {replaced} Cyrillic-encoded Thai strings.")

# Compress
comp = lz4.frame.compress(bytes(rus), block_size=lz4.frame.BLOCKSIZE_MAX256KB, content_checksum=True, store_size=False, block_linked=True)
comp_len = len(comp)
print(f"Compressed size: {comp_len} (Budget: {RUS_COMP_SIZE})")

if comp_len <= RUS_COMP_SIZE:
    pad_size = RUS_COMP_SIZE - comp_len
    comp_padded = bytearray(comp)
    
    if pad_size > 0:
        print(f"Padding {pad_size} bytes with ZEROS...")
        comp_padded += (b'\x00' * pad_size)
            
    game_dat[RUS_OFFSET:RUS_OFFSET+RUS_COMP_SIZE] = comp_padded
    with open(dat_path, 'wb') as f:
        f.write(game_dat)
        
    with open(r'F:\SteamLibrary\steamapps\common\The Surge\language.ini', 'w') as f:
        f.write('game_language_text  = russian\ngame_language_voice = english\n')
    
    print("DEPLOYED FINAL SCRIPT SUCCESSFULLY!")
else:
    print("OVERFLOW!")
