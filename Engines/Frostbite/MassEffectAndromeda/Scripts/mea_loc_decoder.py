"""
MEA Localization Resource Decoder/Encoder
==========================================
Reads and writes BioWare LocalizedStringResource (.res) files directly.
Based on reverse-engineering BiowareLocalizationPlugin source code from
CadeEvs/FrostyToolsuite (branch 1.0.7).

Binary Format:
  Header (variable size):
    uint32 magic = 0xD78B40EB
    uint32 unknown1
    uint32 dataOffset         (position of Huffman-encoded text data)
    uint32 unknown2, unknown3, unknown4
    uint32 nodeCount          (number of Huffman tree nodes)
    uint32 nodeOffset         (byte offset to Huffman tree)
    uint32 stringsCount       (number of string entries)
    uint32 stringsOffset      (byte offset to string ID table)
    [uint32 count, uint32 offset] * N  (additional data segments)
  
  Huffman Tree (at nodeOffset, nodeCount * 4 bytes):
    Nodes read in pairs: left, right -> parent
    Leaf nodes: upper 16 bits = character value (0xFFFF = end marker)
    Branch nodes: value = sequential index
  
  String ID Table (at stringsOffset, stringsCount * 8 bytes):
    [uint32 stringId, uint32 bitPosition] * stringsCount
  
  Encoded Text Data (from dataOffset to end of file):
    Huffman-encoded bit stream. Each string ends with char 0xFFFF.
"""

import struct
import sys
import io
import os
import csv
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

MAGIC = 0xD78B40EB

