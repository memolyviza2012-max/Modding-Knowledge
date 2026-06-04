import os
import sys
import struct
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from Crypto.Cipher import AES

AES_KEY = bytes.fromhex("014AEC0148FBDEE9640633AAB67521AAB4E1083A98F76FF33DDCF78DAD05BE66")
TARGET_CHUNK_INDEX = 8011

def align_to_16(size):
    return (size + 15) & ~15

def encode_offset_and_length(offset, length):
    return offset.to_bytes(5, byteorder='big') + length.to_bytes(5, byteorder='big')

def encode_compressed_block_entry(offset, compressed_size, uncompressed_size, compression_method_index):
    raw = (offset & ((1 << 40) - 1))
    raw |= (compressed_size & ((1 << 24) - 1)) << 40
    raw |= (uncompressed_size & ((1 << 24) - 1)) << 64
    raw |= (compression_method_index & 0xFF) << 88
    return raw.to_bytes(12, byteorder='little')

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def install_mod():
    root = tk.Tk()
    root.withdraw()
    
    messagebox.showinfo("Dead Island 2 Thai Mod Installer", "กรุณาเลือกโฟลเดอร์ Paks ของเกม Dead Island 2\n(ปกติจะอยู่ที่ ...\\DeadIsland2\\DeadIsland\\Content\\Paks)")
    
    paks_dir = filedialog.askdirectory(title="เลือกโฟลเดอร์ Paks ของเกม Dead Island 2")
    if not paks_dir:
        messagebox.showerror("Error", "ยกเลิกการติดตั้ง")
        return
        
    utoc_path = os.path.join(paks_dir, "pakchunk0-WindowsNoEditor.utoc")
    ucas_path = os.path.join(paks_dir, "pakchunk0-WindowsNoEditor.ucas")
    
    if not os.path.exists(utoc_path) or not os.path.exists(ucas_path):
        messagebox.showerror("Error", f"ไม่พบไฟล์ pakchunk0 ในโฟลเดอร์ที่เลือก!\nกรุณาเลือกโฟลเดอร์ Paks ที่ถูกต้อง")
        return
        
    # --- 1. Copy PAK text mod ---
    mod_dir = os.path.join(paks_dir, "~mods")
    os.makedirs(mod_dir, exist_ok=True)
    pak_src = resource_path("pakchunk_default-WindowsNoEditor_Thai_P.pak")
    pak_dst = os.path.join(mod_dir, "pakchunk_default-WindowsNoEditor_Thai_P.pak")
    
    if os.path.exists(pak_src):
        try:
            shutil.copy2(pak_src, pak_dst)
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถคัดลอกไฟล์แพตช์ได้: {e}")
            return
            
    # --- 2. Inject Font to IoStore ---
    font_src = resource_path("fonts_en.uasset")
    if not os.path.exists(font_src):
        messagebox.showerror("Error", "ไม่พบไฟล์ Font ต้นฉบับในตัวติดตั้ง")
        return
        
    with open(font_src, "rb") as f:
        mod_asset = f.read()
        
    mod_size = len(mod_asset)
    
    with open(utoc_path, "r+b") as f_utoc, open(ucas_path, "r+b") as f_ucas:
        utoc_data = bytearray(f_utoc.read())
        
        entry_count = struct.unpack_from('<I', utoc_data, 0x18)[0]
        compression_block_size = struct.unpack_from('<I', utoc_data, 0x2C)[0]
        
        chunk_ids_off = 144
        chunk_ol_off = chunk_ids_off + entry_count * 12
        compressed_blocks_off = chunk_ol_off + entry_count * 10
        
        target_ol_off = chunk_ol_off + TARGET_CHUNK_INDEX * 10
        old_ol = utoc_data[target_ol_off:target_ol_off+10]
        virtual_offset = int.from_bytes(old_ol[0:5], byteorder='big')
        old_length = int.from_bytes(old_ol[5:10], byteorder='big')
        
        first_block = virtual_offset // compression_block_size
        num_blocks = (old_length + compression_block_size - 1) // compression_block_size
        
        mod_blocks = (mod_size + compression_block_size - 1) // compression_block_size
        
        if mod_blocks > num_blocks:
            messagebox.showerror("Error", "ฟอนต์มีขนาดบล็อกเกินต้นฉบับ ไม่สามารถแพตช์ได้")
            return
            
        f_ucas.seek(0, 2)
        ucas_append_offset = align_to_16(f_ucas.tell())
        f_ucas.seek(ucas_append_offset)
        
        current_physical_offset = ucas_append_offset
        new_block_entries = []
        
        for i in range(num_blocks):
            b_start = i * compression_block_size
            b_end = min(b_start + compression_block_size, mod_size)
            if b_start < mod_size:
                b_data = mod_asset[b_start:b_end]
                uncomp_size = len(b_data)
                comp_size = uncomp_size
                
                padded_len = align_to_16(len(b_data))
                enc_buf = b_data + b'\x00' * (padded_len - len(b_data))
                cipher = AES.new(AES_KEY, AES.MODE_ECB)
                enc_data = cipher.encrypt(enc_buf)
                
                f_ucas.write(enc_data)
                
                new_block_entries.append(encode_compressed_block_entry(current_physical_offset, comp_size, uncomp_size, 0))
                current_physical_offset += len(enc_data)
            else:
                new_block_entries.append(encode_compressed_block_entry(0, 0, 0, 0))
                
        utoc_data[target_ol_off:target_ol_off+10] = encode_offset_and_length(virtual_offset, mod_size)
        
        for i, entry in enumerate(new_block_entries):
            idx = first_block + i
            utoc_data[compressed_blocks_off + idx*12 : compressed_blocks_off + (idx+1)*12] = entry
            
        f_utoc.seek(0)
        f_utoc.write(utoc_data)
        f_utoc.truncate()
            
    messagebox.showinfo("Success", "ติดตั้งม็อดภาษาไทยสำเร็จ!\nเข้าเล่นเกมได้เลยครับ")

if __name__ == "__main__":
    install_mod()
