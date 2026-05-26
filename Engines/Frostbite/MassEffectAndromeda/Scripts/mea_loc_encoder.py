"""
MEA Localization Resource Encoder
==================================
Reads original .res, replaces text with Thai, writes new .res file.
Uses Huffman encoding matching the BiowareLocalizationPlugin format.

Usage:
  python mea_loc_encoder.py <input.res> <thai.csv> <output.res>
"""

import struct
import sys
import io
import os
import csv
import heapq
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAGIC = 0xD78B40EB

# ============================================================
# Huffman Tree Builder
# ============================================================

class HuffNode:
    """Huffman tree node for encoding."""
    def __init__(self, char=None, freq=0, left=None, right=None):
        self.char = char      # None for internal nodes, character for leaves
        self.freq = freq
        self.left = left
        self.right = right
    
    def __lt__(self, other):
        return self.freq < other.freq
    
    def is_leaf(self):
        return self.char is not None


def build_huffman_tree(text_list):
    """Build a Huffman tree from a list of strings."""
    # Count character frequencies across all strings
    freq = Counter()
    for text in text_list:
        for ch in text:
            freq[ch] += 1
    # Add the end-of-string marker (char code 0)
    freq['\x00'] = len(text_list)
    
    # Build priority queue
    heap = []
    for ch, f in freq.items():
        heapq.heappush(heap, HuffNode(char=ch, freq=f))
    
    # Build tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        parent = HuffNode(freq=left.freq + right.freq, left=left, right=right)
        heapq.heappush(heap, parent)
    
    return heap[0] if heap else None


def get_huffman_codes(root):
    """Get the binary code for each character."""
    codes = {}
    def traverse(node, code):
        if node is None:
            return
        if node.is_leaf():
            codes[node.char] = code if code else [0]  # Handle single-node tree
            return
        traverse(node.left, code + [0])
        traverse(node.right, code + [1])
    traverse(root, [])
    return codes


def flatten_huffman_tree(root):
    """
    Flatten the Huffman tree into the BioWare node list format.
    
    Format: nodes are written in pairs (left, right) bottom-up.
    Leaf node value = ~char_code (bitwise NOT as uint32)
    Branch node value = sequential index (0, 1, 2, ...)
    
    Returns list of uint32 values.
    """
    node_values = []
    branch_index = 0
    branch_map = {}  # node id -> branch index
    
    def serialize(node):
        nonlocal branch_index
        if node is None:
            return
        if node.is_leaf():
            # Leaf: value = ~ord(char) as uint32
            char_code = ord(node.char)
            val = (~char_code) & 0xFFFFFFFF  # bitwise NOT, as unsigned 32-bit
            return val
        
        # Internal node: serialize children first (bottom-up)
        left_val = serialize(node.left)
        right_val = serialize(node.right)
        
        # Write left, right pair
        node_values.append(left_val)
        node_values.append(right_val)
        
        # This internal node gets a sequential index
        idx = branch_index
        branch_index += 1
        branch_map[id(node)] = idx
        
        return idx  # Branch reference value
    
    serialize(root)
    return node_values


def encode_string(text, codes):
    """Encode a string into a bit array using Huffman codes."""
    bits = []
    for ch in text:
        if ch in codes:
            bits.extend(codes[ch])
        else:
            # Unknown character - skip or use replacement
            print("  WARNING: Character {} (U+{:04X}) not in Huffman tree, skipping".format(repr(ch), ord(ch)))
    # Add end-of-string marker
    if '\x00' in codes:
        bits.extend(codes['\x00'])
    return bits


def bits_to_bytes(all_bits):
    """Convert a flat list of bits to bytes (LSB first within each byte)."""
    result = bytearray()
    for i in range(0, len(all_bits), 8):
        byte_bits = all_bits[i:i+8]
        byte_val = 0
        for j, bit in enumerate(byte_bits):
            if bit:
                byte_val |= (1 << j)  # LSB first
        result.append(byte_val)
    return bytes(result)


# ============================================================
# Resource Reader (simplified)
# ============================================================