class HuffmanNode:
    def __init__(self, value=0, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right
    
    @property
    def is_leaf(self):
        return self.left is None and self.right is None
    
    @property
    def letter(self):
        """Extract the character from the node value (upper 16 bits inverted)."""
        # In Frostbite, leaf node values encode characters
        # The value is stored as ~char (bitwise NOT) in the upper bits
        # Actually, based on source code: node.Letter property
        # Looking at HuffmanNode.cs: Letter = (char)(Value >> 16) but with special handling
        # For leaf nodes, Value has the character encoded
        # 0xFFFFFFFF = end marker (char 0xFFFF)
        return chr(self.value >> 16) if self.value != 0xFFFFFFFF else '\x00'


def read_uint32(data, offset):
    return struct.unpack_from('<I', data, offset)[0]


def read_header(data):
    """Read the resource header."""
    magic = read_uint32(data, 0)
    if magic != MAGIC:
        raise ValueError("Invalid magic: 0x{:08X} (expected 0x{:08X})".format(magic, MAGIC))
    
    header = {
        'magic': magic,
        'unknown1': read_uint32(data, 4),
        'data_offset': read_uint32(data, 8),
        'unknown2': read_uint32(data, 12),
        'unknown3': read_uint32(data, 16),
        'unknown4': read_uint32(data, 20),
        'node_count': read_uint32(data, 24),
        'node_offset': read_uint32(data, 28),
        'strings_count': read_uint32(data, 32),
        'strings_offset': read_uint32(data, 36),
    }
    
    # Read additional data segments (pairs of count,offset) until node_offset
    pos = 40
    header['additional_segments'] = []
    while pos < header['node_offset']:
        count = read_uint32(data, pos)
        offset = read_uint32(data, pos + 4)
        header['additional_segments'].append((count, offset))
        pos += 8
    
    return header


def read_huffman_tree(data, node_offset, node_count):
    """
    Read the Huffman tree from the binary data.
    Nodes are read in pairs: each pair creates a parent node.
    Returns the root node.
    """
    nodes = []
    left_node = None
    right_node = None
    node_value_counter = 0
    
    for i in range(node_count):
        value = read_uint32(data, node_offset + i * 4)
        
        # Check if this value already exists in our node list
        existing = None
        for n in nodes:
            if n.value == value:
                existing = n
                break
        
        current = existing if existing is not None else HuffmanNode(value=value)
        
        if left_node is None:
            left_node = current
        elif right_node is None:
            right_node = current
            if existing is None:
                nodes.append(right_node)
            
            # Create parent
            parent = HuffmanNode(value=node_value_counter, left=left_node, right=right_node)
            node_value_counter += 1
            root_node = parent
            
            left_node = None
            right_node = None
            
            nodes.append(parent)
        else:
            pass  # shouldn't happen
        
        if left_node is current and existing is None:
            nodes.append(current)
    
    return root_node, nodes


def decode_string(data, data_offset, bit_position, root_node):
    """
    Decode a single Huffman-encoded string starting at the given bit position.
    """
    chars = []
    bit_pos = bit_position
    total_bits = (len(data) - data_offset) * 8
    
    while bit_pos < total_bits:
        node = root_node
        while not node.is_leaf:
            byte_index = data_offset + (bit_pos // 8)
            bit_index = bit_pos % 8
            
            if byte_index >= len(data):
                return ''.join(chars)
            
            byte_val = data[byte_index]
            # Read bit (MSB first or LSB first?)
            # Based on Frostbite convention, bits are read MSB first
            bit = (byte_val >> (7 - bit_index)) & 1
            
            if bit == 0:
                node = node.left
            else:
                node = node.right
            
            bit_pos += 1
            
            if node is None:
                return ''.join(chars)
        
        # Check for end marker
        if node.value == 0xFFFFFFFF:
            break
        
        char_val = node.value >> 16
        if char_val == 0xFFFF:
            break
        
        chars.append(chr(char_val))
    
    return ''.join(chars)


def read_string_table(data, strings_offset, strings_count):
    """Read the string ID table: pairs of (stringId, bitPosition)."""
    entries = []
    for i in range(strings_count):
        offset = strings_offset + i * 8
        string_id = read_uint32(data, offset)
        bit_position = read_uint32(data, offset + 4)
        entries.append((string_id, bit_position))
    return entries


def decode_resource(filepath):
    """
    Decode a BioWare LocalizedStringResource file.
    Returns a dict of {string_id_hex: decoded_text}
    """
    with open(filepath, 'rb') as f:
        data = f.read()
    
    # The file has 16 bytes of metadata BEFORE the actual resource data
    # metadata: uint32 dataOffset, 12 bytes padding
    # But when exported from Frosty, the metadata might be included or not
    
    # Check if the magic is at offset 0 or offset 16
    magic_at_0 = read_uint32(data, 0)
    magic_at_16 = read_uint32(data, 16) if len(data) > 16 else 0
    
    meta_offset = 0
    if magic_at_0 == MAGIC:
        meta_offset = 0
        meta_data_offset = None
    elif magic_at_16 == MAGIC:
        meta_offset = 16
        meta_data_offset = read_uint32(data, 0)
    else:
        # Try to find magic anywhere in the first 64 bytes
        for off in range(0, min(64, len(data) - 4), 4):
            if read_uint32(data, off) == MAGIC:
                meta_offset = off
                break
        else:
            print("ERROR: Cannot find magic 0xD78B40EB in file!")
            return {}
    
    # Read from after metadata
    resource_data = data[meta_offset:]
    
    print("File: {} ({} bytes, meta_offset={})".format(os.path.basename(filepath), len(data), meta_offset))
    
    header = read_header(resource_data)
    print("  Header:")
    print("    data_offset: {}".format(header['data_offset']))
    print("    node_count: {}".format(header['node_count']))
    print("    node_offset: {}".format(header['node_offset']))
    print("    strings_count: {}".format(header['strings_count']))
    print("    strings_offset: {}".format(header['strings_offset']))
    print("    additional_segments: {}".format(header['additional_segments']))
    
    # Read Huffman tree
    root_node, all_nodes = read_huffman_tree(resource_data, header['node_offset'], header['node_count'])
    
    # Get supported characters
    leaf_chars = []
    for n in all_nodes:
        if n.is_leaf and n.value != 0xFFFFFFFF:
            char_val = n.value >> 16
            if char_val < 0xFFFF:
                leaf_chars.append(chr(char_val))
    
    print("  Supported characters: {} unique chars".format(len(leaf_chars)))
    if leaf_chars:
        sample = ''.join(sorted(leaf_chars)[:50])
        print("    Sample: {}".format(sample))
    
    # Read string table
    string_entries = read_string_table(resource_data, header['strings_offset'], header['strings_count'])
    print("  String entries: {}".format(len(string_entries)))
    
    if string_entries:
        print("  First 5 entries: {}".format(string_entries[:5]))
    
    # Decode strings
    results = {}
    decoded = 0
    errors = 0
    
    for string_id, bit_position in string_entries:
        try:
            text = decode_string(resource_data, header['data_offset'], bit_position, root_node)
            hex_id = "{:08X}".format(string_id)
            results[hex_id] = text
            decoded += 1
        except Exception as e:
            errors += 1
            if errors <= 5:
                print("  Error decoding string 0x{:08X}: {}".format(string_id, e))
    
    print("  Decoded: {} strings, Errors: {}".format(decoded, errors))
    
    # Show first few decoded strings
    count = 0
    for hex_id, text in results.items():
        if count >= 5:
            break
        preview = text[:80].replace('\n', '\\n')
        print("  [{}] {}".format(hex_id, preview))
        count += 1
    
    return results


if __name__ == '__main__':
    # Test with globalmaster.res (smaller file)
    test_file = r'E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T\mainmenu.res'
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
    
    results = decode_resource(test_file)
    
    if results:
        # Export to CSV
        out_csv = test_file.replace('.res', '_decoded.csv')
        with open(out_csv, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            for hex_id, text in sorted(results.items()):
                writer.writerow([hex_id, text])
        print("\nExported {} strings to {}".format(len(results), out_csv))
