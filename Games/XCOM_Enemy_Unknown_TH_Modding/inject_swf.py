import struct
import os

upk_path = r'E:\Mod_Workspace\XCom1_mod_workspace\Modded_Files\gfxfonts_ch_SF.upk'
swf_path = r'E:\Mod_Workspace\XCom1_mod_workspace\Modded_Files\fonts_ch.swf'
out_path = r'E:\Mod_Workspace\XCom1_mod_workspace\Modded_Files\gfxfonts_ch_SF_Modded.upk'

with open(upk_path, 'rb') as f:
    upk_data = bytearray(f.read())

with open(swf_path, 'rb') as f:
    swf_data = f.read()

# Offset where SWF data starts (after properties and length integer)
start_idx = 0x48A + 0x74
# Original SWF size
orig_swf_size = struct.unpack('<I', upk_data[start_idx-4:start_idx])[0]

print(f"Original SWF size: {orig_swf_size} bytes")
print(f"New SWF size: {len(swf_data)} bytes")

# Calculate the difference in size
size_diff = len(swf_data) - orig_swf_size

# 1. Update the size prefix just before the SWF data
upk_data[start_idx-4:start_idx] = struct.pack('<I', len(swf_data))

# 2. Update the SerialSize in the UPK Export Table
# In gfxfonts_ch_SF.upk.txt, fonts_ch Export object is index 3
# ExportTable offset is 0x27D (from header analysis or hex editing)
# Actually, the SerialSize of the SwfMovie object needs to be updated.
# The original SerialSize was 0x010222B5 (16917173).
# New SerialSize = 0x74 (properties) + len(swf_data)
new_serial_size = 0x74 + len(swf_data)

# Let's find where 0x010222B5 is stored in the UPK header.
# We will just search for struct.pack('<I', 16917173) in the first 2000 bytes.
orig_serial_size_bytes = struct.pack('<I', 16917173)
idx = upk_data.find(orig_serial_size_bytes, 0, 2000)

if idx != -1:
    print(f"Found SerialSize in Export Table at {hex(idx)}")
    upk_data[idx:idx+4] = struct.pack('<I', new_serial_size)
    
    # 3. Replace the SWF data
    final_upk = upk_data[:start_idx] + swf_data + upk_data[start_idx + orig_swf_size:]
    
    with open(out_path, 'wb') as f:
        f.write(final_upk)
    print(f"Successfully injected SWF! Saved to {out_path}")
else:
    print("Could not find SerialSize in Export Table!")