def read_original_resource(filepath):
    """Read an original .res file and extract its structure."""
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # Detect metadata offset
    if len(data) > 16 and struct.unpack_from('<I', data, 16)[0] == MAGIC:
        meta = data[:16]
        res = data[16:]
    elif struct.unpack_from('<I', data, 0)[0] == MAGIC:
        meta = None
        res = data
    else:
        raise ValueError("Cannot find magic in file")
    
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
    
    # Read additional segments
    pos = 40
    additional_segments = []
    while pos < header['node_offset']:
        count = struct.unpack_from('<I', res, pos)[0]
        offset = struct.unpack_from('<I', res, pos + 4)[0]
        additional_segments.append((count, offset))
        pos += 8
    
    # Read unknown data blocks
    unknown_data_blocks = []
    for count, offset in additional_segments:
        if count > 0:
            block_data = res[offset:offset + count * 8]
            unknown_data_blocks.append(block_data)
        else:
            unknown_data_blocks.append(b'')
    
    # Read original string IDs and decode text
    class Node:
        def __init__(self, val=0):
            self.val = val
            self.left = None
            self.right = None
        def is_leaf(self): return self.left is None and self.right is None

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
        current = existing if existing else Node(raw)
        if left is None:
            left = current
        else:
            right = current
            if existing is None: nodes_list.append(right)
            parent = Node(node_idx)
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
                bit = (b >> bit_idx) & 1  # LSB first
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

    # Read string table
    string_entries = {}
    for i in range(header['strings_count']):
        off = header['strings_offset'] + i * 8
        sid = struct.unpack_from('<I', res, off)[0]
        bpos = struct.unpack_from('<I', res, off + 4)[0]
        text = decode_str(bpos)
        hex_id = "{:08X}".format(sid)
        string_entries[hex_id] = text
    
    return {
        'meta': meta,
        'header': header,
        'additional_segments': additional_segments,
        'unknown_data_blocks': unknown_data_blocks,
        'string_entries': string_entries,
        'node_offset_base': header['node_offset'],
    }


# ============================================================
# Resource Writer
# ============================================================

def write_resource(original_info, new_texts, output_path):
    """
    Write a new .res file with modified texts.
    
    original_info: from read_original_resource()
    new_texts: dict of {hex_id: new_text} to replace
    output_path: path to write the new .res file
    """
    header = original_info['header']
    
    # Merge texts: start with originals, overlay with new
    all_texts = dict(original_info['string_entries'])
    replaced = 0
    for hex_id, text in new_texts.items():
        if hex_id in all_texts:
            all_texts[hex_id] = text
            replaced += 1
    
    print("  Replacing {} out of {} strings".format(replaced, len(all_texts)))
    
    # Collect all text for Huffman tree building
    text_list = list(all_texts.values())
    
    # Build new Huffman tree
    print("  Building Huffman tree...")
    huffman_root = build_huffman_tree(text_list)
    codes = get_huffman_codes(huffman_root)
    print("  Huffman tree has {} unique characters".format(len(codes)))
    
    # Flatten tree to node list
    node_values = flatten_huffman_tree(huffman_root)
    new_node_count = len(node_values)
    print("  Node count: {} (was {})".format(new_node_count, header['node_count']))
    
    # Encode all strings and compute bit positions
    print("  Encoding {} strings...".format(len(all_texts)))
    
    # Sort by string ID (same order as original)
    sorted_ids = sorted(all_texts.keys())
    
    all_bits = []
    string_id_positions = []  # list of (uint32_id, uint32_bit_position)
    
    for hex_id in sorted_ids:
        text = all_texts[hex_id]
        uint_id = int(hex_id, 16)
        bit_position = len(all_bits)
        
        encoded_bits = encode_string(text, codes)
        all_bits.extend(encoded_bits)
        
        string_id_positions.append((uint_id, bit_position))
    
    encoded_text_bytes = bits_to_bytes(all_bits)
    print("  Encoded text size: {} bytes ({} bits)".format(len(encoded_text_bytes), len(all_bits)))
    
    # Calculate offsets
    node_offset = header['node_offset']  # Keep same offset for nodes
    encoding_nodes_size = new_node_count * 4
    new_strings_offset = node_offset + encoding_nodes_size
    new_strings_count = len(string_id_positions)
    
    # After string table: additional data blocks
    block_offset = new_strings_offset + (new_strings_count * 8)
    
    recalculated_segments = []
    for i, (orig_count, orig_offset) in enumerate(original_info['additional_segments']):
        recalculated_segments.append((orig_count, block_offset))
        block_offset += orig_count * 8
    
    new_data_offset = block_offset
    
    # Write the resource
    buf = bytearray()
    
    # Header
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
    
    # Additional segment headers
    for count, offset in recalculated_segments:
        buf.extend(struct.pack('<I', count))
        buf.extend(struct.pack('<I', offset))
    
    # Pad to node_offset if needed
    while len(buf) < node_offset:
        buf.extend(b'\x00')
    
    # Huffman nodes
    for val in node_values:
        buf.extend(struct.pack('<I', val))
    
    assert len(buf) == new_strings_offset, "String offset mismatch: {} vs {}".format(len(buf), new_strings_offset)
    
    # String ID table
    for uint_id, bit_pos in string_id_positions:
        buf.extend(struct.pack('<I', uint_id))
        buf.extend(struct.pack('<I', bit_pos))
    
    # Unknown data blocks
    for block_data in original_info['unknown_data_blocks']:
        buf.extend(block_data)
    
    assert len(buf) == new_data_offset, "Data offset mismatch: {} vs {}".format(len(buf), new_data_offset)
    
    # Encoded text data
    buf.extend(encoded_text_bytes)
    
    # Write with metadata
    with open(output_path, 'wb') as f:
        if original_info['meta'] is not None:
            # Update metadata's dataOffset field
            meta = bytearray(original_info['meta'])
            struct.pack_into('<I', meta, 0, new_data_offset)
            f.write(bytes(meta))
        f.write(bytes(buf))
    
    total_size = (len(original_info['meta']) if original_info['meta'] else 0) + len(buf)
    print("  Written {} bytes to {}".format(total_size, os.path.basename(output_path)))
    
    return True


