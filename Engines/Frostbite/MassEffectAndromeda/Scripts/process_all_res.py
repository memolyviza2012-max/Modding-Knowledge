"""Process ALL .res files with Thai text - standalone version."""
import struct
import sys
import os
import csv
import heapq
from collections import Counter

# Fix encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MAGIC = 0xD78B40EB

class HuffNode:
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char
        self.freq = freq
        self.left = left
        self.right = right
    def __lt__(self, other):
        return self.freq < other.freq
    def is_leaf(self):
        return self.char is not None

def build_huffman_tree(text_list):
    freq = Counter()
    for text in text_list:
        for ch in text:
            freq[ch] += 1
    freq['\x00'] = len(text_list)
    heap = [HuffNode(char=ch, freq=f) for ch, f in freq.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        heapq.heappush(heap, HuffNode(freq=left.freq + right.freq, left=left, right=right))
    return heap[0] if heap else None

def get_huffman_codes(root):
    codes = {}
    def traverse(node, code):
        if node is None: return
        if node.is_leaf():
            codes[node.char] = code if code else [0]
            return
        traverse(node.left, code + [0])
        traverse(node.right, code + [1])
    traverse(root, [])
    return codes

def flatten_huffman_tree(root):
    node_values = []
    branch_index = [0]
    def serialize(node):
        if node is None: return 0
        if node.is_leaf():
            return (~ord(node.char)) & 0xFFFFFFFF
        left_val = serialize(node.left)
        right_val = serialize(node.right)
        node_values.append(left_val)
        node_values.append(right_val)
        idx = branch_index[0]
        branch_index[0] += 1
        return idx
    serialize(root)
    return node_values

def encode_string(text, codes):
    bits = []
    for ch in text:
        if ch in codes:
            bits.extend(codes[ch])
    if '\x00' in codes:
        bits.extend(codes['\x00'])
    return bits

def bits_to_bytes(all_bits):
    result = bytearray()
    for i in range(0, len(all_bits), 8):
        byte_bits = all_bits[i:i+8]
        byte_val = 0
        for j, bit in enumerate(byte_bits):
            if bit:
                byte_val |= (1 << j)
        result.append(byte_val)
    return bytes(result)

class DecNode:
    def __init__(self, val=0):
        self.val = val
        self.left = None
        self.right = None
    def is_leaf(self): return self.left is None and self.right is None

def read_original_resource(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    if len(data) > 16 and struct.unpack_from('<I', data, 16)[0] == MAGIC:
        meta = data[:16]
        res = data[16:]
    elif struct.unpack_from('<I', data, 0)[0] == MAGIC:
        meta = None
        res = data
    else:
        raise ValueError("Cannot find magic")

    header = {
        'unknown1': struct.unpack_from('<I', res, 4)[0],
        'data_offset': struct.unpack_from('<I', res, 8)[0],
        'unknown2': struct.unpack_from('<I', res, 12)[0],
        'unknown3': struct.unpack_from('<I', res, 16)[0],
        'unknown4': struct.unpack_from('<I', res, 20)[0],
        'node_count': struct.unpack_from('<I', res, 24)[0],
        'node_offset': struct.unpack_from('<I', res, 28)[0],
        'strings_count': struct.unpack_from('<I', res, 32)[0],
        'strings_offset': struct.unpack_from('<I', res, 36)[0],
    }

    pos = 40
    additional_segments = []
    while pos < header['node_offset']:
        count = struct.unpack_from('<I', res, pos)[0]
        offset = struct.unpack_from('<I', res, pos + 4)[0]
        additional_segments.append((count, offset))
        pos += 8

    unknown_data_blocks = []
    for count, offset in additional_segments:
        if count > 0:
            unknown_data_blocks.append(res[offset:offset + count * 8])
        else:
            unknown_data_blocks.append(b'')

    # Build Huffman tree for decoding
    nodes_list = []
    left = None
    node_idx = 0
    root = None
    for i in range(header['node_count']):
        raw = struct.unpack_from('<I', res, header['node_offset'] + i * 4)[0]
        existing = None
        for n in nodes_list:
            if n.val == raw:
                existing = n
                break
        current = existing if existing else DecNode(raw)
        if left is None:
            left = current
        else:
            right = current
            if existing is None: nodes_list.append(right)
            parent = DecNode(node_idx)
            parent.left = left
            parent.right = right
            node_idx += 1
            root = parent
            nodes_list.append(parent)
            left = None
            continue
        if existing is None: nodes_list.append(current)

    def decode_str(bit_pos):
        chars = []
        total_bits = (len(res) - header['data_offset']) * 8
        while bit_pos < total_bits:
            node = root
            while not node.is_leaf():
                byte_idx = header['data_offset'] + (bit_pos // 8)
                bit_idx = bit_pos % 8
                if byte_idx >= len(res): return ''.join(chars)
                b = res[byte_idx]
                bit = (b >> bit_idx) & 1
                if bit == 0: node = node.left
                else: node = node.right
                bit_pos += 1
                if node is None: return ''.join(chars)
            sval = struct.unpack('<i', struct.pack('<I', node.val))[0]
            if sval >= 0: return ''.join(chars)
            char_code = ~sval
            if char_code == 0: break
            chars.append(chr(char_code))
        return ''.join(chars)

    string_entries = {}
    for i in range(header['strings_count']):
        off = header['strings_offset'] + i * 8
        sid = struct.unpack_from('<I', res, off)[0]
        bpos = struct.unpack_from('<I', res, off + 4)[0]
        text = decode_str(bpos)
        string_entries["{:08X}".format(sid)] = text

    return {
        'meta': meta, 'header': header,
        'additional_segments': additional_segments,
        'unknown_data_blocks': unknown_data_blocks,
        'string_entries': string_entries,
    }

def write_resource(original_info, new_texts, output_path):
    header = original_info['header']
    all_texts = dict(original_info['string_entries'])
    replaced = 0
    
    # --- GLYPH SWAPPING TRANSLATION (WITH SAFE ZWSP) ---
    import re
    from pythainlp.tokenize import word_tokenize
    
    # Regex to find continuous sequences of Thai characters
    thai_pattern = re.compile(r'[\u0E00-\u0E7F]+')
    
    def tokenize_match(match):
        words = word_tokenize(match.group(0), engine='newmm')
        return '\u200b'.join(words)
    
    def translate_to_asian(text):
        if not text: return text
        
        # 1. Safely insert ZWSP (\u200b) ONLY between Thai words (protects HTML tags & English)
        text = thai_pattern.sub(tokenize_match, text)
            
        # 2. Map Thai to Chinese CJK block (U+4E00) to avoid Kinsoku Shori bugs
        translated = []
        for ch in text:
            code = ord(ch)
            if 0x0E00 <= code <= 0x0E7F:
                translated.append(chr(code + 0x4000))
            else:
                translated.append(ch)
        return "".join(translated)
        
    for hex_id, text in new_texts.items():
        if hex_id in all_texts:
            # Translate text right before injecting it
            all_texts[hex_id] = translate_to_asian(text)
            replaced += 1
    # ----------------------------------

    text_list = list(all_texts.values())
    huffman_root = build_huffman_tree(text_list)
    codes = get_huffman_codes(huffman_root)
    node_values = flatten_huffman_tree(huffman_root)
    new_node_count = len(node_values)

    sorted_ids = sorted(all_texts.keys())
    all_bits = []
    string_id_positions = []
    for hex_id in sorted_ids:
        text = all_texts[hex_id]
        uint_id = int(hex_id, 16)
        bit_position = len(all_bits)
        all_bits.extend(encode_string(text, codes))
        string_id_positions.append((uint_id, bit_position))

    encoded_text_bytes = bits_to_bytes(all_bits)

    node_offset = header['node_offset']
    new_strings_offset = node_offset + new_node_count * 4
    new_strings_count = len(string_id_positions)
    block_offset = new_strings_offset + new_strings_count * 8

    recalculated_segments = []
    for orig_count, _ in original_info['additional_segments']:
        recalculated_segments.append((orig_count, block_offset))
        block_offset += orig_count * 8
    new_data_offset = block_offset

    buf = bytearray()
    buf.extend(struct.pack('<I', MAGIC))
    buf.extend(struct.pack('<I', header['unknown1']))
    buf.extend(struct.pack('<I', new_data_offset))
    buf.extend(struct.pack('<I', header['unknown2']))
    buf.extend(struct.pack('<I', header['unknown3']))
    buf.extend(struct.pack('<I', header['unknown4']))
    buf.extend(struct.pack('<I', new_node_count))
    buf.extend(struct.pack('<I', node_offset))
    buf.extend(struct.pack('<I', new_strings_count))
    buf.extend(struct.pack('<I', new_strings_offset))
    for count, offset in recalculated_segments:
        buf.extend(struct.pack('<I', count))
        buf.extend(struct.pack('<I', offset))
    while len(buf) < node_offset:
        buf.extend(b'\x00')
    for val in node_values:
        buf.extend(struct.pack('<I', val))
    for uint_id, bit_pos in string_id_positions:
        buf.extend(struct.pack('<I', uint_id))
        buf.extend(struct.pack('<I', bit_pos))
    for block_data in original_info['unknown_data_blocks']:
        buf.extend(block_data)
    buf.extend(encoded_text_bytes)

    with open(output_path, 'wb') as f:
        if original_info['meta'] is not None:
            meta = bytearray(original_info['meta'])
            struct.pack_into('<I', meta, 0, new_data_offset)
            f.write(bytes(meta))
        f.write(bytes(buf))

    return replaced

# ============================================================
# MAIN
# ============================================================

res_dir = r'E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T'
thai_csv = r'E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T\int_thai_adjusted_v2.csv'
output_dir = r'E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T\patched'
os.makedirs(output_dir, exist_ok=True)

print('Loading Thai translations...')
csv.field_size_limit(2147483647)
thai_texts = {}
with open(thai_csv, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        if row and len(row) >= 2 and len(row[0]) == 8:
            thai_texts[row[0].upper()] = row[1]
print('Loaded {} Thai strings'.format(len(thai_texts)))

res_files = sorted([f for f in os.listdir(res_dir) if f.endswith('.res')])
print('Found {} .res files\n'.format(len(res_files)))

success = 0
skip = 0
fail = 0

for fname in res_files:
    res_path = os.path.join(res_dir, fname)
    out_path = os.path.join(output_dir, fname)
    try:
        original = read_original_resource(res_path)
        replaceable = sum(1 for k in original['string_entries'] if k in thai_texts)
        if replaceable == 0:
            print('[SKIP] {} (0 Thai matches)'.format(fname))
            skip += 1
            continue
        replaced = write_resource(original, thai_texts, out_path)
        orig_size = os.path.getsize(res_path)
        new_size = os.path.getsize(out_path)
        print('[OK]   {} : {}/{} replaced, {}KB -> {}KB'.format(
            fname, replaced, len(original['string_entries']),
            orig_size//1024, new_size//1024))
        success += 1
    except Exception as e:
        print('[FAIL] {} : {}'.format(fname, e))
        fail += 1

print('\n' + '='*60)
print('DONE: {} success, {} skipped, {} failed'.format(success, skip, fail))
print('Output: {}'.format(output_dir))