# ============================================================
# Main
# ============================================================

def load_thai_csv(csv_path):
    """Load Thai translations from CSV."""
    csv.field_size_limit(2147483647)
    texts = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and len(row) >= 2 and len(row[0]) == 8:
                texts[row[0].upper()] = row[1]
    return texts


def process_single_res(res_path, thai_texts, output_dir):
    """Process a single .res file."""
    basename = os.path.basename(res_path)
    output_path = os.path.join(output_dir, basename)
    
    print("\n" + "=" * 60)
    print("Processing: {}".format(basename))
    print("=" * 60)
    
    try:
        # Read original
        original = read_original_resource(res_path)
        print("  Original: {} strings".format(len(original['string_entries'])))
        
        # Count how many strings we can replace
        replaceable = sum(1 for k in original['string_entries'] if k in thai_texts)
        print("  Replaceable with Thai: {}".format(replaceable))
        
        if replaceable == 0:
            print("  SKIPPING (no matching Thai strings)")
            return False
        
        # Write new resource
        success = write_resource(original, thai_texts, output_path)
        
        if success:
            # Verify by reading back
            print("  Verifying...")
            verify = read_original_resource(output_path)
            sample_count = 0
            for hex_id in sorted(verify['string_entries'].keys()):
                text = verify['string_entries'][hex_id]
                if text and any(0x0E00 <= ord(c) <= 0x0E7F for c in text):
                    preview = text[:60]
                    print("    [{}] {}".format(hex_id, preview))
                    sample_count += 1
                    if sample_count >= 3:
                        break
        
        return success
        
    except Exception as e:
        print("  ERROR: {}".format(e))
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Paths
    res_dir = r'E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T'
    thai_csv = r'E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T\int_thai_adjusted_v2.csv'
    output_dir = r'E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T\patched'
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Load Thai texts
    print("Loading Thai translations...")
    thai_texts = load_thai_csv(thai_csv)
    print("Loaded {} Thai strings".format(len(thai_texts)))
    
    # Test with smallest meaningful file first
    test_file = os.path.join(res_dir, 'mainmenu.res')
    process_single_res(test_file, thai_texts, output_dir)
